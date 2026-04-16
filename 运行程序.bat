@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo ========================================
echo Quora 自动化发帖助手
echo ========================================
echo.
echo 使用系统 Python 运行，避免 conda 环境的中文路径编码问题
echo.
python gui_app.py
if errorlevel 1 (
    echo.
    echo 运行出错，请检查日志
    pause
)
