import asyncio
import json
import threading

from aiokafka import AIOKafkaProducer

from game.game_app import Main
from game.queue_wrapper import DefaultBufferQueue
from config.configuration import (kafka_default_config,
                                  kafka_producer_config,
                                  location_updates_topic,
                                  game_updates_topic,
                                  player_updates_topic)


class AIOGameMapKafkaProducer:
    _instance = None
    _lock = threading.Lock()
    _initialized = False
    _is_running = False
    _kafka_config = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, output_queue: DefaultBufferQueue, game: Main, tick: int):
        if not self._initialized:
            self.game = game
            self.tick = tick
            self.producer = None
            self._output_queue = output_queue
            self._kafka_config = self._get_kafka_config().copy()
            self._kafka_config["acks"] = kafka_producer_config["acks"]
            self._kafka_config["client_id"] = kafka_producer_config["client_id"]

            self._initialized = True

    def _get_kafka_config(self):
        return kafka_default_config

    async def start(self):
        if not self._is_running:
            try:
                self.producer = AIOKafkaProducer(**self._kafka_config)
                await self.producer.start()
            except Exception as err:
                print(f"Producer Kafka error: {err}")
                return
            self._is_running = True

    async def run(self, stop_event: asyncio.Event):
        if self.producer is None:
            await self.start()
        try:
            while not stop_event.is_set():
                await asyncio.sleep(self.tick / 1000)
                buffer = await self._output_queue.drain_buffer()

                try:
                    for topic, data in buffer.items():
                        if topic == player_updates_topic:
                            await self._send_player_updates(data)
                        elif topic == location_updates_topic:
                            await self._send_location_updates(data)
                        elif topic == game_updates_topic:
                            await self._send_game_updates(data)
                    self.game.unlock_all_users()
                except Exception as err:
                    print(f"Kafka error sending message: {err}")

        except asyncio.CancelledError:
            print("Producer task cancelled.")
        finally:
            await self.close()
            self._is_running = False

    async def close(self):
        if self.producer:
            await self.producer.stop()

    async def _send_game_updates(self, data):
        for key, value in data.items():
            await self._send_message(game_updates_topic, key, value)

    async def _send_location_updates(self, data):
        for key, value in data.items():
            await self._send_message(location_updates_topic, key, value)

    async def _send_player_updates(self, data: dict[str, str]):
        user_ids = self.game.player_controllers.keys()
        for user_id in user_ids:
            user_params: dict | None = data.get(user_id, None)
            if user_params is None:
                player = self.game.player_controllers.get(user_id)
                await player.skip_turn()
                # user_params = player.get_player().get_player_parameters()
                if user_params is None:
                    continue
            await self._send_message(player_updates_topic, user_id, user_params)

    async def _send_message(self, topic, key, value):
        encoded_message = self._ecode_message(key, value)
        metadata = await self.producer.send_and_wait(topic=topic,
                                                     key=encoded_message.get("key"),
                                                     value=encoded_message.get("value"))

    def _ecode_message(self, key: str, value: dict) -> dict:
        new_message = {
            "key": key.encode("utf-8"),
            "value": json.dumps(value).encode("utf-8"),
        }
        return new_message
