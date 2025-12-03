from game.item.def_object import DefaultObject


class Meat(DefaultObject):
    def __init__(self):
        super().__init__()
        self.set_collectable(True)
        self.set_consumable(True)
        self.action = {"action": "decrease_hungry", "params": [20]}
        self.name = "meat"
        self.hp = 10
