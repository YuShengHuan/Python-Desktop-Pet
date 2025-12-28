import random

from PySide6.QtCore import *

from widget.util import WindowStatic


class RandomWalkManagement(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 随机行走相关参数
        self.walk_timer = QTimer(self)
        self.walk_timer.setInterval(50)  # 50ms更新一次位置（基础帧率）
        self.walk_timer.timeout.connect(self._update_walk_position)

        # 移动状态变量
        self.current_speed_x = 0  # x轴当前速度（像素/帧）
        self.current_speed_y = 0  # y轴当前速度（像素/帧）
        self.screen_rect = QRect()  # 屏幕可用区域
        self.top_window = None
    def start_walk(self):
        """对外暴露的触发函数：启动/重置随机行走"""
        # 1. 获取最新屏幕可用区域
        self.screen_rect = WindowStatic.get_current_screen_available_rect()
        self.top_window = WindowStatic.get_top_window()
        if not self.screen_rect.isValid():
            print("获取屏幕区域失败！")
            return
        if not self.walk_timer.isActive():
            self.walk_timer.start()
        else:
            self.walk_timer.stop()
        print("开始随机行走...")

    def _update_walk_position(self):
        """定时更新位置：实现随机行走核心逻辑"""
        # 1. 随机重置移动参数（每帧有10%概率换速度/方向/暂停）
        if random.random() < 0.1:
            self._randomize_move_params()

        # 2. 计算新位置
        current_pos = self.top_window.position()
        new_x = current_pos.x() + self.current_speed_x
        new_y = current_pos.y() + self.current_speed_y

        # 3. 边界检测与反弹（避免超出屏幕可用区域）
        # x轴边界：左边界/右边界（减去窗口宽度）
        if new_x < self.screen_rect.left():
            new_x = self.screen_rect.left()
            self.current_speed_x = abs(self.current_speed_x)  # 反弹：x轴反向
        elif new_x > self.screen_rect.right() - self.top_window.width():
            new_x = self.screen_rect.right() - self.top_window.width()
            self.current_speed_x = -abs(self.current_speed_x)

        # y轴边界：上边界/下边界（减去窗口高度）
        if new_y < self.screen_rect.top():
            new_y = self.screen_rect.top()
            self.current_speed_y = abs(self.current_speed_y)  # 反弹：y轴反向
        elif new_y > self.screen_rect.bottom() - self.top_window.height():
            new_y = self.screen_rect.bottom() - self.top_window.height()
            self.current_speed_y = -abs(self.current_speed_y)

        # 4. 更新窗口位置
        self.top_window.setGeometry(new_x, new_y, self.top_window.width(), self.top_window.height())

    def _randomize_move_params(self):
        """随机生成移动参数：速度/方向/是否暂停"""
        # 1. 随机是否暂停（20%概率暂停）
        if random.random() < 0.2:
            self.current_speed_x = 0
            self.current_speed_y = 0
            return

        # 2. 随机速度（1~8像素/帧，模拟“或快或慢”）
        speed = random.randint(1, 8)

        # 3. 随机方向（x/y轴正负，模拟“方向不定”）
        dir_x = random.choice([-1, 1])  # 左/右
        dir_y = random.choice([-1, 1])  # 上/下

        # 4. 随机偏航（x/y轴速度比例，避免匀速直线）
        ratio = random.uniform(0.3, 1.0)
        self.current_speed_x = dir_x * speed * ratio
        self.current_speed_y = dir_y * speed * (1 - ratio)