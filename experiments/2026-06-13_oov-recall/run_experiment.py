"""
EgoMem — Phase 3 experiment: out-of-view object recall (object permanence under egomotion).

Tests H1 (research/hypothesis.md) on the synthetic egomotion testbed (research/design.md).
Three memory arms behind ONE neutral write/query API: no-memory, naive (raw-frame buffer,
no pose transform), EgoMem (pose-aware world-frame persistent object store).
Two tiny CPU read-heads consume the SAME memory unchanged:
  - world-model head: estimate the (occluded) object's 3D position in the current camera frame
  - VLA head:         predict the egocentric unit direction toward the (occluded) goal object

Run: python run_experiment.py --seed 0   (writes metrics.json; stdout is the raw log)

CPU only, deterministic. No fabricated numbers — every value printed is computed here.
"""
import argparse, json, math, os, sys
import numpy as np
import torch
import torch.nn as nn

# ----------------------------- geometry -----------------------------
def cam_basis(theta):
    f = np.array([math.cos(theta), math.sin(theta), 0.0])   # forward
    r = np.array([math.sin(theta), -math.cos(theta), 0.0])  # right (forward rotated -90 about z)
    u = np.array([0.0, 0.0, 1.0])                            # up
    return r, u, f

def cam_pose_mat(pos, theta):
    r, u, f = cam_basis(theta)
    R = np.column_stack([r, u, f])      # world<-camera rotation, cols = [right, up, forward]
    T = np.eye(4); T[:3, :3] = R; T[:3, 3] = pos
    return T

def extract(T):
    return T[:3, :3], T[:3, 3]          # R, c

def to_cam(P_world, T):                 # world point -> camera-frame coords (right, up, forward)
    R, c = extract(T)
    return R.T @ (P_world - c)

def to_world(p_cam, T):
    R, c = extract(T)
    return R @ p_cam + c

# ----------------------------- simulator -----------------------------
HALF_FOV = math.radians(30.0)   # 60 deg horizontal FOV
MAX_RANGE = 6.0
MIN_DEPTH = 0.2
DET_NOISE = 0.05
ROOM = 10.0
CAM_Z = 1.2
STEP_LEN = 0.4
T_FRAMES = 30

def visible(P_world, T):
    p = to_cam(P_world, T)                 # (right, up, forward)
    x, y, z = p
    if z <= MIN_DEPTH or z > MAX_RANGE:
        return False, p
    if abs(math.atan2(x, z)) > HALF_FOV:
        return False, p
    return True, p

def gen_episode(rng):
    M = int(rng.integers(6, 11))
    obj_pos = np.column_stack([
        rng.uniform(0.5, ROOM - 0.5, M),
        rng.uniform(0.5, ROOM - 0.5, M),
        rng.uniform(0.3, 1.9, M),
    ])
    pos = np.array([rng.uniform(1.5, ROOM - 1.5), rng.uniform(1.5, ROOM - 1.5), CAM_Z])
    theta = rng.uniform(-math.pi, math.pi)
    frames = []        # list of (cam_pose, detections[list of (oid, p_cam_noisy, conf)])
    for t in range(T_FRAMES):
        T_mat = cam_pose_mat(pos.copy(), theta)
        dets = []
        for oid in range(M):
            vis, p_cam = visible(obj_pos[oid], T_mat)
            if vis:
                p_noisy = p_cam + rng.normal(0, DET_NOISE, 3)
                conf = float(np.clip(1.0 - p_cam[2] / MAX_RANGE, 0.1, 1.0))
                dets.append((oid, p_noisy, conf))
        frames.append((T_mat, dets))
        # egomotion: smooth random walk, reflect at walls
        theta += rng.uniform(-0.4, 0.4)
        nxt = pos[:2] + STEP_LEN * np.array([math.cos(theta), math.sin(theta)])
        if not (0.5 < nxt[0] < ROOM - 0.5 and 0.5 < nxt[1] < ROOM - 0.5):
            theta += math.pi          # turn around
            nxt = pos[:2] + STEP_LEN * np.array([math.cos(theta), math.sin(theta)])
            nxt = np.clip(nxt, 0.5, ROOM - 0.5)
        pos[:2] = nxt
    return obj_pos, frames

# ----------------------------- the neutral memory API + 3 arms -----------------------------
# query() returns dict: oid -> dict(pos_cam_now(3,), conf, in_view)
class NoMemory:
    def write(self, T_mat, dets): pass
    def query(self, T_now, visible_dets):
        return {oid: dict(pos=p, conf=c, in_view=1.0) for oid, p, c in visible_dets}

class NaiveBuffer:           # raw frame buffer: store last-seen camera-frame pos, NO pose transform
    def __init__(self): self.last = {}
    def write(self, T_mat, dets):
        for oid, p, c in dets:
            self.last[oid] = (p.copy(), c)
    def query(self, T_now, visible_dets):
        out = {oid: dict(pos=p, conf=c, in_view=1.0) for oid, p, c in visible_dets}
        vis_ids = {oid for oid, _, _ in visible_dets}
        for oid, (p_old, c) in self.last.items():
            if oid not in vis_ids:
                out[oid] = dict(pos=p_old, conf=c, in_view=0.0)   # stale, wrong frame
        return out

class EgoMem:                # pose-aware world-frame persistent object memory
    def __init__(self): self.world = {}   # oid -> (mean_world_pos, count)
    def write(self, T_mat, dets):
        for oid, p, c in dets:
            Pw = to_world(p, T_mat)
            if oid in self.world:
                m, n = self.world[oid]
                self.world[oid] = ((m * n + Pw) / (n + 1), n + 1)
            else:
                self.world[oid] = (Pw, 1)
    def query(self, T_now, visible_dets):
        out = {oid: dict(pos=p, conf=c, in_view=1.0) for oid, p, c in visible_dets}
        vis_ids = {oid for oid, _, _ in visible_dets}
        for oid, (Pw, n) in self.world.items():
            if oid not in vis_ids:
                out[oid] = dict(pos=to_cam(Pw, T_now), conf=float(np.clip(0.5, 0.1, 1.0)), in_view=0.0)
        return out

ARMS = {"no-memory": NoMemory, "naive": NaiveBuffer, "egomem": EgoMem}

# ----------------------------- build (feature,target) sets per arm -----------------------------
# A "recall query" = an object out of view at the final frame but seen earlier in the episode.
def build_samples(episodes, arm_name):
    X, Y_pos, Y_dir = [], [], []
    for obj_pos, frames in episodes:
        seen = set()
        for _, dets in frames[:-1]:
            for oid, _, _ in dets:
                seen.add(oid)
        T_now, last_dets = frames[-1]
        vis_now = {oid for oid, _, _ in last_dets}
        mem = ARMS[arm_name]()
        for T_mat, dets in frames:
            mem.write(T_mat, dets)
        records = mem.query(T_now, last_dets)
        for oid in sorted(seen - vis_now):                    # out-of-view recall targets
            true_cam = to_cam(obj_pos[oid], T_now)            # ground-truth position now (noiseless)
            rec = records.get(oid)
            if rec is None:                                   # no-memory: empty record
                feat = [0, 0, 0, 0.0, 0.0, 0.0]
            else:
                p = rec["pos"]
                feat = [p[0], p[1], p[2], rec["conf"], rec["in_view"], 1.0]
            X.append(feat)
            Y_pos.append(true_cam)
            d = true_cam / (np.linalg.norm(true_cam) + 1e-9)
            Y_dir.append(d)
    return (np.array(X, np.float32), np.array(Y_pos, np.float32), np.array(Y_dir, np.float32))

# ----------------------------- tiny read-heads -----------------------------
class Head(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(6, 32), nn.ReLU(), nn.Linear(32, 32), nn.ReLU(), nn.Linear(32, 3))
    def forward(self, x): return self.net(x)

def train_head(Xtr, Ytr, normalize_out, epochs=400, lr=1e-3, seed=0):
    torch.manual_seed(seed)
    head = Head()
    opt = torch.optim.Adam(head.parameters(), lr=lr)
    xt, yt = torch.tensor(Xtr), torch.tensor(Ytr)
    for _ in range(epochs):
        opt.zero_grad()
        out = head(xt)
        if normalize_out:
            out = out / (out.norm(dim=1, keepdim=True) + 1e-9)
            loss = (1 - (out * yt).sum(1)).mean()              # 1 - cosine
        else:
            loss = ((out - yt) ** 2).sum(1).mean()             # MSE position
        loss.backward(); opt.step()
    return head

def eval_pos(head, X, Y, tol=0.5):
    with torch.no_grad():
        pred = head(torch.tensor(X)).numpy()
    err = np.linalg.norm(pred - Y, axis=1)
    return float((err <= tol).mean()), float(err.mean())

def eval_dir(head, X, Y, tol_deg=30.0):
    with torch.no_grad():
        out = head(torch.tensor(X)).numpy()
    out = out / (np.linalg.norm(out, axis=1, keepdims=True) + 1e-9)
    cos = np.clip((out * Y).sum(1), -1, 1)
    ang = np.degrees(np.arccos(cos))
    return float((ang <= tol_deg).mean()), float(ang.mean())

# ----------------------------- main -----------------------------
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n_train", type=int, default=200)
    ap.add_argument("--n_test", type=int, default=100)
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    train_eps = [gen_episode(rng) for _ in range(args.n_train)]
    test_eps = [gen_episode(rng) for _ in range(args.n_test)]

    print(f"=== EgoMem out-of-view recall | seed={args.seed} | "
          f"n_train={args.n_train} n_test={args.n_test} T={T_FRAMES} FOV=60deg ===")
    results = {}
    for arm in ARMS:
        Xtr, Yp_tr, Yd_tr = build_samples(train_eps, arm)
        Xte, Yp_te, Yd_te = build_samples(test_eps, arm)
        wm_head = train_head(Xtr, Yp_tr, normalize_out=False, seed=args.seed)
        vla_head = train_head(Xtr, Yd_tr, normalize_out=True, seed=args.seed)
        wm_succ, wm_err = eval_pos(wm_head, Xte, Yp_te)
        vla_succ, vla_err = eval_dir(vla_head, Xte, Yd_te)
        results[arm] = dict(n_train_q=int(len(Xtr)), n_test_q=int(len(Xte)),
                            wm_success=wm_succ, wm_mean_err_m=wm_err,
                            vla_success=vla_succ, vla_mean_err_deg=vla_err)
        print(f"[{arm:9s}] train_q={len(Xtr):4d} test_q={len(Xte):4d} | "
              f"WM(pos) success={wm_succ:.3f} mean_err={wm_err:.3f}m | "
              f"VLA(dir) success={vla_succ:.3f} mean_err={vla_err:.1f}deg")

    # H1 threshold check: EgoMem >= no-memory + 0.20 AND EgoMem >= naive, for BOTH consumers
    nm, na, eg = results["no-memory"], results["naive"], results["egomem"]
    def check(metric):
        return (eg[metric] >= nm[metric] + 0.20) and (eg[metric] >= na[metric])
    wm_pass, vla_pass = check("wm_success"), check("vla_success")
    h1 = wm_pass and vla_pass
    print("\n--- H1 threshold check (EgoMem >= no-memory + 20pp AND >= naive) ---")
    print(f" world-model consumer: egomem={eg['wm_success']:.3f} no-mem={nm['wm_success']:.3f} "
          f"naive={na['wm_success']:.3f} -> {'PASS' if wm_pass else 'FAIL'}")
    print(f" VLA consumer:         egomem={eg['vla_success']:.3f} no-mem={nm['vla_success']:.3f} "
          f"naive={na['vla_success']:.3f} -> {'PASS' if vla_pass else 'FAIL'}")
    print(f" H1 (both consumers): {'CONFIRMED' if h1 else 'REJECTED'}")

    out = dict(seed=args.seed, config=dict(n_train=args.n_train, n_test=args.n_test,
               T_frames=T_FRAMES, half_fov_deg=30.0, max_range=MAX_RANGE, det_noise=DET_NOISE,
               tol_pos_m=0.5, tol_ang_deg=30.0, threshold_pp=20),
               results=results, wm_pass=wm_pass, vla_pass=vla_pass, H1=("CONFIRMED" if h1 else "REJECTED"))
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, f"metrics_seed{args.seed}.json"), "w") as fh:
        json.dump(out, fh, indent=2)
    print(f"\nwrote metrics_seed{args.seed}.json")

if __name__ == "__main__":
    main()
