from playwright.sync_api import sync_playwright
import time
import logging
import os
from posting_logic import quora_posting_logic

# 配置日志格式
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def check_browser_status(port, logger=logging.getLogger(__name__)):
    import requests
    try:
        response = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=2)
        if response.status_code == 200:
            data = response.json()
            logger.info(f"[+] 发现活跃的 Chrome 实例在端口 {port}")
            return data.get("webSocketDebuggerUrl")
    except requests.ConnectionError:
        pass
    return None

def run_posting_task(playwright, port, ws_endpoint, logger=logging.getLogger(__name__), stop_event=None):
    """
    连接到指定的浏览器并运行发帖任务
    """
    if stop_event and stop_event.is_set(): return

    logger.info(f"[*] 正在连接到端口 {port} 的浏览器...")
    try:
        browser = playwright.chromium.connect_over_cdp(ws_endpoint)
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()
        
        if stop_event and stop_event.is_set(): 
            browser.close()
            return

        logger.info(f"[*] 连接成功！当前页面标题: {page.title()}")
        
        # 将核心发帖逻辑外包给 posting_logic.py
        quora_posting_logic(page, logger, stop_event)
        
        logger.info(f"[+] 端口 {port} 的任务完成")
        
        # 断开连接，不关闭浏览器
        browser.close() 
        
    except Exception as e:
        logger.error(f"[-] 连接或执行任务时出错 (端口 {port}): {e}")

def run_tasks_with_logger(ports, logger_callback=None, stop_event=None, task_params=None):
    """
    供 GUI 调用的任务入口
    """
    class CustomLogger:
        def info(self, msg):
            if logger_callback: logger_callback(msg)
            else: print(msg)
        def error(self, msg):
            if logger_callback: logger_callback(f"ERROR: {msg}")
            else: print(f"ERROR: {msg}")
        def warning(self, msg):
            if logger_callback: logger_callback(f"WARNING: {msg}")
            else: print(f"WARNING: {msg}")
            
    logger = CustomLogger()
    
    from data_manager import DataManager
    data_mgr = None
    if task_params and task_params.get("excel_path"):
        data_mgr = DataManager(task_params["excel_path"])
        if not data_mgr.load():
            logger.error("无法加载 Excel 文件，任务终止")
            return
    
    current_row_index = 1
    
    logger.info("[+] 开始执行发帖任务")
    
    with sync_playwright() as p:
        active_browsers = []
        
        def cleanup_browsers():
            logger.info("[*] 正在关闭所有活动浏览器连接...")
            for browser in active_browsers:
                try:
                    if browser.is_connected():
                        browser.close()
                        logger.info(f"✅ 已关闭浏览器连接")
                except Exception as e:
                    logger.error(f"[-] 关闭浏览器连接时出错: {e}")
            active_browsers.clear()
        
        try:
            for port in ports:
                if stop_event and stop_event.is_set():
                    logger.info("[!] 任务已停止")
                    break
                
                ws_endpoint = check_browser_status(port, logger)
                if ws_endpoint:
                    post_count = task_params.get("post_count", 1) if task_params else 1
                    logger.info(f"[*] 准备在端口 {port} 发帖 {post_count} 次")
                    
                    try:
                        browser = p.chromium.connect_over_cdp(ws_endpoint)
                        active_browsers.append(browser)
                        context = browser.contexts[0] if browser.contexts else browser.new_context()
                        page = context.pages[0] if context.pages else context.new_page()

                        if stop_event and stop_event.is_set():
                            break

                        logger.info(f"[*] 连接成功！当前页面标题: {page.title()}")
                        
                        for i in range(post_count):
                            if stop_event and stop_event.is_set():
                                logger.info("[!] 任务已停止")
                                break
                            
                            logger.info(f"--- 端口 {port} | 第 {i+1}/{post_count} 篇帖子 ---")
                            
                            content, img_name = "", None
                            if data_mgr:
                                content, img_name = data_mgr.get_data(current_row_index)
                                if not content:
                                    logger.info("Excel 数据已读完，停止当前及后续任务")
                                    stop_event.set() # 设置停止标志，以停止所有后续任务
                                    break
                            
                            img_path = None
                            if img_name and task_params.get("image_folder"):
                                img_path = os.path.join(task_params.get("image_folder"), str(img_name))
                                if not os.path.exists(img_path):
                                    logger.error(f"图片不存在: {img_path}")
                                    img_path = None

                            success = quora_posting_logic(page, logger, stop_event, content=content, image_path=img_path, screenshot_folder=task_params.get("screenshot_folder"), row_index=current_row_index)
                            
                            if not success and data_mgr:
                                data_mgr.mark_failed(current_row_index)
                            
                            current_row_index += 1
                            
                            if stop_event and stop_event.is_set():
                                break
                            
                            logger.info("[*] 等待 2 秒后继续下一篇...")
                            time.sleep(2)

                        logger.info(f"[+] 端口 {port} 的任务完成")
                        
                    except Exception as e:
                        logger.error(f"[-] 连接或执行任务时出错 (端口 {port}): {e}")
        finally:
            cleanup_browsers()

def main():
    # 扫描端口范围，例如 9222 到 9230
    start_port = 9222
    end_port = 9230
    ports = range(start_port, end_port + 1)
    
    print(f"[*] 开始扫描本地端口 {start_port}-{end_port}...")
    run_tasks_with_logger(ports)
    print("[*] 所有扫描完成")

if __name__ == "__main__":
    main()
