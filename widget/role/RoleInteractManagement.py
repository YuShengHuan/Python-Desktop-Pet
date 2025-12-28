
from PySide6.QtCore import *

from widget.role import RoleGifManagement
from widget.role.food.ShapeFoodManagement import ShapeFoodManagement
from widget.role.walk.FollowWalkManagement import FollowWalkManagement
from widget.role.walk.RandomWalkManagement import RandomWalkManagement


class RoleInteractManagement(QObject):
    interact_name_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.interact_name_changed.connect(self.click_role_interact_action)
        self.roleGifManagement = None
        self.interact_names = [
            "投喂",
            "玩耍",
            "随意行走"
        ]
        self.shapeFoodManagement = ShapeFoodManagement()
        self.followWalkManagement=FollowWalkManagement()
        self.randomWalkManagement=RandomWalkManagement()

    def get_interact_names(self):
        return self.interact_names

    def set_gif_role_management(self, management: RoleGifManagement):
        if not self.roleGifManagement:
            self.roleGifManagement = management

    def click_role_interact_action(self, text):
        if text == self.interact_names[0]:
            self.shapeFoodManagement.start_feeding_food()
        elif text == self.interact_names[1]:
            self.followWalkManagement.start_follow_play()
        elif text == self.interact_names[2]:
            self.randomWalkManagement.start_walk()

