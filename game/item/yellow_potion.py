from game.item.def_object import DefaultObject


class EnergyPotion(DefaultObject):
    def __init__(self):
        super().__init__()
        self.set_collectable(True)
        self.set_consumable(True)
        self.action = {"action": "increase_energy", "params": [50]}
        self.name = "yellow potion"
        self.hp = 5
