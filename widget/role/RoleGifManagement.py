import os

from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *


class RoleGifManagement(QObject):
    gif_name_changed = Signal(str)

    def __init__(self, parent: QLabel = None):
        super().__init__(parent)
        self.parent = parent
        self.movie = None
        self.start_movie(
            list(self._init_gif_file_paths().values())[0]
        )
        self.gif_name_changed.connect(self.click_role_gif_action)

    def _init_gif_file_paths(self, gif_dir="image/gif"):
        gif_file_paths = {}
        file_names = os.listdir(gif_dir)
        for name in file_names:
            file_path = os.path.join(gif_dir, name).replace("\\", "/")
            if os.path.exists(file_path) and os.path.isfile(file_path) and os.path.splitext(file_path)[1] == ".gif":
                file_name_key = os.path.splitext(os.path.basename(file_path))[0]
                gif_file_paths[file_name_key] = file_path
        return gif_file_paths

    def start_movie(self, gif_path):
        self.movie = QMovie(gif_path)
        target_size = QSize(100, 100)  # 目标显示尺寸
        self.movie.setScaledSize(target_size)  # QMovie会对帧进行平滑缩放
        # 优化QMovie解码和缓存
        self.movie.setCacheMode(QMovie.CacheMode.CacheAll)  # 缓存所有帧，避免重复解码失真
        self.movie.setSpeed(100)  # 正常播放速度
        self.parent.setMovie(self.movie)
        self.movie.start()

    def get_gif_names(self):
        return self._init_gif_file_paths().keys()

    def click_role_gif_action(self, text):
        print(text)
        self.start_movie(
            self._init_gif_file_paths()[text]
        )

