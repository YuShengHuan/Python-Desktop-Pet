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
        self.first_init = True
        self.setPlainText(text)

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

    def apply_style_to_selected(self, format: QTextCharFormat):
        """应用样式到文本（PySide6原生API）"""
        doc = self.document()
        cursor = QTextCursor(doc)
        text_cursor = self.textCursor()
        if self.open_edit:
            if text_cursor.hasSelection():
                # 应用到选中的文本片段
                cursor.setPosition(text_cursor.selectionStart())
                cursor.setPosition(text_cursor.selectionEnd(), QTextCursor.MoveMode.KeepAnchor)
            else:
                cursor.setPosition(text_cursor.position(), QTextCursor.MoveMode.MoveAnchor)
        elif self.first_init:
            cursor.select(QTextCursor.SelectionType.Document)
            self.first_init = False
        cursor.mergeCharFormat(format)
        doc.setModified(True)
        if self.open_edit and not text_cursor.hasSelection():
            self.setTextCursor(cursor)
        self.update()
