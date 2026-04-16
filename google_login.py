import requests
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
import time
import sys
import os

# 添加当前目录到路径，以便导入image_clicker和config_manager
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def get_chrome_debug_port(port=9222):
    max_retries = 5
    for attempt in range(max_retries):
        try:
            response = requests.get(f"http://127.0.0.1:{port}/json/version", timeout=5)
            if response.status_code == 200:
                data = response.json()
                ws_url = data.get("webSocketDebuggerUrl")
                if ws_url:
                    return ws_url
        except Exception as e:
            print(f"获取WebSocket端点时出错 (尝试 {attempt+1}/{max_retries}): {e}")
        
        if attempt < max_retries - 1:
            print(f"等待2秒后重试...")
            import time
            time.sleep(2)
    
    print(f"所有重试均失败，无法获取WebSocket端点")
    return None

def click_element(page, locator_str, timeout=5000):
    try:
        locator = page.locator(locator_str)
        if locator.count() == 0:
            return False
        locator.first.click(timeout=timeout, force=True)
        return True
    except Exception as e:
        print(f"点击元素时出错: {e}")
        return False

# def handle_popups(page, log, template_image_path=None):
#     log("[*] 开始处理弹窗...")
#     max_attempts = 10
#     
#     for attempt in range(max_attempts):
#         log(f"[*] 第 {attempt+1}/{max_attempts} 次检查弹窗...")
#         
#         try:
#             # 简化方法：直接查找包含关键文本的按钮
#             # 1. 查找包含"继续"的按钮
#             continue_buttons = page.locator("button:has-text('继续')")
#             if continue_buttons.count() > 0:
#                 log("[!] 找到'继续'按钮")
#                 continue_buttons.first.click(force=True)
#                 log("[*] 已点击'继续'按钮")
#                 time.sleep(1)
#                 return True
#             
#             # 2. 查找包含"Continue"的按钮
#             continue_en_buttons = page.locator("button:has-text('Continue')")
#             if continue_en_buttons.count() > 0:
#                 log("[!] 找到'Continue'按钮")
#                 continue_en_buttons.first.click(force=True)
#                 log("[*] 已点击'Continue'按钮")
#                 time.sleep(1)
#                 return True
#             
#             # 3. 查找包含"身份"的按钮
#             identity_buttons = page.locator("button:has-text('身份')")
#             if identity_buttons.count() > 0:
#                 log("[!] 找到'身份'按钮")
#                 identity_buttons.first.click(force=True)
#                 log("[*] 已点击'身份'按钮")
#                 time.sleep(1)
#                 return True
#             
#             # 4. 查找包含"Sign in"的按钮
#             signin_buttons = page.locator("button:has-text('Sign in')")
#             if signin_buttons.count() > 0:
#                 log("[!] 找到'Sign in'按钮")
#                 signin_buttons.first.click(force=True)
#                 log("[*] 已点击'Sign in'按钮")
#                 time.sleep(1)
#                 return True
#             
#             # 5. 查找包含"Next"的按钮
#             next_buttons = page.locator("button:has-text('Next')")
#             if next_buttons.count() > 0:
#                 log("[!] 找到'Next'按钮")
#                 next_buttons.first.click(force=True)
#                 log("[*] 已点击'Next'按钮")
#                 time.sleep(1)
#                 return True
#             
#             # 6. 查找可见的按钮并点击第一个
#             visible_buttons = page.locator("button:visible")
#             if visible_buttons.count() > 0:
#                 log("[!] 找到可见按钮")
#                 visible_buttons.first.click(force=True)
#                 log("[*] 已点击可见按钮")
#                 time.sleep(1)
#                 return True
#             
#         except Exception as e:
#             log(f"[!] 检查弹窗时出错: {e}")
#         
#         time.sleep(0.5)
#     
#     log("[*] 未找到弹窗按钮")
#     return False

def login_google_account(google_account, google_pwd, logger=None, port=9222, template_image_path=None, default_website=None, enable_website_navigation=True, exit_on_pw_submit=False):
    def log(msg):
        if logger:
            if callable(logger):
                logger(msg)
            else:
                logger.info(msg)
        else:
            print(msg)

    try:
        log("[*] 开始登录谷歌账号...")
        
        ws_endpoint = get_chrome_debug_port(port)
        if not ws_endpoint:
            log(f"❌ 无法连接到端口 {port} 的浏览器调试接口，请确保浏览器已启动。")
            return None

        log(f"[*] 成功连接到端口 {port} 的浏览器。")
        
        with sync_playwright() as p:
            page = None  # 在外部定义，以便except块可以访问
            try:
                browser = p.chromium.connect_over_cdp(ws_endpoint)
                context = browser.contexts[0] if browser.contexts else browser.new_context()
                page = context.pages[0] if context.pages else context.new_page()
                
                log("[*] 访问谷歌登录页面...")
                page.goto("https://accounts.google.com/signin", timeout=60000)
                
                log(f"[*] 输入账号: {google_account}")
                page.locator('input[type="email"]').fill(google_account)
                page.click('button:has-text("下一步")')
                
                log("[*] 输入密码...")
                page.wait_for_selector('input[type="password"]', timeout=15000)
                page.locator('input[type="password"]').fill(google_pwd)
                page.click('button:has-text("下一步")')

                # 新逻辑：如果设置了标志，则在提交密码后立即认为成功并导航
                if exit_on_pw_submit:
                    log("[!] 已设置--exit-on-pw-submit，提交密码后立即认为成功。")
                    if enable_website_navigation and default_website:
                        log(f"[*] 网站导航已启用，立即跳转到: {default_website}")
                        time.sleep(4)
                        try:
                            # 使用 wait_until="load" 确保页面完全加载，这是最可靠的方式
                            page.goto(default_website, timeout=30000, wait_until="load")
                            log(f"[+] 已成功加载页面: {default_website}")
                        except Exception as nav_e:
                            log(f"[!] 导航到预设网站时出错: {nav_e}")
                    else:
                        log("[*] 登录成功（未配置跳转网站或导航未启用）。")

                    return browser # 立即返回成功
                
                log("[*] 等待登录跳转...")
                try:
                    page.wait_for_url(
                        lambda url: "signin" not in url and "challenge" not in url,
                        timeout=20000 # 等待最多20秒，直到URL不再包含登录或验证字样
                    )
                    log(f"[*] 登录成功，跳转后URL: {page.url}")
                except PlaywrightTimeoutError:
                    log("⚠️ 登录超时或需要额外验证。登录失败。")
                    raise Exception("Google login timed out or requires additional verification.")

                if enable_website_navigation:
                    if default_website and default_website.strip():
                        log(f"[*] 网站导航已启用，跳转到: {default_website}")
                        page.goto(default_website, timeout=30000, wait_until="load")
                        log(f"[+] 已成功跳转到: {page.url}")
                    else:
                        log("[*] 谷歌账号登录成功（未配置跳转网站）。")
                else:
                    log("[*] 谷歌账号登录成功（网站导航未启用）。")

                return browser
            
            except Exception as e:
                log(f"[-] 登录操作失败: {e}")
                if page:
                    screenshot_path = os.path.join(current_dir, f"login_error_port_{port}.png")
                    try:
                        page.screenshot(path=screenshot_path, full_page=True)
                        log(f"[!] 错误截图已保存到: {screenshot_path}")
                    except Exception as se:
                        log(f"[-] 保存错误截图失败: {se}")
                
                import traceback
                log(traceback.format_exc())
                return None
                
    except Exception as e:
        log(f"[-] 登录谷歌账号时发生严重错误: {e}")
        import traceback
        log(traceback.format_exc())
        return None

def get_browser_with_google_login(google_account, google_pwd, logger=None, default_website=None, enable_website_navigation=True):
    return login_google_account(google_account, google_pwd, logger, default_website=default_website, enable_website_navigation=enable_website_navigation)
