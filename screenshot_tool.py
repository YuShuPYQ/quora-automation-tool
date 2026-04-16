import pyautogui
import tkinter as tk
from tkinter import messagebox
from PIL import ImageGrab, ImageTk
import time
import os

class ScreenshotTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("截图工具")
        self.root.geometry("400x200")
        self.root.attributes("-topmost", True)
        
        tk.Label(self.root, text="准备截图，请将鼠标移动到按钮位置").pack(pady=20)
        
        tk.Button(self.root, text="开始截图（5秒后）", command=self.start_screenshot, 
                 height=2, width=20).pack(pady=10)
        
        tk.Label(self.root, text="截图后会保存为 template_button.png").pack(pady=10)
    
    def start_screenshot(self):
        self.root.withdraw()
        print("[*] 5秒后开始截图，请将鼠标移动到按钮位置...")
        for i in range(5, 0, -1):
            print(f"[*] {i}秒...")
            time.sleep(1)
        
        # 获取鼠标位置
        x, y = pyautogui.position()
        print(f"[*] 鼠标位置: ({x}, {y})")
        
        # 截取鼠标周围的区域（150x60像素）
        left = max(0, x - 75)
        top = max(0, y - 30)
        right = left + 150
        bottom = top + 60
        
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        screenshot.save("template_button.png")
        print(f"[!] 截图已保存为 template_button.png")
        print(f"[*] 截取区域: 左={left}, 上={top}, 右={right}, 下={bottom}")
        
        self.root.deiconify()
        messagebox.showinfo("成功", "截图已保存为 template_button.png！")
        
        # 显示截图
        self.show_screenshot()
    
    def show_screenshot(self):
        preview = tk.Toplevel(self.root)
        preview.title("截图预览")
        
        img = ImageTk.PhotoImage(file="template_button.png")
        label = tk.Label(preview, image=img)
        label.image = img
        label.pack()

if __name__ == "__main__":
    tool = ScreenshotTool()
    tool.root.mainloop()
