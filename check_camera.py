"""
Quick check that the RealSense camera is visible to pyrealsense2.
Run: python check_camera.py
If no device is found, close RealSense Viewer, reconnect the camera, and ensure the SDK is installed.
"""

import sys

try:
    import pyrealsense2 as rs
except ImportError:
    print("pyrealsense2 not installed. Run: pip install pyrealsense2")
    sys.exit(1)

ctx = rs.context()
devices = ctx.query_devices()
n = devices.size()

if n == 0:
    print("No RealSense device found.")
    print("  - Plug in the camera (USB 3.0) and close RealSense Viewer if it is open.")
    print("  - Install Intel RealSense SDK 2.0 from:")
    print("    https://github.com/realsenseai/librealsense/releases")
    sys.exit(1)

print(f"Found {n} RealSense device(s):")
for i in range(n):
    d = devices[i]
    name = d.get_info(rs.camera_info.name)
    serial = d.get_info(rs.camera_info.serial_number)
    print(f"  - {name}  (SN: {serial})")
print("Camera is ready for the demo. Run: python run_demo.py")
