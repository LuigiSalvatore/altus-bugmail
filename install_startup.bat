@echo off
:: install_startup.bat

setlocal

set TASK_NAME=BugzillaTracker
set SCRIPT_DIR=%~dp0
set VBS_FULL=%SCRIPT_DIR%launch.vbs

echo.
echo Bugzilla Tracker - Startup Installer
echo ===================================
echo Task name : %TASK_NAME%
echo Launcher  : %VBS_FULL%
echo.

:: Delete existing task
schtasks /delete /tn "%TASK_NAME%" /f >nul 2>&1

:: Create task for current user
schtasks /create ^
 /tn "%TASK_NAME%" ^
 /tr "wscript.exe \"%VBS_FULL%\"" ^
 /sc onlogon ^
 /f

if %errorlevel% equ 0 (
    echo.
    echo [OK] Startup task installed.
) else (
    echo.
    echo [ERROR] Could not create task.
)

pause