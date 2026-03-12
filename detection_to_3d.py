"""
2D bounding box + aligned depth + color intrinsics → 3D centroid, distance, and OBB corners for wireframe.
"""

from __future__ import annotations

import numpy as np
import pyrealsense2 as rs
import open3d as o3d
from dataclasses import dataclass
from typing import List, Tuple, Optional, Any


@dataclass
class Detection3D:
    """One detection with 2D bbox, label, and 3D info."""
    label: str
    confidence: float
    bbox_xyxy: Tuple[float, float, float, float]  # x1, y1, x2, y2
    centroid_xyz: Tuple[float, float, float]      # meters, color frame
    distance: float                               # meters (Z or median depth)
    obb_corners_3d: Optional[np.ndarray]          # (8, 3) in meters; None if too few points


def _deproject_roi(
    depth: np.ndarray,
    intrinsics: rs.intrinsics,
    x1: int, y1: int, x2: int, y2: int,
    min_depth: float = 0.2,
    max_depth: float = 10.0,
) -> np.ndarray:
    """Return (N, 3) array of 3D points in meters for valid pixels in the ROI."""
    h, w = depth.shape
    x1, x2 = max(0, int(x1)), min(w, int(x2))
    y1, y2 = max(0, int(y1)), min(h, int(y2))
    roi = depth[y1:y2, x1:x2]
    valid = (roi > min_depth) & (roi < max_depth) & np.isfinite(roi)
    ys, xs = np.where(valid)
    if ys.size == 0:
        return np.zeros((0, 3))

    depths = roi[ys, xs]
    xs_abs = xs + x1
    ys_abs = ys + y1
    points = []
    for i in range(len(xs_abs)):
        pt = rs.rs2_deproject_pixel_to_point(intrinsics, [float(xs_abs[i]), float(ys_abs[i])], float(depths[i]))
        points.append(pt)
    return np.array(points, dtype=np.float64)


# Wireframe edges: 12 pairs of corner indices (same order as _obb_corners_from_points).
OBB_EDGES = [
    (0, 1), (1, 2), (2, 3), (3, 0),  # bottom
    (4, 5), (5, 6), (6, 7), (7, 4),  # top
    (0, 4), (1, 5), (2, 6), (3, 7),  # vertical
]


def _obb_corners_from_points(points: np.ndarray) -> Optional[np.ndarray]:
    """(N, 3) → 8 corners of OBB in (8, 3), fixed order for wireframe. Returns None if too few points."""
    if points.shape[0] < 4:
        return None
    pcd = o3d.geometry.PointCloud()
    pcd.points = o3d.utility.Vector3dVector(points)
    try:
        obb = o3d.geometry.OrientedBoundingBox.create_from_points(pcd.points)
        center = np.asarray(obb.center)
        R = np.asarray(obb.R)
        e = np.asarray(obb.extent)
        # Local corners: (±e0/2, ±e1/2, ±e2/2) in fixed order for consistent wireframe.
        signs = np.array([
            [-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
            [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1],
        ])
        local = signs * (e / 2)
        corners = (R @ local.T).T + center  # (8, 3)
        return corners
    except Exception:
        return None


# Depth band (meters) around object: only points within this range of median Z are used for the 3D box.
# Keeps the OBB tight to the object and avoids including background (wall) points in the bbox.
DEPTH_BAND_FOR_OBB = 0.35


def process_detections(
    depth_aligned: np.ndarray,
    intrinsics: rs.intrinsics,
    detections_2d: List[Tuple[str, float, Tuple[float, float, float, float]]],  # (label, conf, xyxy)
) -> List[Detection3D]:
    """
    For each 2D detection (label, confidence, x1,y1,x2,y2), compute 3D centroid, distance, and OBB corners.
    OBB is fit only to points within a depth band of the object so the box doesn't stretch to the background.
    """
    out: List[Detection3D] = []
    for label, conf, (x1, y1, x2, y2) in detections_2d:
        points_3d = _deproject_roi(depth_aligned, intrinsics, x1, y1, x2, y2)
        if points_3d.shape[0] == 0:
            centroid = (0.0, 0.0, 0.0)
            distance = 0.0
            obb_corners = None
        else:
            centroid = tuple(np.median(points_3d, axis=0).tolist())
            distance = float(centroid[2])  # Z forward
            # Use only points near the object's depth so the 3D box doesn't include the background
            z_median = centroid[2]
            in_band = np.abs(points_3d[:, 2] - z_median) <= DEPTH_BAND_FOR_OBB
            points_for_obb = points_3d[in_band]
            obb_corners = _obb_corners_from_points(points_for_obb) if points_for_obb.shape[0] >= 4 else None

        out.append(Detection3D(
            label=label,
            confidence=conf,
            bbox_xyxy=(x1, y1, x2, y2),
            centroid_xyz=centroid,
            distance=distance,
            obb_corners_3d=obb_corners,
        ))
    return out


def project_point_to_pixel(intrinsics: rs.intrinsics, point_3d: Tuple[float, float, float]) -> Tuple[float, float]:
    """Project a 3D point (meters) to 2D pixel (u, v)."""
    [u, v] = rs.rs2_project_point_to_pixel(intrinsics, list(point_3d))
    return (u, v)
