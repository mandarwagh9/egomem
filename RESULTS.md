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
| 2026-06-13 | 2026-06-13_oov-recall | world-model | no-memory | synth-egomotion (200tr/100te, 450 test q) | 0 | OOV pos recall succ@0.5m | 0.016 | 0.016 | 0.000 | experiments/2026-06-13_oov-recall/stdout_seed0.log | floor: out-of-view needs memory |
| 2026-06-13 | 2026-06-13_oov-recall | world-model | naive | synth-egomotion (200tr/100te, 450 test q) | 0 | OOV pos recall succ@0.5m | 0.027 | 0.016 | +0.011 | experiments/2026-06-13_oov-recall/stdout_seed0.log | raw buffer ~floor; no pose transform |
| 2026-06-13 | 2026-06-13_oov-recall | world-model | egomem | synth-egomotion (200tr/100te, 450 test q) | 0 | OOV pos recall succ@0.5m | 1.000 | 0.016 | +0.984 | experiments/2026-06-13_oov-recall/stdout_seed0.log | confirms H1: ≥no-mem+20pp and ≥naive |
| 2026-06-13 | 2026-06-13_oov-recall | VLA | no-memory | synth-egomotion (200tr/100te, 450 test q) | 0 | OOV dir succ@30deg | 0.280 | 0.280 | 0.000 | experiments/2026-06-13_oov-recall/stdout_seed0.log | floor = constant-prior direction |
| 2026-06-13 | 2026-06-13_oov-recall | VLA | naive | synth-egomotion (200tr/100te, 450 test q) | 0 | OOV dir succ@30deg | 0.371 | 0.280 | +0.091 | experiments/2026-06-13_oov-recall/stdout_seed0.log | below threshold |
| 2026-06-13 | 2026-06-13_oov-recall | VLA | egomem | synth-egomotion (200tr/100te, 450 test q) | 0 | OOV dir succ@30deg | 1.000 | 0.280 | +0.720 | experiments/2026-06-13_oov-recall/stdout_seed0.log | confirms H1: ≥no-mem+20pp and ≥naive |
