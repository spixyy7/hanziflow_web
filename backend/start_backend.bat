@echo off
echo HanziFlow Backend Setup
echo =======================

set VENV_PATH=C:\hanziflow_venv

REM Proveri da li venv vec postoji da ne bi gubio vreme
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo Creating virtual environment at %VENV_PATH%...
    python -m venv %VENV_PATH%
)

echo Activating environment...
call %VENV_PATH%\Scripts\activate.bat

echo Updating pip and installing dependencies...
python -m pip install --upgrade pip
pip install -r "%~dp0requirements.txt"

if errorlevel 1 (
    echo ERROR: Instalacija paketa nije uspela. Proveri requirements.txt.
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
"%VENV_PATH%\Scripts\uvicorn.exe" main:app --reload --port 8000

pause