import os

from dotenv import load_dotenv
from aiokafka.helpers import create_ssl_context

load_dotenv()
ca = os.getenv("KAFKA_SSL_CAFILE")
cert = os.getenv("KAFKA_SSL_CERTFILE")
key = os.getenv("KAFKA_SSL_KEYFILE")
ssl_context = create_ssl_context(
    cafile=os.getenv("KAFKA_SSL_CAFILE"),
    certfile=os.getenv("KAFKA_SSL_CERTFILE"),
    keyfile=os.getenv("KAFKA_SSL_KEYFILE"),
    password=os.getenv("KAFKA_SSL_PASS"),
)

kafka_default_config = {
    "security_protocol": os.getenv("SECURITY_PROTOCOL"),
    "bootstrap_servers": os.getenv("BOOTSTRAP_SERVER"),
    "sasl_mechanism": os.getenv("SASL_MECHANISM"),
    "sasl_plain_username": os.getenv("SASL_PLAIN_USERNAME"),
    "sasl_plain_password": os.getenv("SASL_PLAIN_PASSWORD"),
    "ssl_context": ssl_context,
}

kafka_producer_config = {
    "acks": int(os.getenv("ACKS", 1)),
    "client_id": os.getenv("PRODUCER_CLIENT_ID", "game_server_producer"),
}

kafka_consumer_config = {
    "group_id": os.getenv("KAFKA_PLAYER_EVENT_GROUP", "game_server_group"),
    "client_id": os.getenv("CONSUMER_CLIENT_ID", "game_server"),
    "session_timeout_ms": int(os.getenv("SESSION_TIMEOUT_MS", 45000)),
    "auto_offset_reset": os.getenv("AUTO_OFFSET_RESET", "latest"),
    "enable_auto_commit": os.getenv("ENABLE_AUTO_COMMIT", False),
}

location_updates_topic = os.getenv("GAME_LOCATION_UPDATE_KAFKA_TOPIC")
player_updates_topic = os.getenv("GAME_PLAYER_UPDATE_KAFKA_TOPIC")
game_updates_topic = os.getenv("GAME_GAME_UPDATE_KAFKA_TOPIC")
player_event_topic = os.getenv("GAME_PLAYER_EVENT_KAFKA_TOPIC")

game_tick = int(os.getenv("GAME_TICK", "500"))

