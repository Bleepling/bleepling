@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%cd%\src"
python -m bleepling.app
if errorlevel 1 (
    echo.
    echo Start fehlgeschlagen.
    pause
)
endlocal
