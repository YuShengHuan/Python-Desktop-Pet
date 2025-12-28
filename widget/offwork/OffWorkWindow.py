from datetime import datetime, time

from PySide6.QtCore import QPoint, Qt, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtGui import QMouseEvent, QPainter, QLinearGradient, QBrush, QPen, QFont, QColor, QPixmap
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton

from widget.util import WindowStatic


class OffWorkWindow(QWidget):
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
            event.accept()

    # ========== 重写鼠标释放事件 ==========
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_state["is_moving"] = False
            event.accept()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._move_animation = None

        self.bg_pixmap = QPixmap()
        # 替换为你的图片路径（绝对路径/相对路径均可，支持png/jpg等格式）
        img_path = "image/bg/off_word.png"  # 示例：同目录下的background.png
        if self.bg_pixmap.load(img_path):
            # 可选：预处理图片（如缩放/透明化）
            self.bg_pixmap = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,  # 保持比例并覆盖控件
                Qt.TransformationMode.SmoothTransformation  # 平滑缩放，抗锯齿
            )
        # 吸附阈值（可自定义，单位：像素）
        self.text = None
        self.target_time_array = None
        self.target_time = None
        self.attachThreshold = 35
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setObjectName("offWorkWindow")
        self.resize(115, 35)
        self.setStyleSheet('''
                            /* 主容器样式 */
                            #offWorkWindow {
                                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #66bfff, stop:1 #4a90e2);
                                border: 1px solid #e0e0e0;
                                border-radius: 8px;
                                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                            }
                            /* 最小化按钮特殊样式 */
                            #min_window_btn {
                                margin:0;
                                background-color: transparent;
                                color:transparent;
                                border-radius: 0;
                                font-size:10px;
                            }
                            #min_window_btn:hover {
                                background-color: #a70000;
                                color:#ffffff;
                            }
                        ''')
        # 主布局：工具栏容器 + 中间绘图区域
        self.main_layout = QHBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        self.main_layout.addStretch()
        self.timer = QTimer()
        self.timer.timeout.connect(self.timer_change_time_text)
        self.timer.start(1000)

        # ------ 窗口工具栏 ------
        self.top_window_bar = QVBoxLayout()
        self.top_window_bar.setSpacing(10)
        self.top_window_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.min_window_btn = QPushButton("一")
        self.min_window_btn.setObjectName("min_window_btn")
        self.min_window_btn.setFixedSize(20, 20)
        self.min_window_btn.clicked.connect(self.hide)
        self.top_window_bar.addWidget(self.min_window_btn)
        self.top_window_bar.addStretch()
        self.main_layout.addLayout(self.top_window_bar)

        self.timer_change_time_text()
        screen_rect = WindowStatic.get_current_screen_available_rect()
        self.move(int(screen_rect.width() / 2), 0)

        self.timer2 = QTimer()
        self.timer2.timeout.connect(self.auto_move_parent_near)
        self.timer2.start(500)

    def auto_move_parent_near(self):
        top_window = WindowStatic.get_top_window()
        if top_window:
            top_window_g = top_window.geometry()
            # 1. 计算目标位置（保留原有位置计算逻辑）
            target_x = top_window_g.x() + int(top_window_g.width() / 2) - int(self.width() / 2)
            target_y = top_window_g.y()
            target_pos = QPoint(target_x, target_y)
            # 2. 停止之前可能未完成的动画（避免动画冲突）
            if self._move_animation and hasattr(self, '_move_animation') and self._move_animation.state() == QPropertyAnimation.State.Running:
                self._move_animation.stop()

            # 3. 创建位置动画，实现平滑移动
            self._move_animation = QPropertyAnimation(self, b"pos")  # 绑定窗口的pos属性
            self._move_animation.setDuration(300)  # 动画时长（毫秒），可调整（如200/500）
            self._move_animation.setStartValue(self.pos())  # 动画起始位置：当前位置
            self._move_animation.setEndValue(target_pos)  # 动画结束位置：目标位置

            # 4. 设置缓动曲线（让移动更自然，可选但推荐）
            self._move_animation.setEasingCurve(QEasingCurve.Type.OutQuad)  # 先快后慢，贴近真实物理移动

            # 6. 启动动画
            self._move_animation.start()

    def is_in_time_range(self, range_time: tuple):
        current_time = datetime.now().time()
        return range_time[0] <= current_time <= range_time[1]

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿，让文字更平滑
        painter.setFont(QFont("微软雅黑", 12, QFont.Weight.Bold))

        painter.setPen(Qt.PenStyle.NoPen)  # 隐藏边框

        if not self.bg_pixmap.isNull():
            painter.setOpacity(0.8)  # 图片透明度（0-1，0全透，1不透明）
            painter.drawPixmap(self.rect(), self.bg_pixmap)
        else:
            # 图片加载失败时，降级绘制原粉色半透明矩形
            painter.setBrush(QBrush(QColor(255, 192, 203, 180)))
            painter.drawRect(self.rect())

        # 1. 创建线性渐变（水平渐变：从左到右）
        # 渐变范围：覆盖整个控件的文字区域
        gradient = QLinearGradient(0, 0, self.width(), 0)  # 起点(0,0) → 终点(控件宽度,0)（水平）
        # 渐变范围：垂直渐变（从上到下）→ QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0, Qt.GlobalColor.red)  # 渐变起始颜色（左/上）
        gradient.setColorAt(0.5, Qt.GlobalColor.yellow)  # 渐变中间颜色
        gradient.setColorAt(1, Qt.GlobalColor.white)  # 渐变结束颜色（右/下）

        # 2. 将渐变设置为画笔
        brush = QBrush(gradient)
        pen = QPen(brush, 0)  # 笔宽0，仅用画刷颜色
        painter.setPen(pen)

        # 3. 绘制文字（居中）
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text)

    def timer_change_time_text(self):
        self.target_time_array = [
            (time(9, 0, 0), time(12, 0, 0)),
            (time(14, 0, 0), time(18, 0, 0))
        ]
        for r_time in self.target_time_array:
            if self.is_in_time_range(r_time):
                self.target_time = r_time[1]
        now = datetime.now()
        if not self.target_time:
            self.text = f"{now.strftime('%H:%M:%S')}"
        else:
            # 构造今日18:00的datetime对象
            target_datetime = datetime.combine(now.date(), self.target_time)

            # 计算时间差（若已过目标时间，差值为0）
            diff = (target_datetime - now).total_seconds()
            diff = max(0, diff)  # 确保差值非负
            # 转换为小时、分钟、秒
            hours = int(diff // 3600)
            minutes = int((diff % 3600) // 60)
            seconds = int(diff % 60)
            # 格式化为HH:MM:SS（补零）
            time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self.text = f"{time_str}"
        self.update()
