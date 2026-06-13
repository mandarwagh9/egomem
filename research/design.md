# EgoMem — Design (Phase 2)

**Date:** 2026-06-13. Specs the smallest real version that tests **H1**
(`hypothesis.md`). No code here — Phase 3 implements exactly this.

**Environment (verified this run):** Python 3.13.2, numpy 1.26.4,
torch 2.10.0 **CPU-only** (`cuda=False`), sklearn 1.7.0. Everything below is
designed to run on CPU in minutes.

---

## 1. Neutral API (paradigm-neutral — no VLA/world-model-specific fields)

```python
# Pose is a 4x4 SE(3) world<-camera matrix. Positions are 3D (meters).

@dataclass
class Detection:
    category: str          # open-vocab label
    pos_cam: np.ndarray    # (3,) object position in the CURRENT camera frame
    confidence: float      # detector confidence in [0,1]
    obj_id: int | None = None   # if a tracker assigns identities; else None

@dataclass
class Observation:         # one egocentric frame's worth of evidence
    t: int                 # frame index
    cam_pose: np.ndarray   # (4,4) world<-camera at frame t
    detections: list[Detection]

@dataclass
class RecalledObject:      # the unit of the data contract (see §2)
    obj_id: int
    category: str
    pos_cam_now: np.ndarray   # (3,) recalled position, in the *query* camera frame
    last_seen_t: int
    confidence: float
    in_view_now: bool         # currently visible vs recalled-from-memory

class Memory(Protocol):
    def write(self, obs: Observation) -> None: ...
    # query carries the consumer's CURRENT egocentric state; returns context.
    def query(self, state: "QueryState") -> list[RecalledObject]: ...

@dataclass
class QueryState:
    t: int
    cam_pose: np.ndarray      # (4,4) world<-camera NOW
    visible: list[Detection]  # what the consumer can currently see
    goal_category: str | None = None   # optional, for goal-directed reads
```

Key neutrality property: `query` returns positions **re-expressed in the
querying camera frame** (`pos_cam_now`), so any consumer — predictor or policy —
receives an egocentric, current-frame answer and needs no knowledge of the
memory's internals.

## 2. Data contract (what both consumers read)

`query(state) -> list[RecalledObject]`, ordered by confidence (goal object first
if `goal_category` set). Both heads consume the *same* list:

- **World-model head** reads all records → predicts the next frame's object
  positions (including out-of-view ones it must remember persist).
- **VLA head** reads the goal record → predicts the egocentric direction to act
  toward the (out-of-view) goal.

The memory is **non-parametric** (a procedural data structure with no trainable
weights). Therefore "no per-consumer retraining of the memory" is satisfied by
construction: it is written once per episode and queried unchanged by both heads.
The non-trivial, falsifiable questions remain (a) does this neutral context let
each consumer beat its *no-memory* baseline by ≥20 pp, and (b) does EgoMem's
pose-aware integration beat *naive* storage — exactly H1's gates.

## 3. Dataset — synthetic egocentric egomotion testbed (PRIMARY)

Real egocentric corpora (Ego4D/EPIC-Kitchens) need large gated downloads and
lack clean per-object 3D+depth+pose ground truth for a precise out-of-view
metric; CPU-only + no dataset pull here makes them infeasible this iteration.
**Primary path = a synthetic egomotion simulator** — still a *real* run of the
memory layer and the consumers, with exact ground truth:

- A room = M objects (M∈[6,10]), each with a 3D position and a category drawn
  from a small vocab. 
- A smooth camera trajectory of T frames (T≈30): position + yaw vary over time
  (egomotion). Camera intrinsics define a horizontal FOV (e.g. 60°) and range.
- Per frame: an object is **observed** iff inside the view frustum (FOV + max
  range + in front). Each observation → a `Detection` with `pos_cam` (true world
  position transformed into that frame's camera coords) + Gaussian noise +
  confidence. This *is* the RGB+depth+pose-derived detection signal, simulated.

This isolates the geometry that out-of-view recall depends on, with known truth.
It does **not** use real human video — that is the honest limitation, recorded
as a **Phase-4 stretch**: swap the synthetic detector for real detections +
monocular depth + camera pose on a small egocentric clip (e.g. a LeRobot-v3
egocentric sample), same API downstream.

## 4. Baselines (mandatory — 3 arms, identical heads, only the memory differs)

| Arm | Memory behavior |
|---|---|
| **no-memory** | `query` returns ONLY currently-visible detections. Out-of-view objects are unrecoverable. |
| **naive (raw-frame buffer)** | Stores every frame's raw detections + the frame's pose. On query, returns the most recent frame in which an object appeared, reporting its position **in that old camera frame** (no transform to the current frame). Has the data but lacks pose-consistent 3D integration → stale/wrong-frame positions after egomotion. |
| **EgoMem** | Pose-aware persistent object memory: each detection's `pos_cam` is transformed to **world frame** via `cam_pose` and upserted per object (running average / latest). On query, world positions are transformed into the **current** camera frame (`pos_cam_now`). |

The naive arm is the critical control: it ensures any EgoMem win comes from
*pose-aware world-frame integration*, not from mere buffering.

## 5. The single experiment (tests H1)

**Generate** N episodes (e.g. 300: 200 train / 100 test) per seed. For each
episode: run `write()` over all T frames to build the memory, then form
**out-of-view recall queries** for objects that are NOT in view at the final
frame but were seen earlier.

**Two consumer read-heads** (tiny, identical arch across arms; trained per arm on
the train split, evaluated on test):
- **World-model head** (MLP/GRU): input = current visible features +
  `retrieved_context` → predict next-frame 3D positions of all objects. Metric =
  out-of-view object **recall success** = fraction of out-of-view objects whose
  predicted position is within tolerance τ_pos (e.g. 0.5 m). Secondary: mean L2.
- **VLA head** (MLP): input = goal-category embedding + current state +
  `retrieved_context` → predict the unit egocentric direction to the goal.
  Metric = **success** = predicted direction within τ_ang (e.g. 30°) of truth.

**Logged** to `experiments/<date>_<name>/`: `config.json` (seed, N, M, T, FOV,
noise, tolerances), full `stdout.log`, and `metrics.json` (per-arm × per-consumer
success rate + mean error). **One row to RESULTS.md** per run.

**Threshold check (H1):** PASS iff for **both** consumers
`success(EgoMem) ≥ success(no-memory) + 20 pp` **and**
`success(EgoMem) ≥ success(naive)`. Phase 4 requires this stable over ≥2 seeds.

**Falsifier mapping:** maps 1:1 to `hypothesis.md` §Falsifier (no effect / naive
ties / non-transferable / one-consumer-only). Non-transferable cannot occur by
construction here (single non-parametric memory) — so if EgoMem helps both, the
transfer claim is *demonstrated*, not assumed; if it helps neither or only one,
H1 fails on falsifier 1 or 4.

---

**Phase 2 EXIT satisfied:** API signatures (§1), data contract (§2), dataset
(§3, verified-feasible synthetic primary + real-clip stretch), baselines (§4),
and the single experiment that tests H1 (§5). → Advance to Phase 3 (EXPERIMENT).
