# EgoMem — Cycle 3 Hypothesis (H3): robustness to imperfect perception

**Date:** 2026-06-14. New falsifiable claim (one at a time). H1 (synthetic) and H2
(real ARKitScenes) both used **oracle detections** — perfect object identity and
exact 3D position. The sharpest criticism of the whole result is therefore: *"of
course a store of exact positions works."* H3 attacks that directly by feeding
EgoMem **imperfect detections** and asking whether its advantage survives.

This maps the second real-world degradation axis. Cycle 1 mapped *pose* quality
(VIO drift); H3 maps *detection* quality (depth/box error + missed detections),
on the same real ARKitScenes geometry as H2.

## Hypothesis H3

> On real ARKitScenes scenes, EgoMem's out-of-view recall advantage over the
> no-memory and naive baselines (the ≥20 pp-over-no-memory AND ≥naive gate, both
> consumers) **survives realistic detection degradation** — per-frame detection
> position noise and a per-frame miss rate — up to a characterized level, because
> the layer accumulates evidence across frames (running mean per object) rather
> than trusting a single detection.

### Knobs (the degradation, applied to the oracle detections)

- **`det_noise`** (m): Gaussian noise added to each detection's camera-frame 3D
  position (stands in for monocular-depth + box-center error).
- **`miss_rate`** (∈[0,1]): probability a genuinely-visible object is NOT detected
  in a given frame (detector recall < 1).
- Association stays oracle (correct id when detected) — wrong-id association is a
  further axis, noted as out of scope for H3.

### Metric + threshold (identical — replication under degradation)

Out-of-view recall success; world-model pos @0.5 m, VLA dir @30°; EgoMem ≥
no-memory + 20 pp AND ≥ naive, **both consumers**, ≥2 seeds (seed drives both the
degradation RNG and head init).

### What supports vs kills H3

- **Supports:** EgoMem stays above the gate at realistic levels (e.g. `det_noise`
  ≈ 0.1 m, `miss_rate` ≈ 0.3) — and ideally beats naive by a WIDENING margin as
  noise grows (averaging vs single last-seen detection).
- **Falsifier:** EgoMem drops within 20 pp of no-memory, or below naive, for
  either consumer at a realistic degradation level.

### Why this matters (product-relevant)

The breaking point is a **spec for the perception front-end**: it tells Black
Robotics' pipeline what detection accuracy / recall EgoMem needs to remain useful,
before investing in a heavy real detector. A full real-detector run
(GroundingDINO/Detic + monocular depth) is the follow-on once the envelope is known.
