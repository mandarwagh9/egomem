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
| 2026-06-14 | arkit-h3 n0.10_m0.0 | world-model | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.727/1.000 | 0.000/0.032 | +0.73/+0.97 | experiments/2026-06-13_arkit-oov/stdout_h3.log | naive 0.030/0.000; H3 PASS both seeds |
| 2026-06-14 | arkit-h3 n0.10_m0.0 | VLA | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 1.000/1.000 | 0.000/0.032 | +1.00/+0.97 | experiments/2026-06-13_arkit-oov/stdout_h3.log | naive 0.030/0.065; H3 PASS |
| 2026-06-14 | arkit-h3 n0.25_m0.0 | world-model | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.606/0.710 | 0.000/0.032 | +0.61/+0.68 | experiments/2026-06-13_arkit-oov/stdout_h3.log | naive 0.000/0.000; H3 PASS |
| 2026-06-14 | arkit-h3 n0.25_m0.0 | VLA | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.970/1.000 | 0.000/0.032 | +0.97/+0.97 | experiments/2026-06-13_arkit-oov/stdout_h3.log | naive 0.000/0.097; H3 PASS |
| 2026-06-14 | arkit-h3 n0.0_m0.3 | world-model | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.636/0.903 | 0.000/0.032 | +0.64/+0.87 | experiments/2026-06-13_arkit-oov/stdout_h3.log | naive 0.030/0.032; H3 PASS |
| 2026-06-14 | arkit-h3 n0.0_m0.3 | VLA | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.939/0.903 | 0.000/0.032 | +0.94/+0.87 | experiments/2026-06-13_arkit-oov/stdout_h3.log | naive 0.091/0.097; H3 PASS |
| 2026-06-14 | arkit-h3 n0.0_m0.6 | world-model | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.727/0.548 | 0.000/0.032 | +0.73/+0.52 | experiments/2026-06-13_arkit-oov/stdout_h3.log | naive 0.030/0.000; H3 PASS |
| 2026-06-14 | arkit-h3 n0.0_m0.6 | VLA | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.879/0.774 | 0.000/0.032 | +0.88/+0.74 | experiments/2026-06-13_arkit-oov/stdout_h3.log | naive 0.061/0.194; H3 PASS |
| 2026-06-14 | arkit-h3 n0.10_m0.3 | world-model | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.636/0.871 | 0.000/0.032 | +0.64/+0.84 | experiments/2026-06-13_arkit-oov/stdout_h3.log | naive 0.030/0.032; H3 PASS |
| 2026-06-14 | arkit-h3 n0.10_m0.3 | VLA | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.970/0.968 | 0.000/0.032 | +0.97/+0.94 | experiments/2026-06-13_arkit-oov/stdout_h3.log | naive 0.091/0.161; H3 PASS |
| 2026-06-14 | arkit-h3 n0.25_m0.6 | world-model | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.606/0.452 | 0.000/0.032 | +0.61/+0.42 | experiments/2026-06-13_arkit-oov/stdout_h3.log | WORST corner; naive 0.000/0.000; H3 PASS |
| 2026-06-14 | arkit-h3 n0.25_m0.6 | VLA | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.909/0.742 | 0.000/0.032 | +0.91/+0.74 | experiments/2026-06-13_arkit-oov/stdout_h3.log | WORST corner; naive 0.000/0.161; H3 PASS |
| 2026-06-14 | arkit-h4 assoc0.2 | world-model | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.061/0.387 | 0.000/0.032 | +0.06/+0.36 | experiments/2026-06-13_arkit-oov/stdout_h4.log | H4 REJECTED (seed0 <no-mem+20pp); naive 0.030/0.032 |
| 2026-06-14 | arkit-h4 assoc0.2 | VLA | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.182/0.742 | 0.000/0.032 | +0.18/+0.71 | experiments/2026-06-13_arkit-oov/stdout_h4.log | H4 REJECTED (seed0 <no-mem+20pp); naive 0.030/0.097 |
| 2026-06-14 | arkit-h4 assoc0.5 | world-model | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.000/0.065 | 0.000/0.032 | +0.00/+0.03 | experiments/2026-06-13_arkit-oov/stdout_h4.log | H4 REJECTED both seeds; collapses to floor; naive 0.000/0.000 |
| 2026-06-14 | arkit-h4 assoc0.5 | VLA | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.242/0.226 | 0.000/0.032 | +0.24/+0.19 | experiments/2026-06-13_arkit-oov/stdout_h4.log | H4 REJECTED both seeds; naive 0.030/0.097 |
| 2026-06-14 | arkit-h4 n0.10_m0.3_a0.2 | world-model | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.152/0.065 | 0.000/0.032 | +0.15/+0.03 | experiments/2026-06-13_arkit-oov/stdout_h4.log | H4 REJECTED both (realistic combined); naive 0.000/0.032 |
| 2026-06-14 | arkit-h4 n0.10_m0.3_a0.2 | VLA | egomem | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.303/0.355 | 0.000/0.032 | +0.30/+0.32 | experiments/2026-06-13_arkit-oov/stdout_h4.log | H4 REJECTED both; naive 0.061/0.129 |
| 2026-06-14 | arkit-h5 assoc0.2 | world-model | egomem-robust | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.182/0.581 | 0.000/0.032 | vs mean 0.061/0.387 | experiments/2026-06-13_arkit-oov/stdout_h5.log | median > mean; seed0 still <gate (unstable) |
| 2026-06-14 | arkit-h5 assoc0.2 | VLA | egomem-robust | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.364/0.774 | 0.000/0.032 | vs mean 0.182/0.742 | experiments/2026-06-13_arkit-oov/stdout_h5.log | median > mean |
| 2026-06-14 | arkit-h5 assoc0.5 | world-model | egomem-robust | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.182/0.129 | 0.000/0.032 | vs mean 0.000/0.065 | experiments/2026-06-13_arkit-oov/stdout_h5.log | median > mean but still REJECTED (heavy assoc) |
| 2026-06-14 | arkit-h5 assoc0.5 | VLA | egomem-robust | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.515/0.129 | 0.000/0.032 | vs mean 0.242/0.226 | experiments/2026-06-13_arkit-oov/stdout_h5.log | mixed; still REJECTED |
| 2026-06-14 | arkit-h5 n0.10_m0.3_a0.2 | world-model | egomem-robust | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.303/0.258 | 0.000/0.032 | vs mean 0.152/0.065 | experiments/2026-06-13_arkit-oov/stdout_h5.log | RECOVERS gate (CONFIRMED both) where mean failed |
| 2026-06-14 | arkit-h5 n0.10_m0.3_a0.2 | VLA | egomem-robust | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.485/0.581 | 0.000/0.032 | vs mean 0.303/0.355 | experiments/2026-06-13_arkit-oov/stdout_h5.log | RECOVERS gate (CONFIRMED both) |
| 2026-06-14 | arkit-h6 clean | world-model | egomem-assoc | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.485/0.613 | 0.000/0.032 | vs mean 0.697/1.000 | experiments/2026-06-13_arkit-oov/stdout_h6.log | spatial assoc REGRESSES clean (gating cost) |
| 2026-06-14 | arkit-h6 clean | VLA | egomem-assoc | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.727/0.677 | 0.000/0.032 | vs mean 1.000/1.000 | experiments/2026-06-13_arkit-oov/stdout_h6.log | regresses clean |
| 2026-06-14 | arkit-h6 assoc0.2 | world-model | egomem-assoc | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.394/0.355 | 0.000/0.032 | vs mean 0.061/0.387; median 0.182/0.581 | experiments/2026-06-13_arkit-oov/stdout_h6.log | CONFIRMED both (only variant to pass pure assoc0.2) |
| 2026-06-14 | arkit-h6 assoc0.2 | VLA | egomem-assoc | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.424/0.613 | 0.000/0.032 | vs mean 0.182/0.742 | experiments/2026-06-13_arkit-oov/stdout_h6.log | CONFIRMED both |
| 2026-06-14 | arkit-h6 assoc0.5 | world-model | egomem-assoc | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.212/0.194 | 0.000/0.032 | vs mean 0.000/0.065 | experiments/2026-06-13_arkit-oov/stdout_h6.log | improved but split (heavy assoc) |
| 2026-06-14 | arkit-h6 assoc0.5 | VLA | egomem-assoc | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.424/0.226 | 0.000/0.032 | vs mean 0.242/0.226 | experiments/2026-06-13_arkit-oov/stdout_h6.log | split |
| 2026-06-14 | arkit-h6 n0.10_m0.3_a0.2 | world-model | egomem-assoc | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.242/0.129 | 0.000/0.032 | vs median 0.303/0.258 | experiments/2026-06-13_arkit-oov/stdout_h6.log | median wins under noise (gating mis-routes) |
| 2026-06-14 | arkit-h6 n0.10_m0.3_a0.2 | VLA | egomem-assoc | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.485/0.355 | 0.000/0.032 | vs median 0.485/0.581 | experiments/2026-06-13_arkit-oov/stdout_h6.log | split; median better |
| 2026-06-14 | arkit-h6 n0.25_a0.2 | world-model | egomem-assoc | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.273/0.226 | 0.000/0.032 | vs median 0.333/0.226 | experiments/2026-06-13_arkit-oov/stdout_h6.log | high noise: all variants split |
| 2026-06-14 | arkit-h6 n0.25_a0.2 | VLA | egomem-assoc | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.667/0.548 | 0.000/0.032 | vs median 0.758/0.581 | experiments/2026-06-13_arkit-oov/stdout_h6.log | high noise |
| 2026-06-14 | arkit-h7 clean | world-model | egomem-verify | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.697/1.000 | 0.000/0.032 | == mean (no regression) | experiments/2026-06-13_arkit-oov/stdout_h7.log | trust-but-verify = EgoMem on clean |
| 2026-06-14 | arkit-h7 clean | VLA | egomem-verify | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 1.000/1.000 | 0.000/0.032 | == mean | experiments/2026-06-13_arkit-oov/stdout_h7.log | no clean regression (fixes H6) |
| 2026-06-14 | arkit-h7 assoc0.2 | world-model | egomem-verify | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.545/0.581 | 0.000/0.032 | best (mean 0.06/0.39, median 0.18/0.58, assoc 0.39/0.36) | experiments/2026-06-13_arkit-oov/stdout_h7.log | CONFIRMED both; BEST variant |
| 2026-06-14 | arkit-h7 assoc0.2 | VLA | egomem-verify | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.727/0.871 | 0.000/0.032 | best | experiments/2026-06-13_arkit-oov/stdout_h7.log | CONFIRMED both; BEST |
| 2026-06-14 | arkit-h7 assoc0.5 | world-model | egomem-verify | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.364/0.194 | 0.000/0.032 | best of all variants (still split) | experiments/2026-06-13_arkit-oov/stdout_h7.log | improved; heavy assoc still split |
| 2026-06-14 | arkit-h7 assoc0.5 | VLA | egomem-verify | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.485/0.290 | 0.000/0.032 | best | experiments/2026-06-13_arkit-oov/stdout_h7.log | split |
| 2026-06-14 | arkit-h7 n0.10_m0.3_a0.2 | world-model | egomem-verify | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.303/0.290 | 0.000/0.032 | CONFIRMED both (ties median) | experiments/2026-06-13_arkit-oov/stdout_h7.log | recovers realistic cell |
| 2026-06-14 | arkit-h7 n0.10_m0.3_a0.2 | VLA | egomem-verify | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.424/0.484 | 0.000/0.032 | CONFIRMED both | experiments/2026-06-13_arkit-oov/stdout_h7.log | recovers realistic cell |
| 2026-06-14 | arkit-h7 n0.25_a0.2 | world-model | egomem-verify | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV pos recall succ@0.5m | 0.182/0.419 | 0.000/0.032 | split (high noise hard for all) | experiments/2026-06-13_arkit-oov/stdout_h7.log | high noise |
| 2026-06-14 | arkit-h7 n0.25_a0.2 | VLA | egomem-verify | ARKitScenes-3dod REAL (14 scenes) | 0,1 | OOV dir succ@30deg | 0.636/0.677 | 0.000/0.032 | CONFIRMED both | experiments/2026-06-13_arkit-oov/stdout_h7.log | high noise |
| 2026-06-14 | arkit-h8 REAL-perception | combined | egomem | ARKitScenes REAL detector+LiDAR depth (3 gate-pass scenes, 26 targets) | n/a | OOV pos recall succ@0.5m | 0.154 | 0.000 | +0.154 | experiments/2026-06-13_arkit-oov/stdout_h8.log | REAL detector+depth, no oracle; REJECTED @0.5m (real noise >0.5m); naive 0.000 |
| 2026-06-14 | arkit-h8 REAL-perception | combined | egomem | ARKitScenes REAL detector+LiDAR depth (3 gate-pass scenes, 26 targets) | n/a | OOV pos recall succ@1.0m | 1.000 | 0.000 | +1.000 | experiments/2026-06-13_arkit-oov/stdout_h8.log | CONFIRMED @1.0m: real memory recall vs 0.000 baselines (naive 0.038) |
