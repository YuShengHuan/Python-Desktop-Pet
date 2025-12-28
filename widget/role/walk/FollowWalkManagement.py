import sys
from PySide6.QtCore import *
from PySide6.QtGui import QCursor
from PySide6.QtWidgets import *

from widget.util import WindowStatic


class FollowWalkManagement(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 跟随鼠标相关参数
        self.walk_timer = QTimer(self)
        self.walk_timer.setInterval(30)  # 30ms更新（更流畅的跟随效果）
        self.walk_timer.timeout.connect(self._update_walk_position)

        # 移动状态变量
        self.follow_speed = 8  # 跟随速度（像素/帧，值越大跟随越快）
        self.screen_rect = QRect()  # 屏幕可用区域
        self.top_window = None

    def start_follow_play(self):
        """对外暴露的触发函数：启动/停止跟随鼠标"""
        # 1. 获取最新屏幕可用区域和顶层窗口
        self.screen_rect = WindowStatic.get_current_screen_available_rect()
        self.top_window = WindowStatic.get_top_window()

        if not self.screen_rect.isValid() or self.top_window is None:
            print("获取屏幕区域或窗口失败！")
            return

        # 修正原逻辑：点击一次启动，再点击一次停止
        if not self.walk_timer.isActive():
            self.walk_timer.start()
            print("开始跟随鼠标移动...")
        else:
            self.walk_timer.stop()
            print("停止跟随鼠标移动...")

    def _update_walk_position(self):
        """定时更新位置：实现平滑跟随鼠标核心逻辑"""
        if self.top_window is None:
            return

        # 1. 获取鼠标当前的全局坐标
        mouse_global_pos = QCursor.pos()

        # 2. 计算窗口目标位置（鼠标位置 - 窗口中心偏移，避免窗口左上角贴鼠标）
        target_x = mouse_global_pos.x() - self.top_window.width() / 2
        target_y = mouse_global_pos.y() - self.top_window.height() / 2

        # 3. 边界检测（确保窗口不超出屏幕可用区域）
        target_x = max(self.screen_rect.left(),
                       min(target_x, self.screen_rect.right() - self.top_window.width()))
        target_y = max(self.screen_rect.top(),
                       min(target_y, self.screen_rect.bottom() - self.top_window.height()))

        # 4. 平滑移动：逐步靠近目标位置（避免瞬移）
        current_pos = self.top_window.position()
        # 计算x/y轴的偏移量
        dx = target_x - current_pos.x()
        dy = target_y - current_pos.y()

        # 按跟随速度逐步移动（如果偏移量小于速度，直接到位）
        if abs(dx) < self.follow_speed:
            new_x = target_x
        else:
            new_x = current_pos.x() + (self.follow_speed if dx > 0 else -self.follow_speed)

        if abs(dy) < self.follow_speed:
            new_y = target_y
        else:
            new_y = current_pos.y() + (self.follow_speed if dy > 0 else -self.follow_speed)

        # 5. 更新窗口位置
        self.top_window.setGeometry(new_x, new_y, self.top_window.width(), self.top_window.height())