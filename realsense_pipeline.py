"""
RealSense D435i pipeline: color + depth, depth aligned to color, and color intrinsics for deprojection.
"""

from __future__ import annotations

import numpy as np
import pyrealsense2 as rs
from typing import Tuple, Optional


# Resolution presets (width, height)
RESOLUTIONS = {
    "720p": (1280, 720),
    "480p": (640, 480),
}


def get_color_intrinsics(profile: rs.video_stream_profile) -> rs.intrinsics:
    """Return intrinsics of the color stream (use these for deprojection after align)."""
    return profile.get_intrinsics()


def pipeline_config(
    width: int,
    height: int,
    fps: int = 30,
) -> Tuple[rs.pipeline, rs.config]:
    """Build pipeline and config for color + depth at given resolution and FPS."""
    cfg = rs.config()
    cfg.enable_stream(rs.stream.color, width, height, rs.format.bgr8, fps)
    cfg.enable_stream(rs.stream.depth, width, height, rs.format.z16, fps)
    pipe = rs.pipeline()
    return pipe, cfg


def start_pipeline(pipe: rs.pipeline, cfg: rs.config) -> rs.pipeline_profile:
    """Start the pipeline and return the active profile (for intrinsics)."""
    profile = pipe.start(cfg)
    return profile


def get_color_profile(profile: rs.pipeline_profile) -> rs.video_stream_profile:
    """Get color stream profile from pipeline profile."""
    return profile.get_stream(rs.stream.color).as_video_stream_profile()


def create_align(align_to: rs.stream = rs.stream.color) -> rs.align:
    """Create align filter: depth aligned to color."""
    return rs.align(align_to)


def get_frames(
    pipe: rs.pipeline,
    align: rs.align,
) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Optional[rs.intrinsics]]:
    """
    Wait for frames, align depth to color, return color image, aligned depth, and color intrinsics.
    Returns (color_bgr, aligned_depth_meters, color_intrinsics).
    aligned_depth_meters: float32 array, same size as color; invalid = 0 or NaN.
    """
    frames = pipe.wait_for_frames()
    aligned_frames = align.process(frames)

    color_frame = aligned_frames.get_color_frame()
    depth_frame = aligned_frames.get_depth_frame()
    if not color_frame or not depth_frame:
        return None, None, None

    color_profile = color_frame.get_profile().as_video_stream_profile()
    intrinsics = color_profile.get_intrinsics()

    color = np.asanyarray(color_frame.get_data())
    depth = np.asanyarray(depth_frame.get_data()).astype(np.float32)  # mm
    depth_m = depth / 1000.0  # meters; 0 stays 0

    return color, depth_m, intrinsics


def deproject_pixel_to_point(intrinsics: rs.intrinsics, pixel: Tuple[float, float], depth: float) -> Tuple[float, float, float]:
    """Deproject a single pixel and depth to 3D point in camera frame (meters)."""
    return rs.rs2_deproject_pixel_to_point(intrinsics, list(pixel), depth)
