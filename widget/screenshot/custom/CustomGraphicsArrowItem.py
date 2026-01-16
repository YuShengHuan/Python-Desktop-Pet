from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from PySide6.QtCore import Qt, QRectF, QPointF, QLineF
from PySide6.QtGui import QPainter, QPen, QBrush, QPolygonF, QPainterPath
from PySide6.QtWidgets import QGraphicsItem


class CustomGraphicsArrowItem(QGraphicsItem):
    def __init__(self, line: QLineF = QLineF(), parent: QGraphicsItem = None):
        super().__init__(parent)
        self._line = QLineF(line)

        # 核心比例：箭身细，箭头宽（关键区别铅笔）
        self.BODY_WIDTH_RATIO = 5  # 箭身宽度 = 画笔宽度 × 1（细）
        self.ARROW_WIDTH_RATIO = 8  # 箭头宽度 = 画笔宽度 × 5（宽）
        self.ARROW_LENGTH_RATIO = 0.20  # 箭头长度占总长度比例（15%）
        self.BODY_LENGTH_RATIO = 1 - self.ARROW_LENGTH_RATIO  # 箭身占剩余长度

        # 标准化Pen/Brush
        self._pen = QPen()
        self._brush = QBrush()
        self._pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)

        # 交互特性
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    # --------------------- 原有接口完全保留 ---------------------
    def setLine(self, line: QLineF):
        if self._line == line:
            return
        self.prepareGeometryChange()
        self._line = QLineF(line)
        self.update()

    def line(self) -> QLineF:
        return QLineF(self._line)

    def setStartPoint(self, point: QPointF):
        if self._line.p1() == point:
            return
        self.prepareGeometryChange()
        self._line.setP1(point)
        self.update()

    def setEndPoint(self, point: QPointF):
        if self._line.p2() == point:
            return
        self.prepareGeometryChange()
        self._line.setP2(point)
        self.update()

    def startPoint(self) -> QPointF:
        return self._line.p1()

    def endPoint(self) -> QPointF:
        return self._line.p2()

    def setPen(self, pen: QPen):
        if self._pen == pen:
            return
        self.prepareGeometryChange()
        self._pen = pen
        self.update()

    def pen(self) -> QPen:
        return self._pen

    def setBrush(self, brush: QBrush):
        if self._brush == brush:
            return
        self.prepareGeometryChange()
        self._brush = brush
        self.update()

    def brush(self) -> QBrush:
        return self._brush

    # --------------------- 核心修正：计算宽头细身的箭头多边形 ---------------------
    def _calculate_arrow_polygon(self) -> QPolygonF:
        p1 = self._line.p1()  # 箭身起点
        p2 = self._line.p2()  # 箭头尖端
        if p1 == p2:
            return QPolygonF()

        # 1. 基础计算
        total_length = self._line.length()
        pen_width = self._pen.width() if self._pen.width() > 0 else 1

        # 宽度分离：箭身细，箭头宽
        body_width = pen_width * self.BODY_WIDTH_RATIO
        arrow_width = pen_width * self.ARROW_WIDTH_RATIO
        # 长度分配
        body_length = total_length * self.BODY_LENGTH_RATIO
        arrow_length = total_length * self.ARROW_LENGTH_RATIO

        # 2. 方向向量（归一化）
        line_vector = p2 - p1
        line_vector_normalized = line_vector / total_length
        # 垂直向量（用于计算左右边界）
        perpendicular_vector = QPointF(-line_vector_normalized.y(), line_vector_normalized.x())

        # 3. 关键点位
        body_end = p1 + line_vector_normalized * body_length  # 箭身终点 = 箭头底座起点
        arrow_tip = p2  # 箭头尖端

        # 4. 箭身矩形顶点（细）
        body_top = p1 + perpendicular_vector * (body_width / 2)
        body_bottom = p1 - perpendicular_vector * (body_width / 2)
        body_end_top = body_end + perpendicular_vector * (body_width / 2)
        body_end_bottom = body_end - perpendicular_vector * (body_width / 2)

        # 5. 箭头三角形顶点（宽，底边宽于箭身）
        arrow_base_top = body_end + perpendicular_vector * (arrow_width / 2)
        arrow_base_bottom = body_end - perpendicular_vector * (arrow_width / 2)

        # 6. 组合成闭合多边形（箭身细矩形 + 箭头宽三角形）
        polygon = QPolygonF([
            body_top, body_bottom, body_end_bottom,
            arrow_base_bottom, arrow_tip, arrow_base_top,
            body_end_top, body_top
        ])
        return polygon

    # --------------------- 几何方法 ---------------------
    def boundingRect(self) -> QRectF:
        polygon = self._calculate_arrow_polygon()
        if polygon.isEmpty():
            line_rect = QRectF(self._line.p1(), self._line.p2()).normalized()
            expand = self._pen.width() * 3
            return line_rect.adjusted(-expand, -expand, expand, expand)
        return polygon.boundingRect().adjusted(-2, -2, 2, 2)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        polygon = self._calculate_arrow_polygon()
        if not polygon.isEmpty():
            path.addPolygon(polygon)
        return path

    # --------------------- 绘制：一次性画整体箭头 ---------------------
    def paint(self, painter: QPainter, option, widget=None):
        if self._line.isNull():
            return

        painter.setPen(self._pen)
        painter.setBrush(self._brush)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # 绘制宽头细身的整体箭头
        arrow_polygon = self._calculate_arrow_polygon()
        if not arrow_polygon.isEmpty():
            painter.drawPolygon(arrow_polygon)

        # 选中状态
        if self.isSelected():
            selected_pen = QPen(
                Qt.GlobalColor.blue,
                self._pen.width() + 1,
                Qt.PenStyle.DashLine
            )
            painter.setPen(selected_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(self.boundingRect().adjusted(2, 2, -2, -2))
