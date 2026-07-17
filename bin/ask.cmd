@echo off
setlocal

where py.exe >nul 2>nul
if not errorlevel 1 (
    py -3 "%~dp0ask" %*
    exit /b %errorlevel%
)

where python.exe >nul 2>nul
if not errorlevel 1 (
    python "%~dp0ask" %*
    exit /b %errorlevel%
)

>&2 echo ask: Python 3 is not installed or is not in PATH
exit /b 1
