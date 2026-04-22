@echo off
setlocal
cd /d "%~dp0"
set "PYTHONPATH=%cd%\src"
echo Bleepling Debug-Start
echo Arbeitsordner: %cd%
echo PYTHONPATH: %PYTHONPATH%
echo.
python --version
echo.
python -m bleepling.app
if errorlevel 1 (
    echo.
    echo Start fehlgeschlagen.
    pause
)
echo.
echo Bleepling wurde beendet.
pause
endlocal
