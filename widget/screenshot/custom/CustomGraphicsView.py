from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from widget.screenshot.custom.CustomGraphicsArrowItem import CustomGraphicsArrowItem
from widget.screenshot.custom.CustomGraphicsPixmapItem import CustomGraphicsPixmapItem
from widget.screenshot.custom.CustomGraphicsTextItem import CustomGraphicsTextItem
from widget.screenshot.dialog.DrawStyleDialog import DrawStyleDialog
from widget.screenshot.dialog.TextCharFormatDialog import TextCharFormatDialog


class CustomGraphicsView(QGraphicsView):
    model_changed = Signal(str, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setRenderHint(QPainter.RenderHint.TextAntialiasing)
        self.parent.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
        # 3. 样式与边框配置
        self.setStyleSheet("background: transparent;border:none;")
        # 4. 隐藏滚动条
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # 文字
        self.text_char_format = QTextCharFormat()
        self.init_text_char_format()

        # 绘画
        self.draw_pen = QPen()  # 手绘画笔样式
        self.init_draw_pen()  # 初始化画笔

        self.draw_brush = QBrush()
        self.init_draw_brush()  # 初始化画笔

        self.draw_pen_dict = {
        }
        self.draw_brush_dict = {
        }

        self.start_pos = None
        self.end_pos = None
        self.current_mode = None
        self.current_draw_item = None  # 当前绘制的图形项
        self.current_draw_path = None  # 当前手绘路径

        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        # 拖动状态变量（对应Qt内部封装的状态）
        self._is_right_dragging = False  # 是否处于右键拖动中
        self._drag_start_pos = QPoint()  # 拖动起始位置（viewport坐标系）

        # 对应ScrollHandDrag的“拖动开始”逻辑（替换为右键触发）

    def open_text_char_format_dialog(self):
        dialog = TextCharFormatDialog(self.text_char_format, self)
        dialog.text_char_format_confirmed.connect(self.update_selected_text_style)
        dialog.text_char_format_changed.connect(self.update_selected_text_style)
        dialog.move(QCursor.pos())
        dialog.exec()

    def update_selected_text_style(self, text_char_format: QTextCharFormat):
        self.text_char_format = text_char_format
        """将text_style同步到选中的文字项"""
        selected_items = self.parent.selectedItems()
        if not selected_items:
            return
        for item in selected_items:
            if isinstance(item, CustomGraphicsTextItem):
                # 应用样式
                item.apply_style_to_selected(
                    self.text_char_format
                )

    def open_pen_style_dialog(self):
        # 创建自定义画笔对话框，传入当前画笔
        dialog = DrawStyleDialog(
            self.get_current_mode_pen(),
            self.get_current_mode_brush(),
            self)
        # 绑定确认信号
        dialog.pen_confirmed.connect(self.update_custom_pen)
        # 显示对话框
        dialog.move(QCursor.pos())
        dialog.exec()

    def get_current_mode_pen(self):
        return self.draw_pen_dict[self.current_mode] if (
                    self.current_mode and self.current_mode in self.draw_pen_dict.keys()) else self.draw_pen

    def get_current_mode_brush(self):
        return self.draw_brush_dict[self.current_mode] if (
                    self.current_mode and self.current_mode in self.draw_brush_dict.keys()) else self.draw_brush

    def update_custom_pen(self, pen: QPen, brush: QBrush):
        # 更新当前画笔
        if self.current_mode:
            self.draw_pen_dict[self.current_mode] = pen
            self.draw_brush_dict[self.current_mode] = brush
        else:
            self.draw_pen = pen
            self.draw_brush = brush

    def switch_mode(self, mode):
        if self.current_mode == mode:
            self.model_changed.emit(self.current_mode, None)
            self.current_mode = None
            return

        self.model_changed.emit(self.current_mode, mode)
        self.current_mode = mode
    def get_current_mode(self):
        return self.current_mode

    def add_text_to_scene(self, text):
        """添加文字到图片（优化：支持即时应用当前属性）"""
        # 创建文字项
        text_item = CustomGraphicsTextItem(text)
        # 设置文字属性
        text_item.apply_style_to_selected(self.text_char_format)  # 新文字默认应用全部样式
        text_item.setPos(QPointF(
            self.scene().width() / 2.5,
            self.scene().height() / 2.5,
        ))
        text_item.setZValue(11)
        # 允许文字拖拽移动、选中、聚焦
        text_item.setFlags(
            QGraphicsTextItem.GraphicsItemFlag.ItemIsMovable | QGraphicsTextItem.GraphicsItemFlag.ItemIsSelectable
        )
        # 添加到场景和列表
        self.parent.addItem(text_item)

    def add_pixmap_to_scene(self, file_img_path):
        pixmap_item = CustomGraphicsPixmapItem(QPixmap(file_img_path))
        pixmap_item.setPos(QPointF(
            self.scene().width() / 5,
            self.scene().height() / 5,
        ))
        pixmap_item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        pixmap_item.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable | QGraphicsItem.GraphicsItemFlag.ItemIsSelectable
        )
        pixmap_item.setZValue(10)
        self.parent.addItem(pixmap_item)

    def init_text_char_format(self):
        self.text_char_format.setForeground(QColor(Qt.GlobalColor.red))
        self.text_char_format.setFontPointSize(20)
        self.text_char_format.setBackground(QColor(Qt.GlobalColor.transparent))

    def init_draw_pen(self):
        self.draw_pen.setColor(QColor(255, 0, 0))  # 红色画笔
        self.draw_pen.setWidth(5)  # 画笔宽度
        self.draw_pen.setCapStyle(Qt.PenCapStyle.RoundCap)  # 线条端点圆角
        self.draw_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)  # 线条拐角圆角

    def init_draw_brush(self):
        self.draw_brush = QBrush(QColor(Qt.GlobalColor.transparent))

    def wheelEvent(self, event):
        """滚轮缩放视图"""
        # 计算缩放因子（每次缩放10%）
        scale_factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        # 获取当前视图的变换矩阵
        current_scale = self.transform().m11()
        # 限制缩放范围（0.1倍 ~ 100倍）
        if 0.1 < current_scale * scale_factor < 100:
            self.scale(scale_factor, scale_factor)

    def mousePressEvent(self, event: QMouseEvent):
        self.start_pos = self.mapToScene(event.position().toPoint())
        if event.button() == Qt.MouseButton.LeftButton and self.current_mode:
            # 手绘模式
            if self.current_mode == "pen":
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
            elif self.current_mode == "arrow":
                self.current_draw_item = CustomGraphicsArrowItem(QLineF(self.start_pos, self.start_pos))
            self.current_draw_item.setPen(
                self.get_current_mode_pen()
            )
            if self.current_mode in ["pen", "rect", "ellipse", "arrow"]:
                self.current_draw_item.setBrush(
                    self.get_current_mode_brush().color()
                )
            self.current_draw_item.setZValue(10)
            self.parent.addItem(self.current_draw_item)
        elif event.button() == Qt.MouseButton.RightButton:
            # 1. 标记开始拖动
            self._is_right_dragging = True
            # 2. 记录鼠标按下时的初始位置（必须用viewport的坐标）
            self._drag_start_pos = self.mapToGlobal(event.pos())
            # 3. 模拟ScrollHandDrag的手型光标
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.end_pos = self.mapToScene(event.position().toPoint())
        if event.buttons() & Qt.MouseButton.LeftButton and self.current_mode:
            # 手绘
            if self.current_mode == "pen":
                self.current_draw_path.lineTo(self.end_pos)
                self.current_draw_item.setPath(self.current_draw_path)
            elif self.current_mode in ["rect", "ellipse"]:
                self.current_draw_item.setRect(QRectF(self.start_pos, self.end_pos).normalized())
            elif self.current_mode == "line":
                self.current_draw_item.setLine(QLineF(self.start_pos, self.end_pos))
            elif self.current_mode == "arrow":
                self.current_draw_item.setLine(QLineF(self.start_pos, self.end_pos))
        elif self._is_right_dragging and event.buttons() == Qt.MouseButton.RightButton:
            # 1. 计算鼠标移动的偏移量（当前位置 - 初始位置）
            current_pos = self.mapToGlobal(event.pos())
            delta = current_pos - self._drag_start_pos
            # 2. 平移视图（偏移量取反：鼠标右移→视图左移，和ScrollHandDrag完全一致）
            self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() - delta.x()))
            self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() - delta.y()))
            # 3. 更新初始位置，实现连续拖动
            self._drag_start_pos = current_pos
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            # 1. 标记结束拖动
            self._is_right_dragging = False
            # 2. 恢复默认光标
            self.unsetCursor()
        else:
            super().mouseReleaseEvent(event)
