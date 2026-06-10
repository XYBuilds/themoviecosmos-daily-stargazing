@echo off
setlocal
echo.
echo ============================================
echo  Cursor Workspace Record Restore
echo ============================================
echo.
echo Please make sure ALL Cursor windows are closed.
echo.
pause

python "%~dp0restore-cursor-workspace-records.py"
echo.
pause
