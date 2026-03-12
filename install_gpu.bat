@echo off
REM Install PyTorch with CUDA 12.1 for GPU inference (Ada and other NVIDIA GPUs).
REM Run this once, then use run_demo.bat as usual. Demo will auto-detect and use GPU.
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo Create the venv first: run run_demo.bat once, or: python -m venv .venv
    exit /b 1
)
echo Installing PyTorch with CUDA 12.1...
.venv\Scripts\python.exe -m pip uninstall -y torch torchvision 2>nul
.venv\Scripts\python.exe -m pip install torch==2.5.1+cu121 torchvision==0.20.1+cu121 --index-url https://download.pytorch.org/whl/cu121
echo.
.venv\Scripts\python.exe -c "import torch; print('CUDA available:', torch.cuda.is_available()); print('Device:', torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A')"
echo Done. Run run_demo.bat to start the demo on GPU.
