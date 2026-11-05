@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"

set PYTHON="C:\Users\sanch\miniforge3\envs\expclaim\python.exe"

echo ============================
echo ExpClaim Demo Runner
echo ============================
echo.
echo Python: %PYTHON%
%PYTHON% --version

echo.
echo Running tests...
%PYTHON% -m pytest -q tests
if errorlevel 1 (
    echo.
    echo Tests failed. See output above.
    exit /b 1
)

echo.
echo Running sample ASP inference...
%PYTHON% scripts/test.py --relation spouse --num_claims 2 --bing_evidence 0 --inference_mode ASP
if errorlevel 1 (
    echo.
    echo Sample inference failed.
    exit /b 1
)

echo.
echo Result files:
for /r Results %%F in (*ASP*_results.csv *ASP*_stats.txt) do (
    echo %%~fF
)

echo.
echo Demo completed successfully.
