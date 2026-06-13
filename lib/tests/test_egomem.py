"""Tests for the egomem library. Run: pytest lib/tests  (or python lib/tests/test_egomem.py)."""
import numpy as np

from egomem import (NoMemory, NaiveBuffer, EgoMem, EgoMemRobust, EgoMemVerify,
                    Observation, QueryState, Detection, RecalledObject,
                    cam_pose_mat, to_cam, to_world)


def _det(cat, pos_cam, oid):
    return Detection(category=cat, pos_cam=np.asarray(pos_cam, float), confidence=1.0, obj_id=oid)


# --- geometry ---------------------------------------------------------------
def test_to_world_to_cam_roundtrip():
    T = cam_pose_mat([1.0, -2.0, 1.2], theta=0.7)
    P = np.array([0.5, 0.3, 2.1])
    assert np.allclose(to_world(to_cam(P, T), T), P, atol=1e-9)


def test_cam_pose_orthonormal():
    T = cam_pose_mat([0, 0, 1.2], theta=1.1)
    R = T[:3, :3]
    assert np.allclose(R.T @ R, np.eye(3), atol=1e-9)


# --- shared recall scenario: cup 2 m ahead at theta=0, then turn 90 deg -----
def _write_cup(mem, oid=1, n=3):
    T0 = cam_pose_mat([0, 0, 1.2], 0.0)
    for _ in range(n):
        mem.write(Observation(t=0, cam_pose=T0, detections=[_det("cup", [0, 0, 2.0], oid)]))
    return T0


def _query_turned(mem, goal="cup"):
    T1 = cam_pose_mat([0, 0, 1.2], np.pi / 2)   # turned left; cup now out of view
    recs = mem.query(QueryState(t=10, cam_pose=T1, visible=[], goal_category=goal))
    assert all(isinstance(r, RecalledObject) for r in recs)
    return {r.obj_id: r for r in recs}


def test_egomem_recalls_out_of_view_in_current_frame():
    mem = EgoMem(); _write_cup(mem)
    recs = _query_turned(mem)
    assert 1 in recs and not recs[1].in_view_now
    # cup was 2 m ahead (world +x); after a 90 deg left turn it is 2 m to the right
    assert np.allclose(recs[1].pos_cam_now, [2, 0, 0], atol=1e-6)


def test_no_memory_recalls_nothing_out_of_view():
    mem = NoMemory(); _write_cup(mem)
    recs = _query_turned(mem)
    assert 1 not in recs            # no-memory returns only currently-visible


def test_naive_returns_stale_untransformed_position():
    mem = NaiveBuffer(); _write_cup(mem)
    recs = _query_turned(mem)
    # naive returns the last-seen camera-frame position WITHOUT a pose transform
    assert 1 in recs and np.allclose(recs[1].pos_cam_now, [0, 0, 2.0], atol=1e-6)


def test_query_returns_visible_as_in_view():
    mem = EgoMem(); T0 = _write_cup(mem)
    vis = [_det("cup", [0, 0, 2.0], 1)]
    recs = {r.obj_id: r for r in mem.query(QueryState(t=0, cam_pose=T0, visible=vis))}
    assert recs[1].in_view_now


# --- robustness variants ----------------------------------------------------
def test_robust_median_ignores_outlier_writes():
    mem = EgoMemRobust(); T0 = cam_pose_mat([0, 0, 1.2], 0.0)
    for _ in range(5):                                   # 5 correct + 2 outliers under same id
        mem.write(Observation(0, T0, [_det("cup", [0, 0, 2.0], 1)]))
    mem.write(Observation(0, T0, [_det("cup", [3, 1, 5.0], 1)]))
    mem.write(Observation(0, T0, [_det("cup", [-2, 2, 4.0], 1)]))
    recs = _query_turned(mem)
    assert np.allclose(recs[1].pos_cam_now, [2, 0, 0], atol=0.3)   # median ~ the true value


def test_verify_recovers_from_id_swap():
    mem = EgoMemVerify(); T0 = cam_pose_mat([0, 0, 1.2], 0.0)
    for _ in range(5):                                   # cup correctly id'd
        mem.write(Observation(0, T0, [_det("cup", [0, 0, 2.0], 1)]))
    mem.write(Observation(0, T0, [_det("cup", [0, 0, 2.0], 2)]))   # swap: cup pos under id 2
    for _ in range(4):                                   # a real plate far away, id 2
        mem.write(Observation(0, T0, [_det("plate", [3, 0, 1.0], 2)]))
    recs = _query_turned(mem, goal=None)
    # cup track stays clean despite the swap; plate not corrupted by cup's position
    assert np.allclose(recs[1].pos_cam_now, [2, 0, 0], atol=0.4)
    assert 2 in recs and not np.allclose(recs[2].pos_cam_now, [2, 0, 0], atol=0.4)


def test_verify_clean_matches_egomem():
    a = EgoMem(); b = EgoMemVerify()
    _write_cup(a); _write_cup(b)
    ra = _query_turned(a)[1].pos_cam_now
    rb = _query_turned(b)[1].pos_cam_now
    assert np.allclose(ra, rb, atol=1e-6)               # no clean-data regression


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn(); print("ok:", fn.__name__)
    print(f"\nall {len(fns)} tests passed")
