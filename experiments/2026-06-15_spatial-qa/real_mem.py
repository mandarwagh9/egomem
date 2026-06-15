"""Build EgoMem memory from a REAL detector + real depth (no oracle positions/ids),
reusing the H8/H9 pipeline (arkit_detector.py). Returns a list of (category, world_pos)
that the spatial-QA renderer can turn into a memory summary — the fully no-oracle path.

__main__ validates it: prints the real-detector memory vs GT object categories per scene.
"""
import os, sys
import numpy as np

_AD = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "2026-06-13_arkit-oov"))
sys.path.insert(0, _AD)
import arkit_detector as AD  # noqa: E402


def real_memory(scene_dir, gate_frac=0.5, gate_med=1.6, track_gate=0.8):
    """Returns (tracks, gt, gate_info) or (None, gt, gate_info) if the scene fails the
    back-projection gate. tracks = [(voted_category, median_world_pos)]."""
    sc = AD.detect_scene(scene_dir)
    b = AD.pick_variant(sc)
    if b is None:
        return None, sc["gt"], None
    var, med, frac, n = b
    info = dict(variant=var[0], median=med, frac=frac, n=n)
    if not (frac >= gate_frac and med < gate_med):
        return None, sc["gt"], info
    vv = var
    world = []
    for (cat, u, v, Z, pose, fi) in sc["dets"]:
        pc = AD.backproj(u, v, Z, sc["intr"], vv[1], vv[2])
        world.append((AD.to_world(pc, pose), fi, cat, pc))
    tracks = []
    for tr in AD.form_tracks(world, gate=track_gate):
        cat = max(tr["cats"], key=tr["cats"].get)
        pos = np.median(np.array(tr["poss"]), axis=0)
        tracks.append((cat, pos))
    return tracks, sc["gt"], info


if __name__ == "__main__":
    import glob
    from collections import Counter
    WP = sys.argv[1] if len(sys.argv) > 1 else "C:/Users/Mandar/AppData/Local/Temp/arkit_scenes"
    dirs = sorted(d for d in glob.glob(os.path.join(WP, "*")) if os.path.isdir(d))
    dirs = [d for d in dirs if glob.glob(os.path.join(d, f"{os.path.basename(d)}_frames", "lowres_wide", "*.png"))]
    for sd in dirs[:6]:
        vid = os.path.basename(sd)
        tracks, gt, info = real_memory(sd)
        gtc = Counter(o["label"] for o in gt)   # gt is a list of {label,pos} dicts
        if tracks is None:
            print(f"[{vid}] GATE FAIL {info}  GT={dict(gtc)}")
            continue
        mc = Counter(c for c, _ in tracks)
        print(f"[{vid}] gate {info['variant']} frac={info['frac']:.2f} | "
              f"real-mem tracks={len(tracks)} {dict(mc)} | GT {dict(gtc)}")
