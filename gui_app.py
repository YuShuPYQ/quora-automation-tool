import customtkinter as ctk
import os
import sys
import threading
import logging
import uuid
import shutil
import subprocess
import time
import socket
from tkinter import messagebox, simpledialog, filedialog
from config_manager import ConfigManager

# Poster imports
from poster.quora_poster import QuoraPoster
from poster.ok_poster import OkRuPoster
from poster.tumblr_poster import TumblrPoster
from poster.tiktok_poster import TikTokPoster
from poster.google_login import GoogleLoginTask

# UI Constants
from ui_constants import Colors, Fonts, Dimens

# ==============================================================================
# HELPER FUNCTIONS AND CLASSES
# ==============================================================================

def setup_tcl_tk():
    """设置 Tcl/Tk 环境变量，解决中文路径编码问题"""
    if hasattr(sys, '_MEIPASS'):
        return
    
    if 'conda' in sys.prefix.lower() or '.conda' in sys.executable.lower():
        script_dir = os.path.dirname(os.path.abspath(__file__))
        conda_lib = os.path.join(script_dir, '.conda', 'Library', 'lib')
        tcl_path = os.path.join(conda_lib, 'tcl8.6')
        tk_path = os.path.join(conda_lib, 'tk8.6')
        
        if os.path.exists(tcl_path):
            os.environ['TCL_LIBRARY'] = tcl_path
            os.environ['TK_LIBRARY'] = tk_path

class TextHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget

    def emit(self, record):
        msg = self.format(record)
        self.text_widget.after(0, lambda: self.append_log(msg))

    def append_log(self, msg):
        self.text_widget.insert("end", msg + "\n")
        self.text_widget.see("end")

# ==============================================================================
# INITIALIZATION
# ==============================================================================
setup_tcl_tk()
config_mgr = ConfigManager()

# ==============================================================================
# MAIN APPLICATION CLASS
# ==============================================================================
class BrowserManagerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("多平台登录 发帖助手")
        self.geometry("1280x900")
        self._setup_icon()
        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self.theme_mode = config_mgr.get("theme_mode", "Light")
        ctk.set_appearance_mode(self.theme_mode)

        self.task_thread = None
        self.stop_event = None
        self.browser_processes = []
        self._log_lock = threading.Lock()

        self.tab_frames = {}
        self.nav_buttons = []
        self.active_tab = "run"
        self.filter_group_var = ctk.StringVar(value="全部实例")
        self.group_dropdown_list = ["全部实例"]
        self.auto_login_var = ctk.BooleanVar(value=False)
        self.instance_vars = []
        self.delete_instances_vars = {}


        self.setup_ui()

    # ==============================================================================
    # UI Setup & Core
    # ==============================================================================

    def setup_ui(self):
        """构建主界面"""
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.main_container = ctk.CTkFrame(self, fg_color=Colors.BG_MAIN, corner_radius=0)
        self.main_container.grid(row=0, column=0, sticky="nsew")

        self.nav_frame = ctk.CTkFrame(self.main_container, fg_color=Colors.BG_NAV, corner_radius=Dimens.CORNER_RADIUS_L, height=65)
        self.nav_frame.pack(fill="x", padx=Dimens.MAIN_PAD_X, pady=Dimens.NAV_PAD_Y)
        self.nav_frame.grid_columnconfigure(1, weight=1)
        
        nav_left_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        nav_left_frame.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        
        theme_switch_frame = ctk.CTkFrame(self.nav_frame, fg_color="transparent")
        theme_switch_frame.grid(row=0, column=2, padx=20, pady=10, sticky="e")
        
        ctk.CTkLabel(theme_switch_frame, text="🌙", font=Fonts.ICON).pack(side="left")
        ctk.CTkSwitch(theme_switch_frame, text="", command=self.toggle_theme, variable=ctk.StringVar(value="on" if self.theme_mode == "Dark" else "off")).pack(side="left")
        
        ctk.CTkLabel(nav_left_frame, text="🚀 多平台登录 发帖助手", font=Fonts.H1, text_color=Colors.TEXT_PRIMARY).pack(side="left", padx=(10, 25))

        tabs = [("run", "🚀 运行任务"), ("config", "⚙️ 基础配置"), ("multi_platform_config", "🌐 多平台配置"), ("log", "📜 运行日志")]
        for name, text in tabs:
            btn = ctk.CTkButton(nav_left_frame, text=text, font=Fonts.NAV_BTN, fg_color="transparent", text_color=Colors.TEXT_NAV_INACTIVE, hover_color=Colors.BTN_NAV_HOVER, corner_radius=Dimens.CORNER_RADIUS_M, height=40, width=120, command=lambda n=name: self._switch_tab(n))
            btn.pack(side="left", padx=6)
            self.nav_buttons.append((btn, name))

        self.tabs_container = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.tabs_container.pack(fill="both", expand=True, padx=Dimens.MAIN_PAD_X, pady=Dimens.MAIN_PAD_Y)
        self.tabs_container.grid_rowconfigure(0, weight=1)
        self.tabs_container.grid_columnconfigure(0, weight=1)

        for name, _ in tabs:
            frame = ctk.CTkFrame(self.tabs_container, fg_color="transparent")
            frame.grid(row=0, column=0, sticky="nsew")
            self.tab_frames[name] = frame

        self.setup_run_tab()
        self.setup_config_tab()
        self.setup_multi_platform_config_tab()
        self.setup_log_tab()

        self._switch_tab("run")

    def _switch_tab(self, tab_name):
        self.active_tab = tab_name
        for name, frame in self.tab_frames.items():
            frame.tkraise() if name == tab_name else frame.lower()
        
        for btn, name in self.nav_buttons:
            if name == tab_name:
                btn.configure(fg_color=Colors.BTN_NAV_ACTIVE, text_color=Colors.TEXT_NAV_ACTIVE)
            else:
                btn.configure(fg_color="transparent", text_color=Colors.TEXT_NAV_INACTIVE)

    def toggle_theme(self):
        new_mode = "Dark" if ctk.get_appearance_mode() == "Light" else "Light"
        ctk.set_appearance_mode(new_mode)
        config_mgr.set("theme_mode", new_mode)
        config_mgr.save()

    # ==============================================================================
    # Run Tab Setup
    # ==============================================================================
    def setup_run_tab(self):
        self.tab_frames["run"].grid_columnconfigure(0, weight=1)
        self.tab_frames["run"].grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(self.tab_frames["run"], text="浏览器实例", font=Fonts.H2, text_color=Colors.TEXT_SECONDARY).pack(padx=20, pady=(20, 10), anchor="w")
        
        manage_frame = ctk.CTkFrame(self.tab_frames["run"], fg_color="transparent")
        manage_frame.pack(padx=20, pady=(0, 15), fill="x")
        
        ctk.CTkButton(manage_frame, text="➕ 新建", font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=70, corner_radius=Dimens.CORNER_RADIUS_M, fg_color=Colors.BTN_GREEN, text_color=Colors.TEXT_WHITE, hover_color=Colors.BTN_GREEN_HOVER, command=self.add_instance).pack(side="left", padx=(0, 6))
        ctk.CTkButton(manage_frame, text="🗑️ 删除", font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=70, corner_radius=Dimens.CORNER_RADIUS_M, fg_color=Colors.BTN_RED, text_color=Colors.TEXT_WHITE, hover_color=Colors.BTN_RED_HOVER, command=self.delete_selected_instances).pack(side="left", padx=(0, 6))
        ctk.CTkButton(manage_frame, text="🔄 重置", font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=70, corner_radius=Dimens.CORNER_RADIUS_M, fg_color=Colors.BTN_YELLOW, text_color=Colors.TEXT_WHITE, hover_color=Colors.BTN_YELLOW_HOVER, command=self.reset_selected_instances).pack(side="left", padx=(0, 6))
        ctk.CTkButton(manage_frame, text="☑️ 全选", font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=70, corner_radius=Dimens.CORNER_RADIUS_M, command=self.select_all_instances).pack(side="left", padx=(0, 6))
        
        range_frame = ctk.CTkFrame(manage_frame, fg_color="transparent")
        range_frame.pack(side="left", padx=10)
        ctk.CTkLabel(range_frame, text="🔢 选择区间：", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 8))
        self.range_start_entry = ctk.CTkEntry(range_frame, font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=50, corner_radius=Dimens.CORNER_RADIUS_M, border_width=1, placeholder_text="起始")
        self.range_start_entry.pack(side="left", padx=2)
        ctk.CTkLabel(range_frame, text="到", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=4)
        self.range_end_entry = ctk.CTkEntry(range_frame, font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=50, corner_radius=Dimens.CORNER_RADIUS_M, border_width=1, placeholder_text="结束")
        self.range_end_entry.pack(side="left", padx=2)
        ctk.CTkButton(range_frame, text="确定", font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=50, corner_radius=Dimens.CORNER_RADIUS_M, command=self.select_instances_by_range).pack(side="left", padx=2)
        ctk.CTkButton(range_frame, text="反选", font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=50, corner_radius=Dimens.CORNER_RADIUS_M, fg_color=Colors.BTN_PURPLE, hover_color=Colors.BTN_PURPLE_HOVER, command=self.invert_instances_selection).pack(side="left", padx=2)
        
        ctk.CTkLabel(manage_frame, text="📁 分组筛选：", font=Fonts.BODY_BOLD, text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(10, 5))
        self.filter_dropdown = ctk.CTkOptionMenu(manage_frame, variable=self.filter_group_var, values=self.group_dropdown_list, command=self.on_group_filter_changed, font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=140, corner_radius=Dimens.CORNER_RADIUS_M)
        self.filter_dropdown.pack(side="left", padx=(0, 10), pady=2)
        self._update_group_dropdown_list()
        
        ctk.CTkButton(manage_frame, text="➕ 加入分组", font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=90, corner_radius=Dimens.CORNER_RADIUS_M, fg_color=Colors.BTN_TEAL, hover_color=Colors.BTN_TEAL_HOVER, command=self.show_add_group_dialog).pack(side="left", padx=(0, 6))
        ctk.CTkButton(manage_frame, text="📁 管理", font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=70, corner_radius=Dimens.CORNER_RADIUS_M, fg_color=Colors.BTN_PURPLE, hover_color=Colors.BTN_PURPLE_HOVER, command=self.show_group_manager).pack(side="left", padx=(0, 6))
        
        self.instance_frame = ctk.CTkScrollableFrame(self.tab_frames["run"], fg_color=Colors.BG_SCROLL_FRAME, border_color=Colors.BORDER_PRIMARY, border_width=1, corner_radius=Dimens.CORNER_RADIUS_S)
        self.instance_frame.pack(padx=20, pady=10, fill="both", expand=True)
        self._refresh_instance_list()
        
        start_row_frame = ctk.CTkFrame(self.tab_frames["run"], fg_color="transparent")
        start_row_frame.pack(padx=20, pady=(0, 10), fill="x", anchor="w")
        ctk.CTkLabel(start_row_frame, text="从第几行开始登录：", font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 10))
        self.start_row_entry = ctk.CTkEntry(start_row_frame, font=Fonts.BODY, height=Dimens.BTN_HEIGHT_XS, width=80, corner_radius=Dimens.CORNER_RADIUS_XS, border_width=1)
        self.start_row_entry.insert(0, "2")
        self.start_row_entry.pack(side="left")

        concurrent_frame = ctk.CTkFrame(self.tab_frames["run"], fg_color="transparent")
        concurrent_frame.pack(padx=20, pady=(0, 10), fill="x", anchor="w")
        ctk.CTkLabel(concurrent_frame, text="同时登录数量：", font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 10))
        self.concurrent_login_entry = ctk.CTkEntry(concurrent_frame, font=Fonts.BODY, height=Dimens.BTN_HEIGHT_XS, width=80, corner_radius=Dimens.CORNER_RADIUS_XS, border_width=1)
        self.concurrent_login_entry.insert(0, "3")
        self.concurrent_login_entry.pack(side="left")
        
        btn_frame = ctk.CTkFrame(self.tab_frames["run"], fg_color="transparent")
        btn_frame.pack(padx=20, pady=(10, 20), fill="x")
        ctk.CTkButton(btn_frame, text="🚀 启动浏览器", font=Fonts.BODY, height=Dimens.BTN_HEIGHT_M, corner_radius=Dimens.CORNER_RADIUS_S, command=self.launch_selected_browsers).pack(side="left", padx=4)
        ctk.CTkCheckBox(btn_frame, text="启动后自动登录", variable=self.auto_login_var, font=Fonts.BODY, corner_radius=Dimens.CORNER_RADIUS_S).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="🔐 登录谷歌", font=Fonts.BODY, height=Dimens.BTN_HEIGHT_M, corner_radius=Dimens.CORNER_RADIUS_S, command=self.login_google_account).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="▶️ 开始发帖", font=Fonts.BODY, height=Dimens.BTN_HEIGHT_M, corner_radius=Dimens.CORNER_RADIUS_S, command=self.start_task).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="⏹️ 停止任务", font=Fonts.BODY, height=Dimens.BTN_HEIGHT_M, corner_radius=Dimens.CORNER_RADIUS_S, command=self.stop_task).pack(side="left", padx=4)
        ctk.CTkButton(btn_frame, text="⛔ 关闭浏览器", font=Fonts.BODY, height=Dimens.BTN_HEIGHT_M, corner_radius=Dimens.CORNER_RADIUS_S, fg_color=Colors.BTN_CLOSE, hover_color=Colors.BTN_CLOSE_HOVER, command=self.kill_all_browsers).pack(side="left", padx=4)

    # ==============================================================================
    # Config Tab Setup
    # ==============================================================================
    def setup_config_tab(self):
        self.tab_frames["config"].grid_columnconfigure(0, weight=1)
        self.tab_frames["config"].grid_rowconfigure(0, weight=1)
        
        scrollable_frame = ctk.CTkScrollableFrame(self.tab_frames["config"], fg_color="transparent", corner_radius=0)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        ctk.CTkLabel(scrollable_frame, text="基础配置", font=Fonts.H2, text_color=Colors.TEXT_SECONDARY).pack(padx=20, pady=(20, 10), anchor="w")
        
        platform_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        platform_frame.pack(padx=20, pady=(0, 10), fill="x")
        
        ctk.CTkLabel(platform_frame, text="选择平台：", font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 10))
        
        self.platform_var = ctk.StringVar(value="Quora")
        
        self.platform_dropdown = ctk.CTkOptionMenu(platform_frame, values=["Quora", "OKru", "Tumblr", "TikTok"], variable=self.platform_var, font=Fonts.BODY, width=150, height=35, corner_radius=Dimens.CORNER_RADIUS_S, command=self.on_platform_changed)
        self.platform_dropdown.pack(side="left")
        
        self.common_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        self.common_frame.pack(padx=20, pady=10, fill="x")
        
        common_header = ctk.CTkFrame(self.common_frame, fg_color=Colors.BG_HEADER)
        common_header.pack(fill="x", pady=(0, 5))
        common_header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(common_header, text="公共配置", font=Fonts.H3, text_color=Colors.TEXT_SECONDARY).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        
        self.common_expanded = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(common_header, text="", variable=self.common_expanded, command=self.toggle_common_config).grid(row=0, column=1, padx=10, pady=8, sticky="e")
        
        self.common_config_frame = ctk.CTkFrame(self.common_frame, fg_color="transparent")
        self.common_config_frame.pack(fill="x")
        self.common_config_frame.grid_columnconfigure(1, weight=1)
        
        common_configs = [
            ("Chrome 路径：", "chrome_path", True, [("Chrome", "chrome.exe")]),
            ("数据目录：", "profile_path", False, None),
            ("截图保存：", "screenshot_folder", False, None),
            ("谷歌账号文件：", "google_account_path", True, [("Excel files", "*.xlsx;*.xls")])
        ]
        


        entries = {}

        for i, (label_text, attr_name, is_file, filetypes) in enumerate(common_configs):
            ctk.CTkLabel(self.common_config_frame, text=label_text, font=Fonts.BODY, text_color=Colors.TEXT_TERTIARY, anchor="e", width=110).grid(row=i, column=0, padx=(0, Dimens.ITEM_PAD_X), pady=Dimens.ITEM_PAD_Y, sticky="e")
            entry = ctk.CTkEntry(self.common_config_frame, font=Fonts.BODY, height=Dimens.ENTRY_HEIGHT, corner_radius=Dimens.CORNER_RADIUS_S, border_width=1)
            entry.grid(row=i, column=1, padx=5, pady=Dimens.ITEM_PAD_Y, sticky="ew")
            entry.insert(0, config_mgr.get(attr_name, ""))
            entries[attr_name] = entry
            ctk.CTkButton(self.common_config_frame, text="浏览...", font=Fonts.BODY, width=80, height=Dimens.ENTRY_HEIGHT, corner_radius=Dimens.CORNER_RADIUS_S, command=lambda e=entry, f=is_file, ft=filetypes: self._browse_path(e, is_file=f, filetypes=ft)).grid(row=i, column=2, padx=(Dimens.ITEM_PAD_X, 0), pady=Dimens.ITEM_PAD_Y)
        
        self.path_entry = entries["chrome_path"]
        self.profile_entry = entries["profile_path"]
        self.screenshot_entry = entries["screenshot_folder"]
        self.google_account_entry = entries["google_account_path"]

        website_row = len(common_configs)
        ctk.CTkLabel(self.common_config_frame, text="登录后网站：", font=Fonts.BODY, text_color=Colors.TEXT_TERTIARY, anchor="e", width=110).grid(row=website_row, column=0, padx=(0, Dimens.ITEM_PAD_X), pady=Dimens.ITEM_PAD_Y, sticky="e")
        self.default_website_entry = ctk.CTkEntry(self.common_config_frame, font=Fonts.BODY, height=Dimens.ENTRY_HEIGHT, corner_radius=Dimens.CORNER_RADIUS_S, border_width=1)
        self.default_website_entry.grid(row=website_row, column=1, padx=5, pady=Dimens.ITEM_PAD_Y, sticky="ew")
        self.default_website_entry.insert(0, config_mgr.get("default_website", "https://mail.google.com/"))
        self.enable_website_nav_var = ctk.BooleanVar(value=config_mgr.get("enable_website_navigation", True))
        self.enable_website_nav_checkbox = ctk.CTkCheckBox(self.common_config_frame, text="启用", variable=self.enable_website_nav_var, font=Fonts.BODY, text_color=Colors.TEXT_TERTIARY, checkbox_width=18, checkbox_height=18, corner_radius=Dimens.CORNER_RADIUS_XS, border_width=1)
        self.enable_website_nav_checkbox.grid(row=website_row, column=2, padx=(Dimens.ITEM_PAD_X, 0), pady=Dimens.ITEM_PAD_Y, sticky="w")

        self.platform_config_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        self.platform_config_container.pack(padx=20, pady=10, fill="x")
        platform_header = ctk.CTkFrame(self.platform_config_container, fg_color=Colors.BG_HEADER)
        platform_header.pack(fill="x", pady=(0, 5))
        platform_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(platform_header, text="平台配置", font=Fonts.H3, text_color=Colors.TEXT_SECONDARY).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.platform_expanded = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(platform_header, text="", variable=self.platform_expanded, command=self.toggle_platform_config).grid(row=0, column=1, padx=10, pady=8, sticky="e")
        self.platform_config_frame = ctk.CTkFrame(self.platform_config_container, fg_color="transparent")
        self.platform_config_frame.pack(fill="x")
        self.platform_config_frame.grid_columnconfigure(1, weight=1)
        self.platform_entries = {}
        self._create_platform_config("Quora")
        
        self.template_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        self.template_frame.pack(padx=20, pady=10, fill="x")
        template_header = ctk.CTkFrame(self.template_frame, fg_color=Colors.BG_HEADER)
        template_header.pack(fill="x", pady=(0, 5))
        template_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(template_header, text="按钮模板图片", font=Fonts.H3, text_color=Colors.TEXT_SECONDARY).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.template_expanded = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(template_header, text="", variable=self.template_expanded, command=self.toggle_template_config).grid(row=0, column=1, padx=10, pady=8, sticky="e")
        self.template_config_frame = ctk.CTkFrame(self.template_frame, fg_color="transparent")
        self.template_config_frame.pack(fill="x")
        self.template_config_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.template_config_frame, text="模板图片：", font=Fonts.BODY, text_color=Colors.TEXT_TERTIARY, anchor="e", width=110).grid(row=0, column=0, padx=(0, Dimens.ITEM_PAD_X), pady=Dimens.ITEM_PAD_Y, sticky="e")
        self.template_button_entry = ctk.CTkEntry(self.template_config_frame, font=Fonts.BODY, height=Dimens.ENTRY_HEIGHT, corner_radius=Dimens.CORNER_RADIUS_S, border_width=1)
        self.template_button_entry.grid(row=0, column=1, padx=5, pady=Dimens.ITEM_PAD_Y, sticky="ew")
        self.template_button_entry.insert(0, config_mgr.get("template_button_path", ""))
        ctk.CTkButton(self.template_config_frame, text="上传图片", font=Fonts.BODY, width=80, height=Dimens.ENTRY_HEIGHT, corner_radius=Dimens.CORNER_RADIUS_S, fg_color=Colors.BTN_BLUE, text_color=Colors.TEXT_WHITE, hover_color=Colors.BTN_BLUE_HOVER, command=self.upload_button_template).grid(row=0, column=2, padx=(Dimens.ITEM_PAD_X, 0), pady=Dimens.ITEM_PAD_Y)
        
        save_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        save_frame.pack(pady=25)
        ctk.CTkButton(save_frame, text="💾 保存公共配置", font=Fonts.NAV_BTN, width=140, height=Dimens.BTN_HEIGHT_L, corner_radius=Dimens.CORNER_RADIUS_S, command=self.save_common_config).pack()

    # ==============================================================================
    # Log Tab Setup
    # ==============================================================================
    def setup_log_tab(self):
        self.tab_frames["log"].grid_columnconfigure(0, weight=1)
        self.tab_frames["log"].grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self.tab_frames["log"], text="运行日志", font=Fonts.H2, text_color=Colors.TEXT_SECONDARY).pack(padx=20, pady=(20, 10), anchor="w")

        self.log_text = ctk.CTkTextbox(self.tab_frames["log"], font=Fonts.LOG, border_width=1, corner_radius=Dimens.CORNER_RADIUS_S, wrap="word")
        self.log_text.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        handler = TextHandler(self.log_text)
        handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
        logging.getLogger().addHandler(handler)
        logging.getLogger().setLevel(logging.INFO)

    # ==============================================================================
    # App Utils & General Logic
    # ==============================================================================

    def _setup_icon(self):
        icon_path = self._get_resource_path("one.ico")
        if os.path.exists(icon_path):
            self.iconbitmap(icon_path)
            try:
                from ctypes import windll
                windll.shell32.SetCurrentProcessExplicitAppUserModelID("multi.platform.poster.v1")
            except ImportError:
                pass

    def _get_resource_path(self, relative_path):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
        return os.path.join(base_path, relative_path)

    def log(self, message):
        with self._log_lock:
            logging.info(message)

    def on_close(self):
        if self.task_thread and self.task_thread.is_alive():
            if not messagebox.askokcancel("退出", "任务正在运行中，确定要退出吗？"):
                return
        self.stop_task()
        time.sleep(0.5)
        self.kill_all_browsers(force=True)
        self.destroy()

    # ==============================================================================
    # Config Tab Logic
    # ==============================================================================
    
    def _create_platform_config(self, platform):
        for widget in self.platform_config_frame.winfo_children():
            widget.destroy()
        
        ctk.CTkLabel(self.platform_config_frame, text=f"{platform} 配置", font=Fonts.H3, text_color=Colors.TEXT_SECONDARY).grid(row=0, column=0, columnspan=3, pady=(0, 10), sticky="w")
        
        platform_configs = [
            ("Excel 文件：", f"{platform}_excel_path", True, [("Excel 文件", "*.xlsx")])
            , ("图片文件夹：", f"{platform}_image_folder", False, None)
        ]
        
        self.excel_entry, self.img_entry = None, None
        
        for i, (label_text, attr_name, is_file, filetypes) in enumerate(platform_configs):
            ctk.CTkLabel(self.platform_config_frame, text=label_text, font=Fonts.BODY, text_color=Colors.TEXT_TERTIARY, anchor="e", width=110).grid(row=i+1, column=0, padx=(0, Dimens.ITEM_PAD_X), pady=Dimens.ITEM_PAD_Y, sticky="e")
            entry = ctk.CTkEntry(self.platform_config_frame, font=Fonts.BODY, height=Dimens.ENTRY_HEIGHT, corner_radius=Dimens.CORNER_RADIUS_S, border_width=1)
            entry.grid(row=i+1, column=1, padx=5, pady=Dimens.ITEM_PAD_Y, sticky="ew")
            entry.insert(0, config_mgr.get(attr_name, ""))
            
            if "excel" in attr_name: self.excel_entry = entry
            elif "image" in attr_name: self.img_entry = entry

            ctk.CTkButton(self.platform_config_frame, text="浏览...", font=Fonts.BODY, width=80, height=Dimens.ENTRY_HEIGHT, corner_radius=Dimens.CORNER_RADIUS_S, command=lambda e=entry, f=is_file, ft=filetypes: self._browse_path(e, is_file=f, filetypes=ft)).grid(row=i+1, column=2, padx=(Dimens.ITEM_PAD_X, 0), pady=Dimens.ITEM_PAD_Y)
        
        ctk.CTkLabel(self.platform_config_frame, text="发帖次数：", font=Fonts.BODY, text_color=Colors.TEXT_TERTIARY, anchor="e", width=110).grid(row=3, column=0, padx=(0, Dimens.ITEM_PAD_X), pady=Dimens.ITEM_PAD_Y, sticky="e")
        self.post_count_entry = ctk.CTkEntry(self.platform_config_frame, font=Fonts.BODY, height=Dimens.ENTRY_HEIGHT, corner_radius=Dimens.CORNER_RADIUS_S, border_width=1, width=100)
        self.post_count_entry.insert(0, str(config_mgr.get(f"{platform}_post_count", 1)))
        self.post_count_entry.grid(row=3, column=1, padx=5, pady=Dimens.ITEM_PAD_Y, sticky="w")

    def on_platform_changed(self, platform):
        self._create_platform_config(platform)
    
    def toggle_common_config(self):
        if self.common_expanded.get(): self.common_config_frame.pack(fill="x")
        else: self.common_config_frame.pack_forget()
    
    def toggle_platform_config(self):
        if self.platform_expanded.get(): self.platform_config_frame.pack(fill="x")
        else: self.platform_config_frame.pack_forget()
    
    def toggle_template_config(self):
        if self.template_expanded.get(): self.template_config_frame.pack(fill="x")
        else: self.template_config_frame.pack_forget()

    def _browse_path(self, entry_widget, title=None, is_file=False, filetypes=None):
        path = filedialog.askopenfilename(title=title, filetypes=filetypes) if is_file else filedialog.askdirectory(title=title)
        if path and entry_widget:
            entry_widget.delete(0, "end")
            entry_widget.insert(0, path)

    def upload_button_template(self):
        file_path = filedialog.askopenfilename(title="选择按钮模板图片", filetypes=[("图片文件", "*.png;*.jpg;*.jpeg;*.bmp"), ("所有文件", "*.*")])
        if not file_path: return
        try:
            template_dir = self._get_resource_path("button_templates")
            if not os.path.exists(template_dir): os.makedirs(template_dir)
            dest_path = os.path.join(template_dir, f"template_button{os.path.splitext(file_path)[1]}")
            shutil.copy2(file_path, dest_path)
            self.template_button_entry.delete(0, "end")
            self.template_button_entry.insert(0, dest_path)
            config_mgr.set("template_button_path", dest_path)
            config_mgr.save()
            messagebox.showinfo("成功", f"模板图片已保存到：\n{dest_path}")
            self.log(f"✅ 按钮模板图片已上传: {dest_path}")
        except Exception as e:
            messagebox.showerror("错误", f"上传失败：{e}")
            self.log(f"❌ 上传按钮模板图片失败: {e}")

    def save_common_config(self):
        try:
            config_mgr.set("chrome_path", self.path_entry.get())
            config_mgr.set("profile_path", self.profile_entry.get())
            config_mgr.set("screenshot_folder", self.screenshot_entry.get())
            config_mgr.set("google_account_path", self.google_account_entry.get())
            config_mgr.set("default_website", self.default_website_entry.get())
            config_mgr.set("enable_website_navigation", self.enable_website_nav_var.get())
            config_mgr.save()
            messagebox.showinfo("成功", "公共配置已保存")
        except Exception as e:
            messagebox.showerror("错误", f"保存公共配置失败: {e}")

    def save_platform_config(self):
        platform = self.platform_var.get()
        try:
            config_mgr.set("template_button_path", self.template_button_entry.get())
            config_mgr.set(f"{platform}_excel_path", self.excel_entry.get())
            config_mgr.set(f"{platform}_image_folder", self.img_entry.get())
            config_mgr.set(f"{platform}_post_count", int(self.post_count_entry.get()))
            config_mgr.save()
            messagebox.showinfo("成功", f"{platform} 平台配置已保存")
        except ValueError:
            messagebox.showerror("错误", "发帖次数必须是数字")
        except Exception as e:
            messagebox.showerror("错误", f"保存平台配置失败: {e}")

    def setup_multi_platform_config_tab(self):
        self.tab_frames["multi_platform_config"].grid_columnconfigure(0, weight=1)
        self.tab_frames["multi_platform_config"].grid_rowconfigure(0, weight=1)
        
        scrollable_frame = ctk.CTkScrollableFrame(self.tab_frames["multi_platform_config"], fg_color="transparent", corner_radius=0)
        scrollable_frame.pack(fill="both", expand=True, padx=0, pady=0)
        
        ctk.CTkLabel(scrollable_frame, text="多平台配置", font=Fonts.H2, text_color=Colors.TEXT_SECONDARY).pack(padx=20, pady=(20, 10), anchor="w")
        
        platform_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        platform_frame.pack(padx=20, pady=(0, 10), fill="x")
        
        ctk.CTkLabel(platform_frame, text="选择平台：", font=Fonts.BODY, text_color=Colors.TEXT_SECONDARY).pack(side="left", padx=(0, 10))
        
        self.platform_var = ctk.StringVar(value="Quora")
        
        self.platform_dropdown = ctk.CTkOptionMenu(platform_frame, values=["Quora", "OKru", "Tumblr", "TikTok"], variable=self.platform_var, font=Fonts.BODY, width=150, height=35, corner_radius=Dimens.CORNER_RADIUS_S, command=self.on_platform_changed)
        self.platform_dropdown.pack(side="left")

        self.platform_config_container = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        self.platform_config_container.pack(padx=20, pady=10, fill="x")
        platform_header = ctk.CTkFrame(self.platform_config_container, fg_color=Colors.BG_HEADER)
        platform_header.pack(fill="x", pady=(0, 5))
        platform_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(platform_header, text="平台配置", font=Fonts.H3, text_color=Colors.TEXT_SECONDARY).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.platform_expanded = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(platform_header, text="", variable=self.platform_expanded, command=self.toggle_platform_config).grid(row=0, column=1, padx=10, pady=8, sticky="e")
        self.platform_config_frame = ctk.CTkFrame(self.platform_config_container, fg_color="transparent")
        self.platform_config_frame.pack(fill="x")
        self.platform_config_frame.grid_columnconfigure(1, weight=1)
        self.platform_entries = {}
        self._create_platform_config("Quora")
        
        self.template_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        self.template_frame.pack(padx=20, pady=10, fill="x")
        template_header = ctk.CTkFrame(self.template_frame, fg_color=Colors.BG_HEADER)
        template_header.pack(fill="x", pady=(0, 5))
        template_header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(template_header, text="按钮模板图片", font=Fonts.H3, text_color=Colors.TEXT_SECONDARY).grid(row=0, column=0, padx=10, pady=8, sticky="w")
        self.template_expanded = ctk.BooleanVar(value=True)
        ctk.CTkSwitch(template_header, text="", variable=self.template_expanded, command=self.toggle_template_config).grid(row=0, column=1, padx=10, pady=8, sticky="e")
        self.template_config_frame = ctk.CTkFrame(self.template_frame, fg_color="transparent")
        self.template_config_frame.pack(fill="x")
        self.template_config_frame.grid_columnconfigure(1, weight=1)
        ctk.CTkLabel(self.template_config_frame, text="模板图片：", font=Fonts.BODY, text_color=Colors.TEXT_TERTIARY, anchor="e", width=110).grid(row=0, column=0, padx=(0, Dimens.ITEM_PAD_X), pady=Dimens.ITEM_PAD_Y, sticky="e")
        self.template_button_entry = ctk.CTkEntry(self.template_config_frame, font=Fonts.BODY, height=Dimens.ENTRY_HEIGHT, corner_radius=Dimens.CORNER_RADIUS_S, border_width=1)
        self.template_button_entry.grid(row=0, column=1, padx=5, pady=Dimens.ITEM_PAD_Y, sticky="ew")
        self.template_button_entry.insert(0, config_mgr.get("template_button_path", ""))
        ctk.CTkButton(self.template_config_frame, text="上传图片", font=Fonts.BODY, width=80, height=Dimens.ENTRY_HEIGHT, corner_radius=Dimens.CORNER_RADIUS_S, fg_color=Colors.BTN_BLUE, text_color=Colors.TEXT_WHITE, hover_color=Colors.BTN_BLUE_HOVER, command=self.upload_button_template).grid(row=0, column=2, padx=(Dimens.ITEM_PAD_X, 0), pady=Dimens.ITEM_PAD_Y)
        
        save_frame = ctk.CTkFrame(scrollable_frame, fg_color="transparent")
        save_frame.pack(pady=25)
        ctk.CTkButton(save_frame, text="💾 保存平台配置", font=Fonts.NAV_BTN, width=140, height=Dimens.BTN_HEIGHT_L, corner_radius=Dimens.CORNER_RADIUS_S, command=self.save_platform_config).pack()


    # ==============================================================================
    # Instance & Group Logic
    # ==============================================================================
    def _refresh_instance_list(self, preserve_selection=True):
        current_selections = {}
        if preserve_selection:
            for item in self.instance_vars:
                current_selections[item["id"]] = item["var"].get()
        
        for widget in self.instance_frame.winfo_children():
            widget.destroy()
        
        self.instance_vars = []
        
        all_instance_ids = config_mgr.get("instance_ids", []) or []
        instance_group_map = config_mgr.get("instance_group_map", {})
        instance_groups = config_mgr.get("instance_groups", {})
        instance_names = config_mgr.get("instance_names", {})
        
        filter_group = self.filter_group_var.get()
        
        if filter_group == "全部实例":
            display_ids = sorted(all_instance_ids, key=lambda x: (0, int(x)) if str(x).isdigit() else (1, str(x)))
        elif filter_group == "未分组":
            grouped_ids = set(instance_group_map.keys())
            display_ids = sorted([uid for uid in all_instance_ids if str(uid) not in grouped_ids], key=lambda x: (0, int(x)) if str(x).isdigit() else (1, str(x)))
        else:
            group_id_to_show = next((gid for gid, gdata in instance_groups.items() if gdata["name"] == filter_group), None)
            display_ids = sorted(instance_groups.get(group_id_to_show, {}).get("instances", []), key=lambda x: (0, int(x)) if str(x).isdigit() else (1, str(x))) if group_id_to_show else []

        self.instance_frame.grid_columnconfigure((0, 1, 2), weight=1)

        cols = 3
        for i, uid in enumerate(display_ids):
            row, col = divmod(i, cols)
            
            port = 9222 + (abs(hash(str(uid))) % 20000) if not str(uid).isdigit() else 9222 + int(uid) - 1

            item_frame = ctk.CTkFrame(self.instance_frame, fg_color=Colors.BG_INSTANCE_ITEM, border_color=Colors.BORDER_INSTANCE_ITEM, border_width=1, corner_radius=Dimens.CORNER_RADIUS_M)
            item_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
            
            var = ctk.BooleanVar(value=current_selections.get(uid, False))
            
            ctk.CTkCheckBox(item_frame, text="", variable=var, width=24, height=24, checkbox_width=24, checkbox_height=24, corner_radius=Dimens.CORNER_RADIUS_S).pack(side="left", padx=(15, 10), pady=15)
            
            uid_str = str(uid)
            visual_index = i + 1
            name = instance_names.get(uid_str, "实例")
            display_name = f"{visual_index}. {name}"

            name_label = ctk.CTkLabel(item_frame, text=display_name, font=Fonts.NAV_BTN, text_color=Colors.TEXT_SECONDARY)
            name_label.pack(side="left", fill="x", expand=True, padx=(0, 15))
            name_label.bind("<Double-1>", lambda e, u=uid, l=name_label: self._update_instance_name(u, l))

            self.instance_vars.append({"id": uid, "var": var, "port": port, "visual_index": visual_index})

    def _update_instance_name(self, uid, label_widget):
        new_name = simpledialog.askstring("修改名称", f"为实例 {uid} 输入新名称:", parent=self)
        if new_name:
            instance_names = config_mgr.get("instance_names", {})
            instance_names[str(uid)] = new_name
            config_mgr.set("instance_names", instance_names)
            config_mgr.save()
            self._refresh_instance_list()
            self.log(f"✅ 实例 {uid} 已重命名为: {new_name}")

    def add_instance(self):
        all_instance_ids = config_mgr.get("instance_ids", [])
        numeric_ids = [int(i) for i in all_instance_ids if str(i).isdigit()]
        new_id = max(numeric_ids) + 1 if numeric_ids else 1
        all_instance_ids.append(new_id)
        config_mgr.set("instance_ids", all_instance_ids)
        config_mgr.save()
        self.log(f"✅ 已添加新实例: {new_id}")
        self._refresh_instance_list()

    def delete_selected_instances(self):
        selected_ids = [item["id"] for item in self.instance_vars if item["var"].get()]
        if not selected_ids:
            messagebox.showwarning("提示", "请至少选择一个实例进行删除")
            return
        if messagebox.askyesno("确认删除", f"确定要删除选中的 {len(selected_ids)} 个实例吗？\n此操作将删除实例的配置文件，不可恢复！"):
            self._delete_instances_by_ids(selected_ids)
            self.log(f"🗑️ 已删除 {len(selected_ids)} 个选中的实例")
            self._refresh_instance_list(preserve_selection=False)
    
    def _delete_instances_by_ids(self, instance_ids_to_delete):
        if not instance_ids_to_delete: return

        all_instance_ids = config_mgr.get("instance_ids", [])
        new_instance_ids = [uid for uid in all_instance_ids if uid not in instance_ids_to_delete]
        
        profile_path = self.profile_entry.get()
        if profile_path and os.path.exists(profile_path):
            for instance_id in instance_ids_to_delete:
                profile_dir = os.path.join(profile_path, f"Profile_{instance_id}")
                if os.path.exists(profile_dir):
                    try:
                        shutil.rmtree(profile_dir)
                        self.log(f"✅ 已删除实例 {instance_id} 的配置文件目录: {profile_dir}")
                    except Exception as e:
                        self.log(f"❌ 删除实例 {instance_id} 目录时出错: {e}")

        instance_groups = config_mgr.get("instance_groups", {})
        instance_group_map = config_mgr.get("instance_group_map", {})
        instance_names = config_mgr.get("instance_names", {})

        for instance_id in instance_ids_to_delete:
            str_id = str(instance_id)
            old_group_id = instance_group_map.pop(str_id, None)
            if old_group_id and old_group_id in instance_groups:
                if instance_id in instance_groups[old_group_id]["instances"]:
                    instance_groups[old_group_id]["instances"].remove(instance_id)
            instance_names.pop(str_id, None)

        config_mgr.set("instance_groups", instance_groups)
        config_mgr.set("instance_group_map", instance_group_map)
        config_mgr.set("instance_names", instance_names)
        config_mgr.set("instance_ids", new_instance_ids)
        config_mgr.save()

    def reset_selected_instances(self):
        selected = [item for item in self.instance_vars if item["var"].get()]
        if not selected: 
            messagebox.showwarning("提示", "请至少选择一个实例进行重置")
            return
        if not messagebox.askyesno("确认重置", f"确定要重置选中的 {len(selected)} 个实例吗？\n这将删除它们的配置文件，但保留实例本身。"): 
            return
        
        base_profile = self.profile_entry.get()
        if not base_profile: 
            messagebox.showerror("错误", "数据目录未设置")
            return
            
        for item in selected:
            profile_dir = os.path.join(base_profile, f"Profile_{item['id']}")
            if os.path.exists(profile_dir):
                try:
                    shutil.rmtree(profile_dir)
                    self.log(f"🔄 已重置实例 {item['id']} (已删除: {profile_dir})")
                except Exception as e:
                    self.log(f"❌ 重置实例 {item['id']} 失败: {e}")
        messagebox.showinfo("完成", f"已重置 {len(selected)} 个实例。")

    def select_all_instances(self):
        is_all_selected = all(item["var"].get() for item in self.instance_vars)
        for item in self.instance_vars: item["var"].set(not is_all_selected)

    def select_instances_by_range(self):
        try:
            start = int(self.range_start_entry.get())
            end = int(self.range_end_entry.get())
            if start > end: start, end = end, start
            for item in self.instance_vars:
                if start <= item["visual_index"] <= end:
                    item["var"].set(True)
        except (ValueError, TypeError):
            messagebox.showerror("错误", "请输入有效的数字区间")

    def invert_instances_selection(self):
        for item in self.instance_vars: item["var"].set(not item["var"].get())

    def on_group_filter_changed(self, choice):
        self._refresh_instance_list()

    # ==============================================================================
    # Group Logic
    # ==============================================================================
    def show_group_manager(self):
        group_window = ctk.CTkToplevel(self)
        group_window.title("分组管理")
        group_window.geometry("550x500")
        group_window.transient(self)
        group_window.grab_set()
        
        self.delete_instances_vars = {}
        main_frame = ctk.CTkFrame(group_window, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        main_frame.grid_columnconfigure(0, weight=1)
        main_frame.grid_rowconfigure(1, weight=1)
        
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(header_frame, text="管理实例分组", font=Fonts.H2, text_color=Colors.TEXT_SECONDARY).grid(row=0, column=0, sticky="w")
        ctk.CTkButton(header_frame, text="➕ 新建分组", font=Fonts.BODY_BOLD, height=Dimens.BTN_HEIGHT_S, width=100, corner_radius=Dimens.CORNER_RADIUS_M, fg_color=Colors.BTN_GREEN, text_color=Colors.TEXT_WHITE, hover_color=Colors.BTN_GREEN_HOVER, command=lambda: self.create_new_group(group_window)).grid(row=0, column=1, sticky="e")
        
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color=Colors.BG_SCROLL_FRAME, corner_radius=Dimens.CORNER_RADIUS_S)
        scroll_frame.grid(row=1, column=0, sticky="nsew")
        scroll_frame.grid_columnconfigure(0, weight=1)
        
        instance_groups = config_mgr.get("instance_groups", {})
        if not instance_groups:
            ctk.CTkLabel(scroll_frame, text="暂无分组", font=Fonts.H3, text_color=Colors.PLACEHOLDER_TEXT).pack(pady=50)
        else:
            for i, (group_id, group_data) in enumerate(instance_groups.items()):
                group_item_frame = ctk.CTkFrame(scroll_frame, fg_color=Colors.BG_NAV, border_color=Colors.BORDER_PRIMARY, border_width=1, corner_radius=Dimens.CORNER_RADIUS_S)
                group_item_frame.pack(fill="x", padx=10, pady=5)
                group_item_frame.grid_columnconfigure(2, weight=1)
                
                ctk.CTkLabel(group_item_frame, text=f"📁 {group_data['name']}", font=Fonts.NAV_BTN, text_color=Colors.TEXT_SECONDARY).grid(row=0, column=0, padx=15, pady=10, sticky="w")
                
                delete_instances_var = ctk.BooleanVar(value=False)
                self.delete_instances_vars[group_id] = delete_instances_var
                ctk.CTkCheckBox(group_item_frame, text="同时删除实例", variable=delete_instances_var, font=Fonts.SMALL, text_color=Colors.TEXT_RED, checkbox_width=18, checkbox_height=18, corner_radius=Dimens.CORNER_RADIUS_XS).grid(row=0, column=2, padx=10, pady=10, sticky="e")
                ctk.CTkButton(group_item_frame, text="删除", font=Fonts.SMALL_BOLD, height=Dimens.BTN_HEIGHT_XS, width=60, corner_radius=Dimens.CORNER_RADIUS_XS, fg_color=Colors.BTN_CLOSE, text_color=Colors.TEXT_WHITE, hover_color=Colors.BTN_CLOSE_HOVER, command=lambda gid=group_id: self.delete_group(gid, group_window)).grid(row=0, column=3, padx=10, pady=10, sticky="e")

    def create_new_group(self, parent_window):
        group_name = simpledialog.askstring("新建分组", "请输入新分组的名称：", parent=parent_window)
        if group_name:
            instance_groups = config_mgr.get("instance_groups", {})
            if any(g["name"] == group_name for g in instance_groups.values()):
                messagebox.showerror("错误", f"分组 '{group_name}' 已存在", parent=parent_window)
                return
            new_group_id = str(uuid.uuid4())
            instance_groups[new_group_id] = {"name": group_name, "instances": []}
            config_mgr.set("instance_groups", instance_groups)
            config_mgr.save()
            self.log(f"✅ 已创建新分组: {group_name}")
            self._update_group_dropdown_list()
            parent_window.destroy()
            self.show_group_manager()

    def delete_group(self, group_id, parent_window):
        instance_groups = config_mgr.get("instance_groups", {})
        if group_id not in instance_groups: return

        group_name = instance_groups[group_id]["name"]
        delete_instances = self.delete_instances_vars.get(group_id, ctk.BooleanVar(value=False)).get()
        
        confirm_text = f"确定要删除分组 '{group_name}' 吗？"
        if delete_instances:
            confirm_text += "\n\n⚠️ 您已勾选【同时删除实例】，该分组下的所有实例及其数据将被永久删除！"
        
        if not messagebox.askyesno("确认删除", confirm_text, icon='warning'): return

        if delete_instances:
            instance_ids_to_delete = list(instance_groups.get(group_id, {}).get("instances", []))
            if instance_ids_to_delete:
                self._delete_instances_by_ids(instance_ids_to_delete)
                self.log(f"🗑️ 随分组 {group_name} 一并删除了 {len(instance_ids_to_delete)} 个实例")
        
        del instance_groups[group_id]
        config_mgr.set("instance_groups", instance_groups)
        config_mgr.save()
        self.log(f"✅ 已删除分组: {group_name}")
        self._update_group_dropdown_list()
        parent_window.destroy()
        self.show_group_manager()
        self._refresh_instance_list()

    def show_add_group_dialog(self):
        selected_ids = [item["id"] for item in self.instance_vars if item["var"].get()]
        if not selected_ids: 
            messagebox.showwarning("提示", "请至少选择一个实例")
            return
            
        instance_groups = config_mgr.get("instance_groups", {})
        if not instance_groups: 
            messagebox.showinfo("提示", "请先在【管理】中创建分组")
            return
            
        dialog = ctk.CTkToplevel(self)
        dialog.title("选择分组")
        dialog.geometry("350x400")
        dialog.transient(self)
        dialog.grab_set()
        dialog.grid_columnconfigure(0, weight=1)
        dialog.grid_rowconfigure(1, weight=1)
        
        ctk.CTkLabel(dialog, text=f"将 {len(selected_ids)} 个实例加入分组", font=Fonts.H3, text_color=Colors.TEXT_SECONDARY).grid(row=0, column=0, padx=20, pady=20, sticky="w")
        
        scroll_frame = ctk.CTkScrollableFrame(dialog, fg_color="transparent")
        scroll_frame.grid(row=1, column=0, padx=20, pady=0, sticky="nsew")
        
        group_var = ctk.StringVar()
        for i, (gid, gdata) in enumerate(instance_groups.items()):
            ctk.CTkRadioButton(scroll_frame, text=gdata["name"], variable=group_var, value=gid, font=Fonts.NAV_BTN, text_color=Colors.TEXT_SECONDARY, border_color=Colors.RADIO_BORDER, hover_color=Colors.RADIO_HOVER).pack(anchor="w", padx=10, pady=8)
            
        btn_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=20, pady=20, sticky="e")
        
        def on_confirm():
            selected_group_id = group_var.get()
            if not selected_group_id:
                messagebox.showerror("错误", "请选择一个分组", parent=dialog)
                return
            self._add_instances_to_group(selected_ids, selected_group_id)
            dialog.destroy()
            
        ctk.CTkButton(btn_frame, text="确定", command=on_confirm).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="取消", command=dialog.destroy, fg_color=Colors.BTN_CANCEL_FG, text_color=Colors.BTN_CANCEL_TEXT).pack(side="left")

    def _add_instances_to_group(self, instance_ids, group_id):
        instance_groups = config_mgr.get("instance_groups", {})
        instance_group_map = config_mgr.get("instance_group_map", {})
        if group_id not in instance_groups: return

        for instance_id in instance_ids:
            str_id = str(instance_id)
            old_group_id = instance_group_map.get(str_id)
            if old_group_id and old_group_id in instance_groups and instance_id in instance_groups[old_group_id]["instances"]:
                instance_groups[old_group_id]["instances"].remove(instance_id)
            if instance_id not in instance_groups[group_id]["instances"]:
                instance_groups[group_id]["instances"].append(instance_id)
            instance_group_map[str_id] = group_id

        config_mgr.set("instance_groups", instance_groups)
        config_mgr.set("instance_group_map", instance_group_map)
        config_mgr.save()
        self.log(f"✅ 已将 {len(instance_ids)} 个实例移动到分组: {instance_groups[group_id]['name']}")
        self._refresh_instance_list()

    def _update_group_dropdown_list(self):
        instance_groups = config_mgr.get("instance_groups", {})
        self.group_dropdown_list = ["全部实例", "未分组"] + [g["name"] for g in instance_groups.values()]
        if hasattr(self, 'filter_dropdown'): 
            self.filter_dropdown.configure(values=self.group_dropdown_list)

    # ==============================================================================
    # Browser & Task Logic
    # ==============================================================================

    def launch_selected_browsers(self):
        self.check_browser_processes()
        chrome_exe = self.path_entry.get()
        base_profile = self.profile_entry.get()
        if not chrome_exe or not os.path.exists(chrome_exe): 
            messagebox.showerror("错误", "Chrome 路径无效，请在【基础配置】中设置")
            return
        if not base_profile: 
            messagebox.showerror("错误", "数据目录为空，请在【基础配置】中设置")
            return

        selected = [item for item in self.instance_vars if item["var"].get()]
        if not selected: 
            messagebox.showwarning("提示", "请至少选择一个浏览器实例")
            return

        threading.Thread(target=self._launch_browsers_thread, args=(selected, chrome_exe, base_profile), daemon=True).start()

    def _launch_browsers_thread(self, selected_items, chrome_exe, base_profile):
        for item in selected_items:
            if self.stop_event and self.stop_event.is_set():
                self.log("ℹ️ 浏览器启动任务被中断")
                return

            port = item["port"]
            if self._is_port_in_use(port):
                self.log(f"⚠️ 实例 {item['id']} (端口 {port}) 已经在运行，跳过启动")
                continue
            
            profile_dir = os.path.join(base_profile, f"Profile_{item['id']}")
            if not os.path.exists(profile_dir): os.makedirs(profile_dir)

            cmd = [
                chrome_exe, f"--remote-debugging-port={port}", f"--user-data-dir={profile_dir}",
                "--no-first-run", "--no-default-browser-check", "--start-maximized",
                "--disable-profile-picker", "--no-new-window", 
                "--disable-features=ChromeSignInUI,TranslateUI,Translate,ChromeBrowserSync,Translate",
                "--password-store=basic", "--disable-sync", "--disable-infobars", "--disable-notifications",
                "https://www.google.com"
            ]

            try:
                proc = subprocess.Popen(cmd)
                is_launched = False
                for _ in range(20): # Poll for 10 seconds max
                    if proc.poll() is not None: break # Process died
                    if self._is_port_in_use(port):
                        is_launched = True
                        break
                    time.sleep(0.5)

                if is_launched:
                    self.browser_processes.append(proc)
                    self.log(f"✅ 实例 {item['id']} 已启动 (端口 {port})")
                else:
                    self.log(f"❌ 实例 {item['id']} 启动失败！(端口 {port} 未在10秒内监听)")
                    try: proc.kill()
                    except: pass
            except Exception as e:
                self.log(f"❌ 实例 {item['id']} 启动时发生未知错误: {e}")
        
        if self.auto_login_var.get():
            self.log("✅ 所有浏览器启动完毕，开始自动登录...")
            self.after(0, self.login_google_account)

    def _is_port_in_use(self, port: int) -> bool:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def check_browser_processes(self):
        alive_processes = [p for p in self.browser_processes if p.poll() is None]
        if len(alive_processes) < len(self.browser_processes):
            self.log(f"🧹 清理了 {len(self.browser_processes) - len(alive_processes)} 个已结束的进程")
        self.browser_processes = alive_processes

    def kill_all_browsers(self, force=False):
        self.check_browser_processes()
        if not self.browser_processes: 
            if not force: self.log("ℹ️ 当前没有正在运行的浏览器实例")
            return
        
        if not force and not messagebox.askyesno("确认", f"确定要关闭所有 {len(self.browser_processes)} 个浏览器吗？"): 
            return

        for proc in self.browser_processes:
            try:
                proc.kill()
                self.log(f"⛔️ 已关闭浏览器进程: {proc.pid}")
            except Exception as e:
                self.log(f"❌ 关闭浏览器 {proc.pid} 失败: {e}")
        self.browser_processes.clear()

    def login_google_account(self):
        if self._is_task_running(): return
        google_account_path = self.google_account_entry.get()
        if not google_account_path: 
            messagebox.showerror("错误", "请在【基础配置】中设置谷歌账号文件路径")
            return
        try: 
            start_row = int(self.start_row_entry.get())
            concurrent_logins = int(self.concurrent_login_entry.get())
        except ValueError: 
            messagebox.showerror("错误", "起始行数和并发数必须是有效数字")
            return
            
        selected = [item for item in self.instance_vars if item["var"].get()]
        if not selected: 
            messagebox.showwarning("提示", "请至少选择一个浏览器实例")
            return

        self.stop_event = threading.Event()
        self.task_thread = GoogleLoginTask(selected, google_account_path, start_row, concurrent_logins, self.stop_event, self.log, self.profile_entry.get(), self.default_website_entry.get(), self.enable_website_nav_var.get())
        self.task_thread.start()

    def start_task(self):
        if self._is_task_running(): return
        platform = self.platform_var.get()
        excel_path = config_mgr.get(f"{platform}_excel_path")
        image_folder = config_mgr.get(f"{platform}_image_folder")
        post_count = config_mgr.get(f"{platform}_post_count")

        if not excel_path or not image_folder: 
            messagebox.showerror("错误", f"请先在【基础配置】中完成 {platform} 的配置")
            return

        selected = [item for item in self.instance_vars if item["var"].get()]
        if not selected: 
            messagebox.showwarning("提示", "请至少选择一个浏览器实例")
            return

        self.stop_event = threading.Event()
        PosterClass = {"Quora": QuoraPoster, "OKru": OkRuPoster, "Tumblr": TumblrPoster, "TikTok": TikTokPoster}.get(platform)
        if not PosterClass: 
            messagebox.showerror("错误", f"不支持的平台: {platform}")
            return
            
        self.task_thread = PosterClass(ports=[item["port"] for item in selected], excel_path=excel_path, image_folder=image_folder, post_count=post_count, stop_event=self.stop_event, log_callback=self.log)
        self.task_thread.start()

    def stop_task(self):
        if self.task_thread and self.task_thread.is_alive():
            self.stop_event.set()
            self.log("⏹️ 正在发送停止信号...")
            # No join(), to keep UI responsive. The thread will see the event and stop.
        else:
            self.log("ℹ️ 当前没有任务在运行")

    def _is_task_running(self):
        if self.task_thread and self.task_thread.is_alive():
            messagebox.showwarning("提示", "已有任务在运行中，请先停止当前任务。")
            return True
        return False

if __name__ == "__main__":
    app = BrowserManagerApp()
    app.mainloop()
