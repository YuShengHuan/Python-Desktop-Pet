
from PySide6.QtCore import *

from widget.role.food.ShapeFood import ShapeFood


class ShapeFoodManagement(QObject):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.feeding_foods = []
        self.food_count = 30

    def start_feeding_food(self):
        if len(self.feeding_foods) == 0:
            for i in range(self.food_count):
                food = ShapeFood()
                food.set_food_id(
                    i
                )
                food.clicked.connect(self.clicked_food)
                self.feeding_foods.append(
                    food
                )
                food.start_move(i*700)

        else:
            print("还有食物")

    def clicked_food(self, food_id):
        print(f"吃掉食物{food_id}")
        for x in range(len(self.feeding_foods)):
            if self.feeding_foods[x].food_id == food_id:
                self.feeding_foods.remove(
                    self.feeding_foods[x]
                )
                print(f"食物移除成功")
                break

