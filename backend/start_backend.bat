@echo off
echo HanziFlow Backend Setup
echo =======================

REM Create venv outside OneDrive to avoid sync issues
set VENV_PATH=C:\hanziflow_venv

echo Creating virtual environment at %VENV_PATH%...
python -m venv %VENV_PATH%

if errorlevel 1 (
    echo ERROR: Failed to create venv. Make sure Python is installed.
    echo Download Python: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Activating...
call %VENV_PATH%\Scripts\activate.bat

echo Installing dependencies...
pip install -r "%~dp0requirements.txt"

if errorlevel 1 (
    echo ERROR: pip install failed
    pause
    exit /b 1
)

echo.
echo ============================================
echo  Setup complete!
echo  Starting HanziFlow backend server...
echo  API: http://localhost:8000
echo  Docs: http://localhost:8000/docs
echo ============================================
echo.

cd /d "%~dp0"
%VENV_PATH%\Scripts\uvicorn.exe main:app --reload --port 8000

pause
