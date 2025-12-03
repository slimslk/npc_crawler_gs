from game.item.def_object import DefaultObject


class Sword(DefaultObject):
    def __init__(self):
        super().__init__()
        self.set_collectable(True)
        self.action = {"action": "attack", "params": [(1, 12)]}
        self.name = "sword"
        self.hp = 100
        