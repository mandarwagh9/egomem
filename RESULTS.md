# RESULTS — EgoMem

**Append-only.** One row per experiment run. NEVER edit or delete a past row.
If a run was wrong, add a NEW row noting the correction. A number lands here
ONLY if this loop ran the code and captured raw output to `experiments/`.

## Schema

| Field | Meaning |
|---|---|
| `date` | run date (YYYY-MM-DD) |
| `exp_id` | matches the `experiments/<date>_<name>/` folder |
| `consumer` | which model consumed the memory (world-model / VLA / both / none) |
| `memory` | memory variant under test (none / raw-frame-buffer / flat-embedding / egomem-vX) |
| `dataset` | dataset + split + size actually used |
| `seed` | random seed |
| `metric` | the named metric from hypothesis.md |
| `value` | measured value (the real number) |
| `baseline_value` | the no-memory (or stated) baseline number |
| `delta` | value − baseline_value |
| `log` | path to raw stdout/config under `experiments/` |
| `notes` | one line: confirms / rejects / inconclusive + why |

## Rows

<!-- No experiments run yet. First row is appended in Phase 3 (EXPERIMENT). -->
| date | exp_id | consumer | memory | dataset | seed | metric | value | baseline_value | delta | log | notes |
|------|--------|----------|--------|---------|------|--------|-------|----------------|-------|-----|-------|
