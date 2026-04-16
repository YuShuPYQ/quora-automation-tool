import os
import subprocess

# 可能的 Chrome 路径
chrome_paths = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
]

print("检查 Chrome 安装路径:")
for path in chrome_paths:
    exists = os.path.exists(path)
    print(f"  {path}: {'存在' if exists else '不存在'}")

# 检查数据目录
profile_path = r"C:\ChromeProfiles"
print(f"\n数据目录: {profile_path}")
print(f"数据目录存在: {os.path.exists(profile_path)}")

if os.path.exists(profile_path):
    print("数据目录内容:")
    for item in os.listdir(profile_path):
        print(f"  {item}")

# 尝试直接启动 Chrome
print("\n尝试启动 Chrome (无参数)...")
chrome_exe = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if os.path.exists(chrome_exe):
    try:
        proc = subprocess.Popen([chrome_exe])
        print(f"启动成功，进程 ID: {proc.pid}")
    except Exception as e:
        print(f"启动失败: {e}")
