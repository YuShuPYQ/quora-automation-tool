import time
import random
import os
from datetime import datetime
import pyautogui

def quora_posting_logic(page, logger, stop_event=None, content="", image_path=None, screenshot_folder="", row_index=0):
    """
    Quora 发帖的具体业务逻辑
    
    参数:
    - page: Playwright 的 page 对象
    - logger: 日志对象
    - stop_event: 停止信号
    - content: 要发布的文本内容
    - image_path: 图片完整路径 (可选)
    - screenshot_folder: 截图保存目录
    - row_index: 当前数据行号 (用于生成截图文件名)
    
    返回:
    - True: 成功
    - False: 失败
    """
    
    # 辅助函数：带中断检测的等待
    def safe_wait(seconds):
        for _ in range(int(seconds * 10)):
            if stop_event and stop_event.is_set(): return True
            time.sleep(0.1)
        return False

    try:
        # 1. 打开 Quora 首页
        logger.info("[-] (1/5) 打开 Quora 首页...")
        # 确保从 Quora 主页开始，不管当前页面是什么
        try:
            page.goto("https://pt.quora.com/", wait_until="domcontentloaded", timeout=30000)
        except Exception as e:
            logger.warning(f"[!] 打开 Quora 首页超时或出错: {e}，继续尝试...")
        if safe_wait(2): return False

        # 2. 点击 "Postar" (发布) 按钮 (首页入口)
        # XPath: //*[@id="mainContent"]/div[2]/div/div[1]/div/div/div[2]/div[3]/button/div/div[2]/div
        logger.info("[-] (2/5) 寻找首页发布按钮...")
        
        # 尝试使用更稳健的 Text 选择器，如果失败则回退到 XPath
        try:
            # 优先尝试点击 "Postar" 或者是 "Adicionar pergunta" 附近的按钮
            # 注意：Quora 界面经常变，这里我们先尝试 XPath
            logger.info("...尝试 XPath 点击")
            page.locator('xpath=//*[@id="mainContent"]/div[2]/div/div[1]/div/div/div[2]/div[3]/button').click(timeout=3000)
        except Exception as e1:
            logger.info(f"[!] XPath 点击失败: {e1}，尝试 Text 选择器...")
            try:
                # 尝试点击包含 "Postar" 的按钮
                page.get_by_text("Postar", exact=True).first.click(timeout=3000)
            except Exception as e2:
                logger.info(f"[!] Text 点击也失败: {e2}")
                return False
            
        if safe_wait(2): return False

        # 3. 输入内容
        logger.info("[-] (3/5) 输入文本内容...")
        
        # 用户反馈：点击 Postar 后直接输入，不需要点击特定的 editor
        # Quora 的弹窗打开后，焦点通常自动在输入框内，或者输入框是页面上唯一的 contenteditable
        # 尝试直接发送键盘指令
        try:
            # 稍微等待弹窗动画
            time.sleep(1)
            
            # 尝试直接聚焦到通用的编辑器容器
            # 许多富文本编辑器捕获全局输入，或者我们可以尝试定位最外层的输入框
            # 既然用户说“直接输入”，我们尝试定位到弹窗内的第一个可编辑区域
            # 或者直接 page.keyboard.type() 看看是否生效 (前提是焦点已自动设置)
            
            # 稳妥起见，我们还是点一下那个框，确保焦点
            # 通常那个框的结构是 role="textbox" 或 contenteditable="true"
            # 我们使用更宽泛的定位：找到页面上可见的、可编辑的元素
            
            # 尝试点击弹窗中央的区域 (如果不知道具体选择器)
            # 但最好的方式是定位 contenteditable
            page.locator('[contenteditable="true"]').first.click()
            
            # 模拟逐字输入
            page.keyboard.type(str(content), delay=10)
            logger.info("[+] 内容已输入 (Direct Type)")
            
        except Exception as e:
            logger.info(f"[!] 直接输入失败: {e}，尝试备用方案...")
            # 备用：尝试 tab 键切换焦点
            page.keyboard.press("Tab")
            page.keyboard.type(str(content), delay=10)

        if safe_wait(1): return False

        # 4. 处理图片 (如果存在)
        if image_path:
            logger.info(f"[-] (3.5/5) 处理图片: {os.path.basename(image_path)}")
            
            # 方案 A: 尝试寻找文件上传 input (最稳健)
            # Quora 编辑器通常有一个 file input 用于上传图片
            try:
                # 尝试点击图片上传按钮触发 input，或者直接找 hidden input
                # 很多时候 input 是隐藏的，直接 set_input_files 就能生效
                # 尝试更宽泛的选择器
                file_inputs = page.locator('input[type="file"]')
                if file_inputs.count() > 0:
                    # 遍历所有 input，看哪个能用
                    file_inputs.first.set_input_files(image_path)
                    logger.info("[+] 图片已通过文件上传接口添加，等待上传完成...")
                    
                    # --- 图片上传等待机制 ---
                    # 1. 强制等待一小段时间，让上传开始
                    time.sleep(2)
                    
                    # 2. 尝试检测编辑器内的图片元素是否出现
                    # Quora 上传的图片通常会有 src 包含 "quoracdn" 或 "blob"
                    try:
                        # 等待编辑器区域出现新的 img 标签
                        # 这里使用一个相对宽泛的选择器，等待任意图片出现在 contenteditable 区域内
                        # timeout 设置为 15 秒，给大图片足够的时间
                        page.locator('[contenteditable="true"] img').first.wait_for(state="visible", timeout=15000)
                        logger.info("[+] 检测到图片预览已加载")
                    except Exception as e:
                        logger.warning(f"[!] 未检测到图片元素 ({e})，启用强制等待...")
                        # 3. 兜底策略：如果检测失败，强制等待 8 秒
                        time.sleep(8)
                    
                    # 4. 再次等待一点点时间，确保图片从 "loading" 状态变为 "完成"
                    time.sleep(2)
                    
                else:
                    logger.info("[!] 未找到 input[type='file']，尝试模拟剪贴板粘贴...")
                    # 方案 B: 剪贴板粘贴 (图片) - 模拟 Ctrl+V
                    # 这需要先用 python 把图片放进剪贴板，这很复杂且不稳定
                    # 替代方案：点击编辑器的“图片”按钮 -> 选择文件 (这需要处理系统弹窗，playwright 做不到)
                    pass
            except Exception as e:
                logger.error(f"[!] 图片上传失败: {e}")
            
            if safe_wait(3): return False # 等待图片上传/渲染

        # 5. 点击 "Postar" (提交) 按钮 (弹窗内)
        # 弹窗内的发布按钮 XPath
        logger.info("[-] (4/5) 提交帖子...")
        
        try:
            # 使用用户提供的更精确 XPath
            user_xpath = '//*[@id="root"]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[2]/div/div[2]/button'
            # 或者尝试点击其内部的 div (有时候事件绑定在 div 上)
            user_xpath_inner = '//*[@id="root"]/div/div[2]/div/div/div/div/div[2]/div/div/div[2]/div[2]/div/div[2]/button/div/div/div'
            
            # 优先尝试点击最内部的 div，往往这是可点击区域
            logger.info("...尝试点击内部 DIV")
            try:
                page.locator(f"xpath={user_xpath_inner}").click(timeout=3000)
            except:
                # 如果失败，点击外层 button
                logger.info("...内部 DIV 点击失败，尝试外层 Button")
                page.locator(f"xpath={user_xpath}").click(timeout=3000)
                
        except Exception as e:
            logger.info(f"[!] XPath 点击失败: {e}，尝试通用文本匹配...")
            # 备用：在整个弹窗中寻找包含 "Postar" 或 "Adicionar pergunta" 的蓝色按钮
            # 通常提交按钮是蓝色的，或者位于弹窗右下角
            try:
                # 寻找包含 "Postar" 的按钮，且是可见的
                page.locator('button').filter(has_text="Postar").last.click(timeout=3000)
            except Exception as e2:
                 logger.error(f"[!] 无法点击提交按钮: {e2}")
                 return False
            
        # 6. 等待跳转并截图
        logger.info("[-] (5/5) 等待发布成功并截图...")
        
        # 关键修改：检测是否跳转到了新页面 (URL 变化) 或者 弹窗消失
        # 记录当前 URL
        start_url = page.url
        
        # 轮询检测 URL 是否变化
        max_wait = 10
        jumped = False
        for _ in range(max_wait * 2): # 每 0.5 秒检查一次
            if stop_event and stop_event.is_set(): return False
            if page.url != start_url:
                logger.info(f"[+] 检测到页面跳转: {page.url}")
                jumped = True
                break
            time.sleep(0.5)
            
        if not jumped:
             logger.warning("[!] 页面未跳转，可能发帖失败或需要手动确认")
             # 但还是截图吧
         
        # 稍微等页面加载
        logger.info("[-] 等待新页面加载 (3秒)...")
        time.sleep(3)
        try:
             # 等待网络空闲，确保图片和内容都加载出来了
             page.wait_for_load_state("networkidle", timeout=5000)
        except:
             pass # 如果超时就不管了，直接截图
         
        # 截图逻辑
        if screenshot_folder:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"post_{row_index}_{timestamp}.png"
            full_path = os.path.join(screenshot_folder, filename)
            
            logger.info("[*] 开始截图...")
            
            # 使用 pyautogui 截取全屏（包括底部导航栏）
            try:
                screenshot = pyautogui.screenshot()
                screenshot.save(full_path)
                logger.info(f"[+] 全屏截图已保存: {filename}")
            except Exception as e:
                logger.error(f"[!] 全屏截图失败: {e}")
                # 备用：尝试使用 Playwright
                try:
                    page.screenshot(path=full_path, full_page=True)
                    logger.info(f"[+] 页面截图已保存 (备用): {filename}")
                except Exception as e2:
                    logger.error(f"[!] 备用截图也失败: {e2}")
        else:
            logger.info("[*] 未设置截图文件夹，跳过截图")
        
        logger.info("[*] 发帖逻辑执行完成，准备返回...")
        return True

    except Exception as e:
        logger.error(f"[!] 发帖过程发生错误: {e}")
        return False
