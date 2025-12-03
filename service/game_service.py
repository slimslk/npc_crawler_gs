import inspect
import random
from typing import Any
from abc import ABC, abstractmethod

import game.characters as characters
from game.errors import InvalidActionNameError
from game.game_app import Main
from game.queue_wrapper import DefaultBufferQueue
from config.configuration import game_updates_topic


class GameManager(ABC):
    _observers = []
    _game = None

    @abstractmethod
    async def process_event(self, user_id, data: Any):
        pass

    @abstractmethod
    def register_observer(self, observer):
        pass

    @abstractmethod
    def unregister_observer(self, observer):
        pass


class KafkaGameManager(GameManager):
    _player_actions = [
        "move_up",
        "move_down",
        "move_left",
        "move_right",
        "take_item",
        "get_items_list",
        "use_item",
        "attack",
        "skip_turn",
    ]
    _game_actions = [
        "create_player",
        "get_full_map",
        "get_player_info",
        "get_map_size",
        "get_player",
    ]

    def __init__(self, game: Main, kafka_producer, output_queue: DefaultBufferQueue):
        self._game: Main = game
        self._kafka_producer = kafka_producer
        self._output_queue = output_queue
        self._users = set()

    def register_observer(self, observer):
        self._game.add_map_observer(observer)

    def unregister_observer(self, observer):
        self._game.remove_map_observer(observer)

    async def process_event(self, user_id, data: Any):
        if not self._game.check_is_user_present(user_id):
            self._game.add_user(user_id)
        if self._game.users[user_id]:
            return
        self._game.lock_user(user_id)
        action = data.get("action", "")
        params = data.get("params", [])
        if params is None:
            params = []
        match action:
            case action if action in self._player_actions:
                await self.__apply_event_to_player(user_id, action, params)
            case action if action in self._game_actions:
                await self.__apply_event_to_game(action, params, user_id=user_id)
            case _:
                raise InvalidActionNameError(action)

    def __process_player_death(self, user_id):
        self._game.remove_user(user_id)

    async def __get_full_map(self, location_id=None):
        location = self._game.get_location(location_id)
        full_map = location.get_map()
        location_id = full_map.map_id
        full_map_data = {f"{i},{j}": full_map.location_map[i][j][0].name
                         for i in range(len(full_map.location_map)) for j in range(len(full_map.location_map[i]))}
        await self._output_queue.put({
            "topic": game_updates_topic,
            "key": location_id,
            "value": {"location_id": location_id,
                      "location_size": location.get_location_size(),
                      "location_data": full_map_data}
        })

    async def __get_player(self, user_id):
        player_controller = await self._game.get_player_controller(user_id)
        if player_controller:
            await self.__fetch_player_parameters(user_id)
        else:
            await self.__create_player(characters.get_character_name(random.randint(1, 11)), user_id=user_id)

    async def __fetch_player_parameters(self, user_id):
        player_controller = await self._game.get_player_controller(user_id)
        player_info = player_controller.get_player_info()
        # await self._output_queue.put({
        #     "topic": player_updates_topic,
        #     "key": user_id,
        #     "value": player_info
        # })

    async def __create_player(self, *params, user_id):
        player_controller = await self._game.create_player(*params, user_id=user_id)

    async def __apply_event_to_player(self, user_id, action, params):
        player_controller = await self._game.get_player_controller(user_id)
        if player_controller is None:
            return
        method = getattr(player_controller, action, "skip_turn")
        if method is None or not callable(method):
            raise InvalidActionNameError(action)
        if inspect.iscoroutinefunction(method):
            result = await method(*params)
        else:
            result = method(*params)

        player_params = player_controller.get_player().get_player_parameters()
        if player_params["is_dead"]:
            self.__process_player_death(user_id)

    async def generate_main_location(self):
        await self._game.generate_main_location()
        await self.__get_full_map()

    async def __apply_event_to_game(self, action, params, user_id):
        match action:
            case "create_player":
                await self.__create_player(*params, user_id=user_id)
            case "get_full_map":
                await self.__get_full_map(*params)
            case "get_player_info":
                await self.__fetch_player_parameters(user_id)
            case "get_map_size":
                await self.__fetch_player_parameters(user_id)
            case "get_player":
                await self.__get_player(user_id)

            case _:
                raise InvalidActionNameError(action)
