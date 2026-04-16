import subprocess
import os
import time

chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
profile_dir = r"C:\ChromeProfiles\Profile1"
port = 9222

print(f"Chrome 路径: {chrome_exe}")
print(f"Chrome 存在: {os.path.exists(chrome_exe)}")
print(f"配置目录: {profile_dir}")
print(f"配置目录存在: {os.path.exists(profile_dir)}")

if not os.path.exists(profile_dir):
    os.makedirs(profile_dir)
    print(f"创建配置目录: {profile_dir}")

cmd = [
    chrome_exe,
    f"--remote-debugging-port={port}",
    f"--user-data-dir={profile_dir}",
    "--no-first-run",
    "--no-default-browser-check",
    "--start-maximized",
    "--disable-profile-picker",
    "--no-new-window",
    "--disable-features=ChromeSignInUI,TranslateUI,Translate",
    "--password-store=basic"
]

print(f"\n启动命令: {' '.join(cmd)}")
print("\n正在启动 Chrome...")

try:
    proc = subprocess.Popen(cmd)
    print(f"进程已启动，PID: {proc.pid}")
    print(f"进程状态: {'运行中' if proc.poll() is None else '已退出'}")
    
    # 等待几秒检查进程
    time.sleep(3)
    print(f"\n3秒后进程状态: {'运行中' if proc.poll() is None else '已退出'}")
    if proc.poll() is not None:
        print(f"退出码: {proc.returncode}")
except Exception as e:
    print(f"启动失败: {e}")
