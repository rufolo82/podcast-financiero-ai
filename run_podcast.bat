@echo off
chcp 65001 >nul
cd /d "%~dp0"
"C:\Users\rlm_1\AppData\Local\Python\pythoncore-3.14-64\python.exe" -u "%~dp0main.py" --run >> "%~dp0podcast_execution.log" 2>&1
