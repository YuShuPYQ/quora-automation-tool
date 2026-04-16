@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Quora 自动化发帖助手
echo ========================================
echo.
echo 正在启动程序...
echo.
C:\Users\yushu\AppData\Local\Programs\Python\Python311\python.exe gui_app.py
if errorlevel 1 (
    echo.
    echo 程序运行出错！
    pause
)
