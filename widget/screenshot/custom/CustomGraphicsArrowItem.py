from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class CustomGraphicsArrowItem(QGraphicsItem):

    def __init__(self, line: QLineF = QLineF(), parent: QGraphicsItem = None):
        super().__init__(parent)
        # 核心：用QLineF存储线条（和QGraphicsLineItem一致）

        self._line = QLineF(line)
        # 箭头头部宽度
        self.Arrow_Head_Height = 5
        self.Arrow_Head_Width = 7

        self._arrow_head_height = self.Arrow_Head_Height
        self._arrow_head_width = self.Arrow_Head_Width
        # 标准化Pen/Brush（使用PySide6完整枚举路径初始化）
        self._pen = QPen()
        self._brush = QBrush()
        self.origin_pen_width = self._pen.width()

        # 交互特性
        self.setFlags(
            QGraphicsItem.GraphicsItemFlag.ItemIsMovable |
            QGraphicsItem.GraphicsItemFlag.ItemIsSelectable |
            QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges
        )

    # --------------------- 对齐QGraphicsLineItem的核心接口 ---------------------
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

    # --------------------- 标准化Pen/Brush接口 ---------------------
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

    # --------------------- 箭头宽度自定义 ---------------------
    def setArrowHeadWidth(self, width: float):
        if self._arrow_head_height == width:
            return
        self.prepareGeometryChange()
        self._arrow_head_height = width
        self.update()

    def arrowHeadWidth(self) -> float:
        return self._arrow_head_height

    # --------------------- 核心绘制/几何方法 ---------------------
    def boundingRect(self) -> QRectF:
        line_rect = QRectF(self._line.p1(), self._line.p2()).normalized()
        expand = self._arrow_head_height + self._pen.width()
        return line_rect.adjusted(-expand, -expand, expand, expand)

    def shape(self) -> QPainterPath:
        path = QPainterPath()
        arrow_body = self._calculate_body_head()
        path.moveTo(arrow_body.p1())
        path.lineTo(arrow_body.p2())
        arrow_head = self._calculate_arrow_head()
        path.addPolygon(arrow_head)
        return path

    def paint(self, painter: QPainter, option, widget=None):
        if self._line.isNull():
            return
        # 设置Pen/Brush
        pen_width = self._pen.width()
        pen = QPen(self._pen)
        pen.setWidthF(self._arrow_head_height * 0.8)
        painter.setPen(pen)
        painter.setBrush(self._brush)
        # 1. 绘制基础线条
        arrow_body = self._calculate_body_head()
        painter.drawLine(arrow_body)

        # 2. 绘制箭头头部
        pen.setWidthF(1)
        origin_pen_width_rate = pen_width / self.origin_pen_width
        self._arrow_head_height = self.Arrow_Head_Height * origin_pen_width_rate
        self._arrow_head_width = self.Arrow_Head_Width * origin_pen_width_rate
        painter.setPen(pen)
        arrow_head = self._calculate_arrow_head()
        painter.drawPolygon(arrow_head)

        # 选中状态样式（使用完整枚举路径）
        if self.isSelected():
            selected_pen = QPen(
                Qt.GlobalColor.blue,
                pen.width() + 1,
                Qt.PenStyle.DashLine  # 修正：完整枚举路径
            )
            painter.setPen(selected_pen)
            painter.setBrush(Qt.BrushStyle.NoBrush)  # 修正：完整枚举路径
            painter.drawRect(self.boundingRect().adjusted(2, 2, -2, -2))


    def _calculate_body_head(self) -> QLineF:
        p1 = self._line.p1()
        p2 = self._line.p2()

        # 处理起点终点重合的情况
        if p1 == p2:
            return QLineF()

        # 计算p1到p2的方向向量并归一化
        line_vector = p2 - p1
        line_length = line_vector.manhattanLength()
        line_vector_normalized = line_vector / line_length

        # 从p2往回减去箭头宽度得到p3
        p3 = p2 - line_vector_normalized * self._arrow_head_width

        # 返回p1到p3的线段（箭身段）
        return QLineF(p1, p3)

    def _calculate_arrow_head(self) -> QPolygonF:
        p1 = self._line.p1()
        p2 = self._line.p2()

        if p1 == p2:
            return QPolygonF()

        line_vector = p2 - p1
        line_vector_normalized = line_vector / line_vector.manhattanLength()
        perpendicular_vector = QPointF(-line_vector_normalized.y(), line_vector_normalized.x())

        arrow_tip = p2
        arrow_base1 = arrow_tip - line_vector_normalized * self._arrow_head_width - perpendicular_vector * self._arrow_head_height
        arrow_base2 = arrow_tip - line_vector_normalized * self._arrow_head_width + perpendicular_vector * self._arrow_head_height

        return QPolygonF([arrow_tip, arrow_base1, arrow_base2])
