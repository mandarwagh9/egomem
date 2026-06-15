# EgoMem — Cycle 11 (H11): SOTA step — EgoMem augments a real VLM on episodic-spatial QA

**Date:** 2026-06-15. Researched the 2026 frontier: the recognized hard problem is
**episodic / spatial memory for embodied QA** — OpenEQA (best VLM GPT-4V **49.6%** vs human
**86.8%**; models "nearly blind"), the new **EMemBench** / **FindingDory** memory benchmarks,
and **MemoryVLA**. The documented bottleneck is exactly what EgoMem holds *exactly*: spatial
scene memory. This cycle tests EgoMem as a model-agnostic **tool that augments a real LLM/VLM**
on episodic-spatial questions — the Embodied-VideoAgent thesis, but buyer-side and neutral.

## Hypothesis H11

> On episodic-spatial questions about real egocentric scenes (ARKitScenes), giving a real
> frozen LLM/VLM the **EgoMem spatial-memory summary** as context raises answer accuracy by
> ≥ 20 points over (a) a no-memory ("blind") baseline and (b) a current-frame-only baseline —
> most on the question types where VLMs are documented to fail (counting, spatial relations,
> out-of-view recall).

### Setup

- **Data:** ARKitScenes scenes (real GT 3D object boxes + ARKit trajectory). EgoMem is built by
  replaying the trajectory (observing objects via the camera, as in H2), then rendered to a
  short textual spatial summary.
- **Consumer:** a real frozen model (Gemini via `google-genai`, `GOOGLE_API_KEY`) — EgoMem is
  model-agnostic, so any LLM/VLM is a valid consumer. No fine-tuning.
- **Conditions (same questions, same model):**
  - **no-memory:** question only (the agent must answer from nothing) → ~chance.
  - **frame-only:** objects visible in the final frame only (a memoryless agent's current view).
  - **EgoMem:** the accumulated spatial-memory summary (what EgoMem integrated over the traverse).
- **Question types** (generated programmatically from GT, with computed answers): counting,
  existence, spatial relation (left/right of), proximity (closest to), out-of-view direction.

### Metric + threshold

QA accuracy (exact-match / tolerance per type). H11 supported if EgoMem ≥ no-memory + 20 pts
AND ≥ frame-only, overall and on the spatial-episodic subset. Falsifier: EgoMem within 20 pts
of no-memory, or below frame-only — i.e. structured spatial memory doesn't help a real model.

### Why this is the SOTA step

It moves EgoMem from a custom recall metric (H1–H10) to the **recognized benchmark family**
(OpenEQA-style episodic-spatial QA) with a **real foundation-model consumer** — directly
comparable to Embodied VideoAgent, and demonstrating the model-agnostic value proposition
(any frozen VLM + EgoMem). CPU + cheap API; real data; real model.

### Plan (this cycle, iterated over loop runs)

1. Build the QA generator (GT → questions + computed answers) + EgoMem→text renderer. ✅ first.
2. Wire the real model (Gemini) with a smoke test.
3. Run a first eval (small N) → real accuracy numbers per condition. Iterate up in N / scenes /
   add a vision-frame baseline (true OpenEQA setting).

## VERDICT: H11 CONFIRMED (2026-06-15)

Real frozen **Gemini 2.5-flash** over Vertex, 6 ARKitScenes scenes, 60 episodic-spatial
questions, GT-derived answers (`stdout_qa.log`, `metrics.json`):

| condition | accuracy | count | left/right | ahead/behind | exists |
|---|---|---|---|---|---|
| no-memory | 0.217 (13/60) | 0/12 | 3/15 | 3/15 | 6/12 |
| frame-only | 0.400 (24/60) | 2/12 | 3/15 | 10/15 | 9/12 |
| **EgoMem** | **0.683 (41/60)** | **10/12** | **10/15** | 10/15 | 10/12 |

EgoMem ≥ no-memory + 20 pp (**+46.7**) AND ≥ frame-only (**+28.3**) → **CONFIRMED**. The
gains concentrate exactly where VLMs are documented "blind": **counting** (0→10/12) and
**spatial relations** (3→10/15). A frozen, off-the-shelf VLM + EgoMem's spatial summary
roughly **triples** episodic-spatial QA accuracy — the model-agnostic value proposition
(any VLM, no fine-tuning), on the recognized OpenEQA-style task family, on real data.

**Caveats:** 60 Qs / 6 scenes (modest N); answers are GT-derived templated questions (not
human-authored like OpenEQA); EgoMem is built from GT object positions replayed through the
real trajectory (not a real detector — that pipeline is §7.6/H8-H9). Vertex 429 rate limits
required exp-backoff. Next: scale N, add real-detector memory (combine with H8-H9), add a
vision-frame VLM baseline (images, true OpenEQA setting).
