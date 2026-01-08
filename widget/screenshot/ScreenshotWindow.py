from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class ScreenshotWindow(QWidget):
    screenshot_canceled = Signal()
    screenshot_selected_area = Signal(QRect)

    def __init__(self, parent=None):
        super().__init__(parent)
        # 窗口属性（核心：保留无边框+置顶，透明属性必须加）
        self.capture_rect = QRect()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setCursor(Qt.CursorShape.CrossCursor)

        # 屏幕信息（主屏幕优先，避免多屏坐标混乱）
        self.main_screen = QApplication.primaryScreen()
        self.screen_geo = self.main_screen.geometry()
        self.setGeometry(self.screen_geo)  # 仅覆盖主屏幕（多屏可扩展）

        # 截图区域变量
        self.is_dragging = False  # 拖拽选取框整体
        self.is_resizing = False  # 拉伸选取框边角/边框
        self.start_pos = QPoint()
        self.end_pos = QPoint()
        self.resize_direction = None

        # 遮罩参数（可自定义）
        self.mask_color = QColor(0, 0, 0, 128)  # 遮罩颜色：黑色+50%不透明度
        self.select_border_color = QColor(255, 0, 0)  # 选取框边框红色
        self.select_fill_color = QColor(0, 0, 255, 50)  # 选取区域填充色
        self.corner_radius = 10  # 角标圆的半径，可根据需要调整
        # 偏移圆

        self.event_count = 0

        # 初始化按钮（独立窗口，避免被遮罩覆盖）
        self._init_buttons()

    def _init_buttons(self):
        """创建独立的按钮窗口（悬浮在截图窗口上）"""
        # 按钮窗口：无边框+置顶+透明背景
        self.btn_window = QWidget(self, Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.btn_window.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.btn_window.setFixedSize(300, 60)  # 固定按钮窗口大小
        # 按钮窗口位置：主屏幕底部居中
        btn_x = (self.screen_geo.width() - self.btn_window.width()) // 2
        btn_y = self.screen_geo.height() - 80  # 距离底部20px
        self.btn_window.setGeometry(btn_x, btn_y, self.btn_window.width(), self.btn_window.height())

        # 按钮布局
        btn_layout = QHBoxLayout(self.btn_window)
        btn_layout.setSpacing(10)
        btn_layout.setContentsMargins(0, 0, 0, 0)
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 确认按钮
        self.confirm_btn = QPushButton("确认")
        self.confirm_btn.setFixedSize(50, 30)
        self.confirm_btn.clicked.connect(self.capture_screenshot)
        self.confirm_btn.setStyleSheet("""
            QPushButton {
                background-color: #409EFF;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #66b1ff;
            }
            QPushButton:pressed {
                background-color: #337ecc;
            }
        """)
        btn_layout.addWidget(self.confirm_btn)

        # 取消按钮
        self.cancel_btn = QPushButton("取消")
        self.cancel_btn.setFixedSize(50, 30)
        self.cancel_btn.clicked.connect(self.on_cancel)
        self.cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #F56C6C;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #F78989;
            }
            QPushButton:pressed {
                background-color: #e45656;
            }
        """)
        btn_layout.addWidget(self.cancel_btn)

        # 显示按钮窗口
        self.btn_window.show()

    def is_point_range(self, pointTarget, pointSource, offset=25):
        return pointSource.x() - offset <= pointTarget.x() <= pointSource.x() + offset and pointSource.y() - offset <= pointTarget.y() <= pointSource.y() + offset

    def get_resize_direction(self, pos):
        """
        检测鼠标位置对应的拉伸方向
        返回值：tl(左上)/tr(右上)/bl(左下)/br(右下)/left/right/top/bottom/None
        """
        if self.is_point_range(pos, self.start_pos):
            return "tl"
        elif self.is_point_range(pos, QPoint(self.start_pos.x(), self.end_pos.y())):
            return "bl"
        elif self.is_point_range(pos, QPoint(self.end_pos.x(), self.start_pos.y())):
            return "tr"
        elif self.is_point_range(pos, self.end_pos):
            return "br"
        return None

    def mousePressEvent(self, event):
        # 核心：点击按钮区域时，不触发拖拽
        if event.button() == Qt.MouseButton.LeftButton and not self.btn_window.underMouse():
            self.resize_direction = self.get_resize_direction(event.globalPosition().toPoint())
            if self.resize_direction:
                self.is_resizing = True
                self.is_dragging = False
            elif not self.is_dragging and not self.is_resizing:
                self.is_dragging = True
                self.is_resizing = False
                self.start_pos = event.globalPosition().toPoint()
                self.end_pos = self.start_pos

    def mouseMoveEvent(self, event):
        if self.is_dragging:
            self.end_pos = event.globalPosition().toPoint()
        elif self.is_resizing:
            current_pos = event.globalPosition().toPoint()
            if self.resize_direction == "tl":
                self.start_pos = current_pos
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif self.resize_direction == "tr":
                self.end_pos = QPoint(current_pos.x(), self.end_pos.y())
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif self.resize_direction == "bl":
                self.start_pos = QPoint(current_pos.x(), self.start_pos.y())
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif self.resize_direction == "br":
                self.end_pos = current_pos
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
        self.update()  # 实时重绘选取框
        self.event_count += 1
        # 不调用父类，避免事件干扰

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.is_dragging = False
            self.is_resizing = True
        if self.event_count == 0 and event.button() == Qt.MouseButton.RightButton:
            self.click()
        else:
            self.event_count = 0
        self.setCursor(Qt.CursorShape.CrossCursor)
        # 不调用父类，避免事件穿透

    def click(self):
        self.reset_status(False)

    def paintEvent(self, event):
        """手动绘制半透明遮罩、选取框，并在四角添加圆形标记（核心完善版）"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿，让图形更平滑

        # 1. 绘制全屏半透明遮罩（黑色+50%不透明度）
        painter.fillRect(self.screen_geo, self.mask_color)

        # 2. 绘制选取区域（擦除遮罩，显示原始屏幕）
        if self.is_dragging or self.is_resizing:
            # 获取规范化的选取矩形（确保左上角为起点，宽高为正）
            current_rect = QRect(self.start_pos, self.end_pos).normalized()
            # 忽略过小的选取框（避免角标绘制异常）

            # ========== 擦除选取区域的遮罩，显示原始屏幕 ==========
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_Clear)
            painter.fillRect(current_rect, Qt.GlobalColor.transparent)
            # ========== 恢复组合模式，绘制选取框和四角圆形 ==========
            painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceOver)
            # 绘制选取框边框
            painter.setPen(QPen(self.select_border_color, 1, Qt.PenStyle.DotLine))  # 加粗边框更醒目
            painter.setBrush(Qt.BrushStyle.NoBrush)  # 无填充，仅绘制边框
            painter.drawRect(current_rect)

            # ========== 绘制四角圆形标记 ==========

            offset = int(self.corner_radius / 2)
            corners = [
                current_rect.topLeft() + QPoint(-offset, -offset),
                # 左上角
                current_rect.topRight() + QPoint(-offset, -offset),
                current_rect.bottomLeft() + QPoint(-offset, -offset),  # 左下角
                current_rect.bottomRight() + QPoint(-offset, -offset)  # 右下角
            ]
            # 设置角标样式：红色填充+白色边框
            painter.setPen(QPen(Qt.GlobalColor.white, 1, Qt.PenStyle.SolidLine))  # 白色边框
            painter.setBrush(QBrush(self.select_border_color))  # 红色填充（与选取框同色）

            # 绘制四个角的圆形
            for corner_pos in corners:
                painter.drawRect(
                    QRect(
                        corner_pos.x(),
                        corner_pos.y(),
                        self.corner_radius,
                        self.corner_radius
                    )
                )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Enter or event.key() == Qt.Key.Key_Return:
            self.capture_screenshot()
        elif event.key() == Qt.Key.Key_Escape:
            self.hide()

    def on_cancel(self):
        """取消截图，关闭所有窗口"""
        self.reset_status()
        self.screenshot_canceled.emit()

    def reset_status(self, is_hide=True):
        self.start_pos = QPoint()
        self.end_pos = QPoint()
        self.is_dragging = False
        self.is_resizing = False
        self.update()
        if is_hide and not self.isHidden():
            self.hide()

    def capture_screenshot(self):
        """执行截图"""
        # 确定截图区域
        if self.start_pos == self.end_pos:
            # 全屏截图
            self.capture_rect = self.screen_geo
        else:
            # 区域截图
            self.capture_rect = QRect(self.start_pos + QPoint(1, 1), self.end_pos + QPoint(-1, -1)).normalized()
        self.reset_status()
        if not self.capture_rect.isNull():
            self.screenshot_selected_area.emit(self.capture_rect)
