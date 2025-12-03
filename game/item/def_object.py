import uuid


class DefaultObject:
    def __init__(self):
        self.pos_x = 0
        self.pos_y = 0
        self.id = uuid.uuid4()
        self.name = "void"
        self.__is_solid: bool = False
        self.__is_collectable: bool = False
        self.__is_consumable: bool = False
        self.action: dict[str, object] = {"action": "do_nothing", "params": 0}
        self.hp = -999
        self.world_map = None

    def get_world_map(self):
        return self.world_map

    def set_world_map(self, world_map):
        self.world_map = world_map

    def set_position(self, x, y):
        self.pos_x = x
        self.pos_y = y

    def get_position(self) -> tuple[int, int]:
        return self.pos_x, self.pos_y

    async def decrease_hp(self, amount: int):
        if self.hp > 0:
            self.hp -= amount
            if self.hp <= 0:
                await self.world_map.remove_object_by_id(self.pos_x, self.pos_y, self.id)

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def is_solid(self):
        return self.__is_solid

    def is_collectable(self):
        return self.__is_collectable

    def is_consumable(self):
        return self.__is_consumable

    def set_consumable(self, is_consumable: bool):
        self.__is_consumable = is_consumable

    def set_collectable(self, value: bool):
        self.__is_collectable = value

    def set_solid(self, value: bool):
        self.__is_solid = value

    def set_action(self, action: str):
        self.action = action

    def use(self):
        return self.action

    def __str__(self):
        return f"{self.id}: {self.name} {self.action} {self.pos_x} {self.pos_y}"
