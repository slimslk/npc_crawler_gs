import threading
import random

from game.errors import LocationNotFoundError
from game.location import Location
from game.game_observer import GameObjectObserver
from game.player import Player
from game.player_controller import PlayerController
from game.location_generator import generate_main_location


class Main:
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _PLAYER_OBSERVER_NAME = "player_observer"
    _MAP_OBSERVER_NAME = "map_observer"

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.locations = {}
            self.player_controllers: dict[str, PlayerController] = {}
            self.main_location = None
            self.users: {str: bool} = {}
            self.observers: dict[str, set] = {}

            Main._initialized = True

    def add_user(self, user_id: str):
        self.users[user_id] = False

    def clear_users(self):
        self.users = {}

    def lock_user(self, user_id: str):
        self.users[user_id] = True

    def unlock_all_users(self):
        for user_id in self.users:
            self.unlock_user(user_id)

    def unlock_user(self, user_id: str):
        self.users[user_id] = False

    def check_is_user_present(self, user_id) -> bool:
        return user_id in self.users

    async def generate_main_location(self) -> Location:
        main_location = await generate_main_location()
        for observer in self.observers.get(self._MAP_OBSERVER_NAME):
            main_location.get_map().add_observer(observer)
        self.add_location(main_location)
        self.main_location = main_location
        return self.main_location

    def get_locations_id(self):
        return [location for location in self.locations.keys()]

    def get_location(self, location_id):
        return self.locations.get(location_id, self.main_location)

    def add_location(self, location):
        self.locations[location.get_location_id()] = location

    async def create_player(self, name, user_id):
        max_height, max_width = self.main_location.get_location_size()
        while True:
            player_coordinates = (random.randint(0, max_height - 1), random.randint(0, max_width - 1))
            if not self.main_location.get_map().get_first_object(*player_coordinates).is_solid():

                player = Player(user_id, name)
                observers = self.observers.get(self._PLAYER_OBSERVER_NAME, None)
                if observers:
                    for observer in observers:
                        player.add_observer(observer)

                player_controller = PlayerController(player)
                self.player_controllers[user_id] = player_controller
                await self.add_player_to_location(player, *player_coordinates,
                                                  location_id=self.main_location.get_location_id())
                break
        await player.notify_observers()
        return player_controller

    def remove_user(self, user_id):
        self.users.pop(user_id, None)
        self.player_controllers.pop(user_id, None)

    async def get_player_controller(self, user_id):
        return await self.__check_if_player_exists(user_id)

    async def add_player_to_location(self, player, pos_x, pos_y, location_id):
        location = self.__check_if_location_exists(location_id)
        await location.add_player(player, pos_x, pos_y)

    async def remove_player_from_location(self, player_id, location_id):
        location = self.__check_if_location_exists(location_id)
        await location.remove_player(player_id)

    def add_map_observer(self, observer: GameObjectObserver):
        self.observers.setdefault(self._MAP_OBSERVER_NAME, set()).add(observer)

    def remove_map_observer(self, observer: GameObjectObserver):
        self.observers.get(self._MAP_OBSERVER_NAME).remove(observer)

    def add_player_observer(self, observer: GameObjectObserver):
        self.observers.setdefault(self._PLAYER_OBSERVER_NAME, set()).add(observer)

    def remove_player_observer(self, observer: GameObjectObserver):
        self.observers.get(self._PLAYER_OBSERVER_NAME).remove(observer)

    def __check_if_location_exists(self, location_id) -> Location:
        location = self.locations.get(location_id, None)
        if location is None:
            raise LocationNotFoundError(location_id)
        return location

    async def __check_if_player_exists(self, user_id) -> PlayerController | None:
        player_controller = self.player_controllers.get(user_id, None)
        return player_controller
