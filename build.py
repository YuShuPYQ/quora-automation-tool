import PyInstaller.__main__
import os
import shutil

APP_NAME = "多平台发帖助手"
MAIN_SCRIPT = "gui_app.py"
ICON_FILE = "one.ico"

# ==============================================================================
# PyInstaller 参数配置
# ==============================================================================
params = [
    '--noconfirm',
    '--log-level=INFO',
    '--onefile',          # 打包成一个独立的 exe 文件
    '--windowed',         # GUI程序，无命令行窗口
    f'--name={APP_NAME}',  # 设置程序名称
    f'--icon={ICON_FILE}', # 设置程序图标

    # -- 添加数据文件 --
    # 语法: --add-data "<来源路径>;<在包内的目标路径>"
    # 将 poster 文件夹完整地添加到包的根目录下的 poster 文件夹中
    '--add-data', f'{os.path.join("poster", "*")};poster',
    # 将 ui_constants.py 添加到包的根目录
    '--add-data', 'ui_constants.py;.',
    # 将图标文件也添加进去，以确保在某些系统下能正确显示
    '--add-data', f'{ICON_FILE};.',

    # -- 隐藏的导入 --
    # 有时 PyInstaller 无法自动检测到某些库，需要手动添加
    '--hidden-import', 'pandas',
    '--hidden-import', 'openpyxl',
    '--hidden-import', 'selenium',

    MAIN_SCRIPT
]

# ==============================================================================
# 执行打包
# ==============================================================================
if __name__ == '__main__':
    print("▶️ 开始执行 PyInstaller 打包...")
    print(f"   - 主脚本: {MAIN_SCRIPT}")
    print(f"   - 程序名: {APP_NAME}")
    
    try:
        PyInstaller.__main__.run(params)
        print("\n✅ 打包成功！")
    except Exception as e:
        print(f"\n❌ 打包失败: {e}")
        exit(1)

    # ==============================================================================
    # 清理临时文件
    # ==============================================================================
    print("\n🧹 开始清理临时文件...")
    try:
        shutil.rmtree('build')
        os.remove(f'{APP_NAME}.spec')
        print("   - 已删除 'build' 文件夹")
        print("   - 已删除 '.spec' 文件")
        print("✅ 清理完成！")
    except FileNotFoundError:
        print("   - 没有找到临时文件，无需清理。")
    except Exception as e:
        print(f"   - 清理临时文件时出错: {e}")

    print(f"\n🚀 您可以在 'dist' 文件夹中找到最终的程序: {APP_NAME}.exe")
