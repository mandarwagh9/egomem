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

## CURRENT PHASE = 4 (ITERATE)

Phase 3 closed: ran `experiments/2026-06-13_oov-recall/run_experiment.py` (seed 0,
CPU, deterministic). **H1 CONFIRMED for both consumers** — egomem 1.000/1.000 vs
no-memory 0.016/0.280 and naive 0.027/0.371 (WM succ@0.5m / VLA dir succ@30deg).
6 rows in RESULTS.md; raw log + `metrics_seed0.json` in the experiment folder.

### Analysis of the seed-0 number (why it is what it is)
- EgoMem near-perfect because its `query` returns the out-of-view object's
  position re-expressed in the CURRENT camera frame, so the tiny head learns a
  near-identity readout — i.e. the *information is linearly present*. naive
  carries the object but in a STALE frame (no pose transform) → ~floor, proving
  the win comes from pose-aware world-frame integration, not buffering.
  no-memory has no record → constant-prior floor, proving the task needs memory.
- Caveats that Phase 4 must stress: (i) one seed only; (ii) clean synthetic
  geometry + oracle data association (obj_id given) make it *easy* — a real-data
  or noisier setting could erode the gap. The near-1.0 is honest but fragile.

### Next single task — seed stability (the minimum for a defended result)
Run seeds 1 and 2 of the SAME config (no design change): 
`python run_experiment.py --seed 1` and `--seed 2`, tee to `stdout_seed{1,2}.log`.
Append the per-arm × per-consumer rows to RESULTS.md (real numbers only). Confirm
H1 holds across all 3 seeds. If it holds, the result is stable → that is the
Phase 4 EXIT (a defended result), THEN consider one stress variant below.

### After stability — one stress variant (change exactly ONE thing)
Pick the single most informative knob to find where the effect breaks:
raise `DET_NOISE` (e.g. 0.05 → 0.25) OR add per-frame pose drift, so EgoMem is no
longer trivially perfect. Rerun 3 seeds. This probes robustness and gives the
paper an ablation. Treat a changed number as a NEW set of RESULTS rows (note the
variant), never an edit of an old row.

### Iteration budget: ≤6 variants (PROGRESS top). Stop iterating when stable
across ≥2 seeds AND at least one stress variant is characterized, then → Phase 5.

## Resources available (for escalation)
- **GCP**: gcloud installed + authenticated as `roboticsblack@gmail.com` (active).
  BlackRobotics project `project-6ee36aac-1137-4fae-b2b`, region `us-central1`.
  Use for the **real-egocentric-clip stretch** (GPU + real detections/depth/pose,
  e.g. a LeRobot-v3 egocentric sample) — the natural Phase-4/5 escalation once the
  synthetic mechanism is defended. Don't spend GPU until the clean case holds.
- Local: CPU only (torch 2.10 cpu). Synthetic runs finish in seconds.

---

## RUN LOG (newest first)

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
