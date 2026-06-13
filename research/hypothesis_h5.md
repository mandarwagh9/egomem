# EgoMem — Cycle 5 Hypothesis (H5): an association-robust aggregator recovers H4

**Date:** 2026-06-14. H4 found EgoMem's failure mode: a wrong-id detection writes
the true position under another id, and the per-id **mean** propagates it. H5 asks
whether a **robust aggregator** fixes it.

## Hypothesis H5

> Replacing EgoMem's per-id running **mean** with a per-id coordinate-wise
> **median** (`EgoMemRobust`) recovers out-of-view recall under association error:
> at `assoc_error = 0.2` it restores the ≥20 pp / ≥naive gate for both consumers
> (which plain mean-EgoMem failed at, H4), because a median tolerates a minority of
> mis-associated outlier positions that a mean does not.

### Metric + threshold

Identical (WM pos @0.5 m, VLA dir @30°; gate vs no-memory + 20 pp AND ≥ naive,
both consumers, both seeds). Compared head-to-head: `egomem` (mean, H4) vs
`egomem-robust` (median) on the H4 association sweep.

### Falsifier

`egomem-robust` does **not** beat plain `egomem` under association error, or still
fails the gate at `assoc_error = 0.2` — i.e. robust aggregation is insufficient and
explicit association handling is required.

### Plan

Prototype `EgoMemRobust` in the experiment (not the shipped library) first; re-run
the H4 assoc sweep with it as a 4th arm. **Promote to `lib/egomem` only if it
recovers the gate** (validate before shipping). If it works, it converts the H4
negative into a positive design contribution.
