from errors.errors import ObjectPositionIsOutOfBoundsError, PositionIsOccupiedError, PlayerPositionIsOutOfBoundsError
from game.item.def_object import DefaultObject
from game.item.grass import Grass
from game.map import Map
from game.player import Player


class Location:
    def __init__(self, location_map: Map, name: str = "default"):
        self.__location_name = name
        self.__location_map: Map = location_map
        # self.__location_id = location_map.map_id
        self.__players = {}
        self.__location_height = len(location_map.location_map)
        self.__location_width = len(location_map.location_map[0])

    def get_map(self):
        return self.__location_map

    def get_location_size(self):
        return self.__location_height, self.__location_width

    def get_location_id(self):
        return self.__location_id

    async def add_player(self, player: Player, x, y):
        if x > self.__location_height or y > self.__location_width:
            raise PlayerPositionIsOutOfBoundsError(f"Location ID: {self.__location_id}\n x = {x}, y = {y} out of bounds"
                                                   f" max_x = {self.__location_height} max_y = {self.__location_width}")
        player.world = self.__location_map
        await self.__location_map.place_object(player, x, y)
        player.set_position(x, y)
        self.__players[player.char_id] = player

    async def remove_player(self, player: Player):
        char_id = player.char_id
        if char_id in self.__players:
            del self.__players[char_id]

    async def add_object_to_world(self, game_object: DefaultObject, pos_x: int, pos_y: int):
        if pos_x > self.__location_height or pos_y > self.__location_width:
            raise ObjectPositionIsOutOfBoundsError(
                f"{game_object}: Location ID: {self.__location_id}\n x = {pos_x}, y = {pos_y} out of bounds"
                f" max_x = {self.__location_height} max_y = {self.__location_width}")
        obj_on_map = self.__location_map.get_first_object(pos_x, pos_y)
        if obj_on_map.is_solid():
            raise PositionIsOccupiedError(f"x = {pos_x}, y = {pos_y} is occupied!")
        if game_object is not Grass:
            game_object.world_map = self.__location_map
            await self.__location_map.place_object(game_object, pos_x, pos_y)
            game_object.set_position(pos_x, pos_y)

    def get_players(self):
        return self.__players
