import math
import random
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from widget.util import WindowStatic


class ShapeFood(QWidget):
    clicked = Signal(int)
    drag_state = {
        "is_drag": False,  # 是否正在拖拽
        "drag_offset": QPoint(0, 0)  # 鼠标相对于窗口左上角的偏移量
    }

    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_state["is_drag"] = True
            self.drag_state["drag_offset"] = event.globalPosition().toPoint() - self.pos()
            event.accept()  # 拦截事件，避免穿透

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.drag_state["is_drag"] and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(
                event.globalPosition().toPoint() - self.drag_state["drag_offset"]
            )
            self.event_count += 1
            event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_state["is_drag"] = False
            if self.event_count == 0:
                self.click()
            elif self.event_count > 0:
                self.event_count = 0
            event.accept()

    def click(self):
        self.close()
        self.clicked.emit(self.food_id)

    def set_food_id(self, food_id):
        self.food_id = food_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.food_id = None
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setObjectName("shapeFood")
        self.resize(50, 50)

        # 显示爱心文本（可替换为图片/绘制爱心）
        self.label = QLabel("💖", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("SimHei", 15))
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.setLayout(layout)

        self.event_count = 0

        # 爱心轨迹核心参数
        self.theta = 0.0  # 角度（0~2π 覆盖完整爱心）
        self.theta_step = 0.02  # 角度步进（越小轨迹越平滑，0.02≈180步走完一圈）
        self.love_scale = 0  # 爱心轨迹缩放系数（适配屏幕）
        self.love_center = QPoint(0, 0)  # 爱心轨迹的中心坐标（屏幕可用区域中心）

        # 定时更新位置（控制移动速度）
        self.move_timer = QTimer(self)
        self.move_timer.setInterval(50)  # 20ms更新一次（50帧/秒，轨迹更丝滑）
        self.move_timer.timeout.connect(self.move_along_love_track)

    def start_move(self,ms):

        QTimer.singleShot(ms,
                          lambda:self.show())
        QTimer.singleShot(ms,
                          lambda: self.move_timer.start())

    def calc_love_coords(self, theta):
        """标准爱心函数：计算指定角度对应的坐标（无随机，精准轨迹）
        公式：x = 16sin³θ, y = -(13cosθ - 5cos2θ - 2cos3θ - cos4θ)
        注：y轴取负是因为Qt坐标系y轴向下，修正后爱心方向正确
        """
        sin_theta = math.sin(theta)
        cos_theta = math.cos(theta)

        x = 16 * (sin_theta ** 3)
        y = -(13 * cos_theta - 5 * math.cos(2 * theta) - 2 * math.cos(3 * theta) - math.cos(4 * theta))
        return QPointF(x, y)

    def adjust_love_scale(self):
        """计算适配屏幕的爱心缩放系数，确保完整轨迹在屏幕内"""
        screen_rect = WindowStatic.get_current_screen_available_rect()
        # 爱心函数的原生最大宽高（x∈[-16,16], y∈[-17,13]）
        love_native_width = 32  # 16 - (-16)
        love_native_height = 30  # 13 - (-17)

        # 缩放系数：取屏幕可用区域的 1/3（避免轨迹超出屏幕）
        scale_w = (screen_rect.width() // 3) / love_native_width
        scale_h = (screen_rect.height() // 3) / love_native_height
        self.love_scale = min(scale_w, scale_h)  # 等比例缩放

        # 爱心轨迹中心设为屏幕可用区域中心
        self.love_center = screen_rect.center()

    def move_along_love_track(self):

        self.check_in_top_window_range()

        """沿完整爱心轨迹环绕移动（核心逻辑）"""
        # 1. 每次更新前适配屏幕（支持屏幕分辨率变化/窗口移动）
        self.adjust_love_scale()

        # 2. 计算当前角度对应的爱心坐标
        love_point = self.calc_love_coords(self.theta)

        # 3. 缩放并偏移到屏幕中心（适配屏幕）
        target_x = self.love_center.x() + love_point.x() * self.love_scale
        target_y = self.love_center.y() + love_point.y() * self.love_scale

        # 4. 边界微调（确保控件完全在屏幕内）
        screen_rect = WindowStatic.get_current_screen_available_rect()
        target_x = max(screen_rect.left(), min(target_x, screen_rect.right() - self.width()))
        target_y = max(screen_rect.top(), min(target_y, screen_rect.bottom() - self.height()))

        # 5. 更新控件位置
        self.move(QPoint(int(target_x), int(target_y)))

        # 6. 角度步进（遍历完整爱心轨迹）
        self.theta += self.theta_step
        # 7. 角度重置（循环环绕）：0~2π 为完整爱心轨迹，重置后重新开始
        if self.theta > 2 * math.pi:
            self.theta = 0.0

    def check_in_top_window_range(self):
        top_w_g = WindowStatic.get_top_window().geometry().center()
        target_w_g=self.geometry().center()
        distance = math.dist(
            [target_w_g.x(), target_w_g.y()],
            [top_w_g.x(), top_w_g.y()]
        )
        if distance < 20 and not self.isHidden():
            self.click()

    def paintEvent(self, event):
        """可选：绘制半透明背景，让控件更美观"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.rotate(random.randint(-45, 45))
        # 半透明圆形背景
        painter.setBrush(QBrush(QColor(255, 192, 203, 180)))  # 粉色半透明
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())
