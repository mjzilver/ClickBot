@echo off
echo Check if venv folder exists
IF NOT EXIST venv (
    echo Creating virtual environment...
    python -m venv venv
) 

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies from requirements.txt...
pip install -r requirements.txt

echo Setup complete.
pause
