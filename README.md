# X-Ray Vision Object Detection Demo

2D AI object detection (YOLO / RT-DETR) combined with Intel RealSense D435i depth to compute **true 3D positions** and **3D bounding boxes** with an on-screen overlay.

**Hardware:** InnoDisk Apex-P200 (Intel i7, Nvidia Ada GPUs) + Intel RealSense D435i.

## What it does

- Runs a neural detector on the color stream (GPU).
- Aligns depth to color and deprojects each 2D detection into 3D.
- Shows per-object: **label**, **distance (m)**, **X, Y, Z** (RealSense color frame: X right, Y down, Z forward).
- Draws **wireframe 3D bounding boxes** on the color image (cyan, X-ray style).

## Setup

1. **Python 3.10+** and a virtual environment:

   ```bash
   python -m venv .venv
   .venv\Scripts\activate   # Windows
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

   For GPU inference, install PyTorch with CUDA, e.g.:

   ```bash
   pip install torch --index-url https://download.pytorch.org/whl/cu121
   ```

3. **RealSense D435i + SDK**
   - **librealsense2 (SDK):** If the camera works in **RealSense Viewer**, the SDK/driver is already installed. Otherwise, install the [Windows precompiled SDK](https://github.com/realsenseai/librealsense/releases) (download the latest release installer) and follow the [Windows setup guide](https://dev.realsenseai.com/docs/compiling-librealsense-for-windows-guide).
   - **pyrealsense2 (Python):** Already listed in `requirements.txt`. Install with:
     ```bash
     pip install pyrealsense2
     ```
     Stable releases: [PyPI pyrealsense2](https://pypi.org/project/pyrealsense2/). Beta: `pip install pyrealsense2-beta`.  
   - Close **RealSense Viewer** (or any app using the camera) before running the demo. Run `python check_camera.py` to confirm the device is detected.

## Run

```bash
python run_demo.py
```

Options:

- `--model yolo11n` or `--model rtdetr-l` – detector model (default: yolo11n).
- `--resolution 720p` or `480p` – color/depth resolution (default: 1280x720).
- `--conf 0.5` – detection confidence threshold.
- `--no-wireframe` – disable 3D wireframe boxes, show only labels and distance/X,Y,Z.
- `--video path/to/file.mp4` – run from a video file instead of the camera (synthetic depth; useful when no RealSense is connected).

## Output

Live window: color feed with 2D boxes (optional), **wireframe 3D boxes**, and per-object overlay:

- **Bottle**  
- Distance: 1.27 m  
- X: -0.21  Y: 0.42  Z: 1.27  

Press **Q** to quit.
