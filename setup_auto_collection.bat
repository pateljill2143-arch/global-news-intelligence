@echo off
REM Setup Windows Task Scheduler for Automatic News Collection
REM This will run the pipeline every 2 hours automatically

echo ============================================================================
echo SETTING UP AUTOMATIC NEWS COLLECTION
echo ============================================================================
echo.

REM Get Python path
for /f "tokens=*" %%i in ('where python') do set PYTHON_PATH=%%i
echo Python found at: %PYTHON_PATH%
echo.

REM Get script path
set SCRIPT_PATH=%~dp0run_pipeline.py

echo Creating scheduled task...
echo Task Name: NewsIntelligence_Pipeline
echo Schedule: Every 2 hours
echo Script: %SCRIPT_PATH%
echo.

REM Delete existing task if it exists
schtasks /query /tn "NewsIntelligence_Pipeline" >nul 2>&1
if %errorlevel% equ 0 (
    echo Removing existing task...
    schtasks /delete /tn "NewsIntelligence_Pipeline" /f
)

REM Create new scheduled task (runs every 2 hours)
schtasks /create /tn "NewsIntelligence_Pipeline" /tr "\"%PYTHON_PATH%\" \"%SCRIPT_PATH%\"" /sc hourly /mo 2 /ru "%USERNAME%" /f

if %errorlevel% equ 0 (
    echo.
    echo ============================================================================
    echo SUCCESS! Automatic collection is now scheduled
    echo ============================================================================
    echo.
    echo Task Details:
    echo   Name: NewsIntelligence_Pipeline
    echo   Schedule: Every 2 hours
    echo   Next Run: Check Task Scheduler
    echo.
    echo To view/manage the task:
    echo   1. Press Win + R
    echo   2. Type: taskschd.msc
    echo   3. Find "NewsIntelligence_Pipeline"
    echo.
    echo To disable: schtasks /change /tn "NewsIntelligence_Pipeline" /disable
    echo To delete: schtasks /delete /tn "NewsIntelligence_Pipeline" /f
    echo.
) else (
    echo.
    echo ERROR: Failed to create scheduled task
    echo Please run this script as Administrator
    echo.
)

pause
