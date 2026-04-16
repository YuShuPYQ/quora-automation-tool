import threading
import time

class TumblrPoster(threading.Thread):
    def __init__(self, ports, excel_path, image_folder, post_count, stop_event, log_callback):
        super().__init__()
        self.ports = ports
        self.excel_path = excel_path
        self.image_folder = image_folder
        self.post_count = post_count
        self.stop_event = stop_event
        self.log_callback = log_callback

    def run(self):
        self.log_callback("▶️ Tumblr 发帖任务开始...")

        for i in range(self.post_count):
            if self.stop_event.is_set():
                self.log_callback("⏹️ 检测到停止信号，正在终止 Tumblr 发帖任务...")
                return
            self.log_callback(f"  - Tumblr 正在进行第 {i + 1}/{self.post_count} 次发帖...")
            time.sleep(2)

        self.log_callback("✅ Tumblr 发帖任务全部完成。")
