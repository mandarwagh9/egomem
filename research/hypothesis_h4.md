# EgoMem — Cycle 4 Hypothesis (H4): robustness to association errors

**Date:** 2026-06-14. New falsifiable claim (one at a time). H3 removed the
"oracle exact positions" crutch by degrading detection *position* and *recall* —
EgoMem tolerated it. The last oracle aspect is **identity association**: H1–H3 all
assume each detection carries the correct object id. H4 tests whether EgoMem's
advantage survives *wrong* ids (tracker id-swaps / fragmentation).

This is the third real-world degradation axis: Cycle 1 mapped pose quality,
Cycle 3 mapped detection quality, H4 maps **association quality**.

## Hypothesis H4

> On real ARKitScenes scenes, EgoMem's out-of-view recall advantage (≥20 pp over
> no-memory AND ≥ naive, both consumers, both seeds) **survives realistic
> data-association error** — a per-detection probability `assoc_error` that the
> object's true position is written under *another* object's id (right detection,
> wrong track) — up to a characterized level.

### Knob

- **`assoc_error`** ∈ [0,1]: per detection, with this probability the `obj_id` is
  replaced by a random *different* object's id present in the scene. The true
  position is kept (right detection), but it is filed under the wrong identity —
  the standard tracker failure. Keying is by id, so a swap both (i) deprives the
  true object of that observation and (ii) corrupts the other object's running
  estimate.

### Metric + threshold (identical replication under association noise)

Out-of-view recall success; WM pos @0.5 m, VLA dir @30°; EgoMem ≥ no-memory + 20 pp
AND ≥ naive, both consumers, **both seeds** (a split verdict = not robust).

### Falsifier

EgoMem drops within 20 pp of no-memory, or below naive, for either consumer at a
realistic `assoc_error` level.

## VERDICT: REJECTED (logged 2026-06-14)

See `experiments/2026-06-13_arkit-oov/stdout_h4.log` and RESULTS.md
(`exp_id = arkit-h4 *`). EgoMem does **not** robustly survive association errors:
- `assoc_error=0.2`: split (seed0 FAIL WM 0.061 / VLA 0.182; seed1 pass) → not
  robust.
- `assoc_error=0.5`: REJECTED both seeds (egomem WM ≈ 0.03, VLA ≈ 0.23).
- combined realistic (det_noise 0.10, miss 0.3, assoc 0.2): REJECTED both seeds.

**Why (and why this differs from H3):** EgoMem averages positions per id. Zero-mean
detection noise averages *out* (H3 robust); a wrong id injects a *systematic* wrong
position that the averaging actively *propagates* (H4 fragile). **Correct data
association — not detector precision — is the binding constraint** for a
model-agnostic memory of this design. This is a clean, honest negative result and
a sharp spec for any perception front-end: invest in tracking/association quality,
not just detection accuracy. (A design response — confidence-weighted or
association-robust integration — is future work, Cycle 5.)
