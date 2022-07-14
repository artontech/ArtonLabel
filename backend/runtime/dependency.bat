@ECHO OFF
SET DEVICE_VERSION=rtx3080ti
SET BASE_REPO_PATH=.\Lib\site-packages
SET EXTRA_REPO_PATH=.\site-packages-%DEVICE_VERSION%
SET MIRROR=-i https://pypi.tuna.tsinghua.edu.cn/simple/

cd %~dp0python
python -m pip install -t %BASE_REPO_PATH% --upgrade pip wheel
python -m pip install -t %BASE_REPO_PATH% --upgrade -r %~dp0requirements.txt %MIRROR%
python -m pip install -t %EXTRA_REPO_PATH% --upgrade -r %~dp0requirements-%DEVICE_VERSION%.txt %MIRROR%
pause