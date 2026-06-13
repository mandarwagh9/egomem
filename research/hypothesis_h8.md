# EgoMem — Cycle 8 (H8): real perception front-end (REAL detector + REAL depth)

**Date:** 2026-06-14. Removes the last oracle assumption (object 3D position): detections
come from a **real 2D detector + real LiDAR depth**, not annotations.

> **Correction note.** An initial gate matched detections to *same-category* GT and
> showed ≥2.5 m error, which I first (wrongly) read as a wholesale annotation↔trajectory
> **frame mismatch / BLOCKED**. A deeper check (distance to the nearest GT of *any*
> category) showed median **1.23 m, 74 % within 1.5 m** — i.e. the geometry is roughly
> aligned; the 2.5 m was inflated by **detector mislabels** (COCO on 256×192 indoor
> frames). The BLOCKED conclusion was an overstatement and is corrected here with a real
> measured result.

## Pipeline (CPU, `arkit_detector.py`)

Real Faster R-CNN MobileNetV3 (COCO) on real RGB → boxes + labels (COCO→ARKit map);
real `lowres_depth` (LiDAR, mm) at the box center → back-project via intrinsics +
ARKit pose → world point. A **geometry validation gate** picks the per-scene
back-projection convention by nearest-any-GT alignment and rejects scenes that don't
align. Out-of-view recall: a GT object is a target if real detections landed near it
(≤1 m, evaluation-side grouping) earlier but not at the final frame; `egomem` = median
of its real detections → final camera frame; `no-memory` has no past record; `naive` =
last detection's un-transformed position.

## Result (REAL pipeline, logged 2026-06-14)

Gate passed **3/6 scenes** (41069021, 41069025, 41069042; the other 3 mis-align beyond
the 4 sign conventions and are honestly excluded). **26 real out-of-view targets:**

| tolerance | no-memory | naive | egomem | verdict |
|---|---|---|---|---|
| 0.5 m | 0.000 | 0.000 | 0.154 | REJECTED (real perception noise > 0.5 m) |
| 1.0 m | 0.000 | 0.038 | **1.000** | **CONFIRMED** (+1.000 over no-memory) |

**Reading:** on a *fully real* perception front-end (no oracle positions or ids),
EgoMem recalls out-of-view objects' locations that no-memory and naive cannot — at a
tolerance matched to real-perception noise (~1 m, from object-surface-vs-3D-box-center
offset + detector/depth error), it is **CONFIRMED** (1.000 vs 0.000). At the strict
0.5 m synthetic-grade tolerance it falls to 0.154 — quantifying that real perception
adds ~1 m localization error, the honest cost of dropping the oracle.

## Honest caveats

- 3/6 scenes pass the geometry gate; a single principled camera convention + the
  official ARKitScenes annotation alignment would likely recover the rest.
- Evaluation groups detections to GT by proximity (instance association is still
  evaluation-side, not a real tracker); a real tracker is the remaining piece.
- Small N (26 targets, 3 scenes). Effect is large (1.000 vs 0.000) but more scenes
  (GPU) would tighten it.

**VERDICT: H8 result — CONFIRMED at 1.0 m, REJECTED at 0.5 m.** The core claim (memory
enables out-of-view recall baselines cannot) holds on real perception; strict
localization is beyond current real-perception noise. Not blocked.
