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

STATUS: COMPLETE

Loop finished 2026-06-13. EgoMem invented, validated (3-seed defended result with a
characterized failure boundary), packaged as an installable library + CLI, and
written up in paper/paper.md. Core claim supported with honest scope. Every number
in RESULTS.md / paper came from a real run logged this loop.
