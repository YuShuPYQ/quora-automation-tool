# -*- mode: python ; coding: utf-8 -*-
import PyInstaller.__main__
import os
import sys
import subprocess

# 获取当前目录
base_path = os.path.dirname(os.path.abspath(__file__))

# 图标路径
icon_path = os.path.join(base_path, "one.ico")

# 检查图标是否存在
if not os.path.exists(icon_path):
    print(f"错误: 图标文件不存在: {icon_path}")
    sys.exit(1)

print(f"使用图标: {icon_path}")

# 使用系统 Python 的 Tcl/Tk 路径
# 先找到系统 Python 的 Tcl/Tk 路径
result = subprocess.run(
    [sys.executable, "-c", "import tkinter; root = tkinter.Tk(); print(root.tk.exprstring('$tcl_library')); root.destroy()"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    print(f"无法获取 Tcl 路径: {result.stderr}")
    # 使用默认路径
    tcl_dir = os.path.join(os.path.dirname(sys.executable), 'tcl8.6')
    tk_dir = os.path.join(os.path.dirname(sys.executable), 'tk8.6')
else:
    tcl_dir = result.stdout.strip()
    tk_dir = tcl_dir.replace('tcl8.6', 'tk8.6')

print(f"Tcl 目录: {tcl_dir} - 存在: {os.path.exists(tcl_dir)}")
print(f"Tk 目录: {tk_dir} - 存在: {os.path.exists(tk_dir)}")

# 收集 Tcl/Tk 数据文件
tcl_tk_datas = []

# 递归收集 Tcl 文件
if os.path.exists(tcl_dir):
    for root_dir, dirs, files in os.walk(tcl_dir):
        for file in files:
            full_path = os.path.join(root_dir, file)
            rel_path = os.path.relpath(os.path.dirname(full_path), os.path.dirname(tcl_dir))
            tcl_tk_datas.append((full_path, rel_path))
    print(f"收集到 {len(tcl_tk_datas)} 个 Tcl 文件")

# 递归收集 Tk 文件
if os.path.exists(tk_dir):
    tk_count = 0
    for root_dir, dirs, files in os.walk(tk_dir):
        for file in files:
            full_path = os.path.join(root_dir, file)
            rel_path = os.path.relpath(os.path.dirname(full_path), os.path.dirname(tk_dir))
            tcl_tk_datas.append((full_path, rel_path))
            tk_count += 1
    print(f"收集到 {tk_count} 个 Tk 文件")

print(f"总共收集到 {len(tcl_tk_datas)} 个 Tcl/Tk 文件")

# 基础数据文件
datas = [
    ('one.ico', '.'),
    ('config.txt', '.'),
    ('xpath.txt', '.'),
]

# 添加 Tcl/Tk 数据文件
datas.extend(tcl_tk_datas)

# PyInstaller 参数
args = [
    'gui_app.py',
    '--name=Quora发帖助手',
    '--onefile',
    '--windowed',
    f'--icon={icon_path}',
    '--add-data=one.ico:.',
    '--add-data=config.txt:.',
    '--add-data=xpath.txt:.',
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
