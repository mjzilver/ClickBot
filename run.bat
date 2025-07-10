@echo off
REM Check if venv folder exists
if not exist "venv\Scripts\activate.bat" (
    echo Virtual environment not found. Running setup.bat...
    call setup.bat
    if errorlevel 1 (
        echo Setup failed. Exiting.
        pause
        exit /b 1
    )
)

call venv\Scripts\activate.bat

echo Starting bot GUI...
python gui.py

echo Bot exited. Press any key to close.
pause >nul
