# EgoMem — Cycle 2 Hypothesis (H2): real-data replication

**Date:** 2026-06-13. New falsifiable claim (HARD RULE: one claim at a time; this
is a *new* hypothesis, not a goalpost move on H1). Cycle 1 confirmed H1 on a
synthetic egomotion testbed and found the advantage is localization-dependent.
H2 asks whether the *same* result survives on **real egocentric data**.

## Hypothesis H2

> On **real egocentric RGB-D scenes** (ARKitScenes 3dod: real iPhone/iPad
> trajectories, real ARKit VIO camera poses, real 3D object layouts), the *same*
> EgoMem layer — the unchanged `egomem` library from Cycle 1, written once per
> scene and queried unchanged by both consumers — improves **out-of-view object
> recall** over a no-memory baseline and a naive raw-frame buffer, for both a
> world-model position consumer and a VLA direction consumer.

### Metric + threshold (identical to H1 — this is a replication on real data)

- **Metric:** out-of-view recall **success rate**. World-model consumer:
  position within **0.5 m** (real meters). VLA consumer: direction within **30°**.
- **Threshold (supports H2):** EgoMem ≥ no-memory + **20 pp** AND EgoMem ≥ naive,
  **for both consumers**, pooled over the evaluated real scenes, ≥ 2 seeds of the
  read-head training.

### Falsifiers (any one kills H2)

1. No-memory within 20 pp of EgoMem on success for either consumer.
2. EgoMem ≤ naive for either consumer (real-pose store no better than raw buffer).
3. Gains for one consumer only.

### Interpretation hook (NOT part of the falsifiable claim)

Cycle 1 predicts EgoMem should work when localization is good and the precise
*position* consumer is the more pose-sensitive one. ARKit VIO poses are
globally consistent within a scene, so H2 is expected to **confirm** — most
robustly for the VLA (direction) consumer; the world-model (position) consumer is
the litmus test for real pose quality. If H2 fails specifically for the
world-model consumer, that is consistent with (not a rescue of) the Cycle-1
pose-drift boundary, and will be reported as such — but the verdict on H2 is set
purely by the threshold above.

### Distinction from H1 (what is genuinely new)

Real camera trajectories, real VIO poses (with real drift/noise), real object
layouts, real scene geometry and visibility patterns — replacing the synthetic
simulator. **Still oracle data association** (object identity + 3D box from
annotations); a fully real 2D detector + monocular depth is a further step
(Cycle 3, out of scope here). The advance is real *sensing/pose/geometry*.
