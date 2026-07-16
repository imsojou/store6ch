@echo off
chcp 65001 >nul
cd /d "%~dp0"
python build.py
if errorlevel 1 (
  echo.
  echo [안내] python 명령이 없으면 py build.py 로 다시 시도합니다...
  py build.py
)
