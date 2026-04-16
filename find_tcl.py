import os
import sys
import tkinter
from tkinter import _tkinter

print(f"Python 版本: {sys.version}")
print(f"Python 路径: {sys.executable}")
print(f"_tkinter 文件: {_tkinter.__file__}")
print(f"tkinter 文件: {tkinter.__file__}")

# 尝试找到 Tcl 库路径
tcl_dir = os.path.join(os.path.dirname(_tkinter.__file__), 'tcl8.6')
print(f"\n尝试路径 1: {tcl_dir}")
print(f"存在: {os.path.exists(tcl_dir)}")

# 尝试其他路径
tcl_dir2 = os.path.join(os.path.dirname(sys.executable), 'tcl8.6')
print(f"\n尝试路径 2: {tcl_dir2}")
print(f"存在: {os.path.exists(tcl_dir2)}")

# 尝试从 _tkinter 获取版本信息
try:
    print(f"\n_tkinter 版本: {_tkinter.Tcl().eval('info version')}")
except Exception as e:
    print(f"\n无法获取 Tcl 版本: {e}")

# 列出 _tkinter 所在目录的内容
print(f"\n_tkinter 所在目录内容:")
tkinter_dir = os.path.dirname(_tkinter.__file__)
if os.path.exists(tkinter_dir):
    for item in os.listdir(tkinter_dir):
        print(f"  {item}")
