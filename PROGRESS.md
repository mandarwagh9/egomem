# PROGRESS — EgoMem

> **This file is the loop's memory.** Read it first, every run. Trust the files, not your recollection.
> Each run: read state → do EXACTLY ONE bounded task → update this file → stop.

## Mission

Invent a **model-agnostic memory layer for robotics**: a neutral
`write` / `query` / `retrieve` layer that BOTH a **world model** AND a **VLA
policy** can call, fed by **egocentric human task video** (LeRobot v3 episodes,
depth, pose). Nothing like this exists as a real artifact yet — in the
literature, memory is baked inside specific VLA models or inside specific world
models, never offered as a paradigm-neutral layer. The closest research bridge
is the **Embodied VideoAgent** line of work (persistent scene memory from
egocentric video). The wedge: **egocentric human video as the substrate for a
buyer-side, model-agnostic memory.**

**End state:** a working library (`/lib`) + a research paper (`/paper`)
documenting a REAL, measured result that supports or kills the core claim.

## The one hard rule

No fabricated, estimated, or "expected" numbers. A number appears in RESULTS.md
or the paper ONLY if THIS loop ran the code and logged it. No run, no number.
Baselines are mandatory. Scale every experiment to the hardware actually
available — a tiny real run beats a large imaginary one.

## Repo map

| Path | Purpose |
|---|---|
| `research/` | lit map, gap statement, hypothesis |
| `experiments/` | one folder per run: `YYYY-MM-DD_name/` with raw logs, configs, seeds |
| `lib/` | the eventual library + CLI |
| `paper/` | `paper.md` + figures |
| `RESULTS.md` | append-only, one row per experiment run — NEVER edit a past row |
| `BIBLIOGRAPHY.md` | real sources only, with working links |

## Phase gates

1. **RESEARCH** — lit map; one-paragraph gap; ONE falsifiable hypothesis with a
   named metric, a threshold, and what would falsify it.
   **EXIT:** `research/hypothesis.md` committed with metric + threshold + falsifier.
2. **DESIGN** — spec the neutral interface (`write(obs) -> mem`,
   `query(state) -> retrieved_context`) + the data contract both a world model
   and a VLA can consume; smallest egocentric dataset; baselines (≥ no-memory +
   one naive memory).
   **EXIT:** `research/design.md` with API signatures, data contract, baselines,
   and the single experiment that tests the hypothesis.
3. **EXPERIMENT** — implement the smallest real version + baselines; run for
   real on real/sample data; raw logs to `experiments/<date>_<name>/`; one row
   to RESULTS.md.
   **EXIT:** hypothesis confirmed or rejected with logged evidence.
4. **ITERATE** — analyze the number; change ONE thing; rerun; until stable
   across ≥2 seeds or the iteration budget is hit.
   **EXIT:** a defended result (positive or clean negative).
5. **BUILD** — clean library + CLI; real install; real demo; honest error
   handling. **EXIT:** fresh clone installs and demo runs.
6. **PAPER** — full `paper.md`; every figure traces to a RESULTS.md row; report
   negatives honestly. **EXIT:** paper complete, zero TODO markers.
7. **PACKAGE** — README with repro steps, demo, BIBLIOGRAPHY; then append
   `STATUS: COMPLETE`.

**Iteration budget (phase 4):** max 6 experiment iterations before forcing a
defended-result writeup. Revisit if compute proves cheaper/dearer than expected.

---

## ===== ACTIVE: CYCLE 2 — real-data validation (H2) =====

Cycle 1 (synthetic) is COMPLETE (full loop, history below). Cycle 2 tests whether
the result survives on **real egocentric data**, reusing the unchanged `egomem`
library. New falsifiable claim: `research/hypothesis_h2.md` (H2 = same ≥20 pp /
≥naive gate, both consumers, on ARKitScenes 3dod). Design: `research/design_h2.md`.
Cycle-1 `landscape.md` still covers the field.

**CYCLE 2 COMPLETE — H2 CONFIRMED on real data.** Paper §7 (Table 3).
**CYCLE 3 COMPLETE — H3 CONFIRMED (perception robustness).** Paper §7.1 (Table 4).

### H3 result (perception-degradation ablation on real ARKitScenes, 2026-06-14)
Extended `arkit_loader.py` with `--det_noise` (Gaussian m on detection pos_cam) +
`--miss_rate` (per-frame detection dropout); degrade-once/consume-per-arm so all
arms see identical degraded detections (fair, reproducible; 0/0 reproduces H2
exactly — verified). Swept det_noise {0,0.10,0.25} × miss_rate {0,0.3,0.6}, 2 seeds.
- **H3 CONFIRMED in EVERY cell, both seeds, both consumers.** EgoMem WM (2-seed
  mean) 0.85 clean → 0.66 @0.25m → 0.64 @0.6 miss → **0.53 at worst corner**
  (0.25m + 0.6 miss); VLA 1.00 → 0.83 worst. Baselines stay ≤0.03 (no-mem) /
  ≤0.10 (naive). naive WM often DROPS to 0.00 under noise → EgoMem's margin
  **widens** with degradation (cross-frame averaging = the robustness).
- 12 RESULTS rows; raw `stdout_h3.log`. Paper §7.1 + abstract + conclusion +
  limitations updated; sections 1–9/3.x/7.1 consistent, zero TODOs.
- **Reading:** rebuts the "oracle positions" criticism — EgoMem tolerates ~0.25 m
  detection error + ~0.6 miss while keeping the advantage; that envelope is a spec
  a real detector + monocular depth can meet. Remaining oracle aspect = *identity*
  association (Cycle 4, future).

### H2 result (real ARKitScenes, logged 2026-06-14)
Implemented `experiments/2026-06-13_arkit-oov/arkit_loader.py`, resolved the
coordinate frame empirically (OBB centroids in **cm** → /100 m, same world frame
as the trajectory; 18/18 inside camera extent), passed the **projection
validation gate on 14/14 scenes** before any number. Drove the **unchanged**
`egomem` library on 14 real Validation scenes (real ARKit VIO poses, real 3D box
layouts), 2 head seeds:
- seed 0: egomem WM **0.697** / VLA **1.000** vs no-mem 0.000/0.000, naive
  0.030/0.030 → **H2 CONFIRMED** (both).
- seed 1: egomem WM **1.000** / VLA **1.000** vs no-mem/naive 0.032 →
  **H2 CONFIRMED** (both).
EgoMem errors: WM 0.17–0.38 m, VLA 4.7–5.2°. The world-model (position) consumer
shows the expected extra variance under real pose noise (0.697 at seed 0),
consistent with the Cycle-1 drift boundary. 12 rows in RESULTS.md.

### Honest limitations of H2 (carry into the paper)
- Small N (14 scenes, ~31–33 test queries/seed) — large, consistent effect but
  modest sample; more scenes (GCP) would tighten it.
- **Oracle data association** (object id + 3D box from annotations); no real 2D
  detector / monocular depth yet (Cycle 3).
- Projection convention auto-selected **per scene** by max in-image visibility
  (scenes picked differing fwd/v signs). This only affects visible/out-of-view
  labeling and is applied identically across all three arms, so the comparison is
  fair — but a single principled convention is cleaner (note as impl detail).

**CYCLE 4 COMPLETE — H4 REJECTED (association errors break EgoMem).** Paper §7.2
(Table 5, a reported negative result).

### H4 result (association-error ablation on real ARKitScenes, 2026-06-14)
Added `--assoc_error` (per-detection prob the true position is written under
another object's id — right detection, wrong track). Swept assoc {0.2, 0.5} alone
+ one realistic combined cell (noise0.10/miss0.3/assoc0.2), 2 seeds.
- **H4 REJECTED.** assoc 0.2 → split (seed0 FAIL WM 0.061/VLA 0.182; seed1 pass)
  = not robust. assoc 0.5 → REJECTED both (WM ≈0.03, VLA ≈0.23). Combined →
  REJECTED both. 6 RESULTS rows; raw `stdout_h4.log`.
- **Why (vs H3 positive):** EgoMem averages positions per id. Zero-mean *position*
  noise averages out (H3 robust); a wrong *id* injects a systematic wrong position
  the averaging propagates + starves the true id (H4 fragile). **Correct data
  association — not detector precision — is the binding constraint.**
- Honest negative result, fully reported (paper §7.2, abstract, conclusion,
  limitations). Sharp product spec: invest in tracking/association quality.

**CYCLE 5 COMPLETE — H5 partial mitigation; `EgoMemRobust` shipped.** Paper §7.3
(Table 6).

### H5 result (association-robust aggregator, 2026-06-14)
Prototyped + validated a median (vs mean) per-id aggregator, then promoted to the
library as `EgoMemRobust` (lib v0.2.0; NOT added to sim's MEMORIES so the 3-arm
reproduction is unchanged — verified `egomem sim --seed 0` identical).
- **Median = mean on clean data** (0.85/1.00, no regression) and **strictly better
  in every degraded cell**. **Recovers the gate** at the realistic combined cell
  (noise0.10+miss0.3+assoc0.2: CONFIRMED both seeds, where mean was REJECTED).
- Does NOT fully fix pure heavy association error (assoc0.5 still rejected; assoc0.2
  one-seed-unstable) → strict H5 not met, but a clear free win → shipped. 6 RESULTS
  rows; `stdout_h5.log`; paper §7.3 + abstract/conclusion.

**CYCLE 6 COMPLETE — H6 partial (regime tradeoff); EgoMemAssoc prototype, NOT shipped.**
Paper §7.4 (Table 7).

### H6 result (explicit spatial association, 2026-06-14)
Prototyped `EgoMemAssoc` (ignore incoming id; nearest-track gating @1 m; median agg;
majority-vote id) in the loader (5th arm). Swept clean + assoc + combined + high-noise.
- **Spatial assoc UNIQUELY clears the gate under pure assoc 0.2 (both seeds)** —
  where mean (H4) and median (H5) both failed. Root-cause fix works on root cause.
- **But regresses clean data** (WM 0.55 vs 0.85 — 1 m gate mis-routes some correct
  ids) and **loses to median under high detection noise** (noise shifts dets across
  gates). **No universal winner — regime tradeoff:** median if detection-noise-
  limited, spatial-assoc if id-swap-limited. 10 RESULTS rows; `stdout_h6.log`.
- **NOT shipped** (regresses clean) — kept as documented prototype; a noise-aware/
  appearance-gated hybrid is the real fix. Paper §7.4 + conclusion.

**CYCLE 7 COMPLETE — H7: `EgoMemVerify` RESOLVES the tradeoff; shipped (lib v0.3.0).**
Paper §7.5 (Table 8).

### H7 result (trust-but-verify, 2026-06-14)
`EgoMemVerify`: trust claimed id when spatially consistent; new id → spawn; reused-
but-inconsistent id → spatial re-association. Median agg, majority-vote id.
- **Identical to mean-EgoMem on clean data (no regression)** AND **best variant
  under pure assoc 0.2 (CONFIRMED both seeds, highest scores)** → **strict Pareto
  improvement** over mean/median/spatial-assoc. Matches median on combined/high-noise.
- Promoted to `lib/egomem` v0.3.0 as the **recommended aggregator** (MEMORIES kept
  at 3 arms; sim reproduction verified unchanged; smoke-tested). 10 RESULTS rows;
  `stdout_h7.log`; paper §7.5 + abstract/conclusion + lib README.
- Only extreme cells (assoc 0.5, noise 0.25) remain split — all variants degrade;
  better perception is the only remedy there.

**CYCLE 8 COMPLETE — H8 real-perception result: CONFIRMED @1.0 m / REJECTED @0.5 m.**
Paper §7.6 (Table 9). (Initial "BLOCKED/frame-mismatch" call was an overstatement,
corrected — see below.)

### H8 (2026-06-14): real detector + real LiDAR depth, NO oracle positions/ids
Built `arkit_detector.py` (CPU): real torchvision Faster R-CNN (COCO) on real RGB +
real `lowres_depth` (LiDAR) + intrinsics + ARKit pose → back-projected world points;
per-scene back-projection convention chosen by a geometry validation gate; out-of-view
recall on real detections (detections grouped to GT by proximity for eval only).
- **Correction:** a first gate matched detections to *same-category* GT → ≥2.5 m → I
  wrongly called it a frame mismatch / BLOCKED. A *nearest-any-GT* check showed median
  1.23 m, 74% <1.5 m — geometry is roughly aligned; the 2.5 m was **detector mislabels**.
  Corrected to a real measured result; no fabricated numbers were ever logged.
- **Result (3/6 scenes pass gate, 26 real targets):** tol 1.0 m — egomem **1.000** vs
  no-memory 0.000, naive 0.038 → **CONFIRMED** (+1.000). tol 0.5 m — egomem 0.154 →
  REJECTED (real-perception noise ~1 m: surface-vs-box-center + detector). 2 RESULTS
  rows; `stdout_h8.log`; paper §7.6.
- **Reading:** the core claim (memory enables out-of-view recall baselines cannot)
  holds **end-to-end on real perception** at a realistic tolerance; strict 0.5 m
  localization is beyond current real-perception noise — the honest cost of dropping
  the oracle.

**CYCLE 9 COMPLETE — H9: fully GT-free real pipeline; CONFIRMED @1.0 m.** Paper §7.6.

### H9 (2026-06-14): GT-free spatial tracker (no oracle anywhere)
Added an online spatial tracker (`--tracker`): detections associated to nearest
world-space track (else spawn), GT used ONLY to score (match track→GT via early obs;
MOT-style; spurious FP tracks excluded). Closes the H8 eval-side GT-grouping caveat.
- **Result (3 scenes, 56 self-formed tracks, 31 targets):** tol 1.0 m egomem **0.484**
  vs no-memory 0.000 / naive 0.000 → **CONFIRMED (+0.484)**; tol 0.5 m egomem 0.161 →
  REJECTED. 2 RESULTS rows; `stdout_h9.log`; paper §7.6.
- **Reading:** with NO oracle anywhere (real detector + real LiDAR depth + GT-free
  tracking), EgoMem recalls ~half of out-of-view objects within 1 m while both
  baselines recall ZERO. The drop from H8's 1.000 to 0.484 is the honest cost of real
  data association. The core claim survives the strictest, fully-real test.

**CYCLE 10 COMPLETE — H10: downstream TASK SUCCESS (the DD-proof headline).** Paper §8.

### H10 (2026-06-14): closed-loop long-horizon fetch — task completion, not recall
`experiments/2026-06-14_task-success/fetch_task.py`: scan-then-fetch — map a room, then
navigate to K=4 targets in order under FOV+range-limited sensing. Same rule-based
controller for all arms; differ only in what memory supplies for out-of-view targets.
- **Result (difficulty sweep, 3 seeds×200):** easy (room8/range6) egomem 1.000 vs
  no-mem 0.975 → +2.5 (REJECTED, search cheap); medium (11/5) 1.000 vs 0.205 → **+79.5**;
  hard (14/4) 1.000 vs 0.010 → **+99.0** (CONFIRMED). naive ≈ no-mem or worse.
- **Finding:** memory's task value **scales with partial observability**; in the
  realistic regime it lifts completion **~1% → 100%**. Converts the recall proxy
  (H1–H9) into a task-level number. 3 RESULTS rows; `stdout_fetch.log`; paper §8.
- **Strategic context:** this was the "harden the claim" ask — the headline is now
  "+X-point long-horizon task success", DD-proof, not a recall@tol proxy.

### Next (optional, refinements only)
Learned policy (vs rule-based controller); real-perception task-success (combine §8 with
§7.6 pipeline); stronger detector/tracker; larger-scale (GPU). No open scientific
questions in the core arc.

(Cycle-1 history below.)

---

## CURRENT PHASE = 7 (PACKAGE)

Phase 6 closed: `paper/paper.md` written in full (abstract, intro, related work,
method, experiments, results Table 1, pose-drift ablation Table 2, limitations,
conclusion, references, repro). Verified **zero TODO/placeholder markers**; every
table cell traces to a `RESULTS.md` row; the negative boundary (drift 0.15 rejects
H1 for the world-model consumer) is reported honestly.

### Next single task — finalize packaging, then mark COMPLETE
1. Rewrite the top-level `README.md` into a proper package front page: one-line
   pitch, the headline result (with the honest localization caveat), install +
   **reproduce** commands (`pip install -e lib`; `egomem demo`; `egomem sim
   --seed 0`), and links to `paper/paper.md`, `RESULTS.md`, `BIBLIOGRAPHY.md`,
   `research/`. The `egomem demo` CLI is the demo (no gif needed; note it as the
   one-command demo).
2. Sanity-check the repo: BIBLIOGRAPHY present (7 sources), demo command runs,
   `.gitignore` keeps egg-info/artifacts out.
3. Append `STATUS: COMPLETE` to the bottom of this file.
Phase 7 EXIT: README has repro steps, the demo runs, BIBLIOGRAPHY is in place →
STATUS: COMPLETE.

(Defended-result detail retained below.)

Phase 4 closed with a **defended result** (3 seeds clean + a characterized
stress boundary). See RESULTS.md (24 rows) and `experiments/2026-06-13_oov-recall/`.

### Defended result (stated plainly)
- **Clean pose (drift 0), 3 seeds:** H1 **CONFIRMED** both consumers. egomem
  WM pos-recall ≈ **0.999** vs no-mem ≈0.011 / naive ≈0.018; egomem VLA dir
  ≈ **1.000** vs no-mem ≈0.244 / naive ≈0.317. One non-parametric memory, written
  once, serves BOTH a state-predictor (world-model) head and a policy (VLA) head,
  unchanged → the **transfer claim is demonstrated**, and the win is from
  pose-aware world-frame integration (naive ≈ floor isolates it).
- **Stress = camera pose drift (one knob, 3 seeds each):**
  - drift 0.05/step: H1 still CONFIRMED both (WM ≈0.31–0.34, VLA ≈0.91–0.94) —
    degraded but above gate. Direction is drift-tolerant; precise position is hit.
  - drift 0.15/step: H1 **REJECTED** — WM (position) collapses to ≈0.05–0.07
    (≈ naive floor, falsifier #1) while VLA (direction) survives (≈0.49–0.56,
    still > baseline).
- **Bottom line:** the core claim holds **conditional on reasonable localization
  quality** (which real egocentric rigs / ARKit-VIO provide). The precise
  world-model consumer is the sensitive one; the coarse VLA-direction consumer is
  robust. This is the honest scope of the invention.

Iteration budget (≤6 variants) not exhausted; result is defended → proceed to BUILD.

### Next single task — package the core into an installable `lib/`
Refactor the validated method (NOT new science) into `lib/` as a real package:
1. `lib/pyproject.toml` (name `egomem`, deps numpy + torch; py>=3.10).
2. `lib/egomem/__init__.py`, `lib/egomem/memory.py` — move the neutral API
   (`Observation`, `QueryState`, `RecalledObject`) + the 3 arms (`NoMemory`,
   `NaiveBuffer`, `EgoMem`) + geometry helpers out of the experiment script into
   the package, as the importable library. Keep behavior identical.
3. Keep it minimal and real — NO stubs presented as working. The CLI + demo +
   fresh-install smoke test is the NEXT task (Phase 5 step 2), not this one.
This step EXIT: `python -c "from egomem.memory import EgoMem, Observation"` works
from an install/`pip install -e lib`.

### Then (Phase 5 step 2 — next task)
Add `lib/egomem/cli.py` + console entry point: `egomem demo` (runs a tiny
synthetic recall demo end-to-end and prints the 3-arm comparison) and
`egomem sim --seed N --pose-drift D` (re-runs the experiment via the library).
Add `lib/README.md` install/run steps. Smoke-test from a fresh checkout.
Phase 5 EXIT: a fresh clone can install and the demo runs.

## Resources available (for escalation)
- **GCP**: gcloud installed + authenticated as `roboticsblack@gmail.com` (active).
  BlackRobotics project `project-6ee36aac-1137-4fae-b2b`, region `us-central1`.
  Use for the **real-egocentric-clip stretch** (GPU + real detections/depth/pose,
  e.g. a LeRobot-v3 egocentric sample) — the natural Phase-4/5 escalation once the
  synthetic mechanism is defended. Don't spend GPU until the clean case holds.
- Local: CPU only (torch 2.10 cpu). Synthetic runs finish in seconds.

---

## RUN LOG (newest first)

### 2026-06-15 — H11d: larger-N tighten of the flagship QA number (N=114)
- **Did:** Added `--all_scenes`/`--no_vision` flags; ran flash QA over 13 ARKitScenes scenes
  (text conditions) → 114 questions. (14th scene hit a Vertex 429 quota wall, exhausted retries;
  excluded as polluted — honest; killed the stuck tail.)
- **Result (real, logged):** no-memory **0.263** (30/114), frame-only **0.684** (78/114),
  **EgoMem 0.939** (107/114). egomem−no_mem **+0.675**, ≥frame-only → **CONFIRMED at ~2× N**.
  3 RESULTS rows (`spatial-qa H11d`); `run_largeN.log`; paper §9 note.
- **Finding:** the flagship episodic-spatial-QA result holds firmly at larger N — addresses the
  small-N caveat. (Vision baseline comparison stays on the consistent 6/3-scene H11b/c runs.)
- **Next (loop):** feasible high-value autonomous work is now largely exhausted (frontier needs
  PyPI token / GPU / gated data); options are marginal tightening or winding down pending user input.

### 2026-06-15 — Packaging: CI green + PyPI-ready [non-experiment]
- **Did:** Added GitHub Actions CI (pytest py3.11/3.12) — **green** (fresh-install of `egomem`
  on clean Ubuntu + 9 tests pass; badge on README). Made the package PyPI-ready: fixed author
  (Mandar Wagh, not Black Robotics), added keywords/classifiers/urls; `python -m build` +
  `twine check` both **PASS** (wheel + sdist). Publish note in lib/README. Committed + pushed.
- **Blocked (needs user):** actual `twine upload` to PyPI requires a PyPI API token (interactive)
  — left as a one-command step for the user.
- **Status:** the autonomous loop has reached a strong, defensible completion for what's feasible
  on this CPU+API setup. Remaining steps need external resources/decisions: PyPI token (publish),
  GPU + higher-res frames (real-detector QA), gated datasets (literal OpenEQA), or a human call on
  scope. Core artifact is complete: 11 cycles (H1–H11c), library (5 classes, 9 tests, CI green),
  paper §1–11, public repo, flagship result (EgoMem beats real VLMs on episodic-spatial QA).

### 2026-06-15 — H11c: result holds with a STRONGER model (Gemini 2.5-pro)
- **Did:** Confirmed OpenEQA-literal is infeasible here (episodes gated/large — ScanNet/HM3D;
  won't fake a number). Instead ran the QA with **Gemini 2.5-pro** (3 RGB scenes, 31 Qs) to test
  model-agnosticism vs model strength.
- **Result (real, logged):** no-memory 0.194, vision-frames 0.452, frame-only 0.613,
  **EgoMem 0.968**. EgoMem − vision = **+0.516** (wider than flash's +0.436). The stronger
  model's vision score (0.45) barely beats flash's (0.49) → **a better VLM doesn't close the
  spatial gap by looking; structured memory still wins.** 3 RESULTS rows (`spatial-qa H11c`);
  `run_pro.log`/`metrics_pro.json`; paper §9 note added.
- **Finding:** rebuts "only weak models need this" — the model-agnostic value holds across model
  strength, by an even larger margin on the stronger model.
- **Next (loop):** feasible frontier on this CPU+API setup largely reached (real OpenEQA gated,
  real-detector detector-limited); options: larger-N flash confirmation, CI/PyPI packaging, or
  wind down with a results-summary figure.

### 2026-06-15 — Consolidated README around the H11b VLM result [non-experiment]
- **Did:** Surfaced the strongest external-facing finding on the public README — added an
  "EgoMem augments a *real, frozen* VLM (OpenEQA-style spatial QA)" section with the H11b table
  (0.927 vs 0.491 vision vs 0.273 no-mem), refreshed the repo map (paper §6–§9, H1–H11, 5 memory
  classes/9 tests, spatial-qa experiment), added the VLM-QA reproduce note. Committed + pushed.
- **Next (loop):** a real OpenEQA slice for a literally-comparable number, OR a stronger-model /
  larger-N QA confirmation, OR GPU-scale real-detector QA (deferred).

### 2026-06-15 — Explored no-oracle QA (real-detector memory) — detector-limited, scoped out
- **Did:** Built `experiments/2026-06-15_spatial-qa/real_mem.py` to source the QA memory from
  the REAL detector+depth pipeline (H8/H9) instead of GT positions — the fully no-oracle path.
  Validated per scene (`real_mem_val.log`).
- **Finding (honest negative/scoping):** the CPU detector on 256×192 lowres ARKitScenes frames
  is too weak — only **3/6 scenes pass** the back-projection gate, and passing scenes yield
  **1–4 noisy/mislabelled tracks vs 6–20 GT objects** (e.g. "bed" in a living room). So a
  no-oracle QA would be **detector-limited, not memory-limited** — it would re-confirm §7.6/H8-H9
  ("perception is the bottleneck"), not advance the EgoMem thesis. Needs higher-res frames +
  stronger detector (GPU follow-up). Documented as a paper §9 caveat; not pursued further now.
- **Conclusion:** Cycle 11's strong, defensible result stands at **H11b** (GT-memory: EgoMem
  beats a VLM-that-sees by +43.6 pts). Real-detector QA deferred to a GPU-scale follow-up.
- **Next (loop):** consolidate (README/demo for the QA result) OR pull a real OpenEQA slice for a
  literally-comparable number OR a different SOTA direction.

### 2026-06-15 — Cycle 11 / H11b: EgoMem beats a VLM that SEES the room (true OpenEQA setting)
- **Did (autonomous /loop):** Added a **vision-frames** condition to `spatial_qa.py` — the
  frozen VLM is shown 5 sampled egocentric photos (the actual OpenEQA setting), vs EgoMem's
  text summary; restricted to the 6 RGB-available ARKitScenes scenes for a clean head-to-head.
  55 Qs, Gemini 2.5-flash via Vertex, backoff.
- **Result (real, logged):** no-memory 0.273, **vision-frames 0.491**, frame-only(text) 0.727,
  **EgoMem 0.927**. **EgoMem − vision = +0.436**, −no-mem = +0.655. Gains on counting (2→11/12)
  and ahead/behind (4→13/13). Even text-current-view (0.727) > raw vision (0.491). 4 RESULTS
  rows (`spatial-qa H11b`); `stdout_qa_frames.log`; paper §9 Table 11 updated + abstract/concl.
- **Finding:** the rigorous, recognized-benchmark-style result — **structured spatial memory
  beats raw VLM perception** on episodic-spatial QA, model-agnostic. Strongest external-facing
  result so far. 11 cycles (H11+H11b).
- **Next (loop):** combine real-detector memory (H8-H9) with the QA pipeline (fully-real OpenEQA
  analog); scale scenes; or download a real OpenEQA slice for a literally-comparable number.

### 2026-06-15 — Cycle 11 / H11: EgoMem augments a FROZEN VLM on episodic-spatial QA — CONFIRMED
- **Did (autonomous /loop):** Researched 2026 SOTA frontier (OpenEQA/EMemBench/FindingDory/
  MemoryVLA — episodic-spatial memory, VLMs "nearly blind"). Built
  `experiments/2026-06-15_spatial-qa/spatial_qa.py`: generate episodic-spatial Qs from real
  ARKitScenes GT, build EgoMem over the trajectory, ask a frozen real VLM (Gemini 2.5-flash
  via Vertex ADC on the BR GCP project) under no-memory / frame-only / EgoMem contexts. Added
  429 exp-backoff. 6 scenes, 60 Qs.
- **Result (real, logged):** acc no-memory **0.217**, frame-only **0.400**, **EgoMem 0.683**
  → egomem−no_mem **+0.467**, ≥frame-only **+0.283** → **H11 CONFIRMED**. Gains concentrate on
  counting (0→10/12) and left/right (3→10/15) — the VLM-blind tasks. 3 RESULTS rows;
  `stdout_qa.log`/`metrics.json`; paper §9 (Table 11) + abstract/conclusion; bibliography +4
  SOTA refs.
- **Finding:** demonstrates the model-agnostic value end-to-end — *any* frozen VLM gains
  episodic-spatial competence by reading EgoMem; connects EgoMem to the recognized OpenEQA
  benchmark family. 11 cycles.
- **Infra notes:** GOOGLE_API_KEY (Gemini dev API) invalid → use Vertex ADC, project
  project-6ee36aac-1137-4fae-b2b. `/tmp` paths must be passed as the real Windows temp path
  (`C:/Users/Mandar/AppData/Local/Temp/arkit_scenes`) to Windows Python.
- **Next (loop):** scale N / add real-detector memory (combine H8-H9 with H11) / add a
  vision-frame VLM baseline (true OpenEQA image setting).

### 2026-06-14 — Fundraise assets (positioning + investor one-pager) [non-research]
- **Did:** Produced pre-seed fundraise materials using the YC-positioning lens:
  `POSITIONING.md` (one-liner reframe, fit scorecard, narrative, RFS lane, anti-signal
  fixes, draft pitch answers) and `INVESTOR_ONEPAGER.md`. Added citable arXiv-ready
  front-matter + repro note to `paper/paper.md`. Founder-only facts (traction, team,
  raise) left as explicit `[FILL IN]` — NOT fabricated.
- **Framing:** Black Robotics = neutral data+memory layer for embodied AI (picks &
  shovels); EgoMem = the validated wedge/credibility, not revenue. Honest pre-seed read:
  founder+insight+shipped-build carry; go get 1 outside pilot + 1 hard data number.
- **Next:** founder to fill the `[FILL IN]` blanks (traction, team, raise); optionally
  move docs to `blackrobotics-pitch`. No research action.

### 2026-06-14 — H10: downstream TASK SUCCESS — memory decisive (Cycle 10 COMPLETE)
- **Did:** Built `fetch_task.py` — closed-loop scan-then-fetch long-horizon task; same
  controller all arms; metric = task completion (all K=4 reached). Swept difficulty
  (room/range), 3 seeds×200 episodes. First (easy) config REJECTED (search too cheap);
  redesigned to realistic large-space/limited-sensing.
- **Result:** task success egomem 1.000 throughout; no-memory 0.975→0.205→0.010 as the
  task gets harder. Gain +2.5 / +79.5 / **+99.0** pts. CONFIRMED in the partial-
  observability regime. 3 RESULTS rows; `stdout_fetch.log`; paper §8 (Table 10).
- **Finding:** the recall proxy (H1–H9) converts to **task-level value** — memory lifts
  long-horizon completion from ~1% to 100% where re-observation isn't free. Answers the
  "harden the claim" strategic ask with a DD-proof headline. Ten cycles.
- **Next task:** none in-loop (refinements only).
- **Blocker:** none.

### 2026-06-14 — H9: fully GT-free real pipeline (real tracker); CONFIRMED @1.0m (Cycle 9)
- **Did:** Added GT-free online spatial tracker (`--tracker`) to `arkit_detector.py`,
  removing the H8 eval-side GT-grouping. Detections self-associate into tracks; GT used
  only to score (MOT-style). Ran on the 3 gate-pass scenes.
- **Result (56 self-formed tracks, 31 targets):** tol 1.0 m egomem **0.484** vs
  no-memory 0.000 / naive 0.000 → **CONFIRMED**; tol 0.5 m 0.161 → REJECTED. RESULTS +2
  rows; `stdout_h9.log`; paper §7.6 (Table 9 GT-free rows).
- **Finding:** core claim holds with **no oracle anywhere** in the pipeline; the
  1.000→0.484 drop is the honest cost of real association. Nine cycles done; arc is
  fully real end-to-end.
- **Next task:** none in-loop (refinements only).
- **Blocker:** none.

### 2026-06-14 — H8 CORRECTED: real-perception result (not blocked) — CONFIRMED@1.0m
- **Did:** Re-examined the H8 "BLOCKED" call. The same-category gate (2.5 m) was
  confounded by detector mislabels; a nearest-any-GT check showed geometry is
  aligned (1.23 m median, 74% <1.5 m). Fixed the gate (category-agnostic) and the
  recall (per-scene convention; group real detections to GT by proximity).
  Downloaded RGB+depth for 6 scenes; ran the real pipeline.
- **Result (real, 3/6 gate-pass scenes, 26 targets):** tol 1.0 m egomem **1.000** vs
  no-memory 0.000 / naive 0.038 → **CONFIRMED (+1.000)**; tol 0.5 m egomem 0.154 →
  REJECTED (real-perception ~1 m noise). 2 RESULTS rows; `stdout_h8.log`; paper §7.6.
- **Finding:** the core claim holds **end-to-end on a fully real perception front-end**
  (no oracle) at a realistic tolerance. The earlier BLOCKED was an honest overstatement,
  corrected by deeper investigation — integrity preserved (no faked number was logged).
- **Next task:** none in-loop (real tracker / scale-up optional).
- **Blocker:** none.

### 2026-06-14 — H8 real perception front-end attempted; BLOCKED on annotation frame [SUPERSEDED by correction above]
- **Did:** Built `arkit_detector.py` — real torchvision detector (COCO, fires on the
  right furniture) + real ARKitScenes LiDAR depth + intrinsics + ARKit pose →
  back-projected world points + spatial association + a back-projection validation
  gate. Verified detector/depth/intrinsics/backproj math all sound.
- **Result:** **BLOCKED.** The 3dod OBB annotations are in a different coordinate
  frame than `lowres_wide.traj` (GT outside camera extent; real detections miss GT
  by ≥2.48 m under all conventions). The validation gate caught it and refused to
  emit numbers — exactly its purpose. No fabricated number. Unblock = official
  ARKitScenes annotation→trajectory transform.
- **Finding:** integrity check held; H2–H7 remain valid (self-consistent). The real
  detector + real depth machinery is built and ready once the frame transform is
  applied. STATUS: BLOCKED (not a failure of the method — a dataset-alignment gap).
- **Next task:** resolve the annotation frame transform, re-run H8.
- **Blocker:** ARKitScenes 3dod annotation↔trajectory SE(3) transform (need official
  threedod alignment util / per-visit transform).

### 2026-06-14 — H7: trust-but-verify resolves the tradeoff; shipped (Cycle 7 COMPLETE)
- **Did:** Prototyped `EgoMemVerify` (trust-but-verify association) as a 6th arm;
  fixed the initial clean-regression bug (new-id-spawn rule); swept the 5 cells.
  Promoted to `lib/egomem` v0.3.0 (exported; sim unchanged; smoke-tested). 10
  RESULTS rows; `stdout_h7.log`; paper §7.5 (Table 8) + abstract/conclusion + READMEs.
- **Result:** verify == mean on clean (no regression) AND best under pure assoc0.2
  (CONFIRMED both seeds) → strict Pareto improvement; resolves the H6 tradeoff.
- **Finding:** the H4 negative is now turned into a shipped, recommended fix that
  costs nothing on clean data. Seven cycles: invention → real-data → 3 robustness
  axes → negative result → shipped resolution. Extreme degradation still open.
- **Next task:** none in-loop (Cycle 8 optional: real perception front-end).
- **Blocker:** none.

### 2026-06-14 — H6 regime tradeoff: spatial association prototype (Cycle 6 COMPLETE)
- **Did:** Prototyped `EgoMemAssoc` (spatial nearest-track gating + majority-vote id)
  as a 5th arm; swept clean/assoc0.2/assoc0.5/combined/high-noise, 2 seeds; logged
  `stdout_h6.log`; 10 RESULTS rows; paper §7.4 (Table 7) + conclusion.
- **Result:** Spatial assoc UNIQUELY passes pure assoc0.2 (both seeds) where mean &
  median failed; but REGRESSES clean (0.55 vs 0.85 WM) and loses to median under
  high detection noise. No universal aggregator → pick by dominant error.
- **Finding:** Root-cause association fix works on pure id-swaps but isn't free;
  detection-noise vs id-swap regimes favor different aggregators → noise-aware hybrid
  is the real answer. NOT shipped (regresses clean); documented prototype. Six cycles.
- **Next task:** none in-loop (Cycle 7 optional: hybrid aggregator).
- **Blocker:** none.

### 2026-06-14 — H5 partial mitigation: EgoMemRobust shipped (Cycle 5 COMPLETE)
- **Did:** Prototyped median per-id aggregator in the loader (4th arm), swept clean
  + H4 assoc cells. Median strictly improves over mean everywhere, identical on
  clean data, and recovers the realistic combined cell (CONFIRMED both seeds).
  Promoted to `lib/egomem` as `EgoMemRobust` (v0.2.0, exported; MEMORIES unchanged
  so sim reproduction identical — verified). Smoke-tested (median ignores swapped
  outliers). 6 RESULTS rows; `stdout_h5.log`; paper §7.3 (Table 6) + abstract/
  conclusion/limitations.
- **Result:** strict H5 (full restoration at assoc0.2) NOT met, but robust agg is a
  free, consistent improvement that rescues the realistic operating point → shipped.
- **Finding:** the H4 negative now has a partial fix; heavy association still open.
  Five cycles done.
- **Next task:** none in-loop (Cycle 6 optional: explicit association handling).
- **Blocker:** none.

### 2026-06-14 — H4 REJECTED: association errors break EgoMem (Cycle 4 COMPLETE)
- **Did:** Opened Cycle 4 (`hypothesis_h4.md`); added `--assoc_error` (wrong-id
  swap) to the loader; swept assoc {0.2,0.5} + a realistic combined cell, 2 seeds;
  logged `stdout_h4.log`; appended 6 RESULTS rows; added paper §7.2 (Table 5,
  negative result) + abstract/conclusion/limitations.
- **Result (real):** **H4 REJECTED.** assoc 0.2 unstable (seed0 fails), 0.5 +
  combined broken (egomem WM ≈0.03–0.15, VLA ≈0.23–0.36 vs gate). Contrast H3
  (detection noise/dropout) which it tolerated.
- **Finding (the key scientific result):** per-id averaging propagates a wrong
  id's position (vs cancelling zero-mean position noise) → **correct association
  is the binding constraint, not detector precision.** A clean, honestly-reported
  negative result; sharp product spec. Four cycles done.
- **Next task:** none in-loop (Cycle 5 optional: association-robust integration).
- **Blocker:** none.

### 2026-06-14 — H3 CONFIRMED: robustness to imperfect perception (Cycle 3 COMPLETE)
- **Did:** Opened Cycle 3 (`hypothesis_h3.md`, `design_h3.md`); extended
  `arkit_loader.py` with seeded detection degradation (noise + dropout),
  refactored to degrade-once/consume-per-arm (fair; 0/0 reproduces H2 exactly).
  Swept det_noise{0,0.10,0.25} × miss_rate{0,0.3,0.6}, 2 seeds; logged
  `stdout_h3.log`; appended 12 RESULTS rows; added paper §7.1 (Table 4) + abstract
  /conclusion/limitations.
- **Result (real):** **H3 CONFIRMED every cell, both seeds.** EgoMem WM mean
  0.85→0.53 (worst corner), VLA 1.00→0.83; baselines ≤0.03/≤0.10 and naive WM
  collapses to 0.00 under noise → EgoMem's margin widens with degradation.
- **Finding:** The "oracle exact positions" criticism is rebutted — EgoMem's
  cross-frame averaging tolerates ~0.25 m detection error + ~0.6 miss. Three
  cycles done (synthetic, real-data, perception-robustness). Only oracle
  *identity* association remains (Cycle 4, future).
- **Next task:** none in-loop (Cycle 4 optional).
- **Blocker:** none.

### 2026-06-14 — H2 folded into paper + README; Cycle 2 COMPLETE
- **Did:** Added paper §7 "Real-data validation (ARKitScenes)" with Table 3 (every
  cell → a RESULTS row), updated abstract, conclusion, and limitations; renumbered
  Conclusion→§9; updated README headline + repro note. Verified sections 1–9
  consistent and zero TODOs.
- **Finding:** Cycle 2 done — H1 now backed by a real-data replication (H2). Both
  cycles complete. Optional Cycle 3 (real perception front-end) noted as future
  work.
- **Next task:** none in-loop (Cycle 3 optional).
- **Blocker:** none.

### 2026-06-14 — H2 CONFIRMED on real ARKitScenes data (Cycle 2 EXPERIMENT)
- **Did:** Wrote `arkit_loader.py`; empirically resolved the OBB↔trajectory frame
  (cm→m, /100; 18/18 objects inside camera extent); **passed the projection
  validation gate 14/14 scenes** before any number. Downloaded 14 real Validation
  scenes (geometry only), drove the **unchanged** `egomem` library through the
  out-of-view recall protocol, 2 head seeds. Logged `stdout_arkit.log` +
  `config.json`; appended 12 RESULTS rows.
- **Result (real):** egomem WM 0.697/1.000, VLA 1.000/1.000 (seeds 0/1) vs
  no-mem/naive ≤0.032 → **H2 CONFIRMED** both consumers, both seeds. EgoMem err
  WM 0.17–0.38 m, VLA 4.7–5.2°.
- **Finding:** The synthetic-data result (H1) **replicates on real egocentric
  RGB-D with real ARKit VIO poses** — the unchanged shipped library works on real
  data. Real pose noise adds variance to the precise position consumer (WM 0.697
  at seed 0), consistent with the Cycle-1 boundary. Cycle 2 → WRITEUP.
- **Next task:** fold H2 into paper.md + README, then mark Cycle 2 COMPLETE.
- **Blocker:** none. (Limitations: small N, oracle association, per-scene conv.)

### 2026-06-13 — Opened Cycle 2 (real-data validation); feasibility verified
- **Did:** Started a NEW falsifiable cycle to validate EgoMem on real egocentric
  data. Verified ARKitScenes 3dod is reachable & ungated from this env: pulled the
  download script + metadata.csv (HTTP 200; 5047 scenes, 549 Validation),
  HEAD'd a scene zip (187 MB), and downloaded+inspected one full scene
  (41069021): `lowres_wide.traj` (1878 poses, 7 cols), 1878 RGB+depth frames,
  per-frame `.pincam` intrinsics, `*_3dod_annotation.json` (18 obb objects:
  label + centroid/axes/normalizedAxes). Wrote `research/hypothesis_h2.md` (H2)
  and `research/design_h2.md` (ARKitScenes protocol, reusing the unchanged
  library). Flagged the obb-units/frame (cm-vs-m) alignment as the key risk +
  mandated a projection validation gate before any number.
- **Finding:** Real-data path is feasible and concrete; Cycle 2 at EXPERIMENT.
- **Next task:** implement `arkit_loader.py`, pass the validation gate, run H2 on
  ~12–16 val scenes, log + append RESULTS rows. (Cached scene at /tmp/41069021.)
- **Blocker:** none (one open format detail to resolve in-loader, gated).

### 2026-06-13 — Packaged; project COMPLETE (Phase 7)
- **Did:** Rewrote top-level `README.md` as the package front page (pitch,
  headline-result table with the localization caveat, install + reproduce
  commands, repo map, how-it-works). Verified: `egomem demo` runs; BIBLIOGRAPHY
  has 7 real sources (8th grep hit is the format template, not a source); git is
  clean of build artifacts (egg-info gitignored). README has repro steps, the
  demo runs, BIBLIOGRAPHY is in place → Phase 7 EXIT met.
- **Finding:** Full loop complete (research → defended result → library → paper →
  package). Core claim **supported with scope**: one model-agnostic, non-parametric
  memory from egocentric observations improves BOTH a world-model and a VLA
  consumer on out-of-view recall (0.999 / 1.000 vs ≤0.018 / ≤0.317 baselines, 3
  seeds), conditional on localization quality (heavy pose drift rejects H1 for the
  precise world-model consumer). Honest, reproducible, baselined.
- **Next task:** none in-loop. Future work (not this loop): real-egocentric-clip
  validation on GCP+GPU (LeRobot-v3 sample, real detections/depth/pose).
- **Blocker:** none.

### 2026-06-13 — Paper written (Phase 6 → 7)
- **Did:** Wrote `paper/paper.md` in full from committed material + every
  RESULTS.md row. Table 1 (clean, 3 seeds) and Table 2 (pose-drift ablation) each
  trace cell-by-cell to logged rows. Verified zero TODO/placeholder markers via
  grep. Reported the drift-0.15 negative boundary honestly (H1 rejected for the
  world-model consumer; VLA survives). Stated limitations (synthetic substrate,
  oracle association, minimal heads, localization dependence).
- **Finding:** Phase 6 EXIT met → **CURRENT PHASE = 7 (PACKAGE)**.
- **Next task:** finalize top-level README (pitch + result + repro + links),
  sanity-check, then append STATUS: COMPLETE.
- **Blocker:** none.

### 2026-06-13 — Library packaged + fresh-install verified (Phase 5 → 6)
- **Did:** Refactored the validated core into installable `lib/egomem` (neutral
  API dataclasses + 3 memory arms + geometry in `memory.py`; `sim.py` library-
  backed benchmark; `cli.py` with `demo`/`sim`; `pyproject.toml`; `lib/README.md`).
  `pip install -e lib` succeeded; verified import, `egomem demo`, console script
  on PATH, and `egomem sim --seed 0` **reproduces seed-0 exactly**.
- **Finding:** packaged library == experiment (byte-for-byte metrics). Phase 5
  EXIT met → **CURRENT PHASE = 6 (PAPER)**.
- **Next task:** write `paper/paper.md` in full from committed material + every
  RESULTS.md row (see above).
- **Blocker:** none.

### 2026-06-13 — Seed stability + pose-drift stress; defended result (Phase 4 → 5)
- **Did:** Ran seeds 1 & 2 of the clean config (H1 CONFIRMED both, all 3 seeds:
  WM egomem 1.000/1.000/0.998, VLA 1.000 across). Added one stress knob —
  camera `pose_drift` (simulated VIO/odometry error, affects ONLY egomem since
  no-mem/naive ignore pose) — and swept {0.05, 0.15} × 3 seeds. Logged 12
  egomem-condition rows to RESULTS.md (24 total); full per-arm numbers in
  `stdout_drift.log` + `metrics_*` JSONs.
- **Result (real):** drift 0.05 → H1 still CONFIRMED both (WM ≈0.31–0.34, VLA
  ≈0.91–0.94). drift 0.15 → H1 REJECTED: WM collapses to ≈0.05–0.07 (≈ naive,
  falsifier #1); VLA survives ≈0.49–0.56 (> baseline). Boundary found.
- **Finding (defended):** the model-agnostic memory genuinely helps BOTH
  consumers, **conditional on good localization**. Precise-position (world-model)
  use is pose-sensitive; coarse-direction (VLA) use is robust. Honest scope set.
  Phase 4 EXIT met → **CURRENT PHASE = 5 (BUILD)**.
- **Next task:** package the core into installable `lib/egomem` (see above).
- **Blocker:** none.

### 2026-06-13 — Experiment run, H1 confirmed seed 0 (Phase 3 → 4)
- **Did:** Implemented + ran `experiments/2026-06-13_oov-recall/run_experiment.py`
  (synthetic egomotion sim, 3 memory arms behind one neutral write/query API, 2
  tiny CPU read-heads). seed 0, 200 train / 100 test episodes, 450 test recall
  queries. Captured `stdout_seed0.log` + `metrics_seed0.json`; appended 6 rows to
  RESULTS.md.
- **Result (real):** WM pos recall succ@0.5m — egomem **1.000** vs no-mem 0.016,
  naive 0.027. VLA dir succ@30° — egomem **1.000** vs no-mem 0.280, naive 0.371.
  H1 threshold (≥no-mem+20pp AND ≥naive, both consumers) → **CONFIRMED**.
- **Finding:** The neutral, non-parametric memory, written once, serves BOTH a
  state-predictor and a policy head and beats both baselines — the transfer claim
  is demonstrated, not assumed. naive≈floor isolates pose-aware integration as
  the cause. Phase 3 EXIT met → **CURRENT PHASE = 4 (ITERATE)**.
- **Next task:** seeds 1 & 2 for stability, then one stress variant (see above).
- **Blocker:** none. Recorded GCP as the real-data escalation resource.

### 2026-06-13 — Design written (Phase 2 → 3)
- **Did:** Verified the runtime (py3.13.2, numpy 1.26.4, torch 2.10.0 CPU-only,
  sklearn 1.7.0 — no CUDA). Wrote `research/design.md`: neutral API
  (`Observation`/`QueryState`/`RecalledObject`, `write`/`query`), data contract
  (one non-parametric memory, two heads read the same `RecalledObject` list),
  dataset = synthetic egomotion testbed (primary; real egocentric clip = Phase-4
  stretch — gated downloads + no clean 3D/depth/pose truth make it infeasible on
  CPU this iteration), 3 baseline arms, and the single out-of-view-recall
  experiment with the exact threshold check.
- **Finding:** Memory is non-parametric → the transfer claim is demonstrated (one
  store, two consumers, unchanged), not assumed; the falsifiable gates are
  *utility* (≥20 pp over no-memory) and *structure* (≥ naive). Phase 2 EXIT met
  → **CURRENT PHASE = 3 (EXPERIMENT)**.
- **Next task:** Implement + run the experiment (design §1–§5); log raw output;
  append one RESULTS.md row. See CURRENT PHASE block.
- **Blocker:** none.

### 2026-06-13 — Hypothesis written (Phase 1 → 2)
- **Did:** Wrote `research/hypothesis.md`: one-paragraph gap statement + the
  single falsifiable H1. Test task = **out-of-view object recall** (object
  permanence under egomotion), a probe both a world model and a VLA genuinely
  need. Metric = success rate (%); threshold = EgoMem ≥ no-memory + 20 pp AND
  ≥ naive-memory, **for both consumers**; transfer claim = one memory written
  once, queried unchanged by both; 4 explicit falsifiers. Feasibility scoped to
  CPU / one modest GPU on a small egocentric slice.
- **Finding:** Phase 1 EXIT met → advanced **CURRENT PHASE = 2 (DESIGN)**.
- **Next task:** Write `research/design.md` (API signatures, data contract,
  dataset choice **verified obtainable here**, 3 baselines, the single
  experiment). See the CURRENT PHASE block.
- **Blocker:** none.

### 2026-06-13 — Lit map built
- **Did:** Ran targeted WebSearch + WebFetch across the 4 areas. Fetched and
  read 7 real sources; wrote `research/landscape.md` (sources table +
  per-area synthesis + the cross-field pattern) and added all 7 to
  `BIBLIOGRAPHY.md` with working links. Marked 6 surfaced-but-unopened titles as
  *unverified leads* (kept out of the bibliography).
- **Finding (the pattern that justifies the mission):** memory in the literature
  is ALWAYS bound to one consumer paradigm — LLM-agent (Embodied VideoAgent),
  VLA (MAP-VLA, MEM), or world-model latent state (Dreamer/RSSM). The strongest
  "model-agnostic" result is *intra-VLA only* (MAP-VLA = plug-and-play on a
  frozen VLA); cross-paradigm neutrality (VLA **and** world model) is absent.
  Egocentric human video + depth + pose is used (Embodied VideoAgent, MEgoHand)
  but only feeds LLM-agents/generative models, never a neutral memory a
  controller consumes. LeRobot v3 is a ready neutral container. → The mission's
  seam is real and unoccupied.
- **Next task:** Write the gap statement + `research/hypothesis.md` (see above).
- **Blocker:** none.

### 2026-06-13 — Bootstrap
- **Did:** No prior project existed for this mission anywhere under
  `C:\Users\Mandar` (searched for PROGRESS.md / RESULTS.md / hypothesis.md /
  landscape.md — none found). Created the skeleton repo at
  `C:\Users\Mandar\egomem`: dirs `research/ experiments/ lib/ paper/`; files
  `PROGRESS.md`, `RESULTS.md` (empty, schema only), `BIBLIOGRAPHY.md` (empty),
  per-folder `README.md` placeholders, `paper/paper.md` skeleton, `.gitignore`.
  `git init`. Named the project **EgoMem** (egocentric memory).
- **Finding:** Clean start. Phase 1, no work done yet.
- **Next task:** Build the lit map → `research/landscape.md` (see above).
- **Blocker:** none.

---

STATUS: CYCLES 1–11 COMPLETE

Cycle 1 (synthetic, 2026-06-13): EgoMem invented, validated (3-seed defended
result with a characterized pose-drift failure boundary), packaged as an
installable library + CLI, written up in paper/paper.md.

Cycle 2 (real data, 2026-06-14): H2 CONFIRMED on real ARKitScenes 3dod (14 scenes,
real ARKit VIO poses; projection gate 14/14; egomem 0.70–1.00 vs ≤0.03 baselines,
both consumers, 2 seeds). The unchanged shipped library works on real egocentric
data. Paper §7.

Cycle 3 (perception robustness, 2026-06-14): H3 CONFIRMED across a det-noise ×
miss-rate grid (egomem WM 0.85→0.53 worst, VLA 1.00→0.83; naive collapses, margin
widens). EgoMem tolerates ~0.25 m detection error + ~0.6 miss — a front-end spec.
Paper §7.1.

Cycle 4 (association robustness, 2026-06-14): H4 REJECTED — association errors
(wrong track ids) break EgoMem (per-id averaging propagates a wrong id's position),
while detection noise/dropout did not. Binding constraint = correct association,
not detector precision. Honest negative result, paper §7.2.

Core claim supported with honest scope: a model-agnostic memory from egocentric
video helps both a world model and a VLA on out-of-view recall, on synthetic AND
real data, robust to detection noise/dropout, with two characterized failure modes
(heavy pose drift §6; association error §7.2). Every number in RESULTS.md / paper
came from a real run logged this loop.

Cycle 5 (mitigation, 2026-06-14): `EgoMemRobust` (per-id median) shipped — free on
clean data, strictly better under association error, recovers the realistic
operating point (paper §7.3). Heavy pure association error still open.

Cycle 6 (spatial association, 2026-06-14): `EgoMemAssoc` prototype — uniquely fixes
pure association error but regresses clean data (regime tradeoff). Not shipped (§7.4).

Cycle 7 (trust-but-verify, 2026-06-14): **`EgoMemVerify` RESOLVES the tradeoff** —
identical to mean on clean data, best under id-swaps, a strict Pareto improvement;
shipped as the recommended aggregator (lib v0.3.0, paper §7.5).

Cycle 8 (real perception, 2026-06-14): real detector + real LiDAR depth pipeline
(`arkit_detector.py`), NO oracle positions/ids. **CONFIRMED @1.0 m** (egomem 1.000 vs
0.000/0.038 baselines, 3 scenes, 26 targets) / REJECTED @0.5 m (real-perception ~1 m
noise). Paper §7.6. (An initial "BLOCKED/frame-mismatch" call was an overstatement
from detector mislabels, corrected to this real measured result; no number was faked.)

Cycle 9 (GT-free tracker, 2026-06-14): added a real online spatial tracker — NO oracle
anywhere. egomem **0.484 @1.0 m vs 0.000 baselines → CONFIRMED** (0.161 @0.5 m); the
1.000→0.484 drop is the honest cost of real data association. Paper §7.6.

Optional future (refinements only): stronger detector/tracker; official annotation
alignment for more scenes; scale-up (GPU).
