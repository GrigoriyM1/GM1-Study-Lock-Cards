@echo off
cd /d "%~dp0"

REM Using pythonw.exe to launch without showing console
start "" /B pythonw.exe study_lock.py --autostart

REM 
exit