import PyInstaller.__main__
import os
import sys

# 获取当前目录
base_path = os.path.dirname(os.path.abspath(__file__))

# 图标路径
icon_path = os.path.join(base_path, "one.ico")

# 检查图标是否存在
if not os.path.exists(icon_path):
    print(f"错误: 图标文件不存在: {icon_path}")
    sys.exit(1)

print(f"使用图标: {icon_path}")

# PyInstaller 参数 - 使用 collect-all 自动收集 tkinter 及其依赖
args = [
    'gui_app.py',  # 主程序文件
    '--name=Quora发帖助手',  # 生成的 exe 名称
    '--onefile',  # 打包成单个文件
    '--windowed',  # 不显示控制台窗口
    f'--icon={icon_path}',  # 图标路径
    '--add-data=one.ico:.',  # 将图标打包进程序
    '--add-data=config.txt:.',  # 将配置文件打包进程序
    '--add-data=xpath.txt:.',  # 将 xpath 文件打包进程序
    # 自动收集 tkinter 及其所有依赖
    '--collect-all=tkinter',
    '--collect-all=_tkinter',
    '--collect-all=customtkinter',
    '--clean',  # 清理临时文件
    '--noconfirm',  # 不确认覆盖
    # 隐藏导入的模块
    '--hidden-import=customtkinter',
    '--hidden-import=tkinter',
    '--hidden-import=_tkinter',
    '--hidden-import=openpyxl',
    '--hidden-import=pyautogui',
    '--hidden-import=PIL',
    '--hidden-import=playwright',
]

print("\n开始打包...")
print(f"参数: {args}")
PyInstaller.__main__.run(args)
print("\n打包完成!")
