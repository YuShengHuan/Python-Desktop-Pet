import os.path
import sys

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from widget.screenshot.custom.CustomGraphicsView import CustomGraphicsView
from widget.util import WindowStatic


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
        self.scene_bg_color = QColor(Qt.GlobalColor.transparent)
        self.resize_direction = None
        self.add_file_dir = "./data"
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
        # self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
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

                    #clear_scene_btn,#del_text_btn {
                        background-color: #ff6b6b;
                    }
                    #clear_scene_btn:hover,#del_text_btn:hover {
                        background-color: #ff8787;
                    }
                    #clear_scene_btn:pressed,#del_text_btn:pressed {
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
        self.main_layout.setSpacing(5)

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

        self.top_operate_bar = QHBoxLayout()
        self.top_operate_bar.setSpacing(10)
        self.top_operate_bar.setContentsMargins(5, 0, 5, 3)
        self.top_operate_bar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.select_scene_bg_btn = QPushButton()
        self.select_scene_bg_btn.setObjectName("select_scene_bg_btn")
        self.select_scene_bg_btn.setIcon(QIcon("image/icon/select_scene_bg_btn.png"))
        self.select_scene_bg_btn.setFixedSize(30, 30)
        self.select_scene_bg_btn.setToolTip("选择场景背景")
        self.select_scene_bg_btn.clicked.connect(self.select_scene_bg_to_view)
        self.top_operate_bar.addWidget(self.select_scene_bg_btn)

        self.select_scene_bg_color_btn = QPushButton()
        self.select_scene_bg_color_btn.setFixedSize(30, 30)
        self.select_scene_bg_color_btn.setObjectName("select_scene_bg_color_btn")
        self.select_scene_bg_color_btn.clicked.connect(self.select_scene_bg_color)
        self.select_scene_bg_color_btn.setToolTip("选择场景颜色")
        self.select_scene_bg_color_btn.setStyleSheet(
            f"background-color: {WindowStatic.get_color(self.scene_bg_color)}; border: 1px solid #ccc;")
        self.top_operate_bar.addWidget(self.select_scene_bg_color_btn)

        self.clear_scene_btn = QPushButton()
        self.clear_scene_btn.setObjectName("clear_scene_btn")
        self.clear_scene_btn.setIcon(QIcon("image/icon/clear_scene_btn.png"))
        self.clear_scene_btn.setToolTip("清除场景")
        self.clear_scene_btn.setFixedSize(30, 30)
        self.clear_scene_btn.clicked.connect(self.clear_picture_to_view)
        self.top_operate_bar.addWidget(self.clear_scene_btn)

        self.scene_history_operatebar = QHBoxLayout()
        self.scene_history_operatebar.setSpacing(0)
        self.scene_history_operatebar.setContentsMargins(0, 0, 0, 0)
        self.scene_history_operatebar.setAlignment(Qt.AlignmentFlag.AlignLeft)

        self.forward_scene_history_btn = QPushButton("")
        self.forward_scene_history_btn.setIcon(QIcon("image/icon/forward_scene_history_btn.png"))
        self.forward_scene_history_btn.setFixedSize(30, 30)
        self.forward_scene_history_btn.setToolTip("前进场景")
        self.forward_scene_history_btn.setObjectName("forward_scene_history_btn")
        self.forward_scene_history_btn.clicked.connect(self.forward_scene_history)
        self.scene_history_operatebar.addWidget(self.forward_scene_history_btn)

        self.save_scene_history_btn = QPushButton("")
        self.save_scene_history_btn.setIcon(QIcon("image/icon/save_scene_history_btn.png"))
        self.save_scene_history_btn.setFixedSize(30, 30)
        self.save_scene_history_btn.setToolTip("保存场景历史")
        self.save_scene_history_btn.setObjectName("save_scene_history_btn")
        self.save_scene_history_btn.clicked.connect(self.save_scene_history)
        self.scene_history_operatebar.addWidget(self.save_scene_history_btn)

        self.backward_scene_history_btn = QPushButton("")
        self.backward_scene_history_btn.setIcon(QIcon("image/icon/backward_scene_history_btn.png"))
        self.backward_scene_history_btn.setFixedSize(30, 30)
        self.backward_scene_history_btn.setToolTip("回退场景")
        self.backward_scene_history_btn.setObjectName("backward_scene_history_btn")
        self.backward_scene_history_btn.clicked.connect(self.backward_scene_history)
        self.scene_history_operatebar.addWidget(self.backward_scene_history_btn)

        self.top_operate_bar.addLayout(
            self.scene_history_operatebar
        )

        self.text_style_btn = QPushButton()
        self.text_style_btn.setIcon(QIcon("image/icon/text_style_btn.png"))
        self.text_style_btn.setFixedSize(30, 30)
        self.text_style_btn.setToolTip("选择文字样式")
        self.text_style_btn.setObjectName("text_style_btn")
        self.top_operate_bar.addWidget(self.text_style_btn)

        self.draw_style_btn = QPushButton()
        self.draw_style_btn.setFixedSize(30, 30)
        self.draw_style_btn.setObjectName("draw_style_btn")
        self.draw_style_btn.setToolTip("选择涂画样式")
        self.draw_style_btn.setIcon(QIcon("image/icon/draw_style_btn.png"))
        self.top_operate_bar.addWidget(self.draw_style_btn)

        self.save_picture_btn = QPushButton()
        self.save_picture_btn.setIcon(QIcon("image/icon/save_picture_btn.png"))
        self.save_picture_btn.setFixedSize(30, 30)
        self.save_picture_btn.clicked.connect(self.save_image)
        self.save_picture_btn.setObjectName("save_btn")
        self.save_picture_btn.setToolTip("保存图片")
        self.top_operate_bar.addWidget(self.save_picture_btn)

        self.copy_picture_btn = QPushButton()
        self.copy_picture_btn.setIcon(QIcon("image/icon/copy_picture_btn.png"))
        self.copy_picture_btn.setFixedSize(30, 30)
        self.copy_picture_btn.setObjectName("copy_btn")
        self.copy_picture_btn.setToolTip("复制图片")
        self.copy_picture_btn.clicked.connect(self.copy_image)
        self.top_operate_bar.addWidget(self.copy_picture_btn)

        self.add_text_btn = QPushButton()
        self.add_text_btn.setFixedSize(30, 30)
        self.add_text_btn.setObjectName("add_text_btn")
        self.add_text_btn.setIcon(QIcon("image/icon/add_text_btn.png"))
        self.add_text_btn.setToolTip("添加文字")
        self.add_text_btn.clicked.connect(self.add_text_to_scene)
        self.top_operate_bar.addWidget(self.add_text_btn)

        self.add_picture_btn = QPushButton()
        self.add_picture_btn.setFixedSize(30, 30)
        self.add_picture_btn.setObjectName("add_pixmap_btn")
        self.add_picture_btn.setToolTip("添加图片")
        self.add_picture_btn.setIcon(QIcon("image/icon/add_picture_btn.png"))
        self.add_picture_btn.clicked.connect(self.add_pixmap_to_scene)
        self.top_operate_bar.addWidget(self.add_picture_btn)

        self.del_selected_item_btn = QPushButton()
        self.del_selected_item_btn.setFixedSize(30, 30)
        self.del_selected_item_btn.setObjectName("del_selected_item_btn")
        self.del_selected_item_btn.setToolTip("删除场景选中项")
        self.del_selected_item_btn.setIcon(QIcon("image/icon/del_selected_item_btn.png"))
        self.del_selected_item_btn.clicked.connect(self.delete_selected_item)
        self.top_operate_bar.addWidget(self.del_selected_item_btn)

        self.pen_btn = QPushButton()
        self.pen_btn.setIcon(QIcon("image/icon/pen_btn.png"))
        self.pen_btn.setFixedSize(30, 30)
        self.pen_btn.setToolTip("画笔")
        self.top_operate_bar.addWidget(self.pen_btn)

        self.rect_btn = QPushButton()
        self.rect_btn.setIcon(QIcon("image/icon/rect_btn.png"))
        self.rect_btn.setFixedSize(30, 30)
        self.rect_btn.setToolTip("矩形")
        self.top_operate_bar.addWidget(self.rect_btn)

        self.circle_btn = QPushButton()
        self.circle_btn.setIcon(QIcon("image/icon/circle_btn.png"))
        self.circle_btn.setFixedSize(30, 30)
        self.circle_btn.setToolTip("圆")
        self.top_operate_bar.addWidget(self.circle_btn)

        self.line_btn = QPushButton()
        self.line_btn.setIcon(QIcon("image/icon/line_btn.png"))
        self.line_btn.setFixedSize(30, 30)
        self.line_btn.setToolTip("线")
        self.top_operate_bar.addWidget(self.line_btn)

        self.arrow_btn = QPushButton()
        self.arrow_btn.setIcon(QIcon("image/icon/arrow_btn.png"))
        self.arrow_btn.setToolTip("箭头")
        self.arrow_btn.setFixedSize(30, 30)
        self.top_operate_bar.addWidget(self.arrow_btn)

        self.main_layout.addLayout(
            self.top_operate_bar
        )

        # 1. 创建场景（初始大小可设为0，后续更新）
        self.scene = QGraphicsScene()
        # 2. 创建视图并配置基础属性（仅执行一次）
        self.custom_view = CustomGraphicsView(self.scene)
        # 7. 仅首次将视图添加到布局，避免重复添加
        self.main_layout.addWidget(self.custom_view, stretch=1)

        # 场景
        self.main_pixmap_item = None
        self.main_pixmap = None
        self.scene_history = []
        self.scene_history_index = -1

        self.mode_type = {
            "pen": self.pen_btn,
            "rect": self.rect_btn,
            "ellipse": self.circle_btn,
            "line": self.line_btn,
            "arrow": self.arrow_btn
        }
        for mode, btn in self.mode_type.items():
            btn.clicked.connect(lambda checked=False, mode=mode: self.custom_view.switch_mode(mode))

        def model_changed(oid_mode, new_mode):
            if oid_mode:
                # 选中态样式不变（保持原蓝色）
                oid_mode_btn = self.mode_type[oid_mode]
                oid_mode_btn.setStyleSheet(
                    """
                        QPushButton {
                            border: none;
                            border-radius: 0;
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
                    """
                )
            if new_mode:
                new_mode_btn = self.mode_type[new_mode]
                new_mode_btn.setStyleSheet(
                    """
                        QPushButton {
                            border: 2px solid #ff9800;  /* 橙色醒目边框 */
                            border-radius: 0;
                            font-family: "Microsoft YaHei";
                            font-size: 14px;
                            font-weight: bold;
                            color: #e68a00;     /* 深橙色文字 */
                            background-color: #fff8e1;  /* 浅橙背景，温暖且显眼 */
                            padding: 4px 8px;
                            box-shadow: 0 1px 3px rgba(255,152,0,0.2);  /* 轻微阴影，提升层次感 */
                        }
                        QPushButton:hover {
                            background-color: #ffecb3;
                            border-color: #ffa726;
                            box-shadow: 0 2px 5px rgba(255,152,0,0.3);
                        }
                        QPushButton:pressed {
                            background-color: #ffe082;
                            border-color: #fb8c00;
                            padding-left: 9px;
                            padding-top: 5px;
                            box-shadow: 0 1px 2px rgba(255,152,0,0.2);
                        }
                    """
                )

        self.custom_view.model_changed.connect(model_changed)

        self.draw_style_btn.clicked.connect(self.custom_view.open_pen_style_dialog)
        self.text_style_btn.clicked.connect(self.custom_view.open_text_char_format_dialog)

        self.timer_check_status = QTimer()
        self.timer_check_status.timeout.connect(self.checked_status)
        self.timer_check_status.start(200)

    def checked_status(self):
        if len(self.scene.selectedItems()) > 0:
            self.del_selected_item_btn.setDisabled(False)
        else:
            self.del_selected_item_btn.setDisabled(True)

        if len(self.scene.items()) > 0:
            self.clear_scene_btn.setDisabled(False)
        else:
            self.clear_scene_btn.setDisabled(True)

        if self.scene_history_index == 0:
            self.forward_scene_history_btn.setDisabled(True)
        else:
            self.forward_scene_history_btn.setDisabled(False)
        if self.scene_history_index == len(self.scene_history) - 1:
            self.backward_scene_history_btn.setDisabled(True)
        else:
            self.backward_scene_history_btn.setDisabled(False)

    def forward_scene_history(self):
        if self.scene_history_index > 0:
            self.scene_history_index -= 1
        self.clear_scene_load_history_main_pixmap()

    def clear_scene_load_history_main_pixmap(self, new_scene_pixmap: QPixmap = None):
        if self.scene:
            for item in self.scene.items():
                if self.main_pixmap_item and item != self.main_pixmap_item:
                    self.scene.removeItem(item)
        if self.main_pixmap_item:
            self.main_pixmap_item.setPixmap(
                new_scene_pixmap if new_scene_pixmap else self.scene_history[self.scene_history_index]
            )
            self.main_pixmap_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)

    def select_scene_bg_color(self):
        color_dialog = QColorDialog(self.scene_bg_color, self)
        color_dialog.setOptions(QColorDialog.ColorDialogOption.ShowAlphaChannel)
        # 3. 弹出对话框并判断是否确认选择
        if color_dialog.exec():
            # 4. 获取选中的带Alpha值的颜色
            color = color_dialog.selectedColor()
            if color.isValid():
                self.scene_bg_color = color
                self.select_scene_bg_color_btn.setStyleSheet(
                    f"background-color: {WindowStatic.get_color(color)}; border: 1px solid #ccc;")
                main_pixmap = QPixmap(self.custom_view.width(), self.custom_view.height())
                main_pixmap.fill(color)
                self.load_graphics_view_scene(
                    main_pixmap
                )

    def backward_scene_history(self):
        if self.scene_history_index < len(self.scene_history) - 1:
            self.scene_history_index += 1
        self.clear_scene_load_history_main_pixmap()

    def save_scene_history(self):
        new_scene_pixmap = QPixmap.fromImage(
            self.scene_to_image(
                self.scene
            )
        )
        self.scene_history.append(new_scene_pixmap)
        self.scene_history_index = len(self.scene_history) - 1
        self.clear_scene_load_history_main_pixmap(
            new_scene_pixmap
        )

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

    def select_scene_bg_to_view(self):
        # 若用户取消选择，直接返回
        file_img_path = self.select_image()
        if not file_img_path:
            return
        self.load_graphics_view_scene(
            QPixmap(file_img_path)
        )

    def clear_picture_to_view(self):
        self.scene_bg_color = QColor(Qt.GlobalColor.transparent)
        self.select_scene_bg_color_btn.setStyleSheet(
            f"background-color: {WindowStatic.get_color(self.scene_bg_color)}; border: 1px solid #ccc;")
        self.load_graphics_view_scene()

    def load_graphics_view_scene(self, main_pixmap: QPixmap = None):
        # 1. 清空场景中旧的图形项（图片+文字），避免残留
        self.scene.clear()
        self.main_pixmap_item = None
        self.scene_history.clear()
        self.scene_history_index = -1

        # 3. 创建新的图片项并添加到场景
        if main_pixmap:
            byte_array = QByteArray()
            buffer = QBuffer(byte_array)
            buffer.open(QIODevice.OpenModeFlag.WriteOnly)
            main_pixmap.save(buffer, "PNG")
            buffer.close()
            buffer.open(QIODevice.OpenModeFlag.ReadOnly)
            self.main_pixmap = QPixmap()
            self.main_pixmap.loadFromData(byte_array)
            buffer.close()

            pixmap_rect = QRect(0, 0,
                                self.main_pixmap.width(),
                                self.main_pixmap.height())
            self.main_pixmap_item = QGraphicsPixmapItem(self.main_pixmap)
            self.main_pixmap_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
            self.main_pixmap_item.setPos(0, 0)  # 强制图片在场景原点
            self.scene.addItem(self.main_pixmap_item)

            # 关键1：将场景尺寸设置为图片的实际尺寸，消除场景与图片的尺寸差
            self.scene.setSceneRect(pixmap_rect)
            # 关键2：重置视图变换矩阵，清除之前的缩放/平移残留
            self.custom_view.resetTransform()
            # 关键3：基于图片项的边界适配视图，而非场景Rect（更精准）
            self.custom_view.fitInView(pixmap_rect,
                                       Qt.AspectRatioMode.KeepAspectRatio)
        else:
            pixmap_rect = QRect(0, 0,
                                self.custom_view.width(),
                                self.custom_view.height())
            self.scene.setSceneRect(self.custom_view.geometry())
            # 关键2：重置视图变换矩阵，清除之前的缩放/平移残留
            self.custom_view.resetTransform()
            # 关键3：基于图片项的边界适配视图，而非场景Rect（更精准）
            self.custom_view.fitInView(pixmap_rect, Qt.AspectRatioMode.KeepAspectRatio)
        self.save_scene_history()

    def add_text_to_scene(self):
        """添加文字到图片（优化：支持即时应用当前属性）"""
        text = "添加文字"
        orign_icon = self.add_text_btn.icon()
        if len(text) > 0:
            self.custom_view.add_text_to_scene(text)
            self.add_text_btn.setIcon(QIcon("image/icon/success.png"))
        else:
            self.add_text_btn.setIcon(QIcon("image/icon/fail.png"))
        QTimer.singleShot(1000, lambda: self.add_text_btn.setIcon(orign_icon))

    def add_pixmap_to_scene(self):
        file_img_path = self.select_image()
        if not file_img_path:
            return
        self.custom_view.add_pixmap_to_scene(file_img_path)

    def delete_selected_item(self):
        selected_items = self.scene.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "提示", "请先选中内容！")
            return
        for item in selected_items:
            self.scene.removeItem(item)
            del item

    def scene_to_image(self, scene: QGraphicsScene, format=QImage.Format.Format_RGBA8888):
        image = QImage(scene.sceneRect().size().toSize(), format)
        image.fill(self.scene_bg_color)  # 背景设为白色
        painter = QPainter(image)
        # 1. 基础抗锯齿（必开）
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.TextAntialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)
        # 2. 新增高清渲染项（关键）
        painter.setRenderHint(QPainter.RenderHint.NonCosmeticBrushPatterns, True)
        painter.setRenderHint(QPainter.RenderHint.LosslessImageRendering, True)
        painter.setRenderHint(QPainter.RenderHint.VerticalSubpixelPositioning, True)
        # ========== 渲染场景 ==========
        scene.render(painter)
        painter.end()
        return image

    def save_image(self):
        """保存编辑后的图片（优化：添加保存成功提示）"""
        # 选择保存路径和格式
        file_path, filter_type = QFileDialog.getSaveFileName(
            self,
            "保存图片",
            f"{QDateTime.currentDateTime().toString('yyyyMMddhhmmss')}",  # 自动生成文件名
            "PNG图片 (*.png);;JPG图片 (*.jpg);;所有文件 (*.*)"
        )
        if not file_path:
            return
        orign_icon = self.save_picture_btn.icon()
        try:
            # 创建与场景大小一致的图片
            image = self.scene_to_image(self.scene)
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
        orign_icon = self.copy_picture_btn.icon()
        try:
            image = self.scene_to_image(self.scene)
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


# app = QApplication(sys.argv)
# w = EditWindow()
# w.show()
# sys.exit(app.exec())
