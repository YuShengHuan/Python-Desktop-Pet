from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from widget.role.CentralWidget import CentralWidget
from widget.util import WindowStatic


class MainWindow(QMainWindow):
    drag_state = {
        "is_moving": False,  # 是否正在拖拽
        "drag_offset": QPoint(0, 0)  # 鼠标相对于窗口左上角的偏移量
    }

    # ========== 重写鼠标按下事件 ==========
    def mousePressEvent(self, event: QMouseEvent) -> None:
        # 仅处理左键按下
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_state["is_moving"] = True
            # 关键修改：记录鼠标相对于窗口左上角的偏移量（而非全局位置）
            self.drag_state["drag_offset"] = event.globalPosition().toPoint() - self.pos()
            event.accept()  # 拦截事件，避免穿透

    # ========== 重写鼠标移动事件 ==========
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        # 仅当左键按下且处于拖拽状态时执行
        if self.drag_state["is_moving"] and event.buttons() & Qt.MouseButton.LeftButton:
            # 计算新位置：鼠标全局位置 - 偏移量（精准跟随鼠标）
            new_pos = event.globalPosition().toPoint() - self.drag_state["drag_offset"]
            self.move(new_pos)
            self.attach_to_screen_edge()
            # 拖拽过程中实时触发吸附（可选：也可在释放时触发）
            event.accept()

    # ========== 重写鼠标释放事件 ==========
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_state["is_moving"] = False
            # 释放时再次触发吸附（确保最终位置贴边）
            self.attach_to_screen_edge(smooth=True)
            event.accept()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setObjectName("mainWindow")
        self.resize(100, 100)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        # 吸附阈值（可自定义，单位：像素）
        self.attachThreshold = 35

        screen_rect = WindowStatic.get_current_screen_available_rect()
        self.move(screen_rect.width()-200, int(screen_rect.height()*0.35))
        self.attach_to_screen_edge()
        # 设置中心窗口

        self.centralWidget = CentralWidget(self)
        self.centralWidget.setMaximumSize(self.width(), self.height())

        self.setCentralWidget(self.centralWidget)


    def attach_to_screen_edge(self, smooth: bool = False):
        """
        屏幕边缘吸附
        :param smooth: 是否启用平滑动画吸附
        """
        screen_rect = WindowStatic.get_current_screen_available_rect()
        pet_rect = self.geometry()
        new_pos = pet_rect.topLeft()  # 初始化为当前位置
        offset = 15
        # 左边缘吸附
        if pet_rect.left() - screen_rect.left() < self.attachThreshold:
            new_pos.setX(screen_rect.left() - offset)
        # 右边缘吸附（需减去窗口宽度）
        elif screen_rect.right() - pet_rect.right() < self.attachThreshold:
            new_pos.setX(screen_rect.right() - pet_rect.width() + offset)

        # 上边缘吸附
        if pet_rect.top() - screen_rect.top() < self.attachThreshold:
            new_pos.setY(screen_rect.top() - offset)
        # 下边缘吸附（需减去窗口高度）
        elif screen_rect.bottom() - pet_rect.bottom() < self.attachThreshold:
            new_pos.setY(screen_rect.bottom() - pet_rect.height() + offset)

        # 若位置有变化，执行移动/平滑动画
        if new_pos != pet_rect.topLeft():
            if smooth:
                self.smooth_attach_animation(new_pos)
            else:
                self.move(new_pos)

    def smooth_attach_animation(self, target_pos: QPoint):
        """平滑吸附动画（避免生硬跳转）"""
        animation = QPropertyAnimation(self, b"pos")
        animation.setDuration(100)  # 动画时长（毫秒）
        animation.setStartValue(self.pos())
        animation.setEndValue(target_pos)
        animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # 缓动曲线，更自然
        animation.start()  # 启动动画（结束后自动销毁）
