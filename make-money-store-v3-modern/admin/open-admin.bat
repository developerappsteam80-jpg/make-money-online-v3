@echo off
title Make Money Online - Admin Panel
cd /d "%~dp0\.."

if not exist ".venv\Scripts\python.exe" (
  echo Creating Python environment...
  python -m venv .venv
  if errorlevel 1 (
    echo Python could not create the environment.
    pause
    exit /b 1
  )
)

echo Installing required packages...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

if not exist ".env" (
  copy ".env.example" ".env" >nul
  echo Created .env. Add Razorpay credentials later.
)

echo Opening ADMIN panel...
start "" "http://127.0.0.1:8000/admin"
".venv\Scripts\python.exe" -m uvicorn backend.main:app --host 127.0.0.1 --port 8000
pause
