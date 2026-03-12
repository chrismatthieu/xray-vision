"""
X-Ray Vision demo: RealSense D435i + YOLO/RT-DETR → 3D positions and wireframe overlay.
"""

from __future__ import annotations

import argparse
import sys
import time

import cv2
import numpy as np

from realsense_pipeline import (
    pipeline_config,
    start_pipeline,
    get_color_profile,
    create_align,
    get_frames,
    RESOLUTIONS,
)
from detection_to_3d import process_detections
from overlay import draw_overlay


def parse_args():
    p = argparse.ArgumentParser(description="X-Ray Vision: 2D detection + depth → 3D overlay")
    p.add_argument("--model", default="yolo11n.pt", help="Model: yolo11n.pt, rtdetr-l.pt, etc.")
    p.add_argument("--resolution", default="720p", choices=list(RESOLUTIONS.keys()), help="Color/depth resolution")
    p.add_argument("--imgsz", type=int, default=480, help="YOLO inference size (smaller = faster, default 480)")
    p.add_argument("--conf", type=float, default=0.5, help="Detection confidence threshold")
    p.add_argument("--no-wireframe", action="store_true", help="Disable 3D wireframe boxes")
    p.add_argument("--no-2d-boxes", action="store_true", help="Disable 2D bounding boxes")
    p.add_argument("--video", metavar="PATH", help="Use video file instead of RealSense (synthetic depth for testing)")
    return p.parse_args()


def _run_with_realsense(args, width, height, model):
    """Sync capture: one frame at a time (used for --video or when async disabled)."""
    import pyrealsense2 as rs
    pipe, cfg = pipeline_config(width, height)
    try:
        profile = start_pipeline(pipe, cfg)
    except RuntimeError as e:
        if "No device connected" in str(e) or "no device" in str(e).lower():
            print("RealSense: no camera detected.", file=sys.stderr)
            print("  - Plug in the Intel RealSense D435i (USB 3.0).", file=sys.stderr)
            print("  - Try another USB port or cable.", file=sys.stderr)
            print("  - Install Intel RealSense SDK 2.0 if needed.", file=sys.stderr)
            print("  - Or run with a video file: run_demo.py --video path/to/file.mp4", file=sys.stderr)
        raise
    color_profile = get_color_profile(profile)
    intrinsics = color_profile.get_intrinsics()
    align = create_align()

    try:
        while True:
            color, depth_m, intr = get_frames(pipe, align)
            if color is None or depth_m is None or intr is None:
                continue
            yield color, depth_m, intr
    finally:
        pipe.stop()


def _capture_thread(pipe, align, stop_event, latest_holder):
    """Background thread: keep fetching the latest frame so inference doesn't wait on capture."""
    while not stop_event.is_set():
        color, depth_m, intr = get_frames(pipe, align)
        if color is not None and depth_m is not None and intr is not None:
            latest_holder[:] = [(color.copy(), depth_m.copy(), intr)]


def _run_with_realsense_async(args, width, height, model):
    """Async capture: camera runs in a thread, yield latest frame so GPU and camera work in parallel."""
    import threading
    import pyrealsense2 as rs
    pipe, cfg = pipeline_config(width, height)
    try:
        profile = start_pipeline(pipe, cfg)
    except RuntimeError as e:
        if "No device connected" in str(e) or "no device" in str(e).lower():
            print("RealSense: no camera detected.", file=sys.stderr)
            print("  - Plug in the Intel RealSense D435i (USB 3.0).", file=sys.stderr)
            print("  - Try another USB port or cable.", file=sys.stderr)
            print("  - Install Intel RealSense SDK 2.0 if needed.", file=sys.stderr)
            print("  - Or run with a video file: run_demo.py --video path/to/file.mp4", file=sys.stderr)
        raise
    color_profile = get_color_profile(profile)
    intrinsics = color_profile.get_intrinsics()
    align = create_align()

    stop_event = threading.Event()
    latest_holder = []  # [ (color, depth_m, intr) ] or empty
    t = threading.Thread(target=_capture_thread, args=(pipe, align, stop_event, latest_holder), daemon=True)
    t.start()

    try:
        while True:
            if latest_holder:
                color, depth_m, intr = latest_holder[0]
                yield color, depth_m, intr
            else:
                import time
                time.sleep(0.001)
    finally:
        stop_event.set()
        pipe.stop()
        t.join(timeout=1.0)


def _run_with_video(args, video_path, model):
    """Use video file with synthetic depth (for testing without RealSense)."""
    import pyrealsense2 as rs
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Cannot open video: {video_path}", file=sys.stderr)
        sys.exit(1)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Synthetic intrinsics (pinhole, no distortion)
    intr = rs.intrinsics()
    intr.width = w
    intr.height = h
    intr.fx = w * 1.2
    intr.fy = w * 1.2
    intr.ppx = w / 2.0
    intr.ppy = h / 2.0
    intr.model = rs.distortion.none
    intr.coeffs = [0.0, 0.0, 0.0, 0.0, 0.0]
    try:
        while True:
            ok, color = cap.read()
            if not ok:
                cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                continue
            depth_m = 1.5 * np.ones((h, w), dtype=np.float32)  # constant 1.5 m
            yield color, depth_m, intr
    finally:
        cap.release()


def main():
    args = parse_args()

    try:
        import torch
        from ultralytics import YOLO
    except ImportError:
        print("Install ultralytics: pip install ultralytics", file=sys.stderr)
        sys.exit(1)

    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"Inference device: {device}")
    if device == "cuda":
        print(f"  GPU: {torch.cuda.get_device_name(0)}")

    width, height = RESOLUTIONS[args.resolution]
    model = YOLO(args.model)

    use_half = device == "cuda"  # FP16 on GPU for speed
    if use_half:
        print("FP16 inference: on")

    if args.video:
        print("Using video file (synthetic depth). Press Q to quit.")
        frame_iter = _run_with_video(args, args.video, model)
    else:
        print("Starting X-Ray Vision demo. Press Q to quit.")
        print("Resolution:", width, "x", height)
        frame_iter = _run_with_realsense_async(args, width, height, model)

    t0 = time.perf_counter()
    frame_times = []
    try:
        for color, depth_m, intr in frame_iter:
            t_start = time.perf_counter()
            results = model.predict(
                color,
                conf=args.conf,
                verbose=False,
                device=device,
                imgsz=args.imgsz,
                half=use_half,
            )
            detections_2d = []
            for r in results:
                if r.boxes is None:
                    continue
                for i in range(len(r.boxes)):
                    xyxy = r.boxes.xyxy[i].cpu().numpy()
                    conf = float(r.boxes.conf[i].cpu().numpy())
                    cls = int(r.boxes.cls[i].cpu().numpy())
                    name = r.names[cls]
                    detections_2d.append((name, conf, tuple(map(float, xyxy))))

            detections_3d = process_detections(depth_m, intr, detections_2d)

            draw_overlay(
                color,
                intr,
                detections_3d,
                draw_2d_boxes=not args.no_2d_boxes,
                draw_wireframe_3d=not args.no_wireframe,
            )

            elapsed = time.perf_counter() - t_start
            frame_times.append(elapsed)
            if len(frame_times) > 30:
                frame_times.pop(0)
            fps = 1.0 / (sum(frame_times) / len(frame_times)) if frame_times else 0
            cv2.putText(color, f"FPS: {fps:.1f}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow("X-Ray Vision", color)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
    finally:
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
