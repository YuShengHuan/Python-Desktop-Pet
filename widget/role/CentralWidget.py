from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

from widget.agent.AgentWindow import AgentWindow
from widget.offwork.OffWorkWindow import OffWorkWindow
from widget.role.RoleGifManagement import RoleGifManagement
from widget.role.RoleInteractManagement import RoleInteractManagement
from widget.screenshot.ScreenshotEdit import ScreenshotEdit


class CentralWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("centralWidget")
        self.mainWindowVBoxLayout = QVBoxLayout()
        self.mainWindowVBoxLayout.setObjectName("centralWidgetVBoxLayout")
        self.mainWindowVBoxLayout.setSpacing(0)
        self.mainWindowVBoxLayout.setContentsMargins(0, 0, 0, 0)

        self.label = QLabel(self)
        self.label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)  # 居中显示

        self.label.setScaledContents(False)
        self.label.setStyleSheet(
            '''
                    background-color:white;
            ''')

        self.mainWindowVBoxLayout.addWidget(self.label)
        self.setLayout(self.mainWindowVBoxLayout)
        self.screenshotEdit = ScreenshotEdit()
        self.roleGifManagement = RoleGifManagement(self.label)
        self.roleInteractManagement=RoleInteractManagement(self.label)
        self.roleInteractManagement.set_gif_role_management(self.roleGifManagement)
        self.offWorkWindow = OffWorkWindow()
        self.agentWindow=AgentWindow()

        self.screenshotEdit.paddleOCRManagement.predict_finished.connect(self.predict_finished_to_view)


    def contextMenuEvent(self, event: QContextMenuEvent) -> None:
        # 1. 创建菜单
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu{
                background-color:white;
                color:black;
            }
            QMenu::item::selected{
                background-color:black;
                color:white;
            }
            """
        )
        # 2. 添加菜单项
        # 添加动作
        role_action_menu = QMenu("动作", self)
        menu.addMenu(role_action_menu)
        role_action_menu.setStyleSheet(
            """
            QMenu{
                background-color:white;
                color:black;
            }
            QMenu::item::selected{
                background-color:black;
                color:white;
            }
            """
        )
        for name in self.roleGifManagement.get_gif_names():
            role_action = QAction(name, self)
            role_action.triggered.connect(lambda checked, a=role_action: self.clicked_role_action(a))
            role_action_menu.addAction(role_action)

        # 添加交互
        role_interact_menu = QMenu("交互", self)
        role_interact_menu.setStyleSheet(
            """
            QMenu{
                background-color:white;
                color:black;
            }
            QMenu::item::selected{
                background-color:black;
                color:white;
            }
            """
        )
        for name in self.roleInteractManagement.get_interact_names():
            role_interact_action = QAction(name, self)
            role_interact_action.triggered.connect(lambda checked, a=role_interact_action: self.clicked_role_interact_action(a))
            role_interact_menu.addAction(role_interact_action)

        menu.addMenu(role_interact_menu)
        menu.addSeparator()  # 分隔线
        screenshot_action = QAction("截图编辑", self)
        screenshot_action.triggered.connect(self.screenshotEdit.start_screenshot_edit)
        menu.addAction(screenshot_action)

        edit_screenshot_action = QAction("编辑截屏", self)
        edit_screenshot_action.triggered.connect(self.screenshotEdit.open_edit_window)
        menu.addAction(edit_screenshot_action)

        screenshot_predict_action = QAction("截图识别", self)
        screenshot_predict_action.triggered.connect(self.screenshotEdit.start_screenshot_predict)
        menu.addAction(screenshot_predict_action)
        menu.addSeparator()  # 分隔线

        get_off_work_action = QAction("下班计时", self)
        get_off_work_action.triggered.connect(self.offWorkWindow.show)
        menu.addAction(get_off_work_action)


        menu.addSeparator()  # 分隔线
        quit_action = QAction("退出程序", self)
        quit_action.triggered.connect(QApplication.quit)
        menu.addAction(quit_action)
        # 3. 在鼠标位置弹出菜单（关键：使用事件的全局位置）
        # exec()：阻塞式；popup()：非阻塞式（推荐）
        menu.popup(event.globalPos())
        event.accept()

    def clicked_role_action(self, action: QAction):
        self.roleGifManagement.gif_name_changed.emit(action.text())

    def clicked_role_interact_action(self, action: QAction):
        self.roleInteractManagement.interact_name_changed.emit(action.text())
    def predict_finished_to_view(self,status,data):
        print(f"识别状态为：{status}")
        self.agentWindow.append_data_to_view(data)

