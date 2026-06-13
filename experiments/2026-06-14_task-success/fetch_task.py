"""EgoMem Cycle 10 (H10) — downstream TASK SUCCESS (not a recall proxy).

A closed-loop long-horizon "scan-then-fetch" task. An agent (egocentric camera with
position+heading) first scans a room in place (building memory), then must navigate to
K target objects in a fixed order. When a target's turn comes it is usually OUT of view,
so the agent must recall where it is. The SAME rule-based controller drives all arms;
they differ only in what `mem.query` returns for an out-of-view target:
  - no-memory: nothing -> the agent must re-search (spin) to re-acquire it.
  - naive:     a stale last-seen camera-frame position (wrong after moving) -> misdirected.
  - egomem:    the correct recalled bearing -> goes straight there.

Metric = TASK SUCCESS RATE (all K targets reached within the step budget). This isolates
the value of the memory's *information* (controller is identical), and reports a
task-level number, not recall@tol. CPU, deterministic.

Run: python fetch_task.py --seeds 0 1 2
"""
import argparse, json, math, os, sys
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "lib")))
from egomem import NoMemory, NaiveBuffer, EgoMem, Observation, QueryState, Detection, cam_pose_mat, to_cam, to_world

ARMS = {"no-memory": NoMemory, "naive": NaiveBuffer, "egomem": EgoMem}

ROOM = 14.0
M_OBJ = 10
K_TARGETS = 4
HALF_FOV = math.radians(30.0)
MAX_RANGE = 4.0          # limited sensing: cannot re-find a far object by spinning
MIN_DEPTH = 0.2
DET_NOISE = 0.05
REACH = 0.8
STEP_LEN = 0.4
MAX_TURN = 0.6
SCAN_GRID = 4            # 4x4 mapping waypoints (360 deg within range) -> builds memory
FETCH_BUDGET = 130       # steps to reach all K targets under FOV+range-limited sensing


def set_difficulty(room, rng_range, budget):
    global ROOM, MAX_RANGE, FETCH_BUDGET
    ROOM, MAX_RANGE, FETCH_BUDGET = room, rng_range, budget


def cam_basis(theta):
    f = np.array([math.cos(theta), math.sin(theta), 0.0])
    r = np.array([math.sin(theta), -math.cos(theta), 0.0])
    u = np.array([0.0, 0.0, 1.0])
    return r, u, f


def visible(P, T):
    p = to_cam(P, T)
    x, y, z = p
    if z <= MIN_DEPTH or z > MAX_RANGE:
        return False, p
    if abs(math.atan2(x, z)) > HALF_FOV:
        return False, p
    return True, p


def wrap(a):
    return (a + math.pi) % (2 * math.pi) - math.pi


def observe(pos, theta, obj_pos, rng):
    T = cam_pose_mat(np.array([pos[0], pos[1], 1.2]), theta)
    dets = []
    for oid in range(len(obj_pos)):
        vis, pc = visible(obj_pos[oid], T)
        if vis:
            dets.append(Detection(category=f"obj{oid}", pos_cam=pc + rng.normal(0, DET_NOISE, 3),
                                   confidence=1.0, obj_id=oid))
    return T, dets


def run_episode(rng, ArmClass):
    obj_pos = np.column_stack([rng.uniform(0.6, ROOM - 0.6, M_OBJ),
                               rng.uniform(0.6, ROOM - 0.6, M_OBJ),
                               rng.uniform(0.3, 1.6, M_OBJ)])
    targets = list(rng.permutation(M_OBJ)[:K_TARGETS])
    mem = ArmClass()

    # --- scan phase: 360-deg mapping pass over a grid of waypoints (builds memory) ---
    s = 0
    wps = np.linspace(1.5, ROOM - 1.5, SCAN_GRID)
    for wx in wps:
        for wy in wps:
            T = cam_pose_mat(np.array([wx, wy, 1.2]), 0.0)
            dets = []
            for oid in range(M_OBJ):                       # 360-deg map: all objects within range
                pc = to_cam(obj_pos[oid], T)
                if np.linalg.norm(obj_pos[oid][:2] - np.array([wx, wy])) <= MAX_RANGE:
                    dets.append(Detection(category=f"obj{oid}", pos_cam=pc + rng.normal(0, DET_NOISE, 3),
                                          confidence=1.0, obj_id=oid))
            mem.write(Observation(t=s, cam_pose=T, detections=dets)); s += 1

    # fetch starts from a random spot/heading
    pos = np.array([rng.uniform(2, ROOM - 2), rng.uniform(2, ROOM - 2)])
    theta = rng.uniform(-math.pi, math.pi)

    # --- fetch phase: reach each target in order ---
    ti = 0
    for step in range(FETCH_BUDGET):
        T, dets = observe(pos, theta, obj_pos, rng)
        mem.write(Observation(t=s + step, cam_pose=T, detections=dets))
        tgt = int(targets[ti])
        if np.linalg.norm(pos - obj_pos[tgt][:2]) <= REACH:    # reached current target (ground truth)
            ti += 1
            if ti == K_TARGETS:
                return K_TARGETS, step
            tgt = int(targets[ti])
        # decide heading from memory only
        recs = {r.obj_id: r for r in mem.query(QueryState(t=s + step, cam_pose=T,
                                                          visible=dets, goal_category=f"obj{tgt}"))}
        r = recs.get(tgt)
        if r is not None:
            est_world = to_world(r.pos_cam_now, T)             # egomem: correct; naive: stale/wrong
            desired = math.atan2(est_world[1] - pos[1], est_world[0] - pos[0])
            dtheta = np.clip(wrap(desired - theta), -MAX_TURN, MAX_TURN)
            theta = wrap(theta + dtheta)
            pos = pos + STEP_LEN * np.array([math.cos(theta), math.sin(theta)])
        else:
            theta = wrap(theta + MAX_TURN)                     # search: spin to re-acquire
            pos = pos + 0.15 * np.array([math.cos(theta), math.sin(theta)])
        pos = np.clip(pos, 0.3, ROOM - 0.3)
    return ti, FETCH_BUDGET


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, nargs="+", default=[0, 1, 2])
    ap.add_argument("--n", type=int, default=200)
    ap.add_argument("--room", type=float, default=ROOM)
    ap.add_argument("--range", type=float, default=MAX_RANGE)
    ap.add_argument("--budget", type=int, default=FETCH_BUDGET)
    args = ap.parse_args()
    set_difficulty(args.room, getattr(args, "range"), args.budget)
    print(f"=== EgoMem long-horizon fetch: TASK SUCCESS | K={K_TARGETS} targets, M={M_OBJ} objs, "
          f"room={ROOM} range={MAX_RANGE} budget={FETCH_BUDGET}, n={args.n}/seed ===")
    agg = {a: [] for a in ARMS}
    for seed in args.seeds:
        per = {a: dict(succ=0, reached=0) for a in ARMS}
        for i in range(args.n):
            for a, cls in ARMS.items():
                rng = np.random.default_rng(seed * 100000 + i)   # SAME world per arm (fair)
                nr, _ = run_episode(rng, cls)
                per[a]["succ"] += 1 if nr == K_TARGETS else 0
                per[a]["reached"] += nr
        line = []
        for a in ARMS:
            sr = per[a]["succ"] / args.n
            fr = per[a]["reached"] / (args.n * K_TARGETS)
            agg[a].append(sr)
            line.append(f"{a}: succ={sr:.3f} reached={fr:.3f}")
        print(f"seed {seed}: " + " | ".join(line))
    print("\n--- task success rate (mean over seeds) ---")
    nm = float(np.mean(agg["no-memory"])); na = float(np.mean(agg["naive"])); eg = float(np.mean(agg["egomem"]))
    print(f"  no-memory={nm:.3f}  naive={na:.3f}  egomem={eg:.3f}")
    print(f"  egomem - no-memory = {eg - nm:+.3f}  ({(eg-nm)*100:+.1f} points)")
    print(f"  H10 (egomem >= no-memory + 0.20 AND >= naive): "
          f"{'CONFIRMED' if (eg >= nm + 0.20 and eg >= na) else 'REJECTED'}")
    here = os.path.dirname(os.path.abspath(__file__))
    json.dump(dict(no_memory=nm, naive=na, egomem=eg, seeds=args.seeds, n=args.n,
                   K=K_TARGETS, budget=FETCH_BUDGET),
              open(os.path.join(here, "metrics.json"), "w"), indent=2)


if __name__ == "__main__":
    main()
