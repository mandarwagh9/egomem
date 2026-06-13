# EgoMem — Literature Map (Phase 1, RESEARCH)

**Date:** 2026-06-13. **Scope:** survey the named research bridges and
surrounding work to locate, precisely, where a *model-agnostic* memory layer
for robotics does and does not exist. Four areas: (a) persistent scene memory
from egocentric video; (b) memory inside VLAs; (c) memory inside world models;
(d) egocentric human-video data in LeRobot v3 format.

**Verification status:** every row below was fetched and read this run (not just
returned by a search snippet). Each appears in `../BIBLIOGRAPHY.md` with its
link. A handful of additional titles that search surfaced but I did **not**
individually open are listed separately at the bottom as *unverified leads* —
they are NOT in the bibliography and no claim rests on them.

---

## Sources table

| # | Source (year) | Area | Memory mechanism | Bound to which consumer | Model-bound vs agnostic | Substrate that feeds it |
|---|---|---|---|---|---|---|
| 1 | **Embodied VideoAgent** — Fan et al., ICCV 2025 (arXiv 2501.00358) | (a) scene memory | Persistent **object memory** (per-object entry: id, category, state, relations, 3D bbox, CLIP feature) + VideoAgent temporal memory + 2 history buffers; VLM auto-updates entries on perceived actions | An **LLM agent** that answers QA / planning queries | **Bound to the LLM-agent system.** Memory is queried by their agent; not exposed as a standalone API a controller or world model can call | **Egocentric video + depth + camera 6D pose** ✅ (the one source already using exactly our substrate) |
| 2 | **MAP-VLA** — Li et al., 2025 (arXiv 2511.09516) | (b) memory-in-VLA | Memory **library of learnable soft prompts** per task stage, built from demos; **trajectory-similarity retrieval** at run time | A VLA policy | **Agnostic _within_ the VLA paradigm** — explicitly a "plug-and-play module for a **frozen VLA**." But VLA-only; a world model cannot consume it | Robot **teleop demonstrations** (not human video) |
| 3 | **MEM: Multi-Scale Embodied Memory** — Torne, Pertsch, …, Levine, Finn, Driess, 2026 (arXiv 2603.03596) | (b) memory-in-VLA | **Dual** memory: short-term video (encoder-compressed) + long-term text (semantic abstractions); enables ~15-min tasks | A VLA policy | "For VLA models" generally, but architecture is **VLA-bound**; not consumable by a world model | Robot **video observations + text** |
| 4 | **NE-Dreamer / Dreamer-line RSSM** — Bredis et al., 2026 (arXiv 2603.02765) | (c) memory-in-world-model | **RSSM**: deterministic recurrent state `h_t = f(h_{t-1}, z_{t-1}, a_{t-1})` + stochastic latent `z_t`; memory = the rolled latent state | The world model itself (imagination rollouts) | **Internal & inseparable.** RSSM state is not externally queryable; not a layer | The model's **own latent dynamics** (pixels→latents) |
| 5 | **Survey: World Models for Embodied AI** — Li et al., 2025 (arXiv 2510.16732) | (c) memory-in-world-model | Frames world models as "internal simulators that capture environment dynamics"; temporal modeling taxonomy | The world model | Confirms memory is **model-internal** across the field | varies (per surveyed model) |
| 6 | **MEgoHand** — Zhou et al., 2025 (arXiv 2505.16602) | (d) egocentric human data | (a generative model, not a memory) — relevant as a **data point**: large egocentric human HOI corpus, 3.35M RGB-D frames / 24K interactions / 1.2K objects | n/a (hand-motion generation) | n/a | **Egocentric human RGB + monocular depth + initial hand pose** ✅ (proves the substrate exists at scale) |
| 7 | **LeRobotDataset v3.0** — Hugging Face, 2025 | (d) data format | (a storage format, not memory) | n/a | The **neutral container** both consumers already read | parquet (state/action) + MP4 (video) + JSON meta; multi-episode packing; many embodiments |

---

## Per-area synthesis

**(a) Persistent scene memory from egocentric video.** Embodied VideoAgent is
the *only* verified artifact already using our exact substrate (egocentric video
+ depth + pose) to build a persistent, queryable memory. But its memory is wired
to an **LLM agent** for visual-QA / planning — it is not offered as a write/query
API that a *control policy* (VLA) or a *world model* could call. It proves the
substrate→memory step is feasible; it does not provide the neutral layer.

**(b) Memory inside VLAs.** Active, fast-moving (MAP-VLA Nov-2025, MEM Mar-2026,
plus surfaced leads HELM/ECHO/MemoryVLA). The frontier has reached
*model-agnosticism within the VLA paradigm* — MAP-VLA is a plug-and-play module
for any frozen VLA. But (i) the consumer is always a VLA, never also a world
model, and (ii) the substrate is robot **teleop demonstrations**, not egocentric
human video.

**(c) Memory inside world models.** Dreamer/RSSM-line memory is a deterministic
recurrent latent state, **internal and inseparable** from the model — not an
external, queryable layer at all. The survey confirms this is the norm.

**(d) Substrate & container.** Egocentric human video at scale exists (MEgoHand:
3.35M RGB-D frames + depth + hand pose). LeRobot v3 is a neutral container both
ecosystems already read (parquet + MP4 + JSON, multi-episode). So both the data
and the format to carry it are available off-the-shelf.

---

## The pattern (what is consistently true across all verified work)

1. **Memory is always bound to exactly one consumer paradigm.** LLM-agent memory
   (1), VLA memory (2,3), or world-model latent state (4,5). No artifact exposes
   one memory that *both* a world model *and* a VLA can call.
2. **The best "model-agnostic" claim in the field is intra-paradigm only**
   (MAP-VLA: any frozen *VLA*). Cross-paradigm neutrality (VLA *and* world model)
   is absent.
3. **Robot policies are fed teleop demos; egocentric human video is fed to LLM
   agents or generative models** — never to a neutral memory that a controller
   consumes. The substrate and the consumers have not been connected.

This is the seam the mission targets: a single `write/query/retrieve` memory,
fed by **egocentric human video** (LeRobot v3 + depth + pose), consumable by
**both** a world model **and** a VLA **without retraining**. The next run turns
this observation into the one-paragraph gap statement and the falsifiable
`hypothesis.md` — not done here, by design.

---

## Unverified leads (surfaced by search, NOT opened this run — not in bibliography)

Real-looking arXiv URLs returned by search but not individually fetched, so no
claim above depends on them. Candidates to verify in a later run if needed:
- HELM: Harness-Enhanced Long-horizon Memory for VLA (arXiv 2604.18791) — billed as "model-agnostic" memory for VLA.
- ECHO: Continuous Hierarchical Memory for VLA (arXiv 2605.10993).
- MemoryVLA: Dual-Memory for Robotic Manipulation (emergentmind topic; arXiv id not confirmed).
- VL-KnG: persistent spatiotemporal knowledge graphs from egocentric video (arXiv 2510.01483).
- R2I "Mastering Memory Tasks with World Models" (ICLR 2024) — canonical world-model memory benchmark.
- Ego4D / EPIC-Kitchens — canonical egocentric human-video corpora (substrate options).
