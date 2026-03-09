@echo off
:: ============================================================
::  Global News Intelligence  -  Background Daemon Launcher
::  Double-click this file to start the pipeline in the background.
::  No VS Code, no terminal window needed after this.
:: ============================================================

set SCRIPT=%~dp0RUN_COMPLETE_WORKFLOW.py

:: pythonw.exe = Python with no console window
for /f "delims=" %%i in ('python -c "import sys,os; print(os.path.join(os.path.dirname(sys.executable),'pythonw.exe'))"') do set PYTHONW=%%i

if not exist "%PYTHONW%" (
    echo pythonw.exe not found, falling back to python.exe
    set PYTHONW=python
)

echo Starting pipeline daemon in background...
start "" "%PYTHONW%" "%SCRIPT%" --daemon

echo.
echo  Pipeline is now running silently in the background.
echo  Progress is logged to:  %~dp0daemon.log
echo.
echo  To install as a scheduled Task (auto-start after reboot):
echo    python "%SCRIPT%" --install-task
echo.
echo  To check daemon status and recent log:
echo    python "%SCRIPT%" --status
echo.
pause
