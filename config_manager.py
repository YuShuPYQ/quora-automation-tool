import json
import os

# 将配置文件名从 config.json 改为 config.txt，内容格式保持 JSON，方便查看
CONFIG_FILE = "config.txt"

class ConfigManager:
    def __init__(self):
        # 默认配置
        self.config = {
            "chrome_path": r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            "base_profile_path": r"C:\ChromeProfiles",
            "excel_path": "",
            "image_folder": "",
            "screenshot_folder": "",
            "default_website": "https://mail.google.com/",
            "enable_website_navigation": True,  # 默认启用网站导航
            "instance_ids": [], # 存储实例的唯一ID列表
            "instance_groups": {},  # 分组数据：{"group_id": {"name": "分组名", "instances": ["uuid1","uuid2"]}}
            "instance_group_map": {},  # 实例分组映射：{"instance_id": "group_id"}
            "instance_names": {}  # 实例名称：{"instance_id": "实例名称"}
        }
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    content = f.read()
                    if content.strip():
                        data = json.loads(content)
                        self.config.update(data)
            except Exception as e:
                print(f"Error loading config from {CONFIG_FILE}: {e}")

    def save(self):
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving config to {CONFIG_FILE}: {e}")

    def get(self, key, default=None):
        return self.config.get(key, default)

    def set(self, key, value):
        self.config[key] = value
        self.save()
