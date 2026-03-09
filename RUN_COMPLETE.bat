@echo off
REM Run complete_pipeline.py using the virtual environment

echo ============================================================================
echo    COMPLETE ALL-IN-ONE PIPELINE (Using Virtual Environment)
echo ============================================================================
echo.

REM Activate virtual environment and run
call ".venv\Scripts\activate.bat"
python complete_pipeline.py

echo.
pause
