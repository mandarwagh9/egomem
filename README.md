# EgoMem

[![ci](https://github.com/mandarwagh9/egomem/actions/workflows/ci.yml/badge.svg)](https://github.com/mandarwagh9/egomem/actions/workflows/ci.yml)

**A model-agnostic memory layer for robotics from egocentric human video.** One
neutral `write(obs) -> mem` / `query(state) -> retrieved_context` store that
**both a world model and a VLA policy** can call — written once from egocentric
observations (RGB-derived detections + depth + camera pose), queried unchanged by
any consumer. In the literature, memory is always baked inside a specific VLA, a
specific world model, or an LLM agent; EgoMem is the buyer-side, paradigm-neutral
layer that seam is missing (see `paper/paper.md` §2).

## Headline result

On a controlled egomotion testbed, on an **out-of-view object recall** task
("object permanence under egomotion"), a single non-parametric EgoMem store —
queried unchanged by both a world-model position predictor and a VLA direction
policy — beats a no-memory baseline and a naive raw-frame buffer, across 3 seeds:

| Consumer | no-memory | naive buffer | **EgoMem** |
|---|---|---|---|
| World-model (pos recall @0.5 m) | 0.011 | 0.018 | **0.999** |
| VLA (direction @30°) | 0.244 | 0.317 | **1.000** |

(means of seeds 0–2; every cell is a row in [`RESULTS.md`](RESULTS.md).) The
hypothesis is **confirmed for both consumers** from one unchanged memory — the
cross-paradigm transfer is demonstrated, not assumed.

**Replicated on real data.** The *unchanged* library reproduces this on real
egocentric scans (ARKitScenes: real ARKit VIO poses + 3D layouts, 14 scenes):
EgoMem **0.70–1.00** world-model and **1.00** VLA recall vs **≤ 0.03** for both
baselines, across 2 seeds (projection gate passed 14/14). See `paper/paper.md` §7.
It also **survives heavy detection noise + dropout** (§7.1): EgoMem stays above
the baselines across a noise×miss grid (worst-corner 0.53 / 0.83 vs ≤ 0.10), and
its margin over a raw buffer *widens* as detections worsen — the cross-frame
averaging is the robustness.

**Honest caveat (the boundary):** the advantage is *localization-quality
dependent*. Under injected camera-pose drift the precise world-model consumer
degrades and, at heavy drift, **collapses to the baseline** (H1 rejected for that
consumer), while the coarser VLA direction consumer survives. See the ablation in
`paper/paper.md` §6. The current testbed is **synthetic** (no real human video
yet) with oracle data association — real-clip validation is the next step.

## EgoMem augments a *real, frozen* VLM (OpenEQA-style spatial QA)

The recognized 2026 frontier is episodic-spatial QA, where VLMs are documented "nearly
blind" (OpenEQA: best VLM ~0.50). EgoMem is model-agnostic in practice: hand its spatial
summary to a **frozen, off-the-shelf Gemini 2.5-flash** (no fine-tuning) and its accuracy on
real-ARKitScenes episodic-spatial questions jumps — **beating the same VLM that is actually
shown egocentric photos of the room** (the true OpenEQA setting):

| condition (frozen VLM) | spatial-QA accuracy |
|---|---|
| no-memory | 0.273 |
| **VLM shown 5 egocentric photos** | 0.491 |
| current-view object list (text) | 0.727 |
| **+ EgoMem spatial summary** | **0.927** |

**+43.6 points over the VLM that sees the room**, +65.5 over no-memory (6 scenes, 55 Qs);
gains concentrate on counting (2/12 → 11/12) and spatial relations (4/13 → 13/13) — exactly
where VLMs fail. Any VLM gains episodic-spatial competence by reading EgoMem. See
`paper/paper.md` §9; rows in [`RESULTS.md`](RESULTS.md) (`exp_id = spatial-qa H11b`).

## Install & reproduce

```bash
pip install -e lib            # Python >=3.10, numpy + torch (CPU is fine)

egomem demo                   # one-command demo: small synthetic run, prints the 3-arm comparison
egomem sim --seed 0           # full benchmark — reproduces the seed-0 numbers in RESULTS.md
egomem sim --seed 0 --pose-drift 0.15   # the heavy-drift ablation (H1 rejected for world-model)
```

**Real-data run (ARKitScenes).** The loader at
`experiments/2026-06-13_arkit-oov/arkit_loader.py` downloads scene zips from the
public ARKitScenes CDN and drives the unchanged library; see `research/design_h2.md`
for the protocol and `experiments/2026-06-13_arkit-oov/config.json` for the scene ids.

`egomem sim --seed 0` prints no-memory 0.016 / 0.280, naive 0.027 / 0.371, EgoMem
1.000 / 1.000 — identical to the committed experiment
(`experiments/2026-06-13_oov-recall/stdout_lib_seed0.log`).

**VLM spatial-QA run.** `experiments/2026-06-15_spatial-qa/spatial_qa.py` builds EgoMem over
real ARKitScenes scenes and queries a frozen VLM under no-memory / vision-frames / EgoMem
contexts. Needs a Gemini key (`GEMINI_API_KEY`) or Vertex ADC (`EGOMEM_VERTEX_PROJECT`).

Use the layer directly (write once, query from any consumer): see `lib/README.md`.

## Repo map

| Path | What |
|---|---|
| [`paper/paper.md`](paper/paper.md) | the paper: method, results, ablations (§6 drift, §7 real data, §8 task success, §9 VLM-QA), limitations |
| [`RESULTS.md`](RESULTS.md) | append-only experiment log — every reported number |
| [`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md) | verified sources + 2026 SOTA refs (OpenEQA, MemoryVLA, …) |
| [`research/`](research) | `landscape.md` (lit map) + falsifiable hypotheses H1–H11 + designs |
| [`lib/`](lib) | the installable `egomem` package + CLI (5 memory classes, 9 tests) |
| [`experiments/`](experiments) | raw logs, configs, metrics per run (synthetic, ARKitScenes, task, spatial-QA) |
| [`PROGRESS.md`](PROGRESS.md) | the research-loop state and run log |

## How it works (one paragraph)

`EgoMem.write` transforms each detection's camera-frame 3D position into a world
frame via the observation pose and accumulates a running per-object estimate;
`EgoMem.query` transforms those world positions back into the *querying* camera
frame, so every consumer receives an egocentric answer (`pos_cam_now`) without
knowing the memory's internals. The store is non-parametric — written once,
queried unchanged by a state predictor and an action policy alike. The two naive
baselines (no memory; raw buffer with no pose transform) isolate that the win
comes from pose-aware world-frame integration.

## License

MIT.
