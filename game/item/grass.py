from game.item.def_object import DefaultObject


class Grass(DefaultObject):
    def __init__(self):
        super().__init__()
        self.name = "grass"
         