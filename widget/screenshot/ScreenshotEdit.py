import cv2
import numpy as np
from PySide6.QtCore import QRect, QObject, QDateTime
from PySide6.QtWidgets import QApplication

from widget.screenshot.edit.EditWindow import EditWindow
from widget.screenshot.ocr.PaddleOCRManagement import PaddleOCRManagement
from widget.screenshot.ScreenshotWindow import ScreenshotWindow
from PySide6.QtGui import *


class ScreenshotEdit(QObject):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.edit_window = None
        self.screenshot_window = None
        self.screenshot_save_dir = "data/"
        self.paddleOCRManagement = PaddleOCRManagement()
        self.select_area = QRect()

        self.current_operate_index = 0

    def start_screenshot_edit(self):
        """启动截图功能"""
        self.open_screenshot_window()
        self.current_operate_index = 1

    def capture_rect_to_QPixmap(self, capture_rect: QRect):
        pixmap = QApplication.primaryScreen().grabWindow(
            0,  # 窗口句柄：0表示桌面（关键）
            capture_rect.x(),
            capture_rect.y(),
            capture_rect.width(),
            capture_rect.height()
        )
        return pixmap

    def current_screenshot_select_area(self, capture_rect: QRect = None):
        if self.current_operate_index == 1:
            self.open_edit_window(capture_rect)
        elif self.current_operate_index == 2:
            self.orc_predict(capture_rect)

    def open_edit_window(self, capture_rect: QRect = None):
        """打开编辑窗口"""
        if not self.edit_window:
            self.edit_window = EditWindow()
        if capture_rect:
            pixmap = self.capture_rect_to_QPixmap(capture_rect)
            pixmap.save(self.screenshot_save_dir+f"{QDateTime.currentDateTime().toString('yyyyMMddhhmmss')}.png")
            self.edit_window.load_graphics_view_scene(
                pixmap
            )
        self.edit_window.show()

    def open_screenshot_window(self):
        if not self.screenshot_window:
            self.screenshot_window = ScreenshotWindow()
            # 绑定截图完成和取消的信号
            self.screenshot_window.screenshot_selected_area.connect(self.current_screenshot_select_area)
            self.screenshot_window.screenshot_canceled.connect(self.on_screenshot_canceled)
        if self.screenshot_window.isHidden():
            self.screenshot_window.show()

    def start_screenshot_predict(self):
        self.open_screenshot_window()
        self.current_operate_index = 2

    def orc_predict(self, capture_rect: QRect = None):
        self.paddleOCRManagement.start_predict(
            self.resize_big_image(
                self.qpixmap_numpy(
                    self.capture_rect_to_QPixmap(capture_rect)
                ), max_size=2000)
        )

    def qpixmap_numpy(self, pixmap: QPixmap) -> np.ndarray:
        """强制C连续内存，解决OpenCV异常"""
        qimg = pixmap.toImage()
        target_format = QImage.Format.Format_RGB888
        if qimg.format() != target_format:
            qimg = qimg.convertToFormat(target_format)

        height = qimg.height()
        width = qimg.width()
        bytes_per_line = qimg.bytesPerLine()
        channel_num = 3

        img_np = np.frombuffer(qimg.constBits(), dtype=np.uint8)
        img_np = img_np.reshape((height, bytes_per_line))
        img_np = img_np[:, :width * channel_num]
        img_np = img_np.reshape((height, width, channel_num))

        # 核心优化：C连续内存
        img_np = np.ascontiguousarray(img_np)

        return img_np

    def resize_big_image(self, img_np: np.ndarray, max_size: int = 2000) -> np.ndarray:
        """大图片等比例缩放"""
        height, width = img_np.shape[:2]
        if width <= max_size and height <= max_size:
            return img_np

        scale = max_size / max(width, height)
        new_width = int(width * scale)
        new_height = int(height * scale)

        resized_img = cv2.resize(
            img_np,
            (new_width, new_height),
            interpolation=cv2.INTER_LINEAR
        )
        return resized_img

    def on_screenshot_canceled(self):
        """截图取消后的处理"""
        print("截图已取消")
