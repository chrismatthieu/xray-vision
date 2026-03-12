# Windows setup: install Python and run the demo

## 1. Install Python (if needed)

If `python` or `py` is not recognized:

- **Option A – python.org (recommended)**  
  - Go to [python.org/downloads](https://www.python.org/downloads/).  
  - Download **Python 3.10 or 3.11** (64-bit) for Windows.  
  - Run the installer and **check "Add python.exe to PATH"** at the bottom.  
  - Finish the installer, then **close and reopen PowerShell**.

- **Option B – Microsoft Store**  
  - Open Microsoft Store, search for **Python 3.11** (or 3.10), install.  
  - Close and reopen PowerShell.

## 2. Run the demo (after Python is on PATH)

In PowerShell, from the project folder:

```powershell
cd c:\Users\demo\Projects\realsense
.\setup_and_run.ps1
```

Or do it step by step:

```powershell
cd c:\Users\demo\Projects\realsense
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python run_demo.py
```

If you use the **py** launcher instead of **python**:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
py run_demo.py
```

**Note:** If you see "cannot be loaded because running scripts is disabled", run once (as Administrator):  
`Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

## 3. Optional: GPU (CUDA) for faster detection

After the venv is created and activated:

```powershell
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

Then run the demo again.
