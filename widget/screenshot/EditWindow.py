import os.path
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from widget.screenshot.custom.CustomGraphicsPixmapItem import CustomGraphicsPixmapItem
from widget.screenshot.custom.CustomGraphicsTextItem import CustomGraphicsTextItem
# 注意：请确保这两个自定义对话框的路径正确
from widget.screenshot.dialog.PenStyleDialog import PenStyleDialog
from widget.screenshot.dialog.TextCharFormatDialog import TextCharFormatDialog


class EditWindow(QWidget):
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
        if event.button() == Qt.MouseButton.LeftButton and not self.resize_direction and not self.isFullScreen():
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
        self.add_file_dir = "."
        self.bg_pixmap = QPixmap()
        # 替换为你的图片路径（绝对路径/相对路径均可，支持png/jpg等格式）
        img_path = "image/bg/screenshot_edit.png"  # 示例：同目录下的background.png
        if self.bg_pixmap.load(img_path):
            # 可选：预处理图片（如缩放/透明化）
            self.bg_pixmap = self.bg_pixmap.scaled(
                self.size(),
                Qt.AspectRatioMode.KeepAspectRatioByExpanding,  # 保持比例并覆盖控件
                Qt.TransformationMode.SmoothTransformation  # 平滑缩放，抗锯齿
            )
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        #self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(self.width(), 500)
        self.setObjectName("editWindow")

        self.setStyleSheet('''
                    /* 主容器样式 */
                    #editWindow {
                        background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #66bfff, stop:1 #4a90e2);
                        border: 1px solid #e0e0e0;
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                        color:black;
                    }
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
                    /* 功能按钮（添加/删除）样式 */
                    #add_text_btn {
                        background-color: #4ecdc4;
                    }
                    #add_text_btn:hover {
                        background-color: #60d9d0;
                    }
                    #add_text_btn:pressed {
                        background-color: #3eb8b0;
                    }

                    #clear_picture_btn,#del_text_btn {
                        background-color: #ff6b6b;
                    }
                    #clear_picture_btn:hover,#del_text_btn:hover {
                        background-color: #ff8787;
                    }
                    #clear_picture_btn:pressed,#del_text_btn:pressed {
                        background-color: #e55353;
                    }

                    #eraser_btn {
                        background-color: #f39c12;
                    }
                    #eraser_btn:hover {
                        background-color: #e67e22;
                    }
                    #eraser_btn:pressed {
                        background-color: #d35400;
                    }

                    #del_selected_btn {
                        background-color: #9b59b6;
                    }
                    #del_selected_btn:hover {
                        background-color: #8e44ad;
                    }
                    #del_selected_btn:pressed {
                        background-color: #7d3c98;
                    }

                    /* 保存/复制按钮样式 */
                    #save_btn {
                        background-color: #51cf66;
                    }
                    #save_btn:hover {
                        background-color: #67d97c;
                    }
                    #save_btn:pressed {
                        background-color: #40b855;
                    }

                    #copy_btn {
                        background-color: #9c88ff;
                    }
                    #copy_btn:hover {
                        background-color: #aa99ff;
                    }
                    #copy_btn:pressed {
                        background-color: #8b74e8;
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
                    /* 输入框样式 */
                    QLineEdit {
                        border: 1px solid white;
                        border-radius: none;
                        padding: 4px 8px;
                        font-family: "Microsoft YaHei";
                        font-size: 14px;
                        background-color: transparent;
                        color:white;
                        selection-background-color: #66bfff;
                    }
                    QLineEdit:focus {
                        border-color: none;
                        outline: none;
                    }
                ''')
        # 主布局：工具栏容器 + 中间绘图区域
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(10)

        # ------ 上工具栏：功能操作（名称/功能按钮） ------
        self.top_window_bar = QHBoxLayout()
        self.top_window_bar.setContentsMargins(5, 0, 0, 0)
        self.top_window_bar.setSpacing(10)
        self.top_window_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 拉伸因子：将保存按钮推到右侧
        self.top_window_bar.addStretch()

        def min_max_window():
            if self.isFullScreen():
                self.showNormal()
            else:
                self.showFullScreen()

        self.min_max_window_btn = QPushButton("口")
        self.min_max_window_btn.setObjectName("min_window_btn")
        self.min_max_window_btn.setFixedSize(30, 30)
        self.min_max_window_btn.clicked.connect(min_max_window)
        self.top_window_bar.addWidget(self.min_max_window_btn)

        self.min_window_btn = QPushButton("一")
        self.min_window_btn.setObjectName("min_window_btn")
        self.min_window_btn.setFixedSize(30, 30)
        self.min_window_btn.clicked.connect(self.hide)
        self.top_window_bar.addWidget(self.min_window_btn)

        self.main_layout.addLayout(self.top_window_bar)

        self.top_operatebar = QHBoxLayout()
        self.top_operatebar.setSpacing(10)
        self.top_operatebar.setContentsMargins(5, 0, 5, 3)
        self.top_operatebar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.load_picture_btn = QPushButton("加载图片")
        self.load_picture_btn.setObjectName("load_picture_btn")
        self.load_picture_btn.setFixedSize(100, 30)
        self.load_picture_btn.clicked.connect(self.load_picture_to_view)
        self.top_operatebar.addWidget(self.load_picture_btn)

        self.clear_picture_btn = QPushButton("清除图片")
        self.clear_picture_btn.setObjectName("clear_picture_btn")
        self.clear_picture_btn.setIcon(QIcon("image/icon/clear_picture_btn"))
        self.clear_picture_btn.setFixedSize(100, 30)
        self.clear_picture_btn.clicked.connect(self.clear_picture_to_view)
        self.top_operatebar.addWidget(self.clear_picture_btn)

        self.status_show_label = QLabel()
        self.status_show_label.setObjectName("status_show_btn")
        self.status_show_label.setStyleSheet("""
            #status_show_btn {
                /* 字体配置：与现有控件一致（微软雅黑、14号字） */
                font-family: "Microsoft YaHei";
                font-size: 14px;
                /* 文字颜色：白色（适配对话框渐变背景） */
                color: black;
                /* 背景配置：浅蓝半透明背景，与主界面风格呼应 */
                background-color: transparent;
                border-radius: 0;
            }
        """)
        self.top_operatebar.addWidget(self.status_show_label)

        self.top_operatebar.addStretch()

        self.text_style_btn = QPushButton("文字样式")
        self.text_style_btn.setIcon(QIcon("image/icon/text_style_btn.png"))
        self.text_style_btn.setFixedSize(100, 30)
        self.text_style_btn.setObjectName("pen_style_btn")
        self.text_style_btn.clicked.connect(self.open_text_char_format_dialog)
        self.top_operatebar.addWidget(self.text_style_btn)


        self.pen_style_btn = QPushButton("画笔样式")
        self.pen_style_btn.setFixedSize(100, 30)
        self.pen_style_btn.setObjectName("pen_style_btn")
        self.pen_style_btn.setIcon(QIcon("image/icon/pen_style_btn.png"))
        self.pen_style_btn.clicked.connect(self.open_pen_style_dialog)
        self.top_operatebar.addWidget(self.pen_style_btn)


        self.save_picture_btn = QPushButton("保存图片")
        self.save_picture_btn.setIcon(QIcon("image/icon/save_picture_btn.png"))
        self.save_picture_btn.setFixedSize(100, 30)
        self.save_picture_btn.clicked.connect(self.save_image)
        self.save_picture_btn.setObjectName("save_btn")
        self.top_operatebar.addWidget(self.save_picture_btn)

        self.copy_picture_btn = QPushButton("复制图片")
        self.copy_picture_btn.setIcon(QIcon("image/icon/copy_picture_btn.png"))
        self.copy_picture_btn.setFixedSize(100, 30)
        self.copy_picture_btn.setObjectName("copy_btn")
        self.copy_picture_btn.clicked.connect(self.copy_image)
        self.top_operatebar.addWidget(self.copy_picture_btn)

        def status_show_btn_paintEvent(self_, event):
            painter = QPainter(self_)
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 抗锯齿，让文字更平滑
            painter.setFont(QFont("微软雅黑", 9, QFont.Weight.Bold))
            painter.setPen(Qt.PenStyle.NoPen)  # 隐藏边框

            # 1. 创建线性渐变（水平渐变：从左到右）
            # 渐变范围：覆盖整个控件的文字区域
            gradient = QLinearGradient(0, 0, self_.width(), 0)  # 起点(0,0) → 终点(控件宽度,0)（水平）
            # 渐变范围：垂直渐变（从上到下）→ QLinearGradient(0, 0, 0, self.height())
            gradient.setColorAt(0, Qt.GlobalColor.red)  # 渐变起始颜色（左/上）
            gradient.setColorAt(0.5, Qt.GlobalColor.yellow)  # 渐变中间颜色
            gradient.setColorAt(1, Qt.GlobalColor.white)  # 渐变结束颜色（右/下）
            # 2. 将渐变设置为画笔
            brush = QBrush(gradient)
            pen = QPen(brush, 0)  # 笔宽0，仅用画刷颜色
            painter.setPen(pen)
            # 3. 绘制文字（居中）
            painter.drawText(self_.rect(), Qt.AlignmentFlag.AlignCenter, self_.text())

        self.status_show_label.paintEvent = lambda event: status_show_btn_paintEvent(self.status_show_label, event)

        self.main_layout.addLayout(
            self.top_operatebar
        )

        # ========== 工具栏容器（拆分为上下两栏） ==========
        self.tool_container = QWidget()
        self.tool_container_layout = QVBoxLayout(self.tool_container)
        self.tool_container_layout.setContentsMargins(5, 0, 5, 3)
        self.tool_container_layout.setSpacing(10)  # 上下栏间距
        self.main_layout.addWidget(self.tool_container)

        self.top_toolbar = QHBoxLayout()
        self.top_toolbar.setSpacing(10)
        self.top_toolbar.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # ------ 上工具栏：功能操作（名称/功能按钮） ------

        # 上栏控件：文字输入框、添加文字、删除文字、保存图片
        self.text_edit = QLineEdit()
        self.text_edit.setPlaceholderText("输入文字")
        self.text_edit.setFixedSize(150, 30)
        self.top_toolbar.addWidget(self.text_edit)

        self.add_text_btn = QPushButton("添加文字")
        self.add_text_btn.setFixedSize(90, 30)
        self.add_text_btn.setObjectName("add_text_btn")
        self.add_text_btn.setIcon(QIcon("image/icon/add_text_btn.png"))
        self.add_text_btn.clicked.connect(self.add_text_to_scene)
        self.top_toolbar.addWidget(self.add_text_btn)

        def add_pixmap_to_scene():
            file_img_path = self.select_image()
            if not file_img_path:
                return
            pixmap_item = CustomGraphicsPixmapItem(QPixmap(file_img_path))
            # 设置文字初始位置（图片中心）
            center_x = self.img_width / 2 - pixmap_item.boundingRect().width() / 2
            center_y = self.img_height / 2 - pixmap_item.boundingRect().height() / 2
            pixmap_item.setPos(center_x, center_y)
            pixmap_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            pixmap_item.setFlags(
                QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
            )
            pixmap_item.setZValue(10)
            self.scene.addItem(pixmap_item)

        self.add_picture_btn = QPushButton("添加图片")
        self.add_picture_btn.setFixedSize(90, 30)
        self.add_picture_btn.setObjectName("add_pixmap_btn")
        self.add_picture_btn.setIcon(QIcon("image/icon/add_picture_btn.png"))
        self.add_picture_btn.clicked.connect(add_pixmap_to_scene)
        self.top_toolbar.addWidget(self.add_picture_btn)

        self.del_text_btn = QPushButton("删除选中")
        self.del_text_btn.setFixedSize(100, 30)
        self.del_text_btn.setObjectName("del_text_btn")
        self.del_text_btn.setIcon(QIcon("image/icon/del_text_btn.png"))
        self.del_text_btn.clicked.connect(self.delete_selected_item)
        self.top_toolbar.addWidget(self.del_text_btn)


        # ============ 以下是纯新增按钮（形状+画笔） ============
        self.model_type = {
            "画笔": "draw",
            "矩形": "rect",
            "圆形": "ellipse",
            "直线": "line"
        }
        self.pen_btn = QPushButton("画笔")
        self.pen_btn.setIcon(QIcon("image/icon/pen_btn.png"))
        self.pen_btn.setFixedSize(65, 30)
        self.pen_btn.clicked.connect(lambda: self.switch_mode("draw"))
        self.top_toolbar.addWidget(self.pen_btn)

        self.rect_btn = QPushButton("矩形")
        self.rect_btn.setIcon(QIcon("image/icon/rect_btn.png"))
        self.rect_btn.setFixedSize(65, 30)
        self.rect_btn.clicked.connect(lambda: self.switch_mode("rect"))
        self.top_toolbar.addWidget(self.rect_btn)

        self.circle_btn = QPushButton("圆形")
        self.circle_btn.setIcon(QIcon("image/icon/circle_btn.png"))
        self.circle_btn.setFixedSize(65, 30)
        self.circle_btn.clicked.connect(lambda: self.switch_mode("ellipse"))
        self.top_toolbar.addWidget(self.circle_btn)

        self.line_btn = QPushButton("直线")
        self.line_btn.setIcon(QIcon("image/icon/line_btn.png"))
        self.line_btn.setFixedSize(65, 30)
        self.line_btn.clicked.connect(lambda: self.switch_mode("line"))
        self.top_toolbar.addWidget(self.line_btn)

        self.tool_container_layout.addLayout(self.top_toolbar)

        # 文字
        self.view = None
        self.scene = None
        self.main_pixmap_item = None
        self.screenshot_pixmap = None
        self.img_width = 0
        self.img_height = 0
        self.text_items = []  # 文字项列表
        self.text_char_format = QTextCharFormat()
        self.init_text_char_format()

        # 绘画
        self.draw_pen = QPen()  # 手绘画笔样式
        self.init_draw_pen()  # 初始化画笔

        self._init_graphics_view()

        self.start_pos = None
        self.end_pos = None
        self.current_mode = None
        self.current_draw_item = None  # 当前绘制的图形项
        self.current_draw_path = None  # 当前手绘路径
        self.graphics_group = QGraphicsItemGroup()  # 批量管理图形项的组
        self.scene.addItem(self.graphics_group)
        self.timer_check_status = QTimer()
        self.timer_check_status.timeout.connect(self.checked_status)
        self.timer_check_status.start(200)

    def checked_status(self):
        text = ""
        if len(self.scene.selectedItems()) > 0:
            text += " 选中图形 "
        if self.current_mode:
            for k, v in self.model_type.items():
                if v == self.current_mode:
                    text += f" 选择模式：{k} "
                    break
        self.status_show_label.setText(text)

    def open_text_char_format_dialog(self):
        dialog = TextCharFormatDialog(self.text_char_format, self)
        dialog.text_char_format_confirmed.connect(self.update_selected_text_style)
        dialog.text_char_format_changed.connect(self.update_selected_text_style)
        dialog.move(QCursor.pos())
        dialog.exec()


    def open_pen_style_dialog(self):
        # 创建自定义画笔对话框，传入当前画笔
        dialog = PenStyleDialog(self.draw_pen, self)
        # 绑定确认信号
        dialog.pen_confirmed.connect(self.update_custom_pen)
        # 显示对话框
        dialog.move(QCursor.pos())
        dialog.exec()

    def update_custom_pen(self, pen: QPen):
        # 更新当前画笔
        self.draw_pen = pen

    def select_image(self):
        file_img_path, _ = QFileDialog.getOpenFileName(
            parent=self,
            caption="选择图片文件",
            dir=self.add_file_dir,
            filter="图片文件 (*.png *.jpg *.jpeg *.bmp *.gif *.webp);;所有文件 (*.*)"
        )
        # 若用户取消选择，直接返回
        if not file_img_path:
            return
        self.add_file_dir = os.path.dirname(file_img_path)
        return file_img_path

    def load_picture_to_view(self):
        # 若用户取消选择，直接返回
        file_img_path = self.select_image()
        if not file_img_path:
            return
        self.load_screenshot_pixmap(
            QPixmap(file_img_path)
        )

    def clear_picture_to_view(self):
        self.load_screenshot_pixmap(
            None
        )

    def load_screenshot_pixmap(self, screenshot_pixmap):
        self.screenshot_pixmap = screenshot_pixmap  # 截图的Pixmap
        if self.screenshot_pixmap:
            self.img_width = screenshot_pixmap.width()
            self.img_height = screenshot_pixmap.height()
        else:
            self.img_width = self.view.width()
            self.img_height = self.view.height()
        # ========== 优化后的绘图区域 ==========
        self._init_graphics_view()

    def _init_graphics_view(self):
        """初始化QGraphicsView（首次创建+后续更新内容）"""
        # ========== 首次初始化：创建控件并添加到布局 ==========
        if self.view is None:
            # 1. 创建场景（初始大小可设为0，后续更新）
            self.scene = QGraphicsScene()
            self.scene.setBackgroundBrush(QBrush(QColor(0, 0, 0, 0)))
            # 2. 创建视图并配置基础属性（仅执行一次）
            self.view = QGraphicsView(self.scene)
            self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
            self.view.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
            self.view.setRenderHint(QPainter.RenderHint.TextAntialiasing)
            self.scene.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
            # 3. 样式与边框配置
            self.view.setStyleSheet("background: transparent;border:none;")
            # 4. 隐藏滚动条
            self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            self.view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
            # 5. 交互模式
            self.view.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
            # 6. 滚轮缩放（绑定事件）
            self.view.wheelEvent = self._on_wheel_scroll
            self.view.setAlignment(Qt.AlignmentFlag.AlignCenter)

            # ============ 以下是纯新增：鼠标事件绑定（手绘/形状/橡皮擦） ============
            def view_mousePressEvent(self_, event: QMouseEvent):
                self.start_pos = self.view.mapToScene(event.position().toPoint())
                if event.button() == Qt.MouseButton.LeftButton and self.current_mode:
                    # 手绘模式
                    if self.current_mode == "draw":
                        self.current_draw_path = QPainterPath()
                        self.current_draw_path.moveTo(self.start_pos)
                        self.current_draw_item = QGraphicsPathItem(self.current_draw_path)
                    # 形状绘制
                    elif self.current_mode == "rect":
                        self.current_draw_item = QGraphicsRectItem(QRectF(self.start_pos, self.start_pos))
                    elif self.current_mode == "ellipse":
                        self.current_draw_item = QGraphicsEllipseItem(QRectF(self.start_pos, self.start_pos))
                    elif self.current_mode == "line":
                        self.current_draw_item = QGraphicsLineItem(QLineF(self.start_pos, self.start_pos))
                    self.current_draw_item.setPen(self.draw_pen)
                    self.current_draw_item.setFlags(
                        QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
                    )
                    self.scene.addItem(self.current_draw_item)
                    return
                QGraphicsView.mousePressEvent(self_, event)

            def view_mouseMoveEvent(self_, event: QMouseEvent):
                self.end_pos = self.view.mapToScene(event.position().toPoint())
                if event.buttons() & Qt.MouseButton.LeftButton and self.current_mode:
                    # 手绘
                    if self.current_mode == "draw":
                        self.current_draw_path.lineTo(self.end_pos)
                        self.current_draw_item.setPath(self.current_draw_path)
                    elif self.current_mode in ["rect", "ellipse"]:
                        self.current_draw_item.setRect(QRectF(self.start_pos, self.end_pos).normalized())
                    elif self.current_mode == "line":
                        self.current_draw_item.setLine(QLineF(self.start_pos, self.end_pos))
                    return
                QGraphicsView.mouseMoveEvent(self_, event)

            def view_mouseReleaseEvent(self_, event: QMouseEvent):
                if event.button() == Qt.MouseButton.LeftButton and self.current_mode:
                    self.current_draw_item = None
                    self.current_draw_path = None
                QGraphicsView.mouseReleaseEvent(self_, event)

            def view_mouseDoubleClickEvent(self_, event: QMouseEvent):
                self.current_mode = None
                QGraphicsView.mouseDoubleClickEvent(self_, event)

            # 绑定事件到视图
            self.view.mousePressEvent = lambda e: view_mousePressEvent(self.view, e)
            self.view.mouseMoveEvent = lambda e: view_mouseMoveEvent(self.view, e)
            self.view.mouseReleaseEvent = lambda e: view_mouseReleaseEvent(self.view, e)
            self.view.mouseDoubleClickEvent = lambda e: view_mouseDoubleClickEvent(self.view, e)

            # 7. 仅首次将视图添加到布局，避免重复添加
            self.main_layout.addWidget(self.view, stretch=1)
        # ========== 每次更新截图：重置场景和图片（复用控件） ==========
        # 1. 清空场景中旧的图形项（图片+文字），避免残留
        self.scene.clear()
        # 清空文字项列表（新截图需重新添加文字）
        self.text_items.clear()

        # 3. 创建新的图片项并添加到场景
        if self.screenshot_pixmap:
            self.img_width = self.screenshot_pixmap.width()
            self.img_height = self.screenshot_pixmap.height()

            self.pixmap_item = QGraphicsPixmapItem(self.screenshot_pixmap)
            self.pixmap_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            self.pixmap_item.setPos(0, 0)  # 强制图片在场景原点
            self.scene.addItem(self.pixmap_item)

            # 关键1：将场景尺寸设置为图片的实际尺寸，消除场景与图片的尺寸差
            self.scene.setSceneRect(self.pixmap_item.boundingRect())
            # 关键2：重置视图变换矩阵，清除之前的缩放/平移残留
            self.view.resetTransform()
            # 关键3：基于图片项的边界适配视图，而非场景Rect（更精准）
            self.view.fitInView(self.pixmap_item.boundingRect(), Qt.AspectRatioMode.KeepAspectRatio)
        else:
            self.img_width = self.view.width()
            self.img_height = self.view.height()
            self.scene.setSceneRect(QRect(0, 0, self.img_width, self.img_height))
            # 关键2：重置视图变换矩阵，清除之前的缩放/平移残留
            self.view.resetTransform()
            # 关键3：基于图片项的边界适配视图，而非场景Rect（更精准）
            self.view.fitInView(self.view.geometry(), Qt.AspectRatioMode.KeepAspectRatio)

    def _on_wheel_scroll(self, event):
        """滚轮缩放视图"""
        # 计算缩放因子（每次缩放10%）
        scale_factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        # 获取当前视图的变换矩阵
        current_scale = self.view.transform().m11()
        # 限制缩放范围（0.1倍 ~ 100倍）
        if 0.1 < current_scale * scale_factor < 100:
            self.view.scale(scale_factor, scale_factor)

    def update_selected_text_style(self, text_char_format: QTextCharFormat):
        self.text_char_format = text_char_format
        """将text_style同步到选中的文字项"""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return

        for item in selected_items:
            if isinstance(item, CustomGraphicsTextItem) and item in self.text_items:
                # 应用样式
                item.apply_style_to_selected(
                    self.text_char_format
                )

    def init_text_char_format(self):
        self.text_char_format.setForeground(QColor(Qt.GlobalColor.red))
        self.text_char_format.setFontPointSize(20)
        self.text_char_format.setBackground(QColor(Qt.GlobalColor.transparent))

    def init_draw_pen(self):
        self.draw_pen.setColor(QColor(255, 0, 0))  # 红色画笔
        self.draw_pen.setWidth(5)  # 画笔宽度
        self.draw_pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # 线条端点圆角
        self.draw_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)  # 线条拐角圆角

    def add_text_to_scene(self):
        """添加文字到图片（优化：支持即时应用当前属性）"""
        text = self.text_edit.text().strip()
        orign_icon = self.add_text_btn.icon()
        if len(text) > 0:
            # 创建文字项
            text_item = CustomGraphicsTextItem(text)
            # 设置文字属性
            text_item.apply_style_to_selected(self.text_char_format)  # 新文字默认应用全部样式

            # 设置文字初始位置（图片中心）
            center_x = self.img_width / 2 - text_item.boundingRect().width() / 2
            center_y = self.img_height / 2 - text_item.boundingRect().height() / 2
            text_item.setPos(center_x, center_y)
            # 允许文字拖拽移动、选中、聚焦
            text_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable)
            text_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable)
            text_item.setFlag(QGraphicsTextItem.GraphicsItemFlag.ItemIsFocusable)

            # 添加到场景和列表
            self.scene.addItem(text_item)
            self.text_items.append(text_item)
            self.text_edit.clear()
            self.add_text_btn.setIcon(QIcon("image/icon/success.png"))
        else:
            self.add_text_btn.setIcon(QIcon("image/icon/fail.png"))
        QTimer.singleShot(1000, lambda: self.add_text_btn.setIcon(orign_icon))

    def switch_mode(self, mode):
        if self.current_mode == mode:
            self.current_mode = None
            return
        self.current_mode = mode
        if mode == "draw":
            self.view.setCursor(Qt.CursorShape.CrossCursor)
        else:
            self.view.setCursor(Qt.CursorShape.ArrowCursor)

    # ============ 纯新增：兼容删除所有图形项（原有只删文字，现在增强） ============
    def delete_selected_item(self):
        selected_items = self.scene.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选中内容！")
            return
        for item in selected_items:
            if isinstance(item, CustomGraphicsTextItem) and item in self.text_items:
                self.text_items.remove(item)
            self.scene.removeItem(item)
            del item

    # ============ 纯新增：批量添加选中项到组 QGraphicsItemGroup ============
    def add_to_group(self):
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            self.graphics_group.addToGroup(item)

    def save_image(self):
        """保存编辑后的图片（优化：添加保存成功提示）"""
        # 选择保存路径和格式
        file_path, filter_type = QFileDialog.getSaveFileName(
            self,
            "保存图片",
            f"截图_{QDateTime.currentDateTime().toString('yyyyMMddhhmmss')}",  # 自动生成文件名
            "PNG图片 (*.png);;JPG图片 (*.jpg);;所有文件 (*.*)"
        )
        if not file_path:
            return
        orign_icon = self.save_picture_btn.icon()
        try:
            # 创建与场景大小一致的图片
            image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format.Format_RGBA8888)

            image.fill(Qt.GlobalColor.white)  # 背景设为白色（更符合常规图片）
            # 将场景渲染到图片
            painter = QPainter(image)
            # 【关键3】启用全量高清渲染提示（不仅是抗锯齿）
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering, True)  # 无损图片渲染（Qt6.5+）
            self.scene.render(painter)
            painter.end()

            # 保存图片
            if filter_type == "JPG图片 (*.jpg)":
                # JPG不支持透明，转换为RGB格式
                image = image.convertToFormat(QImage.Format.Format_RGB888)
            image.save(file_path)

            self.save_picture_btn.setIcon(QIcon("image/icon/success.png"))
            print("成功", f"图片已保存到：\n{file_path}")
        except Exception as e:
            self.save_picture_btn.setIcon(QIcon("image/icon/fail.png"))
            print("错误", f"保存失败：{str(e)}")
        QTimer.singleShot(1000, lambda: self.save_picture_btn.setIcon(orign_icon))

    def copy_image(self):
        orign_icon=self.copy_picture_btn.icon()
        try:
            # 创建与场景大小一致的图片
            image = QImage(self.scene.sceneRect().size().toSize(), QImage.Format.Format_RGBA8888)

            image.fill(Qt.GlobalColor.white)  # 背景设为白色（更符合常规图片）
            # 将场景渲染到图片
            painter = QPainter(image)
            # 【关键3】启用全量高清渲染提示（不仅是抗锯齿）
            painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
            painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
            painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering, True)  # 无损图片渲染（Qt6.5+）
            self.scene.render(painter)
            painter.end()

            clipboard = QApplication.clipboard()  # 获取系统剪贴板
            pixmap = QPixmap.fromImage(image)  # QImage转QPixmap
            clipboard.setPixmap(pixmap)  # 写入剪贴板

            self.copy_picture_btn.setIcon(QIcon("image/icon/success.png"))
            print("复制成功")
        except Exception as e:
            self.copy_picture_btn.setIcon(QIcon("image/icon/fail.png"))
            print("复制错误", f"失败：{str(e)}")
        QTimer.singleShot(1000, lambda: self.copy_picture_btn.setIcon(orign_icon))

    def paintEvent(self, event):
        """绘制图片背景（替代原纯色矩形），保留抗锯齿和半透明特性"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)  # 保留抗锯齿
        painter.setPen(Qt.PenStyle.NoPen)  # 隐藏边框

        if not self.bg_pixmap.isNull():
            painter.setOpacity(0.8)  # 图片透明度（0-1，0全透，1不透明）
            painter.drawPixmap(self.rect(), self.bg_pixmap)
        else:
            # 图片加载失败时，降级绘制半透明矩形
            painter.setBrush(QBrush(QColor(0, 0, 0, 25)))
            painter.drawRect(self.rect())
app = QApplication(sys.argv)
w = EditWindow()
w.show()
sys.exit(app.exec())