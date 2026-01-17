import asyncio
from abc import ABC, abstractmethod

from config.settings import settings


class DefaultBufferQueue(ABC):

    @abstractmethod
    async def put(self, message):
        pass

    @abstractmethod
    async def drain_buffer(self) -> dict:
        pass


class BufferQueueWithLock(DefaultBufferQueue):
    def __init__(self):
        self._updates_buffer = {}
        self._lock = asyncio.Lock()
        self._location_updates_topic = settings.topic.location_update_kafka_topic
        self._player_updates_topic = settings.topic.player_update_kafka_topic

    async def put(self, message):
        async with self._lock:
            topic = message.get("topic")
            key = message.get("key")
            if topic == self._location_updates_topic:
                self._update_location_map(topic, key, message.get("value"))
                return
            self._updates_buffer.setdefault(topic, {})[key] = message.get("value")

    async def drain_buffer(self) -> dict[str, str]:
        async with self._lock:
            snapshot = self._updates_buffer
            self._updates_buffer = {self._player_updates_topic: {}}
        return snapshot

    def _update_location_map(self, topic, location_id, updates):
        buffer = self._updates_buffer.setdefault(topic, {})
        location = self._updates_buffer[topic].get(location_id)
        if location is None:
            buffer[location_id] = updates
        else:
            location.update(updates)
