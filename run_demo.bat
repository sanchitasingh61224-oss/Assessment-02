@echo off
setlocal
cd /d "%~dp0"

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0run_demo.ps1"
exit /b %ERRORLEVEL%
