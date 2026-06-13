"""EgoMem — a model-agnostic memory layer for robotics from egocentric video.

Public API:
    from egomem import EgoMem, NoMemory, NaiveBuffer
    from egomem import Observation, QueryState, Detection, RecalledObject
"""
from .memory import (
    Detection, Observation, QueryState, RecalledObject,
    NoMemory, NaiveBuffer, EgoMem, EgoMemRobust, EgoMemVerify, MEMORIES,
    cam_pose_mat, to_cam, to_world,
)

__version__ = "0.3.0"

__all__ = [
    "Detection", "Observation", "QueryState", "RecalledObject",
    "NoMemory", "NaiveBuffer", "EgoMem", "EgoMemRobust", "EgoMemVerify", "MEMORIES",
    "cam_pose_mat", "to_cam", "to_world", "__version__",
]
