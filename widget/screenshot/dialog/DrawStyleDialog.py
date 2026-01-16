import sys

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QComboBox, QSlider,
                               QSpinBox, QColorDialog, QApplication)  # QColorButton需注意：部分环境需手动实现
from PySide6.QtGui import QPen, QColor, QMouseEvent, QPixmap, QPainter, QBrush
from PySide6.QtCore import Qt, Signal, QPoint

from widget.util import WindowStatic


class QColorButton(QPushButton):
    color_changed = Signal(QColor)

    def __init__(self, color: QColor, parent=None):
        super().__init__(parent)
        self.current_color = QColor(color)
        self.setText("")
        self.setObjectName("color-btn")
        self.setFixedSize(30, 30)
        self.update_style()
        self.clicked.connect(self.choose_color)

    def update_style(self):
        self.setStyleSheet(
            '#color-btn' + '{background-color: ' + WindowStatic.get_color(self.current_color) + '; border: 1px solid #ccc;}')

    def choose_color(self):
        color_dialog = QColorDialog(self.current_color, self)
        # 关键：启用Alpha通道显示
        color_dialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        # 3. 弹出对话框并判断是否确认选择
        if color_dialog.exec():
            # 4. 获取选中的带Alpha值的颜色
            color = color_dialog.selectedColor()
            if color.isValid():
                if color.alpha() == 0:
                    color = QColor(Qt.GlobalColor.transparent)
                self.current_color = color
                self.update_style()
                self.color_changed.emit(color)

    def get_color(self):
        return self.current_color


# 自定义一站式画笔样式选择窗口
class DrawStyleDialog(QDialog):
    # 定义信号，返回选中的画笔
    pen_confirmed = Signal(QPen, QBrush)
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

    def __init__(self, initial_pen: QPen = QPen(), initial_brush=QBrush(), parent=None):
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
            /* 通用按钮样式 */
            QPushButton {
                border: none;
                border-radius: none;
                font-family: "Microsoft YaHei";
                font-size: 14px;
                color: white;
                background-color: #5093e1;
                padding: 4px 8px;
            }
            QPushButton:hover {
                background-color: #62a1f0;
            }
            QPushButton:pressed {
                background-color: #3a7bc8;
                padding-left: 9px;
                padding-top: 5px;
            }
            /* 最小化按钮特殊样式 */
            #min_window_btn {
                background-color: transparent;
                color:#ffff00;
                font-weight: bold;
                border-radius: 0;
            }
            #min_window_btn:hover {
                background-color: #a70000;
                color:#ffffff;
            }
            QComboBox{
                background-color:white;
            }
            /* 下拉框/SpinBox样式 */
            QSpinBox, QComboBox {
                border: 2px solid #d0e1f9;
                border-radius: 6px;
                padding: 4px 8px;
                font-family: "Microsoft YaHei";
                font-size: 14px;
                background-color: white;
                color:black;
            }
            QSpinBox:focus, QComboBox:focus {
                border-color: #66bfff;
                outline: none;
            }
            QComboBox QAbstractItemView {
                color: #3366FF;
                background-color: #F5F5F5;
                selection-background-color: #FFC107;
            }
            QComboBox QAbstractItemView::item {
                color: black;
                height: 25px;
            }
            QComboBox QAbstractItemView::item:selected {
                color: #3366FF;
            }

            /* 复选框样式 */
            QCheckBox {
                font-family: "Microsoft YaHei";
                font-size: 14px;
                color: white;
                spacing: 8px;
            }
            QCheckBox::indicator {
                border-radius: 4px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                background-color: #5093e1;
            }
            QCheckBox::indicator:hover {
                border: 2px solid #66bfff;
            }
            """
        )
        self.setFixedWidth(350)
        self.current_pen = initial_pen  # 初始画笔样式
        self.current_brush = initial_brush
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
        self.width_slider.setRange(1, 100)
        self.width_slider.setValue(self.current_pen.width())
        self.width_spin = QSpinBox()
        self.width_spin.setRange(1, 100)
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
        self.style_combo.addItem("实线", Qt.PenStyle.SolidLine)
        self.style_combo.addItem("虚线", Qt.PenStyle.DashDotLine)  # 修正：原DashLine，按你示例格式逐行写
        self.style_combo.addItem("点线", Qt.PenStyle.DotLine)
        self.style_combo.addItem("点划线", Qt.PenStyle.DashDotLine)
        self.style_combo.addItem("双点划线", Qt.PenStyle.DashDotDotLine)

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

        # 4. 端点/拐角样式（可选，增强功能）
        join_layout = QHBoxLayout()
        join_layout.addWidget(QLabel("连接样式："))
        self.join_combo = QComboBox()
        self.join_combo.setFixedHeight(30)
        self.join_combo.addItem("尖角", Qt.PenJoinStyle.MiterJoin)
        self.join_combo.addItem("斜角", Qt.PenJoinStyle.BevelJoin)
        self.join_combo.addItem("圆角", Qt.PenJoinStyle.RoundJoin)
        # 选中当前端点样式
        current_join = self.current_pen.joinStyle()
        for i in range(self.cap_combo.count()):
            if self.join_combo.itemData(i) == current_join:
                self.join_combo.setCurrentIndex(i)
                break
        join_layout.addWidget(self.join_combo)
        layout.addLayout(join_layout)

        # 1. 填充颜色选择
        brush_color_layout = QHBoxLayout()
        brush_color_layout.addWidget(QLabel("填充颜色："))
        self.brush_color_btn = QColorButton(self.current_brush.color())
        brush_color_layout.addWidget(self.brush_color_btn)
        layout.addLayout(brush_color_layout)

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

    def on_ok(self):
        # 组装选中的画笔样式
        pen = QPen()
        pen.setColor(self.color_btn.get_color())
        pen.setWidth(self.width_slider.value())
        pen.setStyle(self.style_combo.currentData())
        pen.setCapStyle(self.cap_combo.currentData())
        pen.setJoinStyle(self.join_combo.currentData())  # 固定拐角样式，也可添加ComboBox选择
        brush = QBrush(self.brush_color_btn.get_color())
        # 发送信号
        self.pen_confirmed.emit(pen, brush)
        self.accept()  # 关闭对话框
