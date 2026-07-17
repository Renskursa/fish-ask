@echo off
setlocal
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0install.ps1"
set "ask_status=%errorlevel%"
endlocal & exit /b %ask_status%
