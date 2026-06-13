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
| 2026-06-13 | 2026-06-13_oov-recall | world-model | no-memory | synth-egomotion (200tr/100te, 432 test q) | 1 | OOV pos recall succ@0.5m | 0.009 | 0.009 | 0.000 | experiments/2026-06-13_oov-recall/stdout_seed1.log | floor |
| 2026-06-13 | 2026-06-13_oov-recall | world-model | naive | synth-egomotion (200tr/100te, 432 test q) | 1 | OOV pos recall succ@0.5m | 0.019 | 0.009 | +0.010 | experiments/2026-06-13_oov-recall/stdout_seed1.log | ~floor |
| 2026-06-13 | 2026-06-13_oov-recall | world-model | egomem | synth-egomotion (200tr/100te, 432 test q) | 1 | OOV pos recall succ@0.5m | 1.000 | 0.009 | +0.991 | experiments/2026-06-13_oov-recall/stdout_seed1.log | confirms H1 |
| 2026-06-13 | 2026-06-13_oov-recall | VLA | no-memory | synth-egomotion (200tr/100te, 432 test q) | 1 | OOV dir succ@30deg | 0.220 | 0.220 | 0.000 | experiments/2026-06-13_oov-recall/stdout_seed1.log | floor |
| 2026-06-13 | 2026-06-13_oov-recall | VLA | naive | synth-egomotion (200tr/100te, 432 test q) | 1 | OOV dir succ@30deg | 0.315 | 0.220 | +0.095 | experiments/2026-06-13_oov-recall/stdout_seed1.log | below threshold |
| 2026-06-13 | 2026-06-13_oov-recall | VLA | egomem | synth-egomotion (200tr/100te, 432 test q) | 1 | OOV dir succ@30deg | 1.000 | 0.220 | +0.780 | experiments/2026-06-13_oov-recall/stdout_seed1.log | confirms H1 |
| 2026-06-13 | 2026-06-13_oov-recall | world-model | no-memory | synth-egomotion (200tr/100te, 456 test q) | 2 | OOV pos recall succ@0.5m | 0.007 | 0.007 | 0.000 | experiments/2026-06-13_oov-recall/stdout_seed2.log | floor |
| 2026-06-13 | 2026-06-13_oov-recall | world-model | naive | synth-egomotion (200tr/100te, 456 test q) | 2 | OOV pos recall succ@0.5m | 0.009 | 0.007 | +0.002 | experiments/2026-06-13_oov-recall/stdout_seed2.log | ~floor |
| 2026-06-13 | 2026-06-13_oov-recall | world-model | egomem | synth-egomotion (200tr/100te, 456 test q) | 2 | OOV pos recall succ@0.5m | 0.998 | 0.007 | +0.991 | experiments/2026-06-13_oov-recall/stdout_seed2.log | confirms H1 |
| 2026-06-13 | 2026-06-13_oov-recall | VLA | no-memory | synth-egomotion (200tr/100te, 456 test q) | 2 | OOV dir succ@30deg | 0.232 | 0.232 | 0.000 | experiments/2026-06-13_oov-recall/stdout_seed2.log | floor |
| 2026-06-13 | 2026-06-13_oov-recall | VLA | naive | synth-egomotion (200tr/100te, 456 test q) | 2 | OOV dir succ@30deg | 0.265 | 0.232 | +0.033 | experiments/2026-06-13_oov-recall/stdout_seed2.log | below threshold |
| 2026-06-13 | 2026-06-13_oov-recall | VLA | egomem | synth-egomotion (200tr/100te, 456 test q) | 2 | OOV dir succ@30deg | 1.000 | 0.232 | +0.768 | experiments/2026-06-13_oov-recall/stdout_seed2.log | confirms H1 |
| 2026-06-13 | oov-recall drift0.05 | world-model | egomem | synth-egomotion + pose_drift=0.05/step | 0 | OOV pos recall succ@0.5m | 0.340 | 0.005 | +0.335 | experiments/2026-06-13_oov-recall/stdout_drift.log | PASS (naive 0.017); degraded but ≥no-mem+20pp & ≥naive |
| 2026-06-13 | oov-recall drift0.05 | VLA | egomem | synth-egomotion + pose_drift=0.05/step | 0 | OOV dir succ@30deg | 0.931 | 0.230 | +0.701 | experiments/2026-06-13_oov-recall/stdout_drift.log | PASS (naive 0.328) |
| 2026-06-13 | oov-recall drift0.05 | world-model | egomem | synth-egomotion + pose_drift=0.05/step | 1 | OOV pos recall succ@0.5m | 0.326 | 0.002 | +0.324 | experiments/2026-06-13_oov-recall/stdout_drift.log | PASS (naive 0.009) |
| 2026-06-13 | oov-recall drift0.05 | VLA | egomem | synth-egomotion + pose_drift=0.05/step | 1 | OOV dir succ@30deg | 0.906 | 0.266 | +0.640 | experiments/2026-06-13_oov-recall/stdout_drift.log | PASS (naive 0.307) |
| 2026-06-13 | oov-recall drift0.05 | world-model | egomem | synth-egomotion + pose_drift=0.05/step | 2 | OOV pos recall succ@0.5m | 0.310 | 0.000 | +0.310 | experiments/2026-06-13_oov-recall/stdout_drift.log | PASS (naive 0.028) |
| 2026-06-13 | oov-recall drift0.05 | VLA | egomem | synth-egomotion + pose_drift=0.05/step | 2 | OOV dir succ@30deg | 0.937 | 0.298 | +0.639 | experiments/2026-06-13_oov-recall/stdout_drift.log | PASS (naive 0.336) |
| 2026-06-13 | oov-recall drift0.15 | world-model | egomem | synth-egomotion + pose_drift=0.15/step | 0 | OOV pos recall succ@0.5m | 0.050 | 0.005 | +0.045 | experiments/2026-06-13_oov-recall/stdout_drift.log | FAIL (naive 0.017); <no-mem+20pp — heavy drift breaks position recall |
| 2026-06-13 | oov-recall drift0.15 | VLA | egomem | synth-egomotion + pose_drift=0.15/step | 0 | OOV dir succ@30deg | 0.494 | 0.230 | +0.264 | experiments/2026-06-13_oov-recall/stdout_drift.log | PASS (naive 0.328); direction survives |
| 2026-06-13 | oov-recall drift0.15 | world-model | egomem | synth-egomotion + pose_drift=0.15/step | 1 | OOV pos recall succ@0.5m | 0.048 | 0.002 | +0.046 | experiments/2026-06-13_oov-recall/stdout_drift.log | FAIL (naive 0.009) |
| 2026-06-13 | oov-recall drift0.15 | VLA | egomem | synth-egomotion + pose_drift=0.15/step | 1 | OOV dir succ@30deg | 0.507 | 0.266 | +0.241 | experiments/2026-06-13_oov-recall/stdout_drift.log | PASS (naive 0.307) |
| 2026-06-13 | oov-recall drift0.15 | world-model | egomem | synth-egomotion + pose_drift=0.15/step | 2 | OOV pos recall succ@0.5m | 0.072 | 0.000 | +0.072 | experiments/2026-06-13_oov-recall/stdout_drift.log | FAIL (naive 0.028) |
| 2026-06-13 | oov-recall drift0.15 | VLA | egomem | synth-egomotion + pose_drift=0.15/step | 2 | OOV dir succ@30deg | 0.557 | 0.298 | +0.259 | experiments/2026-06-13_oov-recall/stdout_drift.log | PASS (naive 0.336) |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | world-model | no-memory | ARKitScenes-3dod REAL (14 val scenes, 33 test q) | 0 | OOV pos recall succ@0.5m | 0.000 | 0.000 | 0.000 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | real data; floor |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | world-model | naive | ARKitScenes-3dod REAL (14 val scenes, 33 test q) | 0 | OOV pos recall succ@0.5m | 0.030 | 0.000 | +0.030 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | real data; ~floor |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | world-model | egomem | ARKitScenes-3dod REAL (14 val scenes, 33 test q) | 0 | OOV pos recall succ@0.5m | 0.697 | 0.000 | +0.697 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | H2 PASS; real ARKit poses; err 0.38m |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | VLA | no-memory | ARKitScenes-3dod REAL (14 val scenes, 33 test q) | 0 | OOV dir succ@30deg | 0.000 | 0.000 | 0.000 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | real data; floor |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | VLA | naive | ARKitScenes-3dod REAL (14 val scenes, 33 test q) | 0 | OOV dir succ@30deg | 0.030 | 0.000 | +0.030 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | real data; ~floor |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | VLA | egomem | ARKitScenes-3dod REAL (14 val scenes, 33 test q) | 0 | OOV dir succ@30deg | 1.000 | 0.000 | +1.000 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | H2 PASS; err 5.2deg |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | world-model | no-memory | ARKitScenes-3dod REAL (14 val scenes, 31 test q) | 1 | OOV pos recall succ@0.5m | 0.032 | 0.032 | 0.000 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | real data; floor |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | world-model | naive | ARKitScenes-3dod REAL (14 val scenes, 31 test q) | 1 | OOV pos recall succ@0.5m | 0.032 | 0.032 | 0.000 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | real data; floor |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | world-model | egomem | ARKitScenes-3dod REAL (14 val scenes, 31 test q) | 1 | OOV pos recall succ@0.5m | 1.000 | 0.032 | +0.968 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | H2 PASS; err 0.17m |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | VLA | no-memory | ARKitScenes-3dod REAL (14 val scenes, 31 test q) | 1 | OOV dir succ@30deg | 0.032 | 0.032 | 0.000 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | real data; floor |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | VLA | naive | ARKitScenes-3dod REAL (14 val scenes, 31 test q) | 1 | OOV dir succ@30deg | 0.032 | 0.032 | 0.000 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | real data; floor |
| 2026-06-14 | 2026-06-13_arkit-oov (H2) | VLA | egomem | ARKitScenes-3dod REAL (14 val scenes, 31 test q) | 1 | OOV dir succ@30deg | 1.000 | 0.032 | +0.968 | experiments/2026-06-13_arkit-oov/stdout_arkit.log | H2 PASS; err 4.7deg |
