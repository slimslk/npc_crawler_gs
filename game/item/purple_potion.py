from game.item.def_object import DefaultObject


class SleepPotion(DefaultObject):
    def __init__(self):
        super().__init__()
        self.set_collectable(True)
        self.set_consumable(True)
        self.action = {"action": "sleep", "params": []}
        self.name = "red potion"
        self.hp = 5
