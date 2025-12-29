from PySide6.QtCore import Qt
from PySide6.QtGui import QTextCharFormat, QTextCursor, QPainter
from PySide6.QtWidgets import QGraphicsSceneMouseEvent, QStyleOptionGraphicsItem, QStyle, QGraphicsTextItem, QWidget


class CustomGraphicsTextItem(QGraphicsTextItem):
    """
    支持鼠标选中文本的自定义文字项
    1. 移除选中虚线边框 2. 支持鼠标选中文本 3. 统一样式应用逻辑（选中/全部）
    """

    def __init__(self, text: str, parent=None):
        super().__init__(parent)
        self.open_edit = False
        self.setPlainText(text)
        # 选中状态标记
        self._is_item_selected = False

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget = None) -> None:
        """重写paint，移除选中时的虚线边框"""
        if option is None:
            option = QStyleOptionGraphicsItem()
            option.initFrom(widget)

        op = QStyleOptionGraphicsItem(option)
        if op.state & QStyle.StateFlag.State_Selected:
            if self.open_edit:
               op.state = QStyle.StateFlag.State_None

        super().paint(painter, op, widget)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        self.setSelected(True)
        super().mousePressEvent(event)  # 保证文本选中功能正常

    def mouseDoubleClickEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        if not self.open_edit:
            self.open_edit = True
            self.setTextInteractionFlags(Qt.TextInteractionFlag.TextEditorInteraction)
            self.setCursor(Qt.CursorShape.IBeamCursor)
        else:
            self.open_edit = False
            self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
            self.setCursor(Qt.CursorShape.OpenHandCursor)
        self.update()

    def mouse_leave_range(self):
        self.setTextInteractionFlags(Qt.TextInteractionFlag.NoTextInteraction)
        self.open_edit = False

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        text_cursor = self.textCursor()
        if not text_cursor.hasSelection():
            self._is_item_selected = False
        super().mouseReleaseEvent(event)

    def setSelected(self, selected: bool) -> None:
        """重写选中方法，记录图形项状态"""
        super().setSelected(selected)
        self._is_item_selected = selected
        self.update()

    def apply_style_to_selected(self, format: QTextCharFormat):
        """应用样式到文本（PySide6原生API）"""
        doc = self.document()
        cursor = QTextCursor(doc)

        text_cursor = self.textCursor()
        if self.open_edit:
            if self._is_item_selected:
                # 应用到选中的文本片段
                cursor.setPosition(text_cursor.selectionStart())
                cursor.setPosition(text_cursor.selectionEnd(), QTextCursor.MoveMode.KeepAnchor)
            else:
                #关键：将目标光标同步到当前真实光标位置（不选中任何内容，仅定位）
                cursor.setPosition(text_cursor.position(),QTextCursor.MoveMode.MoveAnchor)

        cursor.mergeCharFormat(format)
        doc.setModified(True)
        self.setTextCursor(cursor)

        self.update()