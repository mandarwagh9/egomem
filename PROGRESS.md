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

## CURRENT PHASE = 1 (RESEARCH)

### Next single task — write the gap statement + `research/hypothesis.md`
`research/landscape.md` now exists (7 verified sources). In one bounded run:
1. Write the **one-paragraph gap statement** (can live at the top of
   `hypothesis.md`). It is already strongly evidenced by the lit map: memory is
   always bound to one consumer paradigm; the best "agnostic" claim is
   intra-VLA only (MAP-VLA); world-model memory is internal/inseparable;
   egocentric human video is fed to LLM-agents/generative models, never to a
   neutral memory a controller consumes.
2. Write **`research/hypothesis.md`** — ONE falsifiable hypothesis with:
   - a **named metric** (e.g. long-horizon task success rate, or
     retrieval-conditioned next-state prediction error),
   - a **numeric threshold** (e.g. "≥ X points over no-memory baseline"),
   - the **transfer claim** (the same memory, written once, improves BOTH a
     world-model consumer AND a VLA consumer without retraining the memory),
   - and an explicit **falsifier** (what observed result would kill it).
   Keep the metric measurable on small/sample data and modest hardware — the
   experiment in Phase 3 must actually run.
Committing `hypothesis.md` meets the **Phase 1 EXIT** → advance to Phase 2 next.

### Constraints to respect when writing the hypothesis
- One claim only; do not bundle two. Pick the single sharpest testable one.
- It must be falsifiable on hardware we actually have (assume CPU / a single
  modest GPU at most until proven otherwise) and on a *small* slice of an
  egocentric dataset — verify dataset availability in Phase 2, not now.

---

## RUN LOG (newest first)

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
