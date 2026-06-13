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

## CURRENT PHASE = 3 (EXPERIMENT)

Phase 2 closed: `research/design.md` committed — neutral API, data contract,
dataset (synthetic egomotion testbed primary; real-clip = Phase-4 stretch; CPU
verified: py3.13/numpy/torch-cpu/sklearn), 3 baseline arms (no-memory / naive /
EgoMem), and the single out-of-view-recall experiment.

### Next single task — implement + run the experiment
Build exactly `design.md` §1–§5 as a single runnable script under
`experiments/2026-06-13_oov-recall/` (or a small `lib/`-staged module it imports;
keep it minimal — clean packaging is Phase 5, not now). Concretely:
1. Synthetic egomotion simulator (rooms, objects, camera trajectory, FOV-based
   observation with noise) — exact ground truth.
2. Three memory arms behind the neutral `write/query` API: no-memory, naive
   (raw-frame buffer, no pose transform), EgoMem (pose-aware world-frame
   persistent object store).
3. Two tiny CPU read-heads (world-model = next-pos MLP; VLA = goal-direction
   MLP), identical arch across arms, trained per arm on train split.
4. Eval on held-out out-of-view recall queries → per-arm × per-consumer success
   rate (+ mean error). Fixed seed first; ≥2 seeds is Phase 4.
5. Write `config.json` + full `stdout.log` + `metrics.json` to the experiment
   folder; **append ONE row to RESULTS.md** with the real numbers.
6. Compute the H1 threshold check (EgoMem ≥ no-memory +20 pp AND ≥ naive, BOTH
   consumers) and record PASS/FAIL — do NOT fabricate; report whatever runs.

### Constraints
- CPU only. Keep N/M/T small enough to finish in minutes (design suggests
  N≈300, M 6–10, T≈30). Scale DOWN if slow; a tiny real run beats a big imaginary
  one. NEVER write a number that wasn't produced by an actual run.
- If something can't run (dep/memory), scale down or mark STATUS: BLOCKED with
  the exact blocker — do not fake output.

---

## RUN LOG (newest first)

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
