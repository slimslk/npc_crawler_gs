from game.item.def_object import DefaultObject


class Dummy(DefaultObject):
    def __init__(self):
        super().__init__()
        self.name = "dummy"
        self.hp = 100
        self.set_solid(True)
