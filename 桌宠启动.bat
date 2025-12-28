@echo off
chcp 65001 > nul
:: ************************ 关键配置 ************************
:: 改为 pythonw.exe（无控制台解释器，与 python.exe 同目录）
set PYTHON_PATH=./env/Scripts/pythonw.exe
set MAIN_PY_PATH=./main.py
set PROJECT_ROOT=./
:: **********************************************************

cd /d "%PROJECT_ROOT%"
start /b /min "" "%PYTHON_PATH%" "%MAIN_PY_PATH%"
exit