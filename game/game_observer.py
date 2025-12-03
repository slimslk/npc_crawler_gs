from abc import ABC, abstractmethod
from datetime import datetime

from game.queue_wrapper import DefaultBufferQueue
from config.configuration import location_updates_topic, player_updates_topic


class GameObjectObserver(ABC):
    @abstractmethod
    async def update(self, data):
        pass


class KafkaMapObserver(GameObjectObserver):
    __updated_data_map: dict[str: dict[tuple, str]] = {}
    __old_map_data: dict[datetime, dict] = {}

    def __init__(self, output_queue: DefaultBufferQueue):
        self._output_queue = output_queue

    async def update(self, data):
        for key, value in data.items():
            location_map = self.__updated_data_map.get(key)
            if location_map:
                location_map.update(value)
            else:
                self.__updated_data_map[key] = value
        await self.flush_map_data()

    async def flush_map_data(self):
        for map_id, map_data in self.__updated_data_map.items():
            msg = self._build_message(map_id, map_data)
            await self._output_queue.put(msg)
        self._store_data()

    def _store_data(self):
        self.__old_map_data[datetime.now()] = self.__updated_data_map
        self.__updated_data_map.clear()

    def _build_message(self, map_id, map_data) -> dict[str: object]:
        msg = {
            "topic": location_updates_topic,
            "key": map_id,
            "value": map_data
        }
        return msg


class KafkaPlayerObserver(GameObjectObserver):

    def __init__(self, output_queue: DefaultBufferQueue):
        self._output_queue = output_queue

    async def update(self, data):
        for key, value in data.items():
            await self.flush_map_data(key, value)

    async def flush_map_data(self, user_id, player_data):
        msg = self._build_message(user_id, player_data)
        await self._output_queue.put(msg)

    def _build_message(self, user_id, player_data) -> dict[str: object]:
        msg = {
            "topic": player_updates_topic,
            "key": user_id,
            "value": player_data
        }
        return msg
