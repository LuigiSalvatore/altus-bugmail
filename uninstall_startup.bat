@echo off
:: uninstall_startup.bat — Remove Bugzilla Tracker from Windows startup.

set TASK_NAME=BugzillaTracker

echo.
echo  Bugzilla Tracker — Startup Uninstaller
echo  ========================================

schtasks /delete /tn "%TASK_NAME%" /f

if %errorlevel% equ 0 (
  echo  [OK] Task "%TASK_NAME%" removed. Bugzilla Tracker will no longer start on login.
) else (
  echo  [WARN] Task not found or already removed.
)

echo.
pause
