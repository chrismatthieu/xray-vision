# RealSense: librealsense2 + pyrealsense2

Your camera works in **RealSense Viewer**, so the SDK/driver is likely already installed. This page summarizes how everything fits together and how to fix "No device connected."

## 1. librealsense2 (SDK and driver)

- **What it is:** The native library and USB driver for RealSense cameras ([realsenseai/librealsense](https://github.com/realsenseai/librealsense)).
- **If RealSense Viewer runs:** You already have a working SDK install (e.g. from the Windows installer). No need to reinstall unless you have issues.
- **If you need to install or reinstall:**
  1. Download the **Windows** installer from [Releases](https://github.com/realsenseai/librealsense/releases) (e.g. "Intel.RealSense.SDK-WIN10-x.x.x.exe" or similar).
  2. Run the installer and complete the steps (including USB driver setup if prompted).
  3. Reboot if asked, then plug in the D435i and open RealSense Viewer to confirm it works.

## 2. pyrealsense2 (Python bindings)

- **What it is:** Python wrapper for librealsense2. Your project already lists it in `requirements.txt`.
- **Install in this project:**
  ```powershell
  cd c:\Users\demo\Projects\realsense
  .venv\Scripts\pip install pyrealsense2
  ```
  Or install everything:  
  `.\run_demo.bat` (which runs `pip install -r requirements.txt`) already installs pyrealsense2.

- **Stable vs beta:**  
  - Stable: `pip install pyrealsense2` (recommended).  
  - Beta: `pip install pyrealsense2-beta` (newer builds; install only one of the two).

## 3. Check that the camera is detected

1. **Close RealSense Viewer** (so it doesn’t hold the camera).
2. Plug in the D435i (USB 3.0).
3. Run:
   ```powershell
   .venv\Scripts\python.exe check_camera.py
   ```
   You should see something like: `Found 1 RealSense device(s): ... D435i ...`

4. If you see **"No RealSense device found"**:
   - Close any other app using the camera (Viewer, other demos).
   - Try another USB 3.0 port or cable.
   - Reinstall the [Windows SDK](https://github.com/realsenseai/librealsense/releases) and reboot if needed.

## 4. Run the X-Ray Vision demo

```powershell
.\run_demo.bat
```

Or:

```powershell
.venv\Scripts\python.exe run_demo.py
```

If the camera is detected by `check_camera.py` but the demo still says "No device connected," run the demo again with the camera plugged in and Viewer closed.
