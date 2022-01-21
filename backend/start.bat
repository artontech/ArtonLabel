@ECHO OFF
cd /d "%~dp0"
SET PATH=.\runtime\python;%PATH%
python %~dp0server.py
pause