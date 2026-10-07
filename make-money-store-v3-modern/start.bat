@echo off
title Make Money Online Store
cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
  echo.
  echo Creating Python environment...
  python -m venv .venv
  if errorlevel 1 (
    echo Could not create the virtual environment.
    echo Make sure Python is installed and added to PATH.
    pause
    exit /b 1
  )
)

echo.
echo Installing/updating required packages...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo.
  echo Created .env from .env.example.
  echo Add your Razorpay TEST keys before testing payments.
)

echo.
echo Starting Make Money Online Store...
start "" "http://127.0.0.1:8000"
".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
