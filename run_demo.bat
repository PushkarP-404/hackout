@echo off
title BharatBanker AI — Unified Platform Demo Launcher
echo ======================================================================
echo           BHARATBANKER AI: UNIFIED DECISIONING PLATFORM
echo ======================================================================
echo Starting FastAPI Gateway and Streamlit Interactive Dashboard...
echo.

start "BharatBanker FastAPI Gateway (Port 8000)" cmd /k "python -m uvicorn main_api:app --host 127.0.0.1 --port 8000 --reload"
timeout /t 3 /nobreak >nul

start "BharatBanker Interactive UI (Streamlit)" cmd /k "streamlit run app.py"

echo.
echo ======================================================================
echo Services Launched:
echo   - Backend API Docs : http://127.0.0.1:8000/docs
echo   - Interactive UI   : http://localhost:8501
echo ======================================================================
pause
