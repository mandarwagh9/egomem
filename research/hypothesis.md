# EgoMem — Gap Statement & Hypothesis (Phase 1 EXIT)

**Date:** 2026-06-13. Grounded entirely in `landscape.md` (7 verified sources).

## Gap statement (one paragraph)

Across every artifact surveyed, robot/embodied memory is **bound to a single
consumer paradigm**: it lives inside an LLM agent (Embodied VideoAgent), inside a
VLA policy (MAP-VLA, MEM), or as a world model's internal recurrent latent state
(Dreamer/RSSM, confirmed by the world-models survey). The strongest
"model-agnostic" result in the field is *intra-paradigm only* — MAP-VLA is
plug-and-play across **frozen VLAs**, but a world model still cannot call it, and
world-model RSSM memory is inseparable from the model so nothing can call it from
outside. Meanwhile egocentric human video with depth and pose — the exact
substrate that makes scene memory cheap (Embodied VideoAgent) and that exists at
scale (MEgoHand: 3.35M RGB-D frames) — is only ever fed to LLM agents or
generative models, never to a neutral memory that a *controller* (VLA) and a
*predictor* (world model) both consume. **No artifact exposes one
`write/query/retrieve` memory, built once from egocentric human video, that BOTH
a world model AND a VLA can consume without retraining.** That is the unoccupied
seam EgoMem targets.

---

## Hypothesis H1 (the single falsifiable claim)

> A **single model-agnostic memory layer** — written once from egocentric human
> video (RGB + depth + camera pose) through a neutral `write(obs) -> mem` /
> `query(state) -> retrieved_context` API, with **no per-consumer retraining of
> the memory** — improves long-horizon performance for **both** consumer
> paradigms (a world-model predictor **and** a VLA-style policy) over a
> no-memory baseline, on a task that requires recalling information no longer in
> view.

The test task is **out-of-view object recall** ("object permanence under
egomotion"): after an egocentric clip in which object *X* was observed and then
left the field of view, a consumer must act on / predict *X* using only what it
can recall. Both paradigms genuinely need this — a world model to predict
consistent futures, a VLA to act toward unseen targets — so it is a fair shared
probe.

### Named metric + threshold

- **Primary metric:** **task success rate (%)** on the out-of-view recall probe
  — success = the consumer produces the correct target (object location, within
  a fixed distance tolerance, or the correct discrete choice) for an object that
  is *currently out of frame* but was seen earlier in the episode.
- **Threshold (what counts as supporting H1):** EgoMem must beat the **no-memory
  baseline by ≥ 20 percentage points** on success rate **for both consumers**,
  **and** must be **≥ the naive-memory baseline** (raw frame buffer / flat
  embedding store) for both. Rationale: for *out-of-view* objects a no-memory
  consumer is near floor, so a real memory effect is large; requiring EgoMem to
  also beat dumb storage ensures the *structure* (pose-aware persistent object
  memory), not mere buffering, is what helps.
- **Secondary metric (world-model consumer):** next-state prediction error
  (e.g. L2 on predicted object position / frame-embedding) — expected *lower*
  with EgoMem-retrieved context. Reported as supporting evidence, not the gate.

### The transfer claim (the novel part)

The **same memory store is written once and queried unchanged by both
consumers** — no fine-tuning or rebuild of the memory between the world-model
consumer and the VLA consumer. Only each consumer's own small read-head may
differ. If meeting the threshold requires a *different memory per consumer*, the
"model-agnostic" claim is false.

### Falsifier (any one of these kills H1)

1. **No effect:** no-memory baseline is within 20 pp of EgoMem on success for
   either consumer.
2. **Structure adds nothing:** EgoMem does not exceed the naive raw-frame-buffer
   baseline for either consumer.
3. **Not transferable:** the gains require rebuilding/retraining the memory per
   consumer (one memory cannot serve both).
4. **No transfer:** gains appear for one consumer but the other shows no
   improvement over its own no-memory baseline.

A clean negative on any of these is a publishable result and will be reported
honestly (the paper states the claim died and why).

### Feasibility scope (so Phase 3 actually runs)

- **Data:** a *small slice* of an egocentric human-video source with depth + pose
  (candidates to confirm in Phase 2: an egocentric HOI corpus, an Ego4D /
  EPIC-Kitchens clip subset, or a LeRobot-v3 egocentric sample). Dataset
  availability is verified in Phase 2 (DESIGN), not assumed here.
- **Hardware:** consumers are *small* models (tiny MLP/GRU read-heads over
  precomputed embeddings; memory built procedurally from detections + depth +
  pose). Target: runnable on CPU or a single modest GPU.
- **Seeds:** ≥ 2 seeds required before the result is called stable (Phase 4).
- **Baselines (mandatory):** (i) no-memory, (ii) naive memory = raw frame buffer
  / flat embedding store. EgoMem is the third arm.

---

**Phase 1 EXIT satisfied:** hypothesis with named metric (out-of-view recall
success rate), numeric threshold (≥ 20 pp over no-memory; ≥ naive memory),
transfer claim (one memory, both consumers, no memory retraining), and explicit
falsifiers. → Advance to Phase 2 (DESIGN).
