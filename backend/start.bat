@ECHO OFF
cd /d "%~dp0"
SET CUDA_BIN_PATH=C:\Program Files\NVIDIA GPU Computing Toolkit\CUDA\v11.1\bin
SET PATH=.\runtime\python;%CUDA_BIN_PATH%;%PATH%
python %~dp0server.py
pause