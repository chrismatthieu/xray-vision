@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" python -m venv .venv
REM Install PyTorch CPU first on Windows to avoid c10.dll WinError 1114
.venv\Scripts\python.exe -m pip install -q torch==2.5.1+cpu torchvision==0.20.1+cpu --index-url https://download.pytorch.org/whl/cpu
.venv\Scripts\python.exe -m pip install -q -r requirements.txt
.venv\Scripts\python.exe run_demo.py %*
