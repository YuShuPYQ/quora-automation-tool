# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.__main__
import os
import sys

# 获取当前目录
base_path = os.path.dirname(os.path.abspath(__file__))

# 图标路径
icon_path = os.path.join(base_path, "one.ico")

print(f"使用图标: {icon_path}")

# PyInstaller 参数 - 使用 --collect-all 自动收集所有依赖
args = [
    'gui_app.py',
    '--name=Quora发帖助手',
    '--onefile',
    '--windowed',
    f'--icon={icon_path}',
    '--add-data=one.ico:.',
    '--add-data=config.txt:.',
    '--add-data=xpath.txt:.',
    # 自动收集 tkinter 及其所有依赖
    '--collect-all=tkinter',
    '--collect-all=_tkinter',
    '--collect-all=customtkinter',
    '--clean',
    '--noconfirm',
    '--hidden-import=customtkinter',
    '--hidden-import=tkinter',
    '--hidden-import=_tkinter',
    '--hidden-import=openpyxl',
    '--hidden-import=pyautogui',
    '--hidden-import=PIL',
    '--hidden-import=playwright',
]

print("\n开始打包...")
PyInstaller.__main__.run(args)
print("\n打包完成!")
