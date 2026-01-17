import asyncio
import json

from aiokafka import AIOKafkaConsumer
from aiokafka.errors import KafkaError
from config.settings import settings, consumer_kafka_settings


class AIOGameMapKafkaConsumer:
    _poll_timeout = 1
    _consumer_config = {}

    def __init__(self, game_manager):
        self.topics = [settings.topic.player_event_kafka_topic]
        self.game_manager = game_manager
        self.consumer: AIOKafkaConsumer | None = None
        self._running = False

    async def start(self):
        if not self._running:
            try:
                self.consumer = AIOKafkaConsumer(**consumer_kafka_settings.get_config())
                self.consumer.subscribe(self.topics)
                await self.consumer.start()
            except KafkaError as err:
                print(f"Consumer Kafka start error: {err}")
                return
            self._running = True

    async def run(self, stop_event: asyncio.Event):
        try:
            while not stop_event.is_set():
                try:
                    messages = await self.consumer.getmany(timeout_ms=250, max_records=10)
                    if messages:
                        await self.__process_messages(messages)
                except RuntimeError as err:
                    print(f"Consumer Kafka error: {err}")
        except asyncio.CancelledError:
            print("Consumer task cancelled.")
        finally:
            await self.close()

    async def __process_messages(self, batch):
        for topic_part, records in batch.items():
            for record in records:
                key = record.key.decode("utf-8")
                value = json.loads(record.value.decode("utf-8"))
                await self.game_manager.process_event(key, value)

    async def close(self):
        if self.consumer:
            await self.consumer.stop()
