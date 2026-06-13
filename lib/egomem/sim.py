"""Synthetic egocentric egomotion testbed + out-of-view recall benchmark.

This is the library-backed version of experiments/2026-06-13_oov-recall: it builds
the same scenes, drives the three memories through the public `egomem` API
(Observation / QueryState / Detection), trains the two tiny read-heads, and
reports the same out-of-view recall metrics. RNG order matches the original
experiment, so `egomem sim --seed 0` reproduces the committed seed-0 numbers.
"""
from __future__ import annotations

import math
import numpy as np

from .memory import Detection, Observation, QueryState, cam_pose_mat, to_cam, to_world, MEMORIES

# Simulator constants (identical to the experiment).
HALF_FOV = math.radians(30.0)
MAX_RANGE = 6.0
MIN_DEPTH = 0.2
DET_NOISE = 0.05
ROOM = 10.0
CAM_Z = 1.2
STEP_LEN = 0.4
T_FRAMES = 30


def _visible(P_world, T):
    p = to_cam(P_world, T)
    x, y, z = p
    if z <= MIN_DEPTH or z > MAX_RANGE:
        return False, p
    if abs(math.atan2(x, z)) > HALF_FOV:
        return False, p
    return True, p


def gen_episode(rng, pose_drift=0.0):
    M = int(rng.integers(6, 11))
    obj_pos = np.column_stack([
        rng.uniform(0.5, ROOM - 0.5, M),
        rng.uniform(0.5, ROOM - 0.5, M),
        rng.uniform(0.3, 1.9, M),
    ])
    pos = np.array([rng.uniform(1.5, ROOM - 1.5), rng.uniform(1.5, ROOM - 1.5), CAM_Z])
    theta = rng.uniform(-math.pi, math.pi)
    dpos = np.zeros(3); dtheta = 0.0
    frames = []
    for t in range(T_FRAMES):
        T_true = cam_pose_mat(pos.copy(), theta)
        if pose_drift > 0:
            dtheta += rng.normal(0, pose_drift)
            dpos[:2] += rng.normal(0, pose_drift, 2)
            T_drift = cam_pose_mat(pos + dpos, theta + dtheta)
        else:
            T_drift = T_true
        dets = []
        for oid in range(M):
            vis, p_cam = _visible(obj_pos[oid], T_true)
            if vis:
                p_noisy = p_cam + rng.normal(0, DET_NOISE, 3)
                conf = float(np.clip(1.0 - p_cam[2] / MAX_RANGE, 0.1, 1.0))
                dets.append(Detection(category=f"obj{oid}", pos_cam=p_noisy, confidence=conf, obj_id=oid))
        frames.append((T_true, T_drift, dets))
        theta += rng.uniform(-0.4, 0.4)
        nxt = pos[:2] + STEP_LEN * np.array([math.cos(theta), math.sin(theta)])
        if not (0.5 < nxt[0] < ROOM - 0.5 and 0.5 < nxt[1] < ROOM - 0.5):
            theta += math.pi
            nxt = pos[:2] + STEP_LEN * np.array([math.cos(theta), math.sin(theta)])
            nxt = np.clip(nxt, 0.5, ROOM - 0.5)
        pos[:2] = nxt
    return obj_pos, frames


def build_samples(episodes, arm_name):
    X, Y_pos, Y_dir = [], [], []
    for obj_pos, frames in episodes:
        seen = set()
        for _, _, dets in frames[:-1]:
            for d in dets:
                seen.add(d.obj_id)
        T_now_true, T_now_drift, last_dets = frames[-1]
        vis_now = {d.obj_id for d in last_dets}
        mem = MEMORIES[arm_name]()
        for T_true, T_drift, dets in frames:
            mem.write(Observation(t=0, cam_pose=T_drift, detections=dets))
        recs = {r.obj_id: r for r in mem.query(QueryState(t=T_FRAMES - 1, cam_pose=T_now_drift, visible=last_dets))}
        for oid in sorted(seen - vis_now):
            true_cam = to_cam(obj_pos[oid], T_now_true)
            r = recs.get(oid)
            if r is None or r.in_view_now:
                feat = [0, 0, 0, 0.0, 0.0, 0.0]
            else:
                p = r.pos_cam_now
                feat = [p[0], p[1], p[2], r.confidence, 0.0, 1.0]
            X.append(feat); Y_pos.append(true_cam)
            d = true_cam / (np.linalg.norm(true_cam) + 1e-9)
            Y_dir.append(d)
    return np.array(X, np.float32), np.array(Y_pos, np.float32), np.array(Y_dir, np.float32)


def _train_eval(Xtr, Ytr, Xte, Yte, normalize_out, metric, seed, epochs=400):
    import torch, torch.nn as nn
    torch.manual_seed(seed)
    net = nn.Sequential(nn.Linear(6, 32), nn.ReLU(), nn.Linear(32, 32), nn.ReLU(), nn.Linear(32, 3))
    opt = torch.optim.Adam(net.parameters(), lr=1e-3)
    xt, yt = torch.tensor(Xtr), torch.tensor(Ytr)
    for _ in range(epochs):
        opt.zero_grad()
        out = net(xt)
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
    cos = np.clip((pred * Yte).sum(1), -1, 1)
    ang = np.degrees(np.arccos(cos))
    return float((ang <= 30.0).mean()), float(ang.mean())


def run(seed=0, n_train=200, n_test=100, pose_drift=0.0, epochs=400):
    """Run the full 3-arm x 2-consumer benchmark. Returns a results dict."""
    rng = np.random.default_rng(seed)
    train_eps = [gen_episode(rng, pose_drift) for _ in range(n_train)]
    test_eps = [gen_episode(rng, pose_drift) for _ in range(n_test)]
    results = {}
    for arm in MEMORIES:
        Xtr, Yp_tr, Yd_tr = build_samples(train_eps, arm)
        Xte, Yp_te, Yd_te = build_samples(test_eps, arm)
        wm_s, wm_e = _train_eval(Xtr, Yp_tr, Xte, Yp_te, False, "pos", seed, epochs)
        vl_s, vl_e = _train_eval(Xtr, Yd_tr, Xte, Yd_te, True, "dir", seed, epochs)
        results[arm] = dict(n_test_q=int(len(Xte)), wm_success=wm_s, wm_mean_err_m=wm_e,
                            vla_success=vl_s, vla_mean_err_deg=vl_e)
    nm, na, eg = results["no-memory"], results["naive"], results["egomem"]
    wm_pass = eg["wm_success"] >= nm["wm_success"] + 0.20 and eg["wm_success"] >= na["wm_success"]
    vla_pass = eg["vla_success"] >= nm["vla_success"] + 0.20 and eg["vla_success"] >= na["vla_success"]
    results["_h1"] = dict(wm_pass=wm_pass, vla_pass=vla_pass, H1="CONFIRMED" if (wm_pass and vla_pass) else "REJECTED")
    results["_config"] = dict(seed=seed, n_train=n_train, n_test=n_test, pose_drift=pose_drift)
    return results
