import pyautogui
import cv2
import numpy as np
from PIL import ImageGrab
import time
import os

def find_and_click_image(template_image_path, confidence=0.7, max_attempts=10, sleep_between=1):
    """
    查找屏幕上的图像并点击
    
    :param template_image_path: 模板图片路径
    :param confidence: 匹配置信度 (0-1)
    :param max_attempts: 最大尝试次数
    :param sleep_between: 每次尝试之间的等待时间（秒）
    :return: 是否成功找到并点击
    """
    if not os.path.exists(template_image_path):
        print(f"[!] 模板图片不存在: {template_image_path}")
        return False
    
    # 读取模板图片
    template = cv2.imread(template_image_path)
    if template is None:
        print(f"[!] 无法读取模板图片: {template_image_path}")
        return False
    
    template_height, template_width = template.shape[:2]
    
    for attempt in range(max_attempts):
        print(f"[*] 第 {attempt + 1}/{max_attempts} 次尝试查找图像...")
        
        # 截取屏幕
        screen = ImageGrab.grab()
        screen_array = np.array(screen)
        screen_gray = cv2.cvtColor(screen_array, cv2.COLOR_RGB2GRAY)
        
        # 转换模板为灰度图
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
        
        # 使用模板匹配
        result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        print(f"[*] 匹配度: {max_val:.4f}")
        
        if max_val >= confidence:
            # 计算中心点
            center_x = max_loc[0] + template_width // 2
            center_y = max_loc[1] + template_height // 2
            
            print(f"[!] 找到图像，位置: ({center_x}, {center_y})")
            
            # 移动鼠标并点击
            pyautogui.moveTo(center_x, center_y, duration=0.3)
            pyautogui.click()
            print(f"[*] 已点击位置: ({center_x}, {center_y})")
            
            return True
        
        time.sleep(sleep_between)
    
    print(f"[!] 未找到匹配的图像 (置信度 >= {confidence})")
    return False

def find_and_click_blue_button(confidence=0.7, max_attempts=10, sleep_between=1):
    """
    查找蓝色按钮并点击（基于颜色）
    这是一个备用方法，当没有模板图片时使用
    
    :param confidence: 匹配置信度 (0-1)
    :param max_attempts: 最大尝试次数
    :param sleep_between: 每次尝试之间的等待时间（秒）
    :return: 是否成功找到并点击
    """
    for attempt in range(max_attempts):
        print(f"[*] 第 {attempt + 1}/{max_attempts} 次尝试查找蓝色按钮...")
        
        # 截取屏幕
        screen = ImageGrab.grab()
        screen_array = np.array(screen)
        
        # 转换到HSV色彩空间
        hsv = cv2.cvtColor(screen_array, cv2.COLOR_RGB2HSV)
        
        # 定义蓝色范围（HSV）
        lower_blue1 = np.array([90, 50, 50])
        upper_blue1 = np.array([130, 255, 255])
        
        lower_blue2 = np.array([100, 100, 100])
        upper_blue2 = np.array([120, 255, 255])
        
        # 创建蓝色掩码
        mask1 = cv2.inRange(hsv, lower_blue1, upper_blue1)
        mask2 = cv2.inRange(hsv, lower_blue2, upper_blue2)
        mask = cv2.bitwise_or(mask1, mask2)
        
        # 查找轮廓
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # 查找最大的蓝色区域
        largest_contour = None
        max_area = 0
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > max_area and area > 500:  # 最小面积过滤
                max_area = area
                largest_contour = contour
        
        if largest_contour is not None:
            # 计算轮廓中心
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                center_x = int(M["m10"] / M["m00"])
                center_y = int(M["m01"] / M["m00"])
                
                print(f"[!] 找到蓝色按钮，位置: ({center_x}, {center_y})")
                
                # 移动鼠标并点击
                pyautogui.moveTo(center_x, center_y, duration=0.3)
                pyautogui.click()
                print(f"[*] 已点击位置: ({center_x}, {center_y})")
                
                return True
        
        time.sleep(sleep_between)
    
    print(f"[!] 未找到蓝色按钮")
    return False

def click_at_position(x, y):
    """
    点击指定位置
    
    :param x: x坐标
    :param y: y坐标
    """
    pyautogui.moveTo(x, y, duration=0.3)
    pyautogui.click()
    print(f"[*] 已点击位置: ({x}, {y})")

if __name__ == "__main__":
    print("图像识别点击模块")
    print("1. find_and_click_image(template_path, confidence=0.7)")
    print("2. find_and_click_blue_button()")
    print("3. click_at_position(x, y)")
