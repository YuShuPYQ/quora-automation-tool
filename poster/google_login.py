import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
import time

class GoogleLoginTask(threading.Thread):
    def __init__(self, selected_instances, account_path, start_row, concurrent_logins, stop_event, log_callback, profile_path, default_website, enable_website_nav):
        super().__init__()
        self.selected_instances = selected_instances
        self.account_path = account_path
        self.start_row = start_row
        self.concurrent_logins = concurrent_logins
        self.stop_event = stop_event
        self.log_callback = log_callback
        self.profile_path = profile_path
        self.default_website = default_website
        self.enable_website_nav = enable_website_nav

    def run(self):
        self.log_callback("▶️ Google登录任务开始...")
        try:
            accounts = pd.read_excel(self.account_path, header=None, sheet_name=0)
        except Exception as e:
            self.log_callback(f"❌ 读取谷歌账号Excel文件失败: {e}")
            return

        drivers = []
        for i, instance in enumerate(self.selected_instances):
            if self.stop_event.is_set():
                self.log_callback("⏹️ 任务被手动停止。")
                break
            
            driver = None
            try:
                row_index = self.start_row + i - 1
                if row_index >= len(accounts):
                    self.log_callback(f"⚠️ 账号不足，任务提前结束。需要 {len(self.selected_instances)} 个账号，但只提供了 {len(accounts) - self.start_row + 1} 个。")
                    break

                username, password, recovery_email = accounts.iloc[row_index, 0], accounts.iloc[row_index, 1], accounts.iloc[row_index, 2]
                port = instance['port']
                
                self.log_callback(f"  - 正在为实例 {instance['id']} (端口: {port}) 登录账号: {username}")
                
                chrome_options = webdriver.ChromeOptions()
                chrome_options.add_experimental_option("debuggerAddress", f"127.0.0.1:{port}")
                driver = webdriver.Chrome(options=chrome_options)
                drivers.append(driver)
                
                driver.get("https://accounts.google.com/signin")
                
                # Step 1: Input username
                self.log_callback("    - 输入用户名...")
                username_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@type="email"]')))
                username_input.send_keys(username)
                driver.find_element(By.XPATH, '//button[.//span[text()="下一步"]]').click()
                time.sleep(2)
                
                # Step 2: Input password
                self.log_callback("    - 输入密码...")
                password_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@type="password"]')))
                password_input.send_keys(password)
                driver.find_element(By.XPATH, '//button[.//span[text()="下一步"]]').click()
                time.sleep(3) # Wait for potential 2FA page

                # Step 3: Handle 2-Factor Authentication (Recovery Email)
                try:
                    self.log_callback("    - 检查二次验证...")
                    confirm_recovery_email_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//div[@data-challengetype="12"]')))
                    self.log_callback("    - 检测到需要辅助邮箱验证，正在处理...")
                    confirm_recovery_email_button.click()
                    time.sleep(2)
                    
                    recovery_email_input = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//input[@type="email"]')))
                    recovery_email_input.send_keys(recovery_email)
                    driver.find_element(By.XPATH, '//button[.//span[text()="下一步"]]').click()
                    time.sleep(3)
                except Exception:
                    self.log_callback("    - 未检测到二次验证或处理失败，继续...")
                
                # Final check for login success (e.g., by checking for a known element on the account page)
                WebDriverWait(driver, 15).until(EC.url_contains("myaccount.google.com"))
                self.log_callback(f"  ✅ 实例 {instance['id']} 登录成功!")

                if self.enable_website_nav and self.default_website:
                    self.log_callback(f"    - 导航到: {self.default_website}")
                    driver.get(self.default_website)

            except Exception as e:
                self.log_callback(f"  ❌ 实例 {instance['id']} 登录失败: {e}")
                continue

        # In a real scenario, you might not want to quit drivers to keep sessions alive.
        # for driver in drivers:
        #     try: driver.quit()
        #     except: pass
        
        self.log_callback("✅ Google登录任务全部完成。")
