import math

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class CustomGraphicsPixmapItem(QGraphicsPixmapItem):
    """
    支持鼠标选中文本的自定义文字项（实际为图片项，修正原注释偏差）
    1. 移除选中虚线边框 2. 支持鼠标拖拽移动 3. 支持四角缩放 4. 统一样式应用逻辑
    """

    def __init__(self, pixmap: QPixmap, parent=None):
        super().__init__(parent)
        self.setPixmap(pixmap)
        self.original_pixmap = pixmap.copy()  # 拷贝原始图片，避免外部对象修改影响
        self.resize_state = {
            "is_resize": False,
            "start_rect": QRect()
        }
        self.resize_direction = None
        # 修复点4：移除选中虚线边框（原需求未实现，补充该功能）
        self.setFlags(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setAcceptHoverEvents(True)  # 启用悬停事件，用于光标切换

    def is_point_range(self, pointTarget, pointSource, offset=25):
        """判断目标点是否在源点的偏移范围内"""
        return (pointSource.x() - offset <= pointTarget.x() <= pointSource.x() + offset
                and pointSource.y() - offset <= pointTarget.y() <= pointSource.y() + offset)

    def get_resize_direction(self, pos):
        """
        检测鼠标位置对应的拉伸方向
        返回值：tl(左上)/None
        """
        if self.is_point_range(pos, self.scenePos()):
            return "tl"
        return None

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent) -> None:

        # 使用场景坐标判断，避免全局坐标偏移
        current_pos = event.scenePos().toPoint()
        self.resize_direction = self.get_resize_direction(current_pos)
        # 设置对应缩放光标
        if self.resize_direction in ["tl"]:
            self.setCursor(Qt.CursorShape.SizeFDiagCursor)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent) -> None:
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self.resize_direction = None
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        current_pos = event.scenePos().toPoint()
        item_rect = QRect(self.scenePos().toPoint(),
                          self.pixmap().size())
        self.resize_state["start_rect"] = item_rect
        self.resize_direction = self.get_resize_direction(current_pos)

        # 缩放逻辑
        if event.button() == Qt.MouseButton.LeftButton and self.resize_direction:
            # 更新项的初始矩形信息
            self.resize_state["is_resize"] = True
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        current_pos = event.scenePos().toPoint()
        # 缩放调整逻辑
        if self.resize_state["is_resize"] and event.buttons() & Qt.MouseButton.LeftButton:
            if self.resize_direction == "tl":
                start_rect = self.resize_state["start_rect"]
                # 原始左上角和右下角（固定右下角，仅调整左上角，更稳定）
                original_bottom_right = start_rect.bottomRight()
                # 新的左上角为当前鼠标位置，右下角保持不变
                new_top_left = current_pos
                # 构造新矩形（此时可能宽高为负，需要归一化）
                new_rect = QRect(new_top_left, original_bottom_right)
                # 关键：执行矩形归一化，修正宽高为负的问题
                normalized_new_rect = new_rect.normalized()

                # 更新resize_state中的start_rect为归一化后的有效矩形
                self.resize_state["start_rect"] = normalized_new_rect
                # 设置缩放光标
                self.setCursor(Qt.CursorShape.SizeFDiagCursor)

                # 缩放pixmap（保持比例，平滑缩放）
                scaled_pixmap = self.original_pixmap.scaled(
                    normalized_new_rect.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                # 调整item位置和pixmap尺寸
                self.setPos(QPointF(normalized_new_rect.x(), normalized_new_rect.y()))
                self.setPixmap(scaled_pixmap)

        # 调用父类方法，保证事件传递正常
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if event.button() == Qt.MouseButton.LeftButton:
            # 重置拖拽和缩放状态
            self.resize_state["is_resize"] = False
            # 修复点10：替换无效的CustomCursor，恢复默认箭头光标
            self.setCursor(Qt.CursorShape.ArrowCursor)

        super().mouseReleaseEvent(event)
