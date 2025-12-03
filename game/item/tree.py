from game.item.def_object import DefaultObject


class Tree(DefaultObject):
    def __init__(self):
        super().__init__()
        self.set_solid(True)
        self.name = "tree"

