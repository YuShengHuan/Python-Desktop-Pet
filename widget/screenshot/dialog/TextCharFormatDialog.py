import sys

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                               QPushButton, QLabel, QComboBox, QSlider,
                               QSpinBox, QColorDialog, QFontComboBox, QCheckBox,
                               QApplication)  # QColorButton需注意：部分环境需手动实现
from PySide6.QtGui import QPen, QColor, QMouseEvent, QFont, QTextCharFormat, QPixmap, QPainter, QBrush
from PySide6.QtCore import Qt, Signal, QPoint



class TextCharFormatDialog(QDialog):
    # 定义信号，返回选中的画笔
    text_char_format_confirmed = Signal(QTextCharFormat)
    text_char_format_changed = Signal(QTextCharFormat)
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
    def __init__(self, initial_text_char_format: QTextCharFormat, parent=None):
        super().__init__(parent)
        self.bg_pixmap = QPixmap()
        # 替换为你的图片路径（绝对路径/相对路径均可，支持png/jpg等格式）
        img_path = "image/bg/text_char_format_dialog.png"  # 示例：同目录下的background.png
        if self.bg_pixmap.load(img_path):
            # 可选：预处理图片（如缩放/透明化）
            self.bg_pixmap = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,  # 保持比例并覆盖控件
                Qt.TransformationMode.SmoothTransformation  # 平滑缩放，抗锯齿
            )
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setObjectName("penStyleDialog")
        self.setFixedWidth(500)
        self.setStyleSheet(
            """
            QComboBox{
                background-color:white;
            }
            /* 颜色选择按钮样式 */

            #color_btn {
                background-color: #f8a5c2;
            }
            #color_btn:hover {
                background-color: #fbb8d0;
            }
            #color_btn:pressed {
                background-color: #e78ca8;
            }
            /* 背景色按钮样式 */
            #bg_color_btn {
                background-color: #c2f8a5;
            }
            #bg_color_btn:hover {
                background-color: #d0fbb8;
            }
            #bg_color_btn:pressed {
                background-color: #a8e78c;
            }
            QComboBox{
                color:black;
            }

            /* 输入框样式 */
            QLineEdit {
                border: 2px solid #d0e1f9;
                border-radius: 6px;
                padding: 4px 8px;
                font-family: "Microsoft YaHei";
                font-size: 14px;
                background-color: white;
                color:black;
                selection-background-color: #66bfff;
            }
            QLineEdit:focus {
                border-color: #66bfff;
                outline: none;
            }

            /* 下拉框/SpinBox样式 */
            QFontComboBox, QSpinBox, QComboBox {
                border: 2px solid #d0e1f9;
                border-radius: 6px;
                padding: 4px 8px;
                font-family: "Microsoft YaHei";
                font-size: 14px;
                background-color: white;
                color:black;
            }
            QFontComboBox:focus, QSpinBox:focus, QComboBox:focus {
                border-color: #66bfff;
                outline: none;
            }
            QFontComboBox QAbstractItemView {
                color: #3366FF;  /* 下拉列表文字颜色（蓝色） */
                background-color: #F5F5F5; /* 下拉列表背景色 */
                selection-background-color: #FFC107; /* 选中项背景色 */
            }

            /* 3. 设置下拉列表项的文字颜色（细化：未选中/选中） */
            QFontComboBox QAbstractItemView::item {
                color: #3366FF;  /* 未选中项文字颜色 */
                height: 25px;    /* 可选：调整列表项高度 */
            }

            /* 选中项的文字颜色（避免被背景色覆盖） */
            QFontComboBox QAbstractItemView::item:selected {
                color: #FFFFFF;  /* 选中项文字为白色 */
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

            /* 颜色预览标签样式 */
            #color_preview {
                border-radius: 12px;
                border: 3px solid white;
                box-shadow: 0 0 4px rgba(0,0,0,0.2);
            }
            """
        )
        self.char_format = initial_text_char_format
        # ========== 新增：补充缺失属性的初始值 ==========
        self.current_style = {
            "font_size": initial_text_char_format.font().pointSize(),
            "font_family": QFont(initial_text_char_format.font().family()),
            "font_bold": initial_text_char_format.font().bold(),
            "font_italic": initial_text_char_format.font().italic(),
            "underline_style": initial_text_char_format.underlineStyle(),  # 下划线样式
            "underline_color": initial_text_char_format.underlineColor(),  # 下划线颜色
            "font_strikeout": initial_text_char_format.fontStrikeOut(),        # 删除线
            "font_overline": initial_text_char_format.fontOverline(),          # 上划线
            "font_color": initial_text_char_format.foreground().color(),
            "bg_color": initial_text_char_format.background().color(),     # 文字背景色
            "vertical_align": initial_text_char_format.verticalAlignment(),# 上下标
            "letter_spacing": initial_text_char_format.fontLetterSpacing(), # 字符间距
            "font_capitalization": initial_text_char_format.font().capitalization() # 大写样式
        }

        self.init_ui()

    def init_ui(self):
        main_layout=QVBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(0, 0, 0,0)

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

        # 1. 字号选择（原有不变）
        font_size_layout = QHBoxLayout()
        font_size_layout.addWidget(QLabel("文字字号："))
        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 72)
        self.font_size_spin.setValue(self.current_style["font_size"])
        self.font_size_spin.setFixedSize(100, 30)
        font_size_layout.addWidget(self.font_size_spin)
        layout.addLayout(font_size_layout)

        # 2. 字体样式选择（原有不变）
        font_family_layout = QHBoxLayout()
        font_family_layout.addWidget(QLabel("文字字体："))
        self.font_family = QFontComboBox()
        self.font_family.setFixedSize(200, 32)
        self.font_family.setCurrentFont(self.current_style["font_family"])
        font_family_layout.addWidget(self.font_family)
        layout.addLayout(font_family_layout)

        # 3. 文字修饰（原有：加粗/斜体/下划线 → 新增：删除线/上划线）
        b_i_u_layout = QHBoxLayout()
        b_i_u_layout.addWidget(QLabel("文字修饰："))
        self.bold_btn = QCheckBox("加粗")
        self.bold_btn.setChecked(self.current_style["font_bold"])
        self.bold_btn.setFixedSize(70, 30)
        self.bold_btn.setObjectName("bold_btn")
        b_i_u_layout.addWidget(self.bold_btn)

        self.italic_btn = QCheckBox("斜体")
        self.italic_btn.setChecked(self.current_style["font_italic"])
        self.italic_btn.setFixedSize(70, 30)
        self.italic_btn.setObjectName("italic_btn")
        b_i_u_layout.addWidget(self.italic_btn)


        # ========== 新增：删除线、上划线复选框 ==========
        self.strikeout_btn = QCheckBox("删除线")
        self.strikeout_btn.setChecked(self.current_style["font_strikeout"])
        self.strikeout_btn.setFixedSize(70, 30)
        self.strikeout_btn.setObjectName("strikeout_btn")
        b_i_u_layout.addWidget(self.strikeout_btn)

        self.overline_btn = QCheckBox("上划线")
        self.overline_btn.setChecked(self.current_style["font_overline"])
        self.overline_btn.setFixedSize(70, 30)
        self.overline_btn.setObjectName("overline_btn")
        b_i_u_layout.addWidget(self.overline_btn)

        layout.addLayout(b_i_u_layout)

        # ========== 新增：下划线样式选择 ==========
        underline_style_layout = QHBoxLayout()
        underline_style_layout.addWidget(QLabel("下划线样式："))
        self.underline_style_combo = QComboBox()
        self.underline_style_combo.addItems(["无下划线","单下划线", "双下划线","段下划线" ,"点划线"])
        # 映射初始值
        style_map = {
            QTextCharFormat.UnderlineStyle.NoUnderline: 0,
            QTextCharFormat.UnderlineStyle.SingleUnderline: 1,
            QTextCharFormat.UnderlineStyle.SpellCheckUnderline: 2,
            QTextCharFormat.UnderlineStyle.DashUnderline: 3,
            QTextCharFormat.UnderlineStyle.DotLine: 4
        }
        self.underline_style_combo.setCurrentIndex(style_map[self.current_style["underline_style"]])
        self.underline_style_combo.setFixedSize(200, 30)
        underline_style_layout.addWidget(self.underline_style_combo)
        layout.addLayout(underline_style_layout)

        # 4. 文字颜色选择（原有不变）
        all_color_layout_contain=QHBoxLayout()
        all_color_layout_contain.setSpacing(10)
        all_color_layout_contain.addWidget(QLabel("颜色："))


        all_color_layout = QHBoxLayout()
        # ========== 新增：划线颜色选择 ==========
        underline_color_layout = QHBoxLayout()
        underline_color_layout.addWidget(QLabel("划线颜色"))
        self.underline_color_btn = QPushButton("")
        self.underline_color_btn.setFixedSize(50, 30)
        self.underline_color_btn.setObjectName("color_btn")
        self.underline_color_btn.setStyleSheet(
            f"background-color: {self.current_style['underline_color'].name()}; border: 1px solid #ccc;")
        underline_color_layout.addWidget(self.underline_color_btn)
        all_color_layout.addLayout(underline_color_layout)


        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("文字颜色"))
        self.color_btn = QPushButton("")
        self.color_btn.setFixedSize(50, 30)
        self.color_btn.setObjectName("color_btn")
        self.color_btn.setStyleSheet(
            f"background-color: {self.current_style['font_color'].name()}; border: 1px solid #ccc;")
        color_layout.addWidget(self.color_btn)
        all_color_layout.addLayout(color_layout)

        # ========== 新增：文字背景色选择 ==========
        bg_color_layout = QHBoxLayout()
        bg_color_layout.addWidget(QLabel("背景颜色"))
        self.bg_color_btn = QPushButton("")
        self.bg_color_btn.setFixedSize(50, 30)
        self.bg_color_btn.setObjectName("bg_color_btn")
        self.bg_color_btn.setStyleSheet(
            f"background-color: {self.current_style['bg_color'].name()}; border: 1px solid #ccc;")
        bg_color_layout.addWidget(self.bg_color_btn)
        all_color_layout.addLayout(bg_color_layout)

        all_color_layout_contain.addLayout(all_color_layout)

        layout.addLayout(all_color_layout_contain)

        # ========== 新增：上下标选择 ==========
        vertical_align_layout = QHBoxLayout()
        vertical_align_layout.addWidget(QLabel("文字对标："))
        self.vertical_align_combo = QComboBox()
        self.vertical_align_combo.addItems(["正常", "上标", "下标"])
        # 映射初始值
        align_map = {
            QTextCharFormat.VerticalAlignment.AlignNormal: 0,
            QTextCharFormat.VerticalAlignment.AlignSuperScript: 1,
            QTextCharFormat.VerticalAlignment.AlignSubScript: 2
        }
        self.vertical_align_combo.setCurrentIndex(align_map[self.current_style["vertical_align"]])
        self.vertical_align_combo.setFixedSize(200, 30)
        vertical_align_layout.addWidget(self.vertical_align_combo)
        layout.addLayout(vertical_align_layout)

        # 5. 确认/取消按钮（原有不变）
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("确认")
        self.cancel_btn = QPushButton("取消")
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(main_layout)
        self._bind_style_events()

        # 绑定事件（原有不变）
        self.ok_btn.clicked.connect(self.on_ok)
        self.cancel_btn.clicked.connect(self.reject)

    def _bind_style_events(self):
        """核心函数：绑定所有属性控件的事件，同步更新text_style"""
        # 原有事件绑定（不变）
        self.font_size_spin.valueChanged.connect(self._update_font_size)
        self.font_family.currentFontChanged.connect(self._update_font_family)
        self.bold_btn.toggled.connect(self._update_font_bold)
        self.italic_btn.toggled.connect(self._update_font_italic)
        self.color_btn.clicked.connect(self.choose_color)

        # ========== 新增：绑定新属性的事件 ==========
        self.strikeout_btn.toggled.connect(self._update_font_strikeout)
        self.overline_btn.toggled.connect(self._update_font_overline)
        self.underline_style_combo.currentIndexChanged.connect(self._update_underline_style)
        self.underline_color_btn.clicked.connect(self.choose_underline_color)
        self.bg_color_btn.clicked.connect(self.choose_bg_color)
        self.vertical_align_combo.currentIndexChanged.connect(self._update_vertical_align)

    def __update_text(self):
        self.update_selected_text_style()

    # 原有事件处理函数（不变）
    def _update_font_size(self, new_size):
        self.current_style["font_size"] = new_size
        self.update_selected_text_style()

    def _update_font_family(self, new_font):
        self.current_style["font_family"] = new_font
        self.update_selected_text_style()

    def _update_font_bold(self, is_bold):
        self.current_style["font_bold"] = is_bold
        self.update_selected_text_style()

    def _update_font_italic(self, is_italic):
        self.current_style["font_italic"] = is_italic
        self.update_selected_text_style()

    def choose_color(self):
        color = QColorDialog.getColor(self.current_style["font_color"], self, "选择文字颜色")
        if color.isValid():
            self.current_style["font_color"] = color
        else:
            self.current_style["bg_color"]=QColor(Qt.GlobalColor.transparent)
        self.update_selected_text_style()
        self.color_btn.setStyleSheet(
            f"background-color: {self.current_style['font_color'].name()}; border: 1px solid #ccc;")

    # ========== 新增：新属性的事件处理函数 ==========
    def _update_font_strikeout(self, is_strikeout):
        self.current_style["font_strikeout"] = is_strikeout
        self.update_selected_text_style()

    def _update_font_overline(self, is_overline):
        self.current_style["font_overline"] = is_overline
        self.update_selected_text_style()

    def _update_underline_style(self, index):
        style_map = {
            0:QTextCharFormat.UnderlineStyle.NoUnderline,
            1:QTextCharFormat.UnderlineStyle.SingleUnderline,
            2:QTextCharFormat.UnderlineStyle.SpellCheckUnderline,
            3:QTextCharFormat.UnderlineStyle.DashUnderline,
            4:QTextCharFormat.UnderlineStyle.DotLine
        }
        self.current_style["underline_style"] = style_map[index]
        self.update_selected_text_style()

    def choose_underline_color(self):
        color = QColorDialog.getColor(self.current_style["underline_color"], self, "选择划线颜色")
        if color.isValid():
            self.current_style["underline_color"] = color
        else:
            self.current_style["bg_color"]=QColor(Qt.GlobalColor.transparent)
        self.update_selected_text_style()
        self.underline_color_btn.setStyleSheet(
            f"background-color: {self.current_style['underline_color'].name()}; border: 1px solid #ccc;")

    def choose_bg_color(self):
        color = QColorDialog.getColor(self.current_style["bg_color"], self, "选择文字背景色")
        if color.isValid():
            self.current_style["bg_color"] = color
        else:
            self.current_style["bg_color"]=QColor(Qt.GlobalColor.transparent)
        self.update_selected_text_style()
        self.bg_color_btn.setStyleSheet(
            f"background-color: {self.current_style['bg_color'].name()}; border: 1px solid #ccc;")

    def _update_vertical_align(self, index):
        align_map = {
            0: QTextCharFormat.VerticalAlignment.AlignNormal,
            1: QTextCharFormat.VerticalAlignment.AlignSuperScript,
            2: QTextCharFormat.VerticalAlignment.AlignSubScript
        }
        self.current_style["vertical_align"] = align_map[index]
        self.update_selected_text_style()


    def update_selected_text_style(self):
        self.text_char_format_changed.emit(self._create_char_format())

    def _create_char_format(self):
        """新增：应用所有缺失的QTextCharFormat属性"""
        # 原有属性设置（不变）
        self.char_format.setForeground(self.current_style["font_color"])
        font = QFont(self.current_style["font_family"])
        font.setPointSize(self.current_style["font_size"])
        font.setItalic(self.current_style["font_italic"])
        font.setBold(self.current_style["font_bold"])

        # ========== 新增：应用新属性 ==========
        self.char_format.setFont(font)
        # 下划线样式+颜色
        self.char_format.setUnderlineStyle(self.current_style["underline_style"])
        self.char_format.setUnderlineColor(self.current_style["underline_color"])
        # 删除线+上划线
        self.char_format.setFontStrikeOut(self.current_style["font_strikeout"])
        self.char_format.setFontOverline(self.current_style["font_overline"])

        # 文字背景色
        self.char_format.setBackground(QColor(self.current_style["bg_color"]))
        # 上下标
        self.char_format.setVerticalAlignment(self.current_style["vertical_align"])

        return self.char_format

    def on_ok(self):
        self.text_char_format_confirmed.emit(self._create_char_format())
        self.accept()  # 关闭对话框

if __name__ == "__main__":
    app = QApplication(sys.argv)
    init_format = QTextCharFormat()
    dialog = TextCharFormatDialog(init_format)
    dialog.show()
    sys.exit(app.exec())