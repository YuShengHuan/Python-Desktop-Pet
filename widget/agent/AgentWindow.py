import random
import sys

from PySide6.QtCore import QPoint, Qt, QPropertyAnimation, QEasingCurve, QTimer, QRect
from PySide6.QtGui import QMouseEvent, QPainter, QLinearGradient, QBrush, QPen, QFont, QColor, QPixmap, QFocusEvent, \
    QRegion, QAction
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QTextEdit, QLabel, \
    QLineEdit, QFrame, QSizePolicy, QMenu

from widget.util import WindowStatic


class AgentWindow(QWidget):
    drag_state = {
        "is_drag": False,  # 是否正在拖拽
        "drag_offset": QPoint(0, 0)  # 鼠标相对于窗口左上角的偏移量
    }
    resize_state = {
        "is_resize": True,
        "start_pos": QPoint(0, 0),
        "end_pos": QPoint(0, 0)
    }

    def is_point_range(self, pointTarget, pointSource, offset=25):
        return pointSource.x() - offset <= pointTarget.x() <= pointSource.x() + offset and pointSource.y() - offset <= pointTarget.y() <= pointSource.y() + offset

    def get_resize_direction(self, pos):
        """
        检测鼠标位置对应的拉伸方向
        返回值：tl(左上)/tr(右上)/bl(左下)/br(右下)/left/right/top/bottom/None
        """
        if self.is_point_range(pos, self.resize_state["start_pos"]):
            return "tl"
        elif self.is_point_range(pos, QPoint(self.resize_state["start_pos"].x(), self.resize_state["end_pos"].y())):
            return "bl"
        elif self.is_point_range(pos, QPoint(self.resize_state["end_pos"].x(), self.resize_state["start_pos"].y())):
            return "tr"
        elif self.is_point_range(pos, self.resize_state["end_pos"]):
            return "br"
        return None

    def mousePressEvent(self, event: QMouseEvent) -> None:
        self.resize_state["start_pos"] = self.geometry().topLeft()
        self.resize_state["end_pos"] = self.geometry().bottomRight()
        # 仅处理左键按下
        self.resize_direction = self.get_resize_direction(event.globalPosition().toPoint())
        if event.button() == Qt.MouseButton.LeftButton and not self.resize_direction:
            self.drag_state["is_drag"] = True
            # 关键修改：记录鼠标相对于窗口左上角的偏移量（而非全局位置）
            self.drag_state["drag_offset"] = event.globalPosition().toPoint() - self.pos()
        if event.button() == Qt.MouseButton.LeftButton and self.resize_direction:
            self.resize_state["is_resize"] = True
        event.accept()  # 拦截事件，避免穿透

    # ========== 重写鼠标移动事件 ==========
    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if self.drag_state["is_drag"] and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(
                event.globalPosition().toPoint() - self.drag_state["drag_offset"]
            )
        elif self.resize_state["is_resize"] and event.buttons() & Qt.MouseButton.LeftButton:
            current_pos = event.globalPosition().toPoint()
            if self.resize_direction == "tl":
                self.resize_state["start_pos"] = current_pos
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            elif self.resize_direction == "tr":
                self.resize_state["end_pos"] = QPoint(current_pos.x(), self.resize_state["end_pos"].y())
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif self.resize_direction == "bl":
                self.resize_state["start_pos"] = QPoint(current_pos.x(), self.resize_state["start_pos"].y())
                self.setCursor(Qt.CursorShape.SizeHorCursor)
            elif self.resize_direction == "br":
                self.resize_state["end_pos"] = current_pos
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)
            current_rect = QRect(
                self.resize_state["start_pos"],
                self.resize_state["end_pos"]
            ).normalized()
            self.setGeometry(
                current_rect
            )
        event.accept()

    def mouseReleaseEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_state["is_drag"] = False
            self.resize_state["is_resize"] = False
            self.setCursor(Qt.CursorShape.CustomCursor)
        event.accept()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize_direction = None
        self.bg_pixmap = QPixmap()
        # 替换为你的图片路径（绝对路径/相对路径均可，支持png/jpg等格式）
        img_path = "image/bg/agent.png"  # 示例：同目录下的background.png
        if self.bg_pixmap.load(img_path):
            # 可选：预处理图片（如缩放/透明化）
            self.bg_pixmap = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,  # 保持比例并覆盖控件
                Qt.TransformationMode.SmoothTransformation  # 平滑缩放，抗锯齿
            )

        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setObjectName("agentWindow")
        self.resize(200, 150)
        self.hide()
        self.setStyleSheet('''
                            /* 主容器样式 */
                            #agentWindow {
                                border-radius: 20px;
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
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)
        self.main_layout.addStretch()

        # ------ 窗口工具栏 ------
        self.top_window_bar = QHBoxLayout()
        self.top_window_bar.setContentsMargins(5, 0, 0, 0)
        self.top_window_bar.setSpacing(10)

        self.title_label = QLabel()
        self.title_label.setText("")
        self.title_label.setObjectName("title_label")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        def title_label_mousePressEvent(self_, event):
            if self.frame:
                self.frame.hide()
                self.richtext_edit.clearFocus()
            QLabel.mousePressEvent(self_, event)

        self.title_label.mousePressEvent = lambda event: title_label_mousePressEvent(self.title_label, event)
        self.title_label.setStyleSheet(
            """
            QLabel{
                 font-size:10px;
            }
            """
        )
        self.top_window_bar.addWidget(
            self.title_label
        )

        self.min_window_btn = QPushButton("一")
        self.min_window_btn.setObjectName("min_window_btn")
        self.min_window_btn.setFixedSize(20, 20)
        self.min_window_btn.clicked.connect(self.hide)
        self.top_window_bar.addWidget(self.min_window_btn)
        self.main_layout.addLayout(self.top_window_bar)

        # ---------------------- 第二部分：富文本组件 ----------------------
        middle_layout = QHBoxLayout()
        middle_layout.setContentsMargins(5, 0, 5, 0)
        middle_layout.setSpacing(10)
        self.richtext_edit = QTextEdit()
        self.richtext_edit.setStyleSheet("""
                            QTextEdit {
                                outline: none;
                                font-size: 12px;
                                border:none;
                                color: #ffffff;
                            }
                        """)
        self.richtext_edit.setPlaceholderText("")
        self.richtext_edit.setReadOnly(True)

        middle_layout.addWidget(self.richtext_edit)

        self.main_layout.addLayout(
            middle_layout
        )

        self.frame = QFrame()

        bottom_layout = QHBoxLayout()
        bottom_layout.setContentsMargins(5, 0, 5, 5)
        bottom_layout.setSpacing(5)

        self.interact_input = QLineEdit()
        self.interact_input.setPlaceholderText("输入交互")
        self.interact_input.setFixedHeight(27)
        self.interact_input.setStyleSheet("""
                                    QLineEdit {
                                        background-color: white;
                                        border: 1px solid #dddddd;
                                        border-radius: 0;
                                        padding: 0 10px;
                                        font-size: 14px;
                                        color:black;
                                    }
                                    QLineEdit:focus {
                                        border-color: #3498db;
                                        outline: none;
                                    }
                                """)

        bottom_layout.addWidget(self.interact_input)

        self.send_interact_btn = QPushButton("发送")
        self.send_interact_btn.setFixedSize(50, 25)
        self.send_interact_btn.setStyleSheet("""
                                    QPushButton {
                                        background-color: #2ecc71;
                                        color: white;
                                        border: none;
                                        border-radius: 0;
                                        font-size: 14px;
                                    }
                                    QPushButton:hover {
                                        background-color: #27ae60;
                                    }
                                """)
        self.send_interact_btn.clicked.connect(self.send_interact_cmd)
        bottom_layout.addWidget(self.send_interact_btn)
        self.frame.setLayout(bottom_layout)
        self.main_layout.addWidget(
            self.frame
        )
        self.frame.hide()

        def custom_focus_in_event(self_, event: QFocusEvent):
            self.frame.show()
            QTextEdit.focusInEvent(self_, event)

        self.richtext_edit.focusInEvent = lambda event: custom_focus_in_event(self.richtext_edit, event)

        def custom_focus_out_event(self_, event: QFocusEvent):

            if not self.interact_input.hasFocus():
                self.frame.hide()
            QTextEdit.focusOutEvent(self_, event)

        self.richtext_edit.focusOutEvent = lambda event: custom_focus_out_event(self.richtext_edit, event)

        def custom_contextMenuEvent_event(self_, event):
            # 1. 创建菜单
            menu = QMenu(self)
            menu.setStyleSheet(
                """
                QMenu{
                    background-color:white;
                    color:black;
                }
                QMenu::item::selected{
                    background-color:black;
                    color:white;
                }
                """
            )
            # 2. 添加菜单项
            # 添加动作
            if self.richtext_edit.textCursor().hasSelection():
                copy_selection_action = QAction("复制", self)
                copy_selection_action.triggered.connect(self.copy_selection_text)
                menu.addAction(copy_selection_action)
            else:
                copy_all_action = QAction("复制全部", self)
                copy_all_action.triggered.connect(self.copy_all_text)
                menu.addAction(copy_all_action)
            clear_all_action = QAction("清除全部", self)
            clear_all_action.triggered.connect(self.richtext_edit.clear)
            menu.addAction(clear_all_action)
            # 4.示菜单（在鼠标点击位置显示）
            menu.exec(event.globalPos())

        self.richtext_edit.contextMenuEvent = lambda event: custom_contextMenuEvent_event(self.richtext_edit, event)

    def copy_all_text(self):
        """“复制全部”的实际功能实现"""
        clipboard = QApplication.clipboard()  # 获取系统剪贴板
        clipboard.setText(
            self.richtext_edit.toPlainText()
        )
        print("已复制全部文本到剪贴板")

    def copy_selection_text(self):
        """“复制全部”的实际功能实现"""
        clipboard = QApplication.clipboard()  # 获取系统剪贴板
        clipboard.setText(
            self.richtext_edit.textCursor().selectedText()
        )
        print("已复制全部文本到剪贴板")

    def paintEvent(self, event):
        """绘制图片背景（替代原纯色矩形），保留抗锯齿和半透明特性"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 保留抗锯齿
        painter.setPen(Qt.PenStyle.NoPen)  # 隐藏边框

        if not self.bg_pixmap.isNull():
            painter.setOpacity(0.8)  # 图片透明度（0-1，0全透，1不透明）
            painter.drawPixmap(self.rect(), self.bg_pixmap)
        else:
            # 图片加载失败时，降级绘制原粉色半透明矩形
            painter.setBrush(QBrush(QColor(255, 192, 203, 180)))
            painter.drawRect(self.rect())

    def send_interact_cmd(self):
        pass

    def append_data_to_view(self, data: list):
        self.richtext_edit.clear()
        for row in data:
            self.richtext_edit.append(
                row
            )
        if self.isHidden():
            top_window_g = WindowStatic.get_top_window().geometry()
            self.move(
                top_window_g.x() - self.width(),
                top_window_g.y() + int(top_window_g.height() / 2) - self.height()
            )
            self.show()
