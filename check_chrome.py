import os
import subprocess

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
print(f"Chrome 路径: {chrome_path}")
print(f"Chrome 存在: {os.path.exists(chrome_path)}")

if os.path.exists(chrome_path):
    print("\n尝试启动 Chrome...")
    try:
        proc = subprocess.Popen([chrome_path, "--version"])
        print(f"进程 ID: {proc.pid}")
    except Exception as e:
        print(f"启动失败: {e}")
