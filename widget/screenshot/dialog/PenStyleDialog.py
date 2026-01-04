from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QComboBox, QSlider,
                               QSpinBox,  QColorDialog)  # QColorButton需注意：部分环境需手动实现
from PySide6.QtGui import QPen, QColor, QMouseEvent, QPixmap, QPainter, QBrush
from PySide6.QtCore import Qt, Signal, QPoint


class QColorButton(QPushButton):
    color_changed = Signal(QColor)
    def __init__(self, color:QColor, parent=None):
        super().__init__(parent)
        self.current_color = QColor(color)
        self.setText("")
        self.setObjectName("color-btn")
        self.setFixedSize(30, 30)
        self.update_style()
        self.clicked.connect(self.choose_color)

    def update_style(self):
        self.setStyleSheet('#color-btn'+'{background-color: '+self.current_color.name()+'; border: 1px solid #ccc;}"')

    def choose_color(self):
        color = QColorDialog.getColor(self.current_color, self, "选择颜色")
        if color.isValid():
            self.current_color = color
            self.update_style()
            self.color_changed.emit(color)
    def get_color(self):
        return self.current_color

# 自定义一站式画笔样式选择窗口
class PenStyleDialog(QDialog):
    # 定义信号，返回选中的画笔
    pen_confirmed = Signal(QPen)
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
            # 拖拽过程中实时触发吸附（可选：也可在释放时触发）
            event.accept()

    # ========== 重写鼠标释放事件 ==========
    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_state["is_moving"] = False
            # 释放时再次触发吸附（确保最终位置贴边）
            event.accept()
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿，让文字更平滑
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        if not self.bg_pixmap.isNull():
            painter.setOpacity(0.8)  # 图片透明度（0-1，0全透，1不透明）
            painter.drawPixmap(self.rect(), self.bg_pixmap)
        else:
            # 图片加载失败时，降级绘制原粉色半透明矩形
            painter.setBrush(QBrush(QColor(255, 192, 203, 180)))
            painter.drawRect(self.rect())

    def __init__(self, initial_pen: QPen, parent=None):
        super().__init__(parent)
        self.bg_pixmap = QPixmap()
        # 替换为你的图片路径（绝对路径/相对路径均可，支持png/jpg等格式）
        img_path = "image/bg/pen_style_dialog"  # 示例：同目录下的background.png
        if self.bg_pixmap.load(img_path):
            # 可选：预处理图片（如缩放/透明化）
            self.bg_pixmap = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,  # 保持比例并覆盖控件
                Qt.TransformationMode.SmoothTransformation  # 平滑缩放，抗锯齿
            )
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setObjectName("penStyleDialog")
        self.setStyleSheet(
            """
            QComboBox{
                background-color:white;
            }
            /* 下拉框/SpinBox样式 */
            QFontComboBox, QSpinBox {
                border: 2px solid #d0e1f9;
                border-radius: 6px;
                padding: 4px 8px;
                font-family: "Microsoft YaHei";
                font-size: 14px;
                background-color: white;
                color:black;
            }
            QFontComboBox:focus, QSpinBox:focus {
                border-color: #66bfff;
                outline: none;
            }
            QComboBox{
               color:black;
            }
            """
        )
        self.setFixedWidth(350)
        self.current_pen = initial_pen  # 初始画笔样式
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 0, 0, 0)

        top_window_bar = QHBoxLayout()
        top_window_bar.setSpacing(10)
        top_window_bar.setContentsMargins(0, 0, 0, 0)
        top_window_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.min_window_btn = QPushButton("一")
        self.min_window_btn.setObjectName("min_window_btn")
        self.min_window_btn.setFixedSize(25, 25)
        self.min_window_btn.clicked.connect(self.hide)
        top_window_bar.addStretch()
        top_window_bar.addWidget(self.min_window_btn)

        main_layout.addLayout(top_window_bar)

        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        main_layout.addLayout(layout)

        # 1. 颜色选择
        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("画笔颜色："))
        self.color_btn = QColorButton(self.current_pen.color())
        color_layout.addWidget(self.color_btn)
        layout.addLayout(color_layout)

        # 2. 宽度选择（滑块+数字输入框联动）
        width_layout = QHBoxLayout()
        width_layout.addWidget(QLabel("画笔宽度："))
        self.width_slider = QSlider(Qt.Orientation.Horizontal)
        self.width_slider.setRange(1, 20)
        self.width_slider.setValue(self.current_pen.width())
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 20)
        self.width_spin.setValue(self.current_pen.width())
        self.width_spin.setFixedHeight(30)
        # 联动滑块和输入框
        self.width_slider.valueChanged.connect(self.width_spin.setValue)
        self.width_spin.valueChanged.connect(self.width_slider.setValue)
        width_layout.addWidget(self.width_slider)
        width_layout.addWidget(self.width_spin)
        layout.addLayout(width_layout)

        # 3. 线条样式选择
        style_layout = QHBoxLayout()
        style_layout.addWidget(QLabel("线条样式："))
        self.style_combo = QComboBox()
        self.style_combo.setFixedHeight(30)
        self.init_style_combo()
        # 选中当前画笔样式
        current_style = self.current_pen.style()
        for i in range(self.style_combo.count()):
            if self.style_combo.itemData(i) == current_style:
                self.style_combo.setCurrentIndex(i)
                break
        style_layout.addWidget(self.style_combo)
        layout.addLayout(style_layout)

        # 4. 端点/拐角样式（可选，增强功能）
        cap_layout = QHBoxLayout()
        cap_layout.addWidget(QLabel("端点样式："))
        self.cap_combo = QComboBox()
        self.cap_combo.setFixedHeight(30)
        self.cap_combo.addItem("圆角", Qt.PenCapStyle.RoundCap)
        self.cap_combo.addItem("方形", Qt.PenCapStyle.SquareCap)
        self.cap_combo.addItem("平角", Qt.PenCapStyle.FlatCap)
        # 选中当前端点样式
        current_cap = self.current_pen.capStyle()
        for i in range(self.cap_combo.count()):
            if self.cap_combo.itemData(i) == current_cap:
                self.cap_combo.setCurrentIndex(i)
                break
        cap_layout.addWidget(self.cap_combo)
        layout.addLayout(cap_layout)

        # 5. 确认/取消按钮
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确认")
        self.cancel_btn = QPushButton("取消")
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(main_layout)

        # 绑定事件
        self.ok_btn.clicked.connect(self.on_ok)
        self.cancel_btn.clicked.connect(self.reject)

    def init_style_combo(self):
        pen_styles = [
            ("实线", Qt.PenStyle.SolidLine),
            ("虚线", Qt.PenStyle.DashLine),
            ("点线", Qt.PenStyle.DotLine),
            ("点划线", Qt.PenStyle.DashDotLine),
            ("双点划线", Qt.PenStyle.DashDotDotLine)
        ]
        for name, style in pen_styles:
            self.style_combo.addItem(name, style)

    def on_ok(self):
        # 组装选中的画笔样式
        pen = QPen()
        pen.setColor(self.color_btn.get_color())
        pen.setWidth(self.width_slider.value())
        pen.setStyle(self.style_combo.currentData())
        pen.setCapStyle(self.cap_combo.currentData())
        pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)  # 固定拐角样式，也可添加ComboBox选择
        # 发送信号
        self.pen_confirmed.emit(pen)
        self.accept()  # 关闭对话框