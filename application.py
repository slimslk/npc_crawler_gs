import asyncio
import logging
from logging.handlers import RotatingFileHandler

from errors.errors import DefaultError
from game.game_app import Main
from game.game_observer import KafkaMapObserver, KafkaPlayerObserver
from game.queue_wrapper import BufferQueueWithLock
from kafka.consumer_async import AIOGameMapKafkaConsumer
from kafka.producer_async import AIOGameMapKafkaProducer
from repository.repository import CharacterRepository
from service.game_service import KafkaGameManager
from config.settings import settings
from db.db import db_helper

log_handler = RotatingFileHandler(
    'app.log',
    maxBytes=5 * 1024 * 1024,
    backupCount=3
)

formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
log_handler.setFormatter(formatter)

logger = logging.getLogger("app")
logger.setLevel(logging.ERROR)
logger.addHandler(log_handler)


async def main():
    __GAME_TICK = settings.game.tick
    stop_event = None
    consumer_task = None
    producer_task = None
    try:
        game = Main()
        output_queue = BufferQueueWithLock()
        stop_event = asyncio.Event()
        char_repository = CharacterRepository()
        kafka_map_producer = AIOGameMapKafkaProducer(output_queue, game, tick=__GAME_TICK)
        game_manager = KafkaGameManager(game, kafka_map_producer, output_queue, char_repository)
        kafka_observer = KafkaMapObserver(output_queue)
        player_observer = KafkaPlayerObserver(output_queue)
        game.add_map_observer(kafka_observer)
        game.add_player_observer(player_observer)
        await game_manager.generate_main_location()
        kafka_game_event_consumer = AIOGameMapKafkaConsumer(game_manager)

        await kafka_map_producer.start()
        await kafka_game_event_consumer.start()

        producer_task = asyncio.create_task(kafka_map_producer.run(stop_event))
        consumer_task = asyncio.create_task(kafka_game_event_consumer.run(stop_event))

        result = await asyncio.gather(consumer_task, producer_task)
        for er in result:
            if isinstance(er, DefaultError):
                logger.error(f"GameError: {er}")
            if isinstance(er, Exception):
                logger.exception(f"Application Error: {er}")
                raise asyncio.CancelledError
    except asyncio.CancelledError:
        print("Tasks cancelled from main.")
    finally:
        await db_helper.dispose()
        if stop_event:
            stop_event.set()
        if consumer_task:
            consumer_task.cancel()
        if producer_task:
            producer_task.cancel()
        await asyncio.gather(producer_task, consumer_task, return_exceptions=True)
        print("Graceful shutdown.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Shutting down gracefully...")
