# ui_constants.py

class Colors:
    """集中管理UI颜色，支持亮/暗模式元组。"""
    # 背景色
    BG_MAIN = ("#f9fafb", "#111827")
    BG_NAV = ("#ffffff", "#1f2937")
    BG_TABS = "transparent"
    BG_INSTANCE_ITEM = ("#eef2ff", "#2d3748")
    BG_HEADER = ("#f0f2f5", "#374151")
    BG_SCROLL_FRAME = ("#fafafa", "#1f2937")

    # 文本颜色
    TEXT_PRIMARY = ("#334155", "#f9fafb")
    TEXT_SECONDARY = ("#4a5568", "#d1d5db")
    TEXT_TERTIARY = ("#718096", "#9ca3af")
    TEXT_NAV_INACTIVE = ("#4a5568", "#9ca3af")
    TEXT_NAV_ACTIVE = ("#ffffff", "#ffffff")
    TEXT_WHITE = "#ffffff"
    TEXT_RED = "#ef4444"

    # 按钮颜色
    BTN_NAV_HOVER = ("#eef2ff", "#374151")
    BTN_NAV_ACTIVE = ("#6366f1", "#4f46e5")
    
    BTN_GREEN = "#22c55e"
    BTN_GREEN_HOVER = "#16a34a"
    BTN_RED = "#ef4444"
    BTN_RED_HOVER = "#dc2626"
    BTN_YELLOW = "#f59e0b"
    BTN_YELLOW_HOVER = "#d97706"
    BTN_PURPLE = "#8b5cf6"
    BTN_PURPLE_HOVER = "#7c3aed"
    BTN_TEAL = "#10b981"
    BTN_TEAL_HOVER = "#059669"
    BTN_BLUE = "#63b3ed"
    BTN_BLUE_HOVER = "#4299e1"
    BTN_CLOSE = "#fc8181"
    BTN_CLOSE_HOVER = "#f56565"
    BTN_CANCEL_FG = "transparent"
    BTN_CANCEL_TEXT = ("#718096", "#9ca3af")
    
    # 边框与特殊颜色
    BORDER_PRIMARY = ("#e2e8f0", "#374151")
    BORDER_INSTANCE_ITEM = ("#dee2e6", "#4a5568")
    RADIO_BORDER = ("#6366f1", "#4f46e5")
    RADIO_HOVER = ("#8b5cf6", "#7c3aed")
    PLACEHOLDER_TEXT = ("#a0aec0", "#718096")

class Fonts:
    """集中管理UI字体。"""
    FAMILY = "Microsoft YaHei UI"
    
    H1 = (FAMILY, 18, "bold")
    H2 = (FAMILY, 16, "bold")
    H3 = (FAMILY, 14, "bold")
    
    NAV_BTN = (FAMILY, 13, "bold")
    BODY_BOLD = (FAMILY, 12, "bold")
    BODY = (FAMILY, 12)
    SMALL = (FAMILY, 11)
    SMALL_BOLD = (FAMILY, 11, "bold")

    ICON = (FAMILY, 16)
    LOG = ("Courier New", 12)

class Dimens:
    """集中管理UI尺寸和间距。"""
    CORNER_RADIUS_L = 10
    CORNER_RADIUS_M = 8
    CORNER_RADIUS_S = 6
    CORNER_RADIUS_XS = 4

    BTN_HEIGHT_L = 42
    BTN_HEIGHT_M = 40
    BTN_HEIGHT_S = 32
    BTN_HEIGHT_XS = 28

    ENTRY_HEIGHT = 38

    MAIN_PAD_X = 20
    MAIN_PAD_Y = 10
    NAV_PAD_Y = (15, 10)

    ITEM_PAD_X = 15
    ITEM_PAD_Y = 12

