"""EgoMem core — a model-agnostic memory layer for robotics from egocentric video.

One neutral `write(obs) -> None` / `query(state) -> list[RecalledObject]` API,
three interchangeable implementations (NoMemory, NaiveBuffer, EgoMem). The memory
is non-parametric: written once from egocentric observations (RGB-derived
detections + depth + camera pose) and queried unchanged by any consumer — a
world-model state-predictor and a VLA policy alike.

This is the validated method from experiments/2026-06-13_oov-recall (see RESULTS.md
and paper/). Behavior is identical to the experiment's arms; only refactored into
an importable package.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Optional

import numpy as np

__all__ = [
    "Detection", "Observation", "QueryState", "RecalledObject",
    "NoMemory", "NaiveBuffer", "EgoMem", "EgoMemRobust", "EgoMemVerify", "MEMORIES",
    "cam_pose_mat", "to_cam", "to_world",
]

# --------------------------------------------------------------------------- #
# Geometry. Pose is a 4x4 SE(3) "world<-camera" matrix; camera-frame coords are
# (right, up, forward), so pos_cam[2] is depth.
# --------------------------------------------------------------------------- #
def cam_basis(theta: float):
    f = np.array([math.cos(theta), math.sin(theta), 0.0])   # forward
    r = np.array([math.sin(theta), -math.cos(theta), 0.0])  # right
    u = np.array([0.0, 0.0, 1.0])                           # up
    return r, u, f


def cam_pose_mat(pos, theta: float) -> np.ndarray:
    """Build a world<-camera 4x4 from a ground position and yaw."""
    r, u, f = cam_basis(theta)
    T = np.eye(4)
    T[:3, :3] = np.column_stack([r, u, f])
    T[:3, 3] = np.asarray(pos, dtype=float)
    return T


def _RC(T: np.ndarray):
    return T[:3, :3], T[:3, 3]


def to_cam(P_world, T: np.ndarray) -> np.ndarray:
    """World point -> camera-frame coords (right, up, forward)."""
    R, c = _RC(T)
    return R.T @ (np.asarray(P_world, dtype=float) - c)


def to_world(p_cam, T: np.ndarray) -> np.ndarray:
    """Camera-frame point -> world coords."""
    R, c = _RC(T)
    return R @ np.asarray(p_cam, dtype=float) + c


# --------------------------------------------------------------------------- #
# Neutral data contract (no VLA/world-model-specific fields).
# --------------------------------------------------------------------------- #
@dataclass
class Detection:
    category: str
    pos_cam: np.ndarray            # (3,) object position in the CURRENT camera frame
    confidence: float = 1.0
    obj_id: Optional[int] = None   # tracker identity if available; else keyed by category

    def key(self):
        return self.obj_id if self.obj_id is not None else self.category


@dataclass
class Observation:
    """One egocentric frame's worth of evidence handed to `write`."""
    t: int
    cam_pose: np.ndarray           # (4,4) world<-camera at frame t
    detections: list               # list[Detection]


@dataclass
class QueryState:
    """The querying consumer's CURRENT egocentric state handed to `query`."""
    t: int
    cam_pose: np.ndarray           # (4,4) world<-camera NOW
    visible: list = field(default_factory=list)   # list[Detection] currently visible
    goal_category: Optional[str] = None


@dataclass
class RecalledObject:
    """The unit returned by `query`; positions are in the QUERY camera frame."""
    obj_id: object
    category: str
    pos_cam_now: np.ndarray        # (3,) recalled position, re-expressed in the query frame
    last_seen_t: int
    confidence: float
    in_view_now: bool


def _visible_records(state: QueryState):
    out = {}
    for d in state.visible:
        out[d.key()] = RecalledObject(d.key(), d.category, np.asarray(d.pos_cam, float),
                                      state.t, d.confidence, True)
    return out


def _ordered(records: dict, goal_category):
    recs = list(records.values())
    recs.sort(key=lambda r: (r.category != goal_category, -r.confidence))
    return recs


# --------------------------------------------------------------------------- #
# Three interchangeable memories behind the same API.
# --------------------------------------------------------------------------- #
class NoMemory:
    """Baseline: remembers nothing; query returns only what is visible now."""
    def write(self, obs: Observation) -> None:
        pass

    def query(self, state: QueryState):
        return _ordered(_visible_records(state), state.goal_category)


class NaiveBuffer:
    """Baseline: raw frame buffer. Stores each object's last-seen camera-frame
    position WITHOUT any pose transform, so recalled positions are stale (wrong
    frame) once the camera has moved. Isolates the value of pose-aware
    integration when compared against EgoMem."""
    def __init__(self):
        self.last = {}   # key -> (category, pos_cam, confidence, t)

    def write(self, obs: Observation) -> None:
        for d in obs.detections:
            self.last[d.key()] = (d.category, np.asarray(d.pos_cam, float), d.confidence, obs.t)

    def query(self, state: QueryState):
        out = _visible_records(state)
        for k, (cat, pos_old, conf, t) in self.last.items():
            if k not in out:
                out[k] = RecalledObject(k, cat, pos_old, t, conf, False)  # stale, untransformed
        return _ordered(out, state.goal_category)


class EgoMem:
    """The proposed layer: pose-aware persistent object memory. Each detection's
    camera-frame position is transformed to a world frame via the observation
    pose and accumulated per object; on query, world positions are re-expressed
    in the querying camera frame. Validated to serve both a world-model and a VLA
    consumer (RESULTS.md), conditional on reasonable localization quality."""
    def __init__(self, default_conf: float = 0.5):
        self.world = {}          # key -> dict(category, pos_world, n, last_seen_t)
        self.default_conf = default_conf

    def write(self, obs: Observation) -> None:
        for d in obs.detections:
            Pw = to_world(d.pos_cam, obs.cam_pose)
            k = d.key()
            if k in self.world:
                e = self.world[k]
                e["pos_world"] = (e["pos_world"] * e["n"] + Pw) / (e["n"] + 1)
                e["n"] += 1
                e["last_seen_t"] = obs.t
            else:
                self.world[k] = dict(category=d.category, pos_world=Pw, n=1, last_seen_t=obs.t)

    def query(self, state: QueryState):
        out = _visible_records(state)
        for k, e in self.world.items():
            if k not in out:
                pos_now = to_cam(e["pos_world"], state.cam_pose)
                out[k] = RecalledObject(k, e["category"], pos_now, e["last_seen_t"],
                                        self.default_conf, False)
        return _ordered(out, state.goal_category)


class EgoMemRobust:
    """Association-robust variant of EgoMem: keeps per-object world-position
    observations and returns the coordinate-wise MEDIAN at query instead of the
    running mean. A median tolerates a minority of mis-associated (wrong-id)
    detections that a mean propagates, so this degrades more gracefully under
    tracker id-swaps (validated: identical to EgoMem on clean data; strictly better
    under association error, recovering the realistic noise+miss+swap operating
    point — see paper §7.3). Heavy association error still needs explicit
    association handling."""
    def __init__(self, default_conf: float = 0.5, max_obs: int = 128):
        self.obs = {}            # key -> dict(category, poss=[world pos], last_seen_t)
        self.default_conf = default_conf
        self.max_obs = max_obs

    def write(self, obs: Observation) -> None:
        for d in obs.detections:
            Pw = to_world(d.pos_cam, obs.cam_pose)
            k = d.key()
            e = self.obs.get(k)
            if e is None:
                e = dict(category=d.category, poss=[], last_seen_t=obs.t)
                self.obs[k] = e
            e["poss"].append(Pw); e["last_seen_t"] = obs.t; e["category"] = d.category
            if len(e["poss"]) > self.max_obs:
                e["poss"].pop(0)

    def query(self, state: QueryState):
        out = _visible_records(state)
        for k, e in self.obs.items():
            if k not in out:
                med = np.median(np.asarray(e["poss"]), axis=0)
                out[k] = RecalledObject(k, e["category"], to_cam(med, state.cam_pose),
                                        e["last_seen_t"], self.default_conf, False)
        return _ordered(out, state.goal_category)


class EgoMemVerify:
    """Trust-but-verify association — the recommended aggregator. Each detection
    prefers the track carrying its claimed id when that track is spatially
    consistent (so correct ids are trusted and nearby distinct objects stay
    separate); a never-seen id spawns its own track; a *reused but spatially
    inconsistent* id is treated as a tracker swap and re-associated to the nearest
    track. Aggregates by median, labels by majority id.

    Validated on real ARKitScenes (paper §7.5): identical to `EgoMem` on clean data
    (no regression) and the best variant under association error — it gets the
    clean-data accuracy of the mean AND the swap-robustness of spatial association,
    a strict Pareto improvement. Extreme association/detection-noise still degrade
    all variants."""
    def __init__(self, gate_radius: float = 1.0, default_conf: float = 0.5):
        self.tracks = []
        self.gate_radius = gate_radius
        self.default_conf = default_conf

    @staticmethod
    def _est(tr):
        return np.median(np.asarray(tr["poss"]), axis=0)

    def write(self, obs: Observation) -> None:
        for d in obs.detections:
            Pw = to_world(d.pos_cam, obs.cam_pose)
            k = d.key()
            by_id = [tr for tr in self.tracks if k in tr["votes"]]
            target = None
            for tr in by_id:                                   # 1) claimed id, spatially consistent
                if float(np.linalg.norm(self._est(tr) - Pw)) <= self.gate_radius:
                    target = tr; break
            if target is None:
                if not by_id:                                  # 2a) new id -> spawn (unless coincident)
                    for tr in self.tracks:
                        if float(np.linalg.norm(self._est(tr) - Pw)) <= self.gate_radius * 0.3:
                            target = tr; break
                else:                                          # 2b) reused id, inconsistent -> swap
                    bestd = self.gate_radius
                    for tr in self.tracks:
                        dist = float(np.linalg.norm(self._est(tr) - Pw))
                        if dist < bestd:
                            bestd, target = dist, tr
            if target is None:                                 # 3) spawn
                target = dict(poss=[], votes={}, cats={}, last_seen_t=obs.t)
                self.tracks.append(target)
            target["poss"].append(Pw)
            target["votes"][k] = target["votes"].get(k, 0) + 1
            target["cats"][d.category] = target["cats"].get(d.category, 0) + 1
            target["last_seen_t"] = obs.t

    def query(self, state: QueryState):
        out = _visible_records(state)
        for tr in self.tracks:
            vid = max(tr["votes"], key=tr["votes"].get)
            if vid in out:
                continue
            cat = max(tr["cats"], key=tr["cats"].get)
            out[vid] = RecalledObject(vid, cat, to_cam(self._est(tr), state.cam_pose),
                                      tr["last_seen_t"], self.default_conf, False)
        return _ordered(out, state.goal_category)


# MEMORIES drives the sim/CLI benchmark arms; kept at the 3 documented arms so
# `egomem sim` reproduction is unchanged. EgoMemRobust / EgoMemVerify are exported
# for direct use (EgoMemVerify is the recommended aggregator under id-swap risk).
MEMORIES = {"no-memory": NoMemory, "naive": NaiveBuffer, "egomem": EgoMem}
