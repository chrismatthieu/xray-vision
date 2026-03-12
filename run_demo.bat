@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" python -m venv .venv
REM Only install CPU PyTorch if CUDA is not available (so install_gpu.bat is not overwritten)
.venv\Scripts\python.exe -c "import torch; exit(0 if torch.cuda.is_available() else 1)" 2>nul
if errorlevel 1 (
  .venv\Scripts\python.exe -m pip install -q torch==2.5.1+cpu torchvision==0.20.1+cpu --index-url https://download.pytorch.org/whl/cpu
)
.venv\Scripts\python.exe -m pip install -q -r requirements.txt
.venv\Scripts\python.exe run_demo.py %*
