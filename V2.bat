@echo off
setlocal

REM Change to the directory of this BAT
cd /d "%~dp0"

REM Optional: activate venv if it exists
if exist ".venv\Scripts\activate.bat" (
    call ".venv\Scripts\activate.bat"
)

REM Try common Python launchers
where python >nul 2>&1
if %errorlevel%==0 (
    python YTDByAzharV2.py
    goto :end
)

where py >nul 2>&1
if %errorlevel%==0 (
    py YTDByAzharV2.py
    goto :end
)

echo Could not find Python on PATH. Please install Python or run in a venv.
pause

:end
endlocal
