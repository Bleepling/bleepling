@echo off
cd /d "%~dp0"
set "PYTHONPATH=%cd%\src"
start "" /b pythonw -m bleepling.app
exit
