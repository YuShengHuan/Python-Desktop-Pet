# ========== 桌面吸附核心逻辑 ==========
from PySide6.QtCore import QPoint, QRect
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QApplication


def get_current_screen_available_rect():
    """获取桌宠当前所在屏幕的可用区域（排除任务栏）"""
    # 获取当前窗口所在屏幕
    screen = QApplication.screenAt(get_top_window().position() if get_top_window() else QPoint(0,0))
    if not screen:
        screen = QApplication.primaryScreen()
    return screen.availableGeometry()


def get_top_window():
    top_window = None
    for w in QApplication.topLevelWindows():
        if w.objectName() == "mainWindowWindow":
            top_window = w
    return top_window
def get_color(color:QColor):
    return 'transparent' if color.alpha() == 0 else color.name()

