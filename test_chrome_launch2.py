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
    
    # 等待几秒检查进程
    for i in range(5):
        time.sleep(1)
        status = "运行中" if proc.poll() is None else f"已退出 (退出码: {proc.returncode})"
        print(f"{i+1}秒后进程状态: {status}")
        if proc.poll() is not None:
            break
    
    # 检查 Chrome 进程
    print("\n检查 Chrome 进程:")
    result = subprocess.run(["tasklist", "|", "findstr", "chrome"], capture_output=True, text=True, shell=True)
    print(result.stdout if result.stdout else "没有 Chrome 进程")
    
except Exception as e:
    print(f"启动失败: {e}")
