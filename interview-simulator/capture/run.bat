@echo off
cd /d %~dp0
python --version >nul 2>&1 || (echo Python not found. Install Python 3.10+ from python.org and tick "Add to PATH". & pause & exit /b)
if not exist .venv (python -m venv .venv)
call .venv\Scripts\activate
pip install -q -r requirements.txt
set /p CODE=Enter practice session code: 
python main.py --code %CODE%
pause
