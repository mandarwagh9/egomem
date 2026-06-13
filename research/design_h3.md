# EgoMem — Cycle 3 Design (perception-robustness ablation, tests H3)

**Date:** 2026-06-14. Minimal extension of the Cycle-2 real-data harness. Same 14
ARKitScenes Validation scenes, same unchanged `egomem` library, same out-of-view
recall protocol and metrics. Only the detection-generation step is degraded.

## Change (one mechanism, two knobs)

In `experiments/2026-06-13_arkit-oov/arkit_loader.py`, where per-frame detections
are built from visible objects, add (seeded) degradation:
- `--det_noise σ` : `pos_cam += N(0, σ)` per detection (3D, metres).
- `--miss_rate p` : with prob `p`, drop a genuinely-visible detection that frame.

The degradation RNG is seeded by the run seed (so it composes with head-init
seeding and is reproducible). `det_noise=0, miss_rate=0` reproduces H2 exactly.
Visibility labeling (which objects are in/out of view, hence which are recall
targets and which are excluded as currently-visible) is computed from the TRUE
geometry and is **identical across arms and across degradation levels** — only the
*detections written into memory* are degraded. Ground-truth targets stay exact.
This isolates the effect of imperfect perception on the memory, fairly across arms.

## Sweep

- `det_noise ∈ {0.0, 0.10, 0.25}` m × `miss_rate ∈ {0.0, 0.3, 0.6}`, the corners
  + center of the grid (≥5 cells incl. the H2 baseline cell 0/0), 2 seeds each.
- Per cell: the 3-arm × 2-consumer success + the H3 gate verdict.

## Expectation (to be confirmed or killed by real numbers)

EgoMem averages detections per object across frames, so noise should average down
and partial misses should be tolerated as long as an object is detected in *some*
frame. The naive arm keeps only the last-seen single detection → should degrade
faster. So EgoMem's margin over naive may *widen* with noise (a strength), until
miss rates get high enough that objects are never detected (then all arms lose the
target). The breaking point = the front-end spec.

## Logging

`experiments/2026-06-13_arkit-oov/stdout_h3.log` + append RESULTS.md rows tagged
`exp_id = arkit-h3 noise{σ}_miss{p}`, dataset = ARKitScenes-3dod REAL. Real numbers
only; H2 (0/0) cell must match the committed H2 result as a consistency check.

## Out of scope (future)

Wrong-id association errors; a full real detector + monocular-depth front-end
(run once the robustness envelope is known); larger scene counts (GCP).
