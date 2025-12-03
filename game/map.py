import uuid

from game.item.corpse import Corpse
from game.item.def_object import DefaultObject


class Map:
    __DEFAULT_SIZE = 10
    __observers = set()
    __map_width = 0
    __map_height = 0

    def __init__(self, loc_map=None):
        if loc_map is None:
            loc_map = [[[] for _ in range(self.__DEFAULT_SIZE)] for _ in range(self.__DEFAULT_SIZE)]
        self.location_map = loc_map
        self.__map_width = len(loc_map[0])
        self.__map_height = len(loc_map)
        self.map_id = str(uuid.uuid4())

    def add_observer(self, observer):
        self.__observers.add(observer)

    def remove_observer(self, observer):
        self.__observers.remove(observer)

    def get_map(self):
        return self.location_map

    def set_map(self, init_map):
        self.location_map = init_map

    def get_map_size(self):
        return self.__map_height, self.__map_width

    def get_first_object(self, x, y):
        return self.location_map[x][y][0]

    def get_objects(self, x, y):
        return self.location_map[x][y]

    async def notify_observers(self, data):
        for observer in self.__observers:
            await observer.update(data)

    async def remove_first_object(self, x: int, y: int):
        if len(self.location_map[x][y]) == 1:
            return None
        removed_obj = self.location_map[x][y].pop(0)
        await self.notify_observers({
            self.map_id: {f"{x},{y}": self.location_map[x][y][0].name}
        })
        return removed_obj

    async def remove_object_by_id(self, x, y, item_id: uuid.UUID):
        objects = self.location_map[x][y]
        for item in objects:
            if item.id == item_id:
                self.location_map[x][y].remove(item)
        await self.notify_observers({
            self.map_id: {f"{x},{y}": self.location_map[x][y][0].name}
        })

    async def place_object(self, object_type, x, y):
        await self.place_objects([object_type], x, y)

    async def place_objects(self, objects: list, x, y):
        for obj in objects:
            obj.set_position(x, y)
        self.location_map[x][y][:0] = objects
        await self.notify_observers({
            self.map_id: {f"{x},{y}": self.location_map[x][y][0].name}
        })

    async def replace_object(self, object_type: DefaultObject, x, y, position=0):
        if not object_type.is_solid():
            if type(object_type) is Corpse:
                self.location_map[x][y].pop(0)
                self.location_map[x][y].insert(-1, object_type)
            else:
                self.location_map[x][y][position] = object_type
            await self.notify_observers({
                self.map_id: {f"{x},{y}": self.location_map[x][y][0].name}
            })

    async def move_player(self, player, old_x, old_y, new_x, new_y):
        self.location_map[new_x][new_y].insert(0, player)
        self.location_map[old_x][old_y].pop(0)
        await self.notify_observers({
            self.map_id: {f"{old_x},{old_y}": self.location_map[old_x][old_y][0].name,
                          f"{new_x},{new_y}": player.name}
        })
