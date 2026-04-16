import threading
import time

class QuoraPoster(threading.Thread):
    def __init__(self, ports, excel_path, image_folder, post_count, stop_event, log_callback):
        super().__init__()
        self.ports = ports
        self.excel_path = excel_path
        self.image_folder = image_folder
        self.post_count = post_count
        self.stop_event = stop_event
        self.log_callback = log_callback

    def run(self):
        self.log_callback("▶️ Quora 发帖任务开始...")

        for i in range(self.post_count):
            # 在每次发帖前检查停止信号
            if self.stop_event.is_set():
                self.log_callback("⏹️ 检测到停止信号，正在终止 Quora 发帖任务...")
                return

            self.log_callback(f"  - 正在进行第 {i + 1}/{self.post_count} 次发帖...")
            
            # 模拟发帖的多个步骤
            for step in range(5):
                if self.stop_event.is_set():
                    self.log_callback("⏹️ 发帖操作被中断。")
                    return
                self.log_callback(f"    - 发帖步骤 {step + 1}/5...")
                time.sleep(1) # 模拟耗时

            self.log_callback(f"  ✅ 第 {i + 1} 次发帖完成。")
            time.sleep(1)

        self.log_callback("✅ Quora 发帖任务全部完成。")
