import os

from dotenv import load_dotenv
from aiokafka.helpers import create_ssl_context

from dto.game_action_dto import CreatePlayerActionDTO, GetPlayerActionDTO, GetFullMapActionDTO, LogoutDTO
from dto.player_action_dto import (
    MovePlayerActionDTO,
    TakeItemActionDTO,
    ListItemsActionDTO,
    UseItemActionDTO,
    AttackActionDTO,
    SkipTurnActionDTO, AwakeTurnActionDTO,
)

load_dotenv()
# ca = os.getenv("KAFKA_SSL_CAFILE")
# cert = os.getenv("KAFKA_SSL_CERTFILE")
# key = os.getenv("KAFKA_SSL_KEYFILE")
# ssl_context = create_ssl_context(
#     cafile=os.getenv("KAFKA_SSL_CAFILE"),
#     certfile=os.getenv("KAFKA_SSL_CERTFILE"),
#     keyfile=os.getenv("KAFKA_SSL_KEYFILE"),
#     password=os.getenv("KAFKA_SSL_PASS"),
# )

# kafka_default_config = {
#     "security_protocol": os.getenv("SECURITY_PROTOCOL"),
#     "bootstrap_servers": os.getenv("BOOTSTRAP_SERVER"),
#     "sasl_mechanism": os.getenv("SASL_MECHANISM"),
#     "sasl_plain_username": os.getenv("SASL_PLAIN_USERNAME"),
#     "sasl_plain_password": os.getenv("SASL_PLAIN_PASSWORD"),
#     "ssl_context": ssl_context,
# }

# kafka_producer_config = {
#     "acks": int(os.getenv("ACKS", 1)),
#     "client_id": os.getenv("PRODUCER_CLIENT_ID", "game_server_producer"),
# }

# kafka_consumer_config = {
#     "group_id": os.getenv("KAFKA_PLAYER_EVENT_GROUP", "game_server_group"),
#     "client_id": os.getenv("CONSUMER_CLIENT_ID", "game_server"),
#     "session_timeout_ms": int(os.getenv("SESSION_TIMEOUT_MS", 45000)),
#     "auto_offset_reset": os.getenv("AUTO_OFFSET_RESET", "latest"),
#     "enable_auto_commit": os.getenv("ENABLE_AUTO_COMMIT", False),
# }

# location_updates_topic = os.getenv("GAME_LOCATION_UPDATE_KAFKA_TOPIC")
# player_updates_topic = os.getenv("GAME_PLAYER_UPDATE_KAFKA_TOPIC")
# game_updates_topic = os.getenv("GAME_GAME_UPDATE_KAFKA_TOPIC")
# player_event_topic = os.getenv("GAME_PLAYER_EVENT_KAFKA_TOPIC")

# game_tick = int(os.getenv("GAME_TICK", "500"))

# db_config = {
#     "url": os.getenv("DB_URL"),
#     "echo": os.getenv("DB_ECHO"),
#     "echo_pool": os.getenv("DB_ECHO_POOL"),
#     "pool_size": os.getenv("DB_POOL_SIZE"),
#     "max_overflow": os.getenv("DB_MAX_OVERFLOW")
# }

# player_config = {
#     "max_health": 100,
#     "max_energy": 100,
#     "max_hungry": 10 * 60 * 1000,  # The player can survive for 10 minutes with a full hunger bar.
#     "default_defence": 8,
#     "default_attack_modifier": 0,
#     "default_attack_damage": 4,
# }

actionDTOMapConfig = {
    "create_player": CreatePlayerActionDTO,
    "get_player": GetPlayerActionDTO,
    "get_full_map": GetFullMapActionDTO,
    "logout": LogoutDTO,

    "move_up": MovePlayerActionDTO,
    "move_down": MovePlayerActionDTO,
    "move_left": MovePlayerActionDTO,
    "move_right": MovePlayerActionDTO,
    "take_item": TakeItemActionDTO,
    "list_items": ListItemsActionDTO,
    "use_item": UseItemActionDTO,
    "attack": AttackActionDTO,
    "skip_turn": SkipTurnActionDTO,
    "awake": AwakeTurnActionDTO,
}
