"""EgoMem Cycle 8 (H8) — REAL perception front-end on ARKitScenes (no oracle association).

Replaces oracle 3D boxes with: a real 2D detector (torchvision Faster R-CNN
MobileNetV3, COCO) on the real RGB frames + the real LiDAR depth map, back-projected
via the per-frame intrinsics and ARKit pose to a world point. No object identities are
given; association is purely spatial (EgoMemAssoc-style clustering). Evaluated on
out-of-view recall of SINGLE-INSTANCE GT categories (unambiguous query-by-category),
against the annotated 3D boxes.

HARD GATE: a back-projection validation gate (detected objects must land near
same-category GT centroids) must pass before any recall number. Tries sign variants
to resolve the camera convention empirically; if none validates -> STATUS: BLOCKED.

CPU only. Usage: python arkit_detector.py --scenes_dir /tmp/arkit_scenes --gate_only
"""
import argparse, glob, json, os, sys
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lib")))
from egomem import to_world, to_cam  # noqa: E402

import torch  # noqa: E402
from torchvision.models.detection import (  # noqa: E402
    fasterrcnn_mobilenet_v3_large_fpn, FasterRCNN_MobileNet_V3_Large_FPN_Weights)

SUBSAMPLE = 20
SCORE_THRESH = 0.3
COCO2ARKIT = {"couch": "sofa", "chair": "chair", "dining table": "table",
              "tv": "tv_monitor", "oven": "oven", "sink": "sink", "bed": "bed",
              "toilet": "toilet", "refrigerator": "refrigerator", "bench": "sofa"}
# back-projection sign variants (y-up?, forward-sign) to resolve ARKit convention
VARIANTS = [("y+,z+", 1, 1), ("y-,z+", -1, 1), ("y+,z-", 1, -1), ("y-,z-", -1, -1)]

_MODEL = None
_CATS = None
_TF = None


def detector():
    global _MODEL, _CATS, _TF
    if _MODEL is None:
        w = FasterRCNN_MobileNet_V3_Large_FPN_Weights.DEFAULT
        _MODEL = fasterrcnn_mobilenet_v3_large_fpn(weights=w, box_score_thresh=SCORE_THRESH).eval()
        _CATS = w.meta["categories"]
        _TF = w.transforms()
    return _MODEL, _CATS, _TF


def rodrigues(r):
    th = np.linalg.norm(r)
    if th < 1e-9:
        return np.eye(3)
    k = r / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * (K @ K)


def load_poses_byts(traj_path):
    out = {}
    for line in open(traj_path):
        t = line.split()
        if len(t) != 7:
            continue
        aa = np.array([float(t[1]), float(t[2]), float(t[3])]); tr = np.array([float(t[4]), float(t[5]), float(t[6])])
        E = np.eye(4); E[:3, :3] = rodrigues(aa); E[:3, 3] = tr
        out[float(t[0])] = np.linalg.inv(E)
    return out


def load_intr(frames_dir):
    vals = [[float(x) for x in open(p).read().split()]
            for p in glob.glob(os.path.join(frames_dir, "lowres_wide_intrinsics", "*.pincam"))]
    v = np.median(np.array(vals), axis=0)
    return dict(w=v[0], h=v[1], fx=v[2], fy=v[3], cx=v[4], cy=v[5])


def load_gt(ann_path):
    d = json.load(open(ann_path))
    return [dict(label=o["label"], pos=np.array(o["segments"]["obb"]["centroid"], float) / 100.0)
            for o in d["data"]]


def _ts_of(path):
    base = os.path.basename(path)[:-4]
    return float(base.split("_")[-1])


def nearest(d, ts):
    k = min(d, key=lambda x: abs(x - ts))
    return k if abs(k - ts) < 0.1 else None


def detect_scene(scene_dir):
    """Return per-frame list of (arkit_category, u, v, depth_m, pose) real detections."""
    vid = os.path.basename(scene_dir.rstrip("/"))
    fdir = os.path.join(scene_dir, f"{vid}_frames")
    poses = load_poses_byts(os.path.join(fdir, "lowres_wide.traj"))
    intr = load_intr(fdir)
    gt = load_gt(os.path.join(scene_dir, f"{vid}_3dod_annotation.json"))
    rgbs = sorted(glob.glob(os.path.join(fdir, "lowres_wide", "*.png")))[::SUBSAMPLE]
    model, cats, tf = detector()
    dets = []  # (cat, u, v, depth, pose, frame_idx)
    for fi, rgb in enumerate(rgbs):
        ts = _ts_of(rgb)
        pk = nearest(poses, ts)
        if pk is None:
            continue
        depth_path = os.path.join(fdir, "lowres_depth", os.path.basename(rgb))
        if not os.path.exists(depth_path):
            continue
        depth = np.asarray(Image.open(depth_path)).astype(np.float32) / 1000.0  # mm -> m
        img = Image.open(rgb).convert("RGB")
        sx, sy = depth.shape[1] / img.size[0], depth.shape[0] / img.size[1]
        with torch.no_grad():
            out = model([tf(img)])[0]
        for box, lab, sc in zip(out["boxes"].tolist(), out["labels"].tolist(), out["scores"].tolist()):
            if sc < SCORE_THRESH:
                continue
            name = COCO2ARKIT.get(cats[lab])
            if name is None:
                continue
            u = 0.5 * (box[0] + box[2]); v = 0.5 * (box[1] + box[3])
            du, dv = int(u * sx), int(v * sy)
            r = 3
            patch = depth[max(0, dv - r):dv + r + 1, max(0, du - r):du + r + 1]
            patch = patch[(patch > 0.1) & (patch < 8.0)]
            if patch.size == 0:
                continue
            dets.append((name, u, v, float(np.median(patch)), poses[pk], fi))
    return dict(vid=vid, intr=intr, gt=gt, dets=dets, n_frames=len(rgbs))


def backproj(u, v, Z, intr, ysign, zsign):
    x = (u - intr["cx"]) * Z / intr["fx"]
    y = ysign * (v - intr["cy"]) * Z / intr["fy"]
    return np.array([x, y, zsign * Z])


def pick_variant(scene):
    """Gate (geometry validity): choose the back-projection convention whose real
    detections land nearest to *any* GT centroid (category-agnostic, since the COCO
    detector mislabels on 256x192 indoor frames). Returns (variant, median, frac<1.5m)."""
    gt = np.array([g["pos"] for g in scene["gt"]]); intr = scene["intr"]
    best = None
    for var in VARIANTS:
        _, ys, zs = var
        dists = [float(np.min(np.linalg.norm(gt - to_world(backproj(u, v, Z, intr, ys, zs), pose), axis=1)))
                 for (cat, u, v, Z, pose, fi) in scene["dets"]]
        if not dists:
            continue
        med = float(np.median(dists)); frac = float(np.mean(np.array(dists) < 1.5))
        if best is None or frac > best[2]:
            best = (var, med, frac, len(dists))
    return best


def single_instance_cats(gt):
    from collections import Counter
    c = Counter(g["label"] for g in gt)
    return {k for k, n in c.items() if n == 1}


def recall_eval(scenes, variant, tols=(0.5, 1.0)):
    """Real-detection out-of-view recall. Detections are assigned to GT objects by
    proximity (<=1 m, evaluation-side only — not fed to memory). A GT object is a
    target if it was detected earlier but is NOT detected near it at the final frame
    (out of view). egomem = median of that object's real detections -> final cam
    frame; no-memory has no record (final-frame only); naive = last detection's
    un-transformed cam position. Reported at multiple tolerances (real perception
    has surface-vs-center + detector noise ~1 m)."""
    GATE = 1.0
    out = {t: {"no-memory": [], "naive": [], "egomem": []} for t in tols}
    for sc in scenes:
        intr = sc["intr"]
        gt = sc["gt"]
        vv = sc.get("variant", variant)          # each scene uses its own gate-selected convention
        world = [(to_world(backproj(u, v, Z, intr, vv[1], vv[2]), pose), fi, pose, (u, v, Z, vv))
                 for (cat, u, v, Z, pose, fi) in sc["dets"]]
        if not world:
            continue
        maxfi = max(w[1] for w in world)
        final_pose = next(w[2] for w in world if w[1] == maxfi)
        for gi, g in enumerate(gt):
            obs = [w for w in world if np.linalg.norm(w[0] - g["pos"]) <= GATE]  # this object's real detections
            if not obs:
                continue
            seen_early = [w for w in obs if w[1] < maxfi]
            seen_final = [w for w in obs if w[1] == maxfi]
            if not seen_early or seen_final:        # need: seen earlier AND out of view now
                continue
            true_cam = to_cam(g["pos"], final_pose)
            est_world = np.median(np.array([w[0] for w in obs]), axis=0)         # egomem cluster median
            est_cam = to_cam(est_world, final_pose)
            last = max(obs, key=lambda w: w[1])
            lu, lv, lZ, lvv = last[3]
            naive_cam = backproj(lu, lv, lZ, intr, lvv[1], lvv[2])  # stale, no pose transform
            for t in tols:
                out[t]["no-memory"].append(0.0)
                out[t]["egomem"].append(1.0 if np.linalg.norm(est_cam - true_cam) <= t else 0.0)
                out[t]["naive"].append(1.0 if np.linalg.norm(naive_cam - true_cam) <= t else 0.0)
    return out


def form_tracks(world, gate=0.8):
    """GT-free online spatial association: each detection -> nearest track (median
    pos) within `gate`, else a new track. world = [(Pw, fi, cat, pc)] (pc = the
    detection's camera-frame point at its own frame)."""
    tracks = []
    for Pw, fi, cat, pc in sorted(world, key=lambda w: w[1]):
        best, bd = None, gate
        for tr in tracks:
            d = float(np.linalg.norm(np.median(np.array(tr["poss"]), axis=0) - Pw))
            if d < bd:
                bd, best = d, tr
        if best is None:
            best = dict(poss=[], fis=[], cats={}, last_pc=None, last_fi=-1); tracks.append(best)
        best["poss"].append(Pw); best["fis"].append(fi)
        best["cats"][cat] = best["cats"].get(cat, 0) + 1
        if fi >= best["last_fi"]:
            best["last_fi"], best["last_pc"] = fi, pc
    return tracks


def tracker_recall(scenes, variant, tols=(0.5, 1.0), gate=0.8, match=1.5):
    """H9: out-of-view recall with GT-free spatial tracking. GT used only to score
    (match a track to a GT object via its EARLY observations)."""
    out = {t: {"no-memory": [], "naive": [], "egomem": []} for t in tols}
    n_tracks = 0
    for sc in scenes:
        intr = sc["intr"]; gt = sc["gt"]
        vv = sc.get("variant", variant)
        world = [(to_world(backproj(u, v, Z, intr, vv[1], vv[2]), pose), fi, cat,
                  backproj(u, v, Z, intr, vv[1], vv[2]))
                 for (cat, u, v, Z, pose, fi) in sc["dets"]]
        if not world:
            continue
        maxfi = max(w[1] for w in world)
        final_pose = next(d[4] for d in sc["dets"] if d[5] == maxfi)
        tracks = form_tracks(world, gate)
        n_tracks += len(tracks)
        for tr in tracks:
            early = [p for p, fi in zip(tr["poss"], tr["fis"]) if fi < maxfi]
            at_final = any(fi == maxfi for fi in tr["fis"])
            if not early or at_final:
                continue                                 # need: seen earlier, out of view now
            early_pos = np.median(np.array(early), axis=0)
            gpos = min(gt, key=lambda g: np.linalg.norm(g["pos"] - early_pos))
            if np.linalg.norm(gpos["pos"] - early_pos) > match:
                continue                                 # spurious track (no GT) -> not a recall target
            true_cam = to_cam(gpos["pos"], final_pose)
            est_cam = to_cam(np.median(np.array(tr["poss"]), axis=0), final_pose)
            naive_cam = tr["last_pc"]                     # last detection, un-transformed (stale frame)
            for t in tols:
                out[t]["no-memory"].append(0.0)          # no final-frame detection of this track
                out[t]["egomem"].append(1.0 if np.linalg.norm(est_cam - true_cam) <= t else 0.0)
                out[t]["naive"].append(1.0 if np.linalg.norm(naive_cam - true_cam) <= t else 0.0)
    return out, n_tracks


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes_dir", required=True)
    ap.add_argument("--scenes", nargs="+", default=None, help="specific video_ids")
    ap.add_argument("--gate_only", action="store_true")
    ap.add_argument("--debug", action="store_true")
    ap.add_argument("--tracker", action="store_true", help="H9: GT-free spatial tracking (no proximity-to-GT grouping)")
    args = ap.parse_args()

    dirs = sorted(d for d in glob.glob(os.path.join(args.scenes_dir, "*")) if os.path.isdir(d))
    if args.scenes:
        dirs = [d for d in dirs if os.path.basename(d) in args.scenes]
    dirs = [d for d in dirs if os.path.exists(os.path.join(d, f"{os.path.basename(d)}_frames", "lowres_depth"))]
    print(f"scenes with RGB+depth: {[os.path.basename(d) for d in dirs]}")
    scenes = []
    for d in dirs:
        sc = detect_scene(d)
        print(f"  {sc['vid']}: {len(sc['dets'])} real detections over {sc['n_frames']} frames; "
              f"GT cats={sorted({g['label'] for g in sc['gt']})}")
        scenes.append(sc)

    if args.debug:
        sc = scenes[0]
        print("\n--- DEBUG ---")
        for g in sc["gt"]:
            if g["label"] in ("sofa", "table", "chair", "tv_monitor", "oven"):
                print("  GT", g["label"], np.round(g["pos"], 2))
        for var in VARIANTS:
            _, ys, zs = var
            ds = []
            for (cat, u, v, Z, pose, fi) in sc["dets"]:
                Pw = to_world(backproj(u, v, Z, sc["intr"], ys, zs), pose)
                same = [g for g in sc["gt"] if g["label"] == cat]
                if same:
                    ds.append(min(float(np.linalg.norm(Pw - g["pos"])) for g in same))
            if ds:
                print(f"  variant {var[0]}: n={len(ds)} median={np.median(ds):.2f}m min={min(ds):.2f}m frac<1m={np.mean(np.array(ds)<1):.2f}")
        for (cat, u, v, Z, pose, fi) in sc["dets"][:6]:
            Pw = to_world(backproj(u, v, Z, sc["intr"], 1, 1), pose)
            print(f"  det {cat:10s} uv=({u:.0f},{v:.0f}) Z={Z:.2f} cam_pos={np.round(pose[:3,3],2)} world={np.round(Pw,2)}")
        return

    print("\n=== back-projection validation gate ===")
    ok_scenes = []
    for sc in scenes:
        b = pick_variant(sc)
        if b is None:
            print(f"  {sc['vid']}: no matchable detections -> skip"); continue
        var, med, frac, n = b
        passed = frac >= 0.5 and med < 1.6
        print(f"  {sc['vid']}: best variant={var[0]} median_to_anyGT={med:.2f}m frac<1.5m={frac:.2f} (n={n}) "
              f"-> {'PASS' if passed else 'FAIL'}")
        sc["variant"] = var; sc["gate_ok"] = passed
        if passed:
            ok_scenes.append(sc)
    if not ok_scenes:
        print("STATUS: BLOCKED — back-projection gate failed on all scenes (convention/depth/intrinsics).")
        return
    if args.gate_only:
        return

    var = ok_scenes[0]["variant"]
    if args.tracker:
        print(f"\n=== H9 out-of-view recall (REAL detector + REAL depth + GT-FREE tracking) ===")
        res, ntr = tracker_recall(ok_scenes, var)
        tols = sorted(res)
        n = len(res[tols[0]]["egomem"])
        print(f"  GT-free tracks formed={ntr} | scored out-of-view targets={n} ({len(ok_scenes)} scenes)")
        if n == 0:
            print("STATUS: INCONCLUSIVE — no out-of-view targets after GT-free tracking.")
            return
        for t in tols:
            r = res[t]
            nm = float(np.mean(r["no-memory"])); na = float(np.mean(r["naive"])); eg = float(np.mean(r["egomem"]))
            verdict = "CONFIRMED" if (eg >= nm + 0.20 and eg >= na) else "REJECTED"
            print(f"  tol={t:.1f}m | no-memory={nm:.3f} naive={na:.3f} egomem={eg:.3f} | "
                  f"egomem-no_mem={eg-nm:+.3f} -> {verdict}")
        return
    print(f"\n=== H8 out-of-view recall (REAL detector + REAL depth) variant={var[0]} ===")
    res = recall_eval(ok_scenes, var)
    tols = sorted(res)
    n = len(res[tols[0]]["egomem"])
    if n == 0:
        print("STATUS: INCONCLUSIVE — no out-of-view recall targets from real detections.")
        return
    print(f"  targets={n} (real detections, {len(ok_scenes)} scene(s))")
    for t in tols:
        r = res[t]
        nm = float(np.mean(r["no-memory"])); na = float(np.mean(r["naive"])); eg = float(np.mean(r["egomem"]))
        verdict = "CONFIRMED" if (eg >= nm + 0.20 and eg >= na) else "REJECTED"
        print(f"  tol={t:.1f}m | no-memory={nm:.3f} naive={na:.3f} egomem={eg:.3f} | "
              f"egomem-no_mem={eg-nm:+.3f} -> {verdict}")


if __name__ == "__main__":
    main()
