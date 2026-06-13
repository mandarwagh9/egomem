"""EgoMem Cycle 2 — real-data out-of-view recall on ARKitScenes 3dod.

Drives the UNCHANGED `egomem` library (NoMemory/NaiveBuffer/EgoMem) on real
iPhone/iPad egocentric scans: real ARKit VIO poses (`lowres_wide.traj`), real 3D
object boxes (`*_3dod_annotation.json`, OBB centroids in cm -> /100 m, same world
frame as the trajectory — verified), per-frame intrinsics (`.pincam`).

HARD GATE: a projection sanity check must pass (box centroids project in-image at
positive depth, with a sane per-object visibility pattern) BEFORE any recall
number is produced. Run with --gate_only to check a scene without downloading more.

Usage:
  python arkit_loader.py --scenes_dir /tmp/arkit_scenes --gate_only
  python arkit_loader.py --scenes_dir /tmp/arkit_scenes --seeds 0 1
"""
import argparse, glob, json, os, sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lib")))
from egomem import NoMemory, NaiveBuffer, EgoMem, Observation, QueryState, Detection  # noqa: E402

MEMORIES = {"no-memory": NoMemory, "naive": NaiveBuffer, "egomem": EgoMem}
SUBSAMPLE = 20
MAX_RANGE = 8.0


def rodrigues(r):
    th = np.linalg.norm(r)
    if th < 1e-9:
        return np.eye(3)
    k = r / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * (K @ K)


def load_poses(traj_path):
    """Official ARKitScenes convention -> camera->world 4x4 (= our cam_pose)."""
    poses = []
    for line in open(traj_path):
        t = line.split()
        if len(t) != 7:
            continue
        aa = np.array([float(t[1]), float(t[2]), float(t[3])])
        tr = np.array([float(t[4]), float(t[5]), float(t[6])])
        E = np.eye(4); E[:3, :3] = rodrigues(aa); E[:3, 3] = tr
        poses.append(np.linalg.inv(E))   # world<-camera (camera->world)
    return poses


def load_intrinsics(frames_dir):
    """.pincam = 'w h fx fy cx cy'; intrinsics ~constant -> use the median."""
    vals = []
    for p in glob.glob(os.path.join(frames_dir, "lowres_wide_intrinsics", "*.pincam")):
        vals.append([float(x) for x in open(p).read().split()])
    v = np.median(np.array(vals), axis=0)
    return dict(w=v[0], h=v[1], fx=v[2], fy=v[3], cx=v[4], cy=v[5])


def load_objects(ann_path):
    d = json.load(open(ann_path))
    objs = []
    for i, o in enumerate(d["data"]):
        c = np.array(o["segments"]["obb"]["centroid"], float) / 100.0   # cm -> m
        objs.append(dict(oid=i, label=o["label"], pos_world=c))
    return objs


def to_cam(P_world, T):
    R, c = T[:3, :3], T[:3, 3]
    return R.T @ (P_world - c)


# 4 projection conventions: forward axis sign x vertical flip.
CONVENTIONS = [
    ("fwd+z,v+", +1, +1), ("fwd+z,v-", +1, -1),
    ("fwd-z,v+", -1, +1), ("fwd-z,v-", -1, -1),
]


def project(p_cam, intr, fwd_sign, vflip):
    fwd = fwd_sign * p_cam[2]
    if fwd <= 1e-6:
        return None
    u = intr["fx"] * (p_cam[0] / fwd) + intr["cx"]
    v = intr["fy"] * ((vflip * p_cam[1]) / fwd) + intr["cy"]
    return u, v, fwd


def visible_objects(pose, objs, intr, conv):
    _, fwd_sign, vflip = conv
    vis = []
    for o in objs:
        pc = to_cam(o["pos_world"], pose)
        pr = project(pc, intr, fwd_sign, vflip)
        if pr is None:
            continue
        u, v, fwd = pr
        if 0 <= u < intr["w"] and 0 <= v < intr["h"] and fwd <= MAX_RANGE:
            vis.append(o["oid"])
    return set(vis)


def pick_convention(scene):
    """Gate: choose the projection convention with the most in-image visibility,
    require a sane pattern (objects visible in some-but-not-all frames)."""
    poses, objs, intr = scene["poses"], scene["objs"], scene["intr"]
    frames = poses[::SUBSAMPLE]
    best = None
    for conv in CONVENTIONS:
        counts = np.zeros(len(objs), int)
        for pose in frames:
            for oid in visible_objects(pose, objs, intr, conv):
                counts[oid] += 1
        total = int(counts.sum())
        n_obj_seen = int((counts > 0).sum())
        n_obj_partial = int(((counts > 0) & (counts < len(frames))).sum())
        score = total if (n_obj_seen >= max(2, len(objs) // 3)) else -1
        info = dict(conv=conv[0], total=total, n_obj_seen=n_obj_seen,
                    n_obj_partial=n_obj_partial, n_obj=len(objs), n_frames=len(frames))
        if best is None or score > best[0]:
            best = (score, conv, info)
    return best[1], best[2]


def degrade_scene(sc, det_noise, miss_rate, rng, assoc_error=0.0):
    """Precompute, ONCE per scene, the (possibly degraded) per-frame detection
    lists + the out-of-view recall targets. The SAME degraded detections are then
    fed to all three arms (fairness). Visibility/targets use TRUE geometry; only
    the detections written to memory are degraded. det_noise=0, miss_rate=0,
    assoc_error=0 reproduces H2 exactly.

    assoc_error: per-detection prob the track id is WRONG (right detection, wrong
    id) — the object's true position written under another object's id (tracker
    id-swap / fragmentation). Keying is by obj_id, so a swap both deprives the true
    object of that observation and corrupts the other."""
    poses, objs, intr, conv = sc["poses"], sc["objs"], sc["intr"], sc["conv"]
    frames = poses[::SUBSAMPLE]
    by_oid = {o["oid"]: o for o in objs}
    all_oids = list(by_oid)
    true_vis = [visible_objects(p, objs, intr, conv) for p in frames]
    det_frames = []
    for pose, vis in zip(frames, true_vis):
        dets = []
        for oid in sorted(vis):
            if miss_rate > 0 and rng.random() < miss_rate:
                continue
            pc = to_cam(by_oid[oid]["pos_world"], pose)
            if det_noise > 0:
                pc = pc + rng.normal(0, det_noise, 3)
            out_oid = oid
            if assoc_error > 0 and len(all_oids) > 1 and rng.random() < assoc_error:
                choices = [x for x in all_oids if x != oid]
                out_oid = int(choices[rng.integers(len(choices))])
            dets.append(Detection(category=by_oid[oid]["label"], pos_cam=pc, confidence=1.0, obj_id=out_oid))
        det_frames.append((pose, dets))
    seen = set().union(*true_vis[:-1]) if len(true_vis) > 1 else set()
    targets = sorted(seen - true_vis[-1])
    return dict(det_frames=det_frames, targets=targets, by_oid=by_oid, final=frames[-1], n_frames=len(frames))


def samples_from(arm_name, degr):
    """Run one memory arm over precomputed (degraded) detections -> (X, Ypos, Ydir)."""
    if degr["n_frames"] < 3:
        return [], [], []
    mem = MEMORIES[arm_name]()
    for pose, dets in degr["det_frames"]:
        mem.write(Observation(t=0, cam_pose=pose, detections=dets))
    last_dets = degr["det_frames"][-1][1]
    recs = {r.obj_id: r for r in mem.query(QueryState(t=degr["n_frames"] - 1, cam_pose=degr["final"], visible=last_dets))}
    X, Ypos, Ydir = [], [], []
    for oid in degr["targets"]:
        true_cam = to_cam(degr["by_oid"][oid]["pos_world"], degr["final"])
        r = recs.get(oid)
        if r is None or r.in_view_now:
            feat = [0, 0, 0, 0.0, 0.0, 0.0]
        else:
            p = r.pos_cam_now
            feat = [p[0], p[1], p[2], r.confidence, 0.0, 1.0]
        X.append(feat); Ypos.append(true_cam)
        Ydir.append(true_cam / (np.linalg.norm(true_cam) + 1e-9))
    return X, Ypos, Ydir


def train_eval(Xtr, Ytr, Xte, Yte, normalize_out, metric, seed, epochs=400):
    import torch, torch.nn as nn
    torch.manual_seed(seed)
    net = nn.Sequential(nn.Linear(6, 32), nn.ReLU(), nn.Linear(32, 32), nn.ReLU(), nn.Linear(32, 3))
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    xt, yt = torch.tensor(Xtr), torch.tensor(Ytr)
    for _ in range(epochs):
        opt.zero_grad(); out = net(xt)
        if normalize_out:
            out = out / (out.norm(dim=1, keepdim=True) + 1e-9)
            loss = (1 - (out * yt).sum(1)).mean()
        else:
            loss = ((out - yt) ** 2).sum(1).mean()
        loss.backward(); opt.step()
    with torch.no_grad():
        pred = net(torch.tensor(Xte)).numpy()
    if metric == "pos":
        err = np.linalg.norm(pred - Yte, axis=1)
        return float((err <= 0.5).mean()), float(err.mean())
    pred = pred / (np.linalg.norm(pred, axis=1, keepdims=True) + 1e-9)
    ang = np.degrees(np.arccos(np.clip((pred * Yte).sum(1), -1, 1)))
    return float((ang <= 30.0).mean()), float(ang.mean())


def load_scene(scene_dir):
    vid = os.path.basename(scene_dir.rstrip("/"))
    frames_dir = os.path.join(scene_dir, f"{vid}_frames")
    return dict(vid=vid,
                poses=load_poses(os.path.join(frames_dir, "lowres_wide.traj")),
                intr=load_intrinsics(frames_dir),
                objs=load_objects(os.path.join(scene_dir, f"{vid}_3dod_annotation.json")))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes_dir", required=True)
    ap.add_argument("--gate_only", action="store_true")
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1])
    ap.add_argument("--det_noise", type=float, default=0.0, help="Gaussian m on detection pos_cam (H3)")
    ap.add_argument("--miss_rate", type=float, default=0.0, help="per-frame detection drop prob (H3)")
    ap.add_argument("--assoc_error", type=float, default=0.0, help="per-detection wrong-id prob (H4)")
    args = ap.parse_args()

    scene_dirs = sorted(d for d in glob.glob(os.path.join(args.scenes_dir, "*")) if os.path.isdir(d))
    scenes = []
    for sd in scene_dirs:
        try:
            scenes.append(load_scene(sd))
        except Exception as e:
            print(f"skip {sd}: {e}")
    print(f"loaded {len(scenes)} scenes: {[s['vid'] for s in scenes]}")

    # ---- GATE ----
    print("\n=== projection validation gate (per scene) ===")
    convs = []
    for sc in scenes:
        conv, info = pick_convention(sc)
        sc["conv"] = conv
        convs.append(conv[0])
        ok = info["n_obj_seen"] >= max(2, info["n_obj"] // 3) and info["n_obj_partial"] >= 1
        print(f"  {sc['vid']}: conv={info['conv']:9s} objs_seen={info['n_obj_seen']}/{info['n_obj']} "
              f"partial={info['n_obj_partial']} total_vis={info['total']} frames={info['n_frames']} "
              f"-> {'PASS' if ok else 'FAIL'}")
        sc["gate_ok"] = ok
    n_ok = sum(s["gate_ok"] for s in scenes)
    chosen = max(set(convs), key=convs.count) if convs else None
    print(f"gate: {n_ok}/{len(scenes)} scenes pass; dominant convention = {chosen}")
    if n_ok < len(scenes) or args.gate_only:
        if n_ok < len(scenes):
            print("NOTE: not all scenes passed the gate.")
        if args.gate_only:
            return
    scenes = [s for s in scenes if s["gate_ok"]]
    if len(scenes) < 4:
        print(f"STATUS: BLOCKED — only {len(scenes)} scenes passed the gate; need >=4 for a train/test split.")
        return

    # ---- recall experiment (split by scene) ----
    degraded = (args.det_noise or args.miss_rate or args.assoc_error)
    tag = ("H2" if not degraded else
           f"H3/H4 det_noise={args.det_noise} miss_rate={args.miss_rate} assoc_error={args.assoc_error}")
    print(f"\n=== {tag} out-of-view recall (real ARKitScenes) ===")
    for seed in args.seeds:
        # degrade each scene ONCE (same degraded detections for all arms; reproducible)
        deg_rng = np.random.default_rng(1000 + seed)
        degr = {sc["vid"]: degrade_scene(sc, args.det_noise, args.miss_rate, deg_rng, args.assoc_error) for sc in scenes}
        split_rng = np.random.default_rng(seed)
        idx = split_rng.permutation(len(scenes))
        n_te = max(1, len(scenes) // 3)
        te = [scenes[i] for i in idx[:n_te]]; tr = [scenes[i] for i in idx[n_te:]]
        print(f"\n-- seed {seed}: {len(tr)} train / {len(te)} test scenes --")
        res = {}
        for arm in MEMORIES:
            def stack(split, k):
                arrs = [np.array(samples_from(arm, degr[s["vid"]])[k], np.float32).reshape(-1, 6 if k == 0 else 3) for s in split]
                return np.concatenate(arrs) if arrs else np.zeros((0, 6 if k == 0 else 3), np.float32)
            Xtr, Yp_tr, Yd_tr = stack(tr, 0), stack(tr, 1), stack(tr, 2)
            Xte, Yp_te, Yd_te = stack(te, 0), stack(te, 1), stack(te, 2)
            wm_s, wm_e = train_eval(Xtr, Yp_tr, Xte, Yp_te, False, "pos", seed)
            vl_s, vl_e = train_eval(Xtr, Yd_tr, Xte, Yd_te, True, "dir", seed)
            res[arm] = dict(ntr=len(Xtr), nte=len(Xte), wm_s=wm_s, wm_e=wm_e, vl_s=vl_s, vl_e=vl_e)
            print(f"  [{arm:9s}] train_q={len(Xtr):4d} test_q={len(Xte):4d} | "
                  f"WM succ={wm_s:.3f} err={wm_e:.2f}m | VLA succ={vl_s:.3f} err={vl_e:.1f}deg")
        nm, na, eg = res["no-memory"], res["naive"], res["egomem"]
        wm_pass = eg["wm_s"] >= nm["wm_s"] + 0.20 and eg["wm_s"] >= na["wm_s"]
        vl_pass = eg["vl_s"] >= nm["vl_s"] + 0.20 and eg["vl_s"] >= na["vl_s"]
        print(f"  check: WM {'PASS' if wm_pass else 'FAIL'} | VLA {'PASS' if vl_pass else 'FAIL'} -> "
              f"{'CONFIRMED' if (wm_pass and vl_pass) else 'REJECTED'}")


if __name__ == "__main__":
    main()
