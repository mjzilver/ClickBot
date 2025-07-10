@echo off
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo Failed to create virtual environment. Exiting.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment. Exiting.
    pause
    exit /b 1
)

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt
if errorlevel 1 (
    echo Failed to install dependencies. Exiting.
    pause
    exit /b 1
)

echo Starting bot GUI...
python gui.py

echo Bot exited. Press any key to close.
pause >nul
