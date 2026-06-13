# EgoMem — Cycle 6 Hypothesis (H6): explicit spatial data association

**Date:** 2026-06-14. H5's median treats the *symptom* (outlier positions). H6
attacks the *root cause* of the H4 failure (wrong ids) with explicit **spatial
data association**: ignore the incoming id, route each detection to the nearest
world-space track (gating radius), aggregate by median, label each track by
majority-voted id.

## Hypothesis H6

> Explicit spatial association (`EgoMemAssoc`) recovers EgoMem's out-of-view recall
> under association error — restoring the ≥20 pp / ≥naive gate at `assoc_error=0.2`
> for both consumers and both seeds (which mean-EgoMem H4 and median-EgoMem H5 did
> not) — because under "right detection, wrong id" the true position routes the
> detection to the correct cluster regardless of the corrupt label.

### Metric/threshold

Identical; compared head-to-head vs `egomem` (mean) and `egomem-robust` (median)
across the H4/H5 cells plus a high-detection-noise cell to probe gating failure.

### Falsifier

`EgoMemAssoc` fails the gate at `assoc_error=0.2`, OR materially regresses clean /
low-association performance (re-association is not free).

## VERDICT: PARTIALLY CONFIRMED — a regime tradeoff (logged 2026-06-14)

Raw: `stdout_h6.log`; RESULTS.md `exp_id = arkit-h6 *`. 2-seed-mean WM/VLA:

| cell | mean | median | assoc | who wins |
|---|---|---|---|---|
| clean 0/0/0 | 0.85/1.00 | 0.85/1.00 | 0.55/0.70 | mean/median (assoc REGRESSES) |
| assoc 0.2 | 0.22/0.46 | 0.38/0.57 | 0.37/0.52 | **assoc** (only one CONFIRMED both seeds) |
| assoc 0.5 | 0.03/0.23 | 0.16/0.32 | 0.20/0.33 | assoc (still split) |
| noise0.10+miss0.3+assoc0.2 | 0.11/0.33 | 0.28/0.53 | 0.19/0.42 | **median** (assoc split) |
| noise0.25+assoc0.2 | 0.28/0.62 | 0.28/0.67 | 0.25/0.61 | median (all split) |

**Finding (honest, nuanced):** H6 is *partially* confirmed. Spatial association
uniquely recovers the gate under **pure** association error (assoc 0.2, both
seeds) — the standard fix works on the standard failure. But it (i) **regresses
clean data** (gating mis-routes some correctly-id'd detections) and (ii) is
**beaten by the median when detection noise is high** (noise moves detections
across gates). **No single aggregator dominates: pick by the bottleneck** —
median when detection-noise-limited, spatial association when id-swap-limited. A
noise-aware / appearance-gated hybrid is the real answer (future work).

**Shipping decision:** `EgoMemRobust` (median) was free on clean data → shipped
(H5). `EgoMemAssoc` regresses clean data → **NOT shipped as default**; kept as a
documented prototype in the experiment. (Promote only a noise-aware version.)
