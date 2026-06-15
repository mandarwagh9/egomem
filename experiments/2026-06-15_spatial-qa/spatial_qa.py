"""EgoMem Cycle 11 (H11) — does EgoMem's spatial memory augment a REAL LLM/VLM on
episodic-spatial QA? (OpenEQA / Embodied-VideoAgent style, model-agnostic.)

For each real ARKitScenes scene: build EgoMem by replaying the trajectory over the GT
objects, generate episodic-spatial questions with ground-truth answers, then ask a real
frozen model (Gemini via google-genai, GOOGLE_API_KEY) the same questions under three
contexts:
  - no-memory : question only (the agent recalls nothing) -> ~chance
  - frame-only: only objects in the current (final) frontal view -> fails episodic/counting
  - egomem    : EgoMem's accumulated spatial summary (what it integrated over the traverse)

Reference frame is convention-free: "you" = final trajectory position, "forward" = travel
direction, left = up x forward. Answers are computed from GT; scoring is exact/tolerant.

Run: python spatial_qa.py --smoke           # 1 model call, check key+model
     python spatial_qa.py --n_scenes 8       # full eval
"""
import argparse, glob, json, math, os, re, sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lib")))
from egomem import EgoMem, Observation, QueryState, Detection, cam_pose_mat, to_cam, to_world

MAX_RANGE = 4.0
VOCAB = ["sofa", "chair", "table", "tv_monitor", "oven", "cabinet", "sink", "bed",
         "toilet", "refrigerator", "stove", "bathtub", "fireplace", "stool"]


def rodrigues(r):
    th = np.linalg.norm(r)
    if th < 1e-9:
        return np.eye(3)
    k = r / th
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + np.sin(th) * K + (1 - np.cos(th)) * (K @ K)


def load_traj(path):
    P = []
    for line in open(path):
        t = line.split()
        if len(t) != 7:
            continue
        aa = np.array([float(t[1]), float(t[2]), float(t[3])]); tr = np.array([float(t[4]), float(t[5]), float(t[6])])
        E = np.eye(4); E[:3, :3] = rodrigues(aa); E[:3, 3] = tr
        P.append(np.linalg.inv(E)[:3, 3])
    return np.array(P)


def load_objects(path):
    d = json.load(open(path))
    return [(o["label"], np.array(o["segments"]["obb"]["centroid"], float) / 100.0) for o in d["data"]]


def ego_frame(traj):
    final = traj[-1]
    k = max(1, len(traj) // 5)
    fwd = final - traj[-1 - k]
    fwd[2] = 0
    if np.linalg.norm(fwd) < 1e-6:
        fwd = np.array([1.0, 0, 0])
    fwd = fwd / np.linalg.norm(fwd)
    up = np.array([0, 0, 1.0])
    left = np.cross(up, fwd)
    return final, fwd, left


def describe(pos, final, fwd, left):
    v = pos - final
    dist = float(np.linalg.norm(v[:2]))
    ahead = float(v @ fwd)
    lft = float(v @ left)
    fb = "ahead" if ahead >= 0 else "behind"
    lr = "left" if lft >= 0 else "right"
    return dist, fb, lr


def build_egomem(objs, traj):
    """Replay the trajectory; observe objects within range; integrate into EgoMem.
    Returns the set of remembered object indices + EgoMem's world estimate per index."""
    mem = EgoMem()
    for p in traj[::5]:
        T = cam_pose_mat(np.array([p[0], p[1], 1.2]), 0.0)
        dets = []
        for i, (lab, P) in enumerate(objs):
            if np.linalg.norm(P[:2] - p[:2]) <= MAX_RANGE:
                dets.append(Detection(category=lab, pos_cam=to_cam(P, T), confidence=1.0, obj_id=i))
        mem.write(Observation(t=0, cam_pose=T, detections=dets))
    finalT = cam_pose_mat(np.array([traj[-1][0], traj[-1][1], 1.2]), 0.0)
    recalled = {}
    for r in mem.query(QueryState(t=0, cam_pose=finalT, visible=[])):
        recalled[r.obj_id] = to_world(r.pos_cam_now, finalT)   # EgoMem's integrated world estimate
    return recalled


def frame_only_idxs(objs, final, fwd, left):
    out = []
    for i, (lab, P) in enumerate(objs):
        d, fb, lr = describe(P, final, fwd, left)
        if d <= MAX_RANGE and fb == "ahead":     # in the current frontal view
            out.append(i)
    return out


def render_objs(idxs, objs, est, final, fwd, left):
    if not idxs:
        return "(no objects)"
    lines = []
    for i in sorted(idxs):
        P = est.get(i, objs[i][1])
        d, fb, lr = describe(P, final, fwd, left)
        lines.append(f"- {objs[i][0]}: {d:.1f} m away, {fb} and to your {lr}")
    return "\n".join(lines)


def gen_questions(objs, final, fwd, left, rng):
    from collections import Counter
    cats = Counter(l for l, _ in objs)
    qs = []
    # counting (top-2 present categories)
    for cat, n in cats.most_common(2):
        qs.append(dict(type="count", q=f"How many {cat} are in the scene? Answer with a single integer.",
                       gold=str(n)))
    # existence: one present, one absent
    present = list(cats)
    absent = [c for c in VOCAB if c not in cats]
    qs.append(dict(type="exists", q=f"Is there a {present[0]} in the scene? Answer yes or no.", gold="yes"))
    if absent:
        a = absent[int(rng.integers(len(absent)))]
        qs.append(dict(type="exists", q=f"Is there a {a} in the scene? Answer yes or no.", gold="no"))
    # direction: pick objects with a dominant axis
    uniq = [i for i, (l, _) in enumerate(objs) if cats[l] == 1]     # unambiguous singletons
    for i in uniq[:3]:
        d, fb, lr = describe(objs[i][1], final, fwd, left)
        qs.append(dict(type="lr", q=f"Is the {objs[i][0]} to your left or right? Answer left or right.", gold=lr))
        qs.append(dict(type="fb", q=f"Is the {objs[i][0]} ahead of you or behind you? Answer ahead or behind.", gold=fb))
    # closest to a reference singleton
    if len(uniq) >= 2:
        ref = uniq[0]
        others = [i for i in range(len(objs)) if i != ref]
        nearest = min(others, key=lambda j: np.linalg.norm(objs[j][1] - objs[ref][1]))
        qs.append(dict(type="closest",
                       q=f"Which object is closest to the {objs[ref][0]}? Answer with the object name.",
                       gold=objs[nearest][0]))
    return qs


def score(ans, gold, qtype):
    a = ans.lower().strip()
    g = gold.lower()
    if qtype == "count":
        m = re.search(r"-?\d+", a)
        return m is not None and m.group() == g
    if qtype == "exists":
        return (g == "yes") == (("yes" in a) and ("no such" not in a) and not a.startswith("no"))
    if qtype in ("lr", "fb", "closest"):
        if qtype == "closest":
            return g.replace("_", " ") in a or g in a
        return g in a
    return False


import time
_CLIENT = None
def _client():
    global _CLIENT
    if _CLIENT is None:
        from google import genai
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if os.environ.get("EGOMEM_VERTEX_PROJECT"):     # Vertex (ADC) path
            _CLIENT = genai.Client(vertexai=True, project=os.environ["EGOMEM_VERTEX_PROJECT"],
                                   location=os.environ.get("EGOMEM_VERTEX_LOCATION", "us-central1"))
        else:
            _CLIENT = genai.Client(api_key=key)
    return _CLIENT


def _gen(model, contents, max_retries=6):
    last = ""
    for attempt in range(max_retries):
        try:
            r = _client().models.generate_content(model=model, contents=contents)
            time.sleep(0.6)                              # gentle pacing to avoid 429
            return (r.text or "").strip()
        except Exception as e:
            last = str(e)
            if "429" in last or "RESOURCE_EXHAUSTED" in last:
                time.sleep(4 * (2 ** attempt))          # exp backoff: 4,8,16,32,64,128s
                continue
            raise
    raise RuntimeError(f"exhausted retries: {last[:120]}")


def ask(model, prompt):
    return _gen(model, prompt)


def ask_vision(model, text, image_paths):
    from google.genai import types
    parts = [types.Part.from_bytes(data=open(p, "rb").read(), mime_type="image/png") for p in image_paths]
    return _gen(model, [text] + parts)


PREAMBLE = ("You are an embodied agent that explored an indoor room. Answer the question "
            "concisely in the exact format requested. ")
CTX = {
    "no-memory": "You have no notes about what you saw.",
    "frame-only": "What you can currently see in front of you:\n{ctx}",
    "egomem": "Your spatial memory of the room (objects you saw while exploring, relative to "
              "where you are now):\n{ctx}",
    "frames": "Here are several photos you took while exploring this room, in temporal order. "
              "Study them to answer.",
}


def sample_frames(scene_dir, vid, k=5):
    fs = sorted(glob.glob(os.path.join(scene_dir, f"{vid}_frames", "lowres_wide", "*.png")))
    if not fs:
        return None
    idx = np.linspace(0, len(fs) - 1, min(k, len(fs))).astype(int)
    return [fs[i] for i in idx]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scenes_dir", default="/tmp/arkit_scenes")
    ap.add_argument("--n_scenes", type=int, default=8)
    ap.add_argument("--model", default="gemini-2.5-flash")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.smoke:
        print("smoke:", ask(args.model, "Reply with exactly: OK")); return

    dirs = sorted(d for d in glob.glob(os.path.join(args.scenes_dir, "*")) if os.path.isdir(d))
    dirs = [d for d in dirs if glob.glob(os.path.join(d, f"{os.path.basename(d)}_frames", "lowres_wide", "*.png"))]
    dirs = dirs[:args.n_scenes]
    conds = ["no-memory", "frame-only", "egomem", "frames"]
    tally = {c: dict(ok=0, n=0) for c in conds}
    by_type = {c: {} for c in conds}
    for sd in dirs:
        vid = os.path.basename(sd)
        fr = os.path.join(sd, f"{vid}_frames")
        try:
            traj = load_traj(os.path.join(fr, "lowres_wide.traj"))
            objs = load_objects(os.path.join(sd, f"{vid}_3dod_annotation.json"))
        except Exception as e:
            print("skip", vid, e); continue
        if len(objs) < 3 or len(traj) < 6:
            continue
        rng = np.random.default_rng(0)
        final, fwd, left = ego_frame(traj)
        est = build_egomem(objs, traj)
        mem_idxs = list(est)
        fo_idxs = frame_only_idxs(objs, final, fwd, left)
        ctx_txt = {"no-memory": "", "frame-only": render_objs(fo_idxs, objs, {}, final, fwd, left),
                   "egomem": render_objs(mem_idxs, objs, est, final, fwd, left)}
        frames = sample_frames(sd, vid, k=5)
        qs = gen_questions(objs, final, fwd, left, rng)
        print(f"\n[{vid}] {len(objs)} objs, mem={len(mem_idxs)} frame={len(fo_idxs)} "
              f"rgb={'yes' if frames else 'no'}, {len(qs)} questions")
        for q in qs:
            for c in conds:
                try:
                    if c == "frames":
                        if not frames:
                            continue            # no RGB for this scene -> don't tally
                        text = PREAMBLE + CTX["frames"] + "\n\nQuestion: " + q["q"]
                        ans = ask_vision(args.model, text, frames)
                    else:
                        prompt = PREAMBLE + CTX[c].format(ctx=ctx_txt[c]) + "\n\nQuestion: " + q["q"]
                        ans = ask(args.model, prompt)
                except Exception as e:
                    print("  API error:", str(e)[:80]); ans = ""
                ok = score(ans, q["gold"], q["type"])
                tally[c]["ok"] += ok; tally[c]["n"] += 1
                bt = by_type[c].setdefault(q["type"], [0, 0]); bt[0] += ok; bt[1] += 1
        # progress line
        print("  running acc:", {c: f"{tally[c]['ok']}/{tally[c]['n']}" for c in conds})

    print("\n=== H11 episodic-spatial QA — accuracy by condition (real model:", args.model, ") ===")
    for c in conds:
        n = tally[c]["n"]; acc = tally[c]["ok"] / n if n else 0
        bts = " ".join(f"{t}:{v[0]}/{v[1]}" for t, v in sorted(by_type[c].items()))
        print(f"  {c:10s} acc={acc:.3f} ({tally[c]['ok']}/{n})  [{bts}]")
    acc = {c: tally[c]["ok"] / max(1, tally[c]["n"]) for c in conds}
    eg, nm, fo, fr = acc["egomem"], acc["no-memory"], acc["frame-only"], acc["frames"]
    print(f"\n  egomem - no-memory = {eg-nm:+.3f} | egomem - frame-only(text) = {eg-fo:+.3f} | "
          f"egomem - frames(vision) = {eg-fr:+.3f}")
    print(f"  H11 (egomem >= no-memory + 0.20 AND >= frame-only): "
          f"{'CONFIRMED' if (eg >= nm + 0.20 and eg >= fo) else 'REJECTED'}")
    print(f"  H11b (egomem >= vision-frames + 0.10 -> structured memory beats raw VLM perception): "
          f"{'CONFIRMED' if eg >= fr + 0.10 else 'REJECTED'}")
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(dict(model=args.model, conds={c: tally[c] for c in conds}, by_type=by_type),
              open(os.path.join(here, "metrics.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
