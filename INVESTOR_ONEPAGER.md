# Black Robotics — pre-seed one-pager

**The neutral data + memory layer for embodied AI.**
We turn cheap, opt-in egocentric human video into signed, training-ready datasets — and a
model-agnostic memory that any world model or robot policy can query, without locking the
buyer to one model. *Picks-and-shovels for robot foundation models.*

---

**The problem.** Robot foundation models (VLAs, world models) just got real — and they're
data- and memory-starved. Every robotics team is overpaying to collect interaction data and
re-building the same scene-memory plumbing in-house, welded to their own model architecture.
There is no neutral, buyer-side layer that serves the data *and* the memory across model
paradigms.

**The insight (why now).** The bottleneck moved from models to **data + memory**, and the
cheapest substrate for both is **egocentric human video** — a person doing real tasks, no
robot or teleop rig required. Capture is now a phone app; the missing piece is the neutral
layer that makes that footage usable by any downstream model. Incumbent model labs *can't*
build it — their whole business is lock-in.

**What we've built.**
- **Product, shipped end-to-end:** opt-in egocentric capture (iOS app) → GCP processing
  pipeline → **signed, schema-validated, DPDP-compliant, LeRobot-format datasets.**
- **EgoMem — the validated wedge:** a model-agnostic `write/query` memory layer (open,
  installable, tested) that *both* a world model and a robot policy can call. We didn't
  hypothesize it — we proved it across a 10-experiment program on **real egocentric data**:
  - One neutral memory serves a world-model **and** a VLA consumer (transfer demonstrated).
  - Survives a **fully real perception pipeline** — real detector + real LiDAR depth + real
    tracking, no oracle anywhere.
  - We found its failure mode (data association) **and shipped the fix** (a strict-improvement
    aggregator) — honest negative result included.
  - **It pays off at the task level: long-horizon task completion ~1% → 100% in simulation**
    (memory's value scaling with how partially-observed the task is).

**Why we win (moat).** (1) An **opt-in proprietary egocentric dataset** with compliance and
trust built in — lower cost-per-hour at scale than US labeling shops; (2) a **model-agnostic
memory layer** positioned to become the standard; (3) **neutrality** — the structural position
the model labs cannot occupy.

**Market.** Embodied-AI data spend is large and already funded (Physical Intelligence ~$600M
raised; Lightwheel ~$100M in Q1 alone). The category is crowded with data-labeling plays — the
**neutral buyer-side layer is the open slot.** Bottoms-up TAM: `[FILL IN]`.

**Traction.** `[FILL IN: data hours collected + growth rate; contributors; any pilot/LOI from
an outside robotics team. Lead with the highest real number; state if any interest is from
outside your own network.]`

**Team.** `[FILL IN: founders, backgrounds, why-you, team size, location.]` Demonstrated:
shipped the full capture-to-dataset stack solo/lean and ran the EgoMem research program
end-to-end.

**The ask.** Raising `[$FILL IN]` pre-seed to `[FILL IN: e.g. scale opt-in capture to N hours,
land first 3 design-partner buyers, harden EgoMem into a product SKU]`.

---
*Proof & repro: EgoMem library + paper (`/lib`, `/paper`), every number traced to a logged run.
Contact: roboticsblack@gmail.com*
