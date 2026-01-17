import inspect
import logging
from typing import Any
from abc import ABC, abstractmethod

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from dto.base_action_dto import BaseActionDto
from errors.action_errors import IncorrectActionValues
from game.game_app import Main
from game.player import Player
from game.queue_wrapper import DefaultBufferQueue
from config.settings import settings
from repository.repository import CharacterRepository
from utils.mapper import character_model_to_player
from config.configuration import actionDTOMapConfig


class GameManager(ABC):
    logger = logging.getLogger("game.manager")
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
    _GAME_UPDATE_TOPIC = settings.topic.game_update_kafka_topic
    _PLAYER_UPDATE_TOPIC = settings.topic.player_update_kafka_topic
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
        "awake",
    ]
    _game_actions = [
        "create_player",
        "get_full_map",
        "get_player",
        "logout"
    ]

    def __init__(self,
                 game: Main,
                 kafka_producer,
                 output_queue: DefaultBufferQueue,
                 char_repository: CharacterRepository
                 ):
        self._game: Main = game
        self._kafka_producer = kafka_producer
        self._output_queue = output_queue
        self._users = set()
        self._char_repository = char_repository

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
        action_dto_class = actionDTOMapConfig.get(action, None)
        if action_dto_class is None:
            raise IncorrectActionValues()
        try:
            action_dto: BaseActionDto = action_dto_class(action=action, params_value=params)
        except ValidationError as err:
            raise IncorrectActionValues()
        match action:
            case action if action in self._player_actions:
                await self.__apply_event_to_player(user_id=user_id, action_dto=action_dto)
            case action if action in self._game_actions:
                await self.__apply_event_to_game(user_id=user_id, action_dto=action_dto)
            case _:
                raise IncorrectActionValues(action)

    async def generate_main_location(self):
        await self._game.generate_main_location()
        await self.__get_full_map()

    async def __process_player_death(self, player: Player):
        self._game.remove_user(player.user_id)
        await player.notify_observers()
        await self.__update_payer_data(player)

    async def __get_full_map(self, location_id=None):
        location = self._game.get_location(location_id)
        full_map = location.get_map()
        location_id = full_map.map_id
        full_map_data = {f"{i},{j}": full_map.location_map[i][j][0].name
                         for i in range(len(full_map.location_map)) for j in range(len(full_map.location_map[i]))}
        await self._output_queue.put({
            "topic": self._GAME_UPDATE_TOPIC,
            "key": location_id,
            "value": {"location_id": location_id,
                      "location_size": location.get_location_size(),
                      "location_data": full_map_data}
        })

    async def __get_player(self, user_id, char_id: int) -> Player | None:
        player_controller = await self._game.get_player_controller(user_id)
        if player_controller:
            return player_controller.get_player()
        try:
            char = await self._char_repository.get_by_user_id_and_character_id(user_id, char_id)
            if not char:
                return None
        except SQLAlchemyError as err:
            self.logger.error(f"Character {char_id} not found", exc_info=err)
            return None
        player = character_model_to_player(char)
        return await self._game.return_character_to_game(player, char.stats.location_id)

    async def __create_player(self, name: str, user_id):
        player = await self._game.create_player(name=name, user_id=user_id)
        try:
            await self._char_repository.create(player)
        except SQLAlchemyError as err:
            self.logger.error(f"Creating char: {player.name} of user: {user_id} is fail", exc_info=err)
            await self._game.remove_player_from_location(player, player.world.map_id)
            return None
        await self._game.create_player_controller(player)
        return player

    async def __apply_event_to_player(self, user_id, action_dto: BaseActionDto):
        player_controller = await self._game.get_player_controller(user_id)
        if player_controller is None:
            return
        if player_controller.get_player().is_dead:
            await self.__process_player_death(player_controller.get_player())
            return
        method = getattr(player_controller, action_dto.action, "skip_turn")
        if method is None or not callable(method):
            raise IncorrectActionValues()
        if inspect.iscoroutinefunction(method):
            result = await method(action_dto.params_value)
        else:
            result = method(action_dto.params_value)

    async def __update_payer_data(self, player: Player):
        try:
            await self._char_repository.update_stats(player)
        except SQLAlchemyError as err:
            self.logger.error(f"Character {player.char_id} not found", exc_info=err)
            return None

    async def __apply_event_to_game(self, action_dto: BaseActionDto, user_id: str):

        match action_dto.action:
            case "logout":
                player = await self.__get_player(user_id, action_dto.params_value)
                if player:
                    try:
                        self._game.remove_user(user_id)
                        await self._char_repository.update_stats(player)
                        return
                    except SQLAlchemyError as err:
                        self.logger.error(f"Character {player.char_id} not found", exc_info=err)
                await self.__send_char_not_found_message(user_id)

            case "create_player":
                player = await self.__create_player(action_dto.params_value, user_id=user_id)
                if player:
                    await player.notify_observers()
                else:
                    await self.__send_char_not_found_message(user_id)

            case "get_full_map":
                await self.__get_full_map(action_dto.params_value)

            case "get_player":
                player = await self.__get_player(user_id, action_dto.params_value)
                if player:
                    await player.notify_observers()
                else:
                    await self.__send_char_not_found_message(user_id)

            case _:
                raise IncorrectActionValues()

    async def __send_char_not_found_message(self, user_id: str):
        await self._output_queue.put({
            "topic": self._PLAYER_UPDATE_TOPIC,
            "key": user_id,
            "value": {"error_info": "Character did not found.", }
        })