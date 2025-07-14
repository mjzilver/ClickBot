@echo off
IF NOT EXIST venv (
    python -m venv venv
)

call venv\Scripts\activate.bat

pip install -r requirements.txt

if not exist captures (
    mkdir captures
)

python gui.py

pause >nul
