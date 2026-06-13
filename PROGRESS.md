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

## CURRENT PHASE = 2 (DESIGN)

Phase 1 closed: `research/hypothesis.md` committed (metric = out-of-view recall
success rate; threshold = ≥20 pp over no-memory AND ≥ naive memory, for both
consumers; transfer claim = one memory, no per-consumer retraining; explicit
falsifiers).

### Next single task — write `research/design.md`
Spec the smallest real version that tests H1. It must contain:
1. **Neutral API signatures** — `write(obs) -> mem` and
   `query(state) -> retrieved_context`, with the exact types of `obs`, `state`,
   and `retrieved_context`. obs carries RGB frame + depth + camera pose (+ any
   detections). Keep it paradigm-neutral (no VLA- or world-model-specific
   fields).
2. **Data contract** both consumers read — what a query returns (e.g. a small
   set of recalled object records: id, category, last-seen 3D position in the
   *current* camera frame, confidence) such that a world-model head and a VLA
   head can each consume it without memory-side changes.
3. **The dataset** — pick the SMALLEST egocentric source with RGB+depth+pose and
   **verify it is actually obtainable this environment** (download size, license,
   a tiny sample). Candidates: egocentric HOI corpus, EPIC-Kitchens/Ego4D clip,
   LeRobot-v3 egocentric sample, or (fallback) a *procedurally generated*
   egomotion-over-a-static-object-layout synthetic set if no real clip is
   feasible on this hardware. State the choice and why.
4. **Baselines** — (i) no-memory, (ii) naive memory (raw frame buffer / flat
   embedding store), (iii) EgoMem (pose-aware persistent object memory).
5. **The single experiment** — the exact out-of-view recall protocol, the two
   consumer read-heads, what gets logged, and how success/threshold is computed.

### Constraints
- Design for CPU / one modest GPU. If a real egocentric clip is too heavy to pull
  here, the design's primary path should be the synthetic egomotion set (still a
  *real* run of the memory layer + consumers), with the real-clip version named
  as a Phase-4 stretch. Decide this in design.md, do not defer it to Phase 3.
- Do not write code yet — Phase 3 implements. Design only.

---

## RUN LOG (newest first)

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
