# EgoMem — Cycle 8 (H8): real perception front-end — STATUS: BLOCKED (evaluation)

**Date:** 2026-06-14. Attempt to remove the last oracle assumption (object 3D
position) by deriving detections from a **real 2D detector + real LiDAR depth**,
not annotations.

## What was built (and works)

`experiments/2026-06-13_arkit-oov/arkit_detector.py`, CPU, no GPU needed:
- **Real detector:** torchvision Faster R-CNN MobileNetV3 (COCO) on the real
  ARKitScenes RGB frames — fires correctly on the scene's furniture (couch→sofa,
  tv→tv_monitor, dining table→table, chair, oven), plus realistic false positives.
- **Real depth:** ARKitScenes `lowres_depth` (uint16 mm; verified range to ~6 m
  across frames) sampled at each detection box center.
- **Back-projection:** pixel + depth + per-frame intrinsics (256×192, fx≈212,
  verified to match the image) + ARKit pose → world point. Math verified
  self-consistent (norms preserved); 4 sign conventions tried.
- **Spatial association** (no oracle ids) + **back-projection validation gate**
  before any number.

## The blocker (caught by the gate — exactly its purpose)

The **3dod OBB annotation frame does not coincide with the `lowres_wide.traj`
frame.** Evidence:
- GT sofa centroid x = 1.56 m lies **outside** the camera x-range [−3.01, 0.04]
  (the earlier containment check only passed under a 2 m margin, which masked it).
- Real depth-backprojected detections miss the nearest same-category GT centroid
  by **median ≥ 2.48 m, frac<1 m ≤ 0.01, under all four sign conventions**
  (`--debug` output). The machinery is sound; the two coordinate frames differ by
  a rigid (SE(3)) transform — the 3dod boxes are defined in the laser-scan frame,
  which ARKitScenes aligns to the trajectory via an official per-scene transform
  not applied here.

I did **not** fit a transform from detection↔GT correspondences: that would be
circular (fitting the thing that makes detections match GT, then "evaluating"
recall on it). Per the loop rule, no fabricated/forced number is reported.

## What is needed to unblock

Apply the official ARKitScenes `threedod` annotation→trajectory alignment (or load
the dataset-provided per-visit transform) so a depth-derived world point and a GT
centroid live in one frame; then the gate should pass and recall can be measured.

## Important: H2–H7 are UNAFFECTED

H2–H7 never compare a measurement to the GT in an absolute frame. Their
"detections" are `to_cam(centroid, pose)` and the memory stores/recalls via the
same centroids + real poses; the recall metric compares quantities computed
identically. So they are a **self-consistent** test of the memory mechanism under
**real camera trajectories and real relative object geometry**, valid regardless
of the annotation's absolute frame. Only H8 — which introduces an *independent*
real-depth measurement — exposes (and is blocked by) the frame mismatch.

**VERDICT: H8 BLOCKED on dataset annotation-frame alignment.** Pipeline built and
validated except for this; prototype committed for a future run.
