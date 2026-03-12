"""
Draw 2D overlay: labels, distance, X/Y/Z, and wireframe 3D boxes on the color image.
"""

from __future__ import annotations

import cv2
import numpy as np
import pyrealsense2 as rs
from typing import List, Optional

from detection_to_3d import Detection3D, OBB_EDGES, project_point_to_pixel


# Cyan wireframe (BGR)
WIREFRAME_COLOR = (255, 255, 0)
WIREFRAME_THICKNESS = 2

# Text
TEXT_COLOR = (255, 255, 255)
TEXT_OUTLINE = (0, 0, 0)
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.55
FONT_THICKNESS = 2
OUTLINE_THICKNESS = 3


def _draw_text_outlined(
    img: np.ndarray,
    text: str,
    org: tuple,
    color: tuple = TEXT_COLOR,
    outline: tuple = TEXT_OUTLINE,
) -> None:
    cv2.putText(img, text, org, FONT, FONT_SCALE, outline, OUTLINE_THICKNESS, cv2.LINE_AA)
    cv2.putText(img, text, org, FONT, FONT_SCALE, color, FONT_THICKNESS, cv2.LINE_AA)


def draw_overlay(
    img: np.ndarray,
    intrinsics: rs.intrinsics,
    detections: List[Detection3D],
    draw_2d_boxes: bool = True,
    draw_wireframe_3d: bool = True,
) -> np.ndarray:
    """
    Draw on `img` (BGR): 2D boxes (optional), wireframe 3D boxes (optional), and per-object
    label, Distance, X, Y, Z. Modifies img in place and returns it.
    """
    h, w = img.shape[:2]

    for i, d in enumerate(detections):
        x1, y1, x2, y2 = (int(round(x)) for x in d.bbox_xyxy)

        if draw_2d_boxes:
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        if draw_wireframe_3d and d.obb_corners_3d is not None:
            corners_2d = []
            for j in range(8):
                pt = d.obb_corners_3d[j]
                u, v = project_point_to_pixel(intrinsics, (float(pt[0]), float(pt[1]), float(pt[2])))
                corners_2d.append((int(round(u)), int(round(v))))
            for (a, b) in OBB_EDGES:
                pt1 = corners_2d[a]
                pt2 = corners_2d[b]
                ok, p1, p2 = cv2.clipLine((0, 0, w, h), pt1, pt2)
                if ok:
                    cv2.line(img, p1, p2, WIREFRAME_COLOR, WIREFRAME_THICKNESS)

        # Label and 3D info above the 2D box (or at top of frame if box is high)
        block = [
            f"{d.label}",
            f"Distance: {d.distance:.2f} m",
            f"X: {d.centroid_xyz[0]:.2f}  Y: {d.centroid_xyz[1]:.2f}  Z: {d.centroid_xyz[2]:.2f}",
        ]
        line_h = int(22 * FONT_SCALE) or 22
        start_y = max(y1 - len(block) * line_h - 4, line_h)
        for k, line in enumerate(block):
            org = (x1, start_y + k * line_h)
            _draw_text_outlined(img, line, org)

    return img
