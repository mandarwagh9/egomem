# egomem

A **model-agnostic memory layer for robotics** from egocentric video. One neutral
`write(obs) -> None` / `query(state) -> list[RecalledObject]` API, three
interchangeable implementations (`NoMemory`, `NaiveBuffer`, `EgoMem`). The memory
is non-parametric: written once from egocentric observations (RGB-derived
detections + depth + camera pose) and queried unchanged by any consumer — a
world-model state-predictor and a VLA policy alike.

This packages the validated method from `experiments/2026-06-13_oov-recall`
(see `../RESULTS.md`). Result in brief: with accurate camera pose, EgoMem lets a
tiny world-model head and a tiny VLA head recall out-of-view objects far better
than a no-memory or raw-buffer baseline (succ ≈1.0 vs ≤0.37 over 3 seeds); the
advantage is pose-quality-dependent (degrades under heavy localization drift).

## Install

```bash
pip install -e lib            # from the repo root
# or:  cd lib && pip install -e .
```

Requires Python ≥3.10, numpy, torch (CPU is fine).

## Run

```bash
egomem demo                       # fast end-to-end demo (small run)
egomem sim --seed 0               # full benchmark, reproduces RESULTS.md seed-0
egomem sim --seed 0 --pose-drift 0.15   # stress: heavy pose drift breaks WM recall
```

## Use the layer directly

```python
import numpy as np
from egomem import EgoMem, Observation, QueryState, Detection, cam_pose_mat

mem = EgoMem()
# write: an egocentric frame at pose T0 sees a cup 2 m ahead
T0 = cam_pose_mat([0, 0, 1.2], theta=0.0)
mem.write(Observation(t=0, cam_pose=T0,
                      detections=[Detection("cup", pos_cam=np.array([0., 0., 2.]), obj_id=1)]))

# query: later, the camera has turned 90 deg and the cup is out of view
T1 = cam_pose_mat([0, 0, 1.2], theta=np.pi / 2)
for rec in mem.query(QueryState(t=10, cam_pose=T1, visible=[], goal_category="cup")):
    print(rec.category, "recalled at (cam frame):", rec.pos_cam_now, "in_view:", rec.in_view_now)
```

`pos_cam_now` is the recalled object position re-expressed in the *querying*
camera frame, so any downstream model consumes an egocentric answer without
knowing the memory's internals.
