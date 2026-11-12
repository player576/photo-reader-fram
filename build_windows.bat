@echo off
chcp 65001 >nul
title Fram - Windows build
py -m pip install --upgrade pip
py -m pip install -r requirements.txt pyinstaller
pyinstaller --noconfirm --clean --windowed --name Fram --collect-all PySide6 main.py
echo Built: dist\Fram\Fram.exe
pause
