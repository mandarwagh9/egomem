# EgoMem

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

**Honest caveat (the boundary):** the advantage is *localization-quality
dependent*. Under injected camera-pose drift the precise world-model consumer
degrades and, at heavy drift, **collapses to the baseline** (H1 rejected for that
consumer), while the coarser VLA direction consumer survives. See the ablation in
`paper/paper.md` §6. The current testbed is **synthetic** (no real human video
yet) with oracle data association — real-clip validation is the next step.

## Install & reproduce

```bash
pip install -e lib            # Python >=3.10, numpy + torch (CPU is fine)

egomem demo                   # one-command demo: small synthetic run, prints the 3-arm comparison
egomem sim --seed 0           # full benchmark — reproduces the seed-0 numbers in RESULTS.md
egomem sim --seed 0 --pose-drift 0.15   # the heavy-drift ablation (H1 rejected for world-model)
```

`egomem sim --seed 0` prints no-memory 0.016 / 0.280, naive 0.027 / 0.371, EgoMem
1.000 / 1.000 — identical to the committed experiment
(`experiments/2026-06-13_oov-recall/stdout_lib_seed0.log`).

Use the layer directly (write once, query from any consumer): see `lib/README.md`.

## Repo map

| Path | What |
|---|---|
| [`paper/paper.md`](paper/paper.md) | the paper: method, results, ablation, limitations |
| [`RESULTS.md`](RESULTS.md) | append-only experiment log — every reported number |
| [`BIBLIOGRAPHY.md`](BIBLIOGRAPHY.md) | 7 verified sources with links |
| [`research/`](research) | `landscape.md` (lit map), `hypothesis.md` (H1), `design.md` |
| [`lib/`](lib) | the installable `egomem` package + CLI |
| [`experiments/`](experiments) | raw logs, configs, metrics per run |
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
