import os
import ssl
from typing import Any

from aiokafka.helpers import create_ssl_context
from pydantic import BaseModel, model_validator
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    DotEnvSettingsSource,
    SettingsConfigDict
)
from utils.helper import build_from_settings


class PlayerSettings(BaseModel):
    max_health: int = 100
    max_energy: int = 100
    max_hungry: int = 10 * 60 * 1000  # The player can survive for 10 minutes with a full hunger bar.
    default_defence: int = 8
    default_attack_modifier: int = 0
    default_attack_damage: int = 4


class KafkaSettings(BaseModel):
    ssl_cafile: str | None = None
    ssl_certfile: str | None = None
    ssl_keyfile: str | None = None
    ssl_pass: str | None = None

    security_protocol: str = "PLAINTEXT"
    bootstrap_servers: str
    sasl_mechanism: str | None = None
    sasl_plain_username: str | None = None
    sasl_plain_password: str | None = None
    ssl_context: ssl.SSLContext | None = None

    model_config = {
        "arbitrary_types_allowed": True
    }

    @model_validator(mode="after")
    def create_ssl_context(self):
        if (
                self.ssl_cafile
                and self.ssl_certfile
                and self.ssl_keyfile
        ):
            self.ssl_context = create_ssl_context(
                cafile=self.ssl_cafile,
                certfile=self.ssl_certfile,
                keyfile=self.ssl_keyfile,
                password=self.ssl_pass,
            )
        return self


class KafkaBaseSettingsMixin:
    base: KafkaSettings

    def _base_kafka_config(self) -> dict[str, Any]:
        return {
            **self.base.model_dump(exclude={"ssl_context",
                                            "ssl_cafile",
                                            "ssl_certfile",
                                            "ssl_keyfile",
                                            "ssl_pass",
                                            }),
            "ssl_context": self.base.ssl_context,
        }


class KafkaProducerSettings(KafkaBaseSettingsMixin, BaseModel):
    base: KafkaSettings
    acks: int
    client_id: str

    def get_config(self) -> dict[str, Any]:
        return {
            **self._base_kafka_config(),
            "acks": self.acks,
            "client_id": self.client_id,
        }


class KafkaConsumerSettings(KafkaBaseSettingsMixin, BaseModel):
    base: KafkaSettings
    player_event_group: str
    client_id: str
    session_timeout_ms: int
    auto_offset_reset: str
    enable_auto_commit: bool

    def get_config(self) -> dict[str, Any]:
        return {
            **self._base_kafka_config(),
            "group_id": self.player_event_group,
            "client_id": self.client_id,
            "session_timeout_ms": self.session_timeout_ms,
            "auto_offset_reset": self.auto_offset_reset,
            "enable_auto_commit": self.enable_auto_commit,
        }


class KafkaTopics(BaseModel):
    location_update_kafka_topic: str = "location_updates"
    player_update_kafka_topic: str = "player_updates"
    game_update_kafka_topic: str = "game_updates"
    player_event_kafka_topic: str = "player_events"


class GameSettings(BaseModel):
    tick: int = 500


class DBSettings(BaseModel):
    url: str
    echo: bool
    echo_pool: bool
    pool_size: int
    max_overflow: int
    current_schema: str = "public"


class Settings(BaseSettings):
    player: PlayerSettings  # = PlayerSettings()
    kafka: KafkaSettings  # = KafkaSettings()
    topic: KafkaTopics  # = KafkaTopics()
    game: GameSettings  # = GameSettings()
    db: DBSettings  # = DBSettings()

    # Consumer settings
    kafka_consumer_player_event_group: str = "game_server_group"
    kafka_consumer_client_id: str = "game_server"
    kafka_consumer_session_timeout_ms: int = 45000
    kafka_consumer_auto_offset_reset: str = "latest"
    kafka_consumer_enable_auto_commit: bool = False

    # Producer settings
    kafka_producer_acks: int = 1
    kafka_producer_client_id: str = "game_server_producer"

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        env = os.getenv("APP_ENV", "dev")
        env_specific = DotEnvSettingsSource(
            settings_cls,
            env_file=f".env.{env}",
            env_file_encoding="utf-8",

        )
        return (
            init_settings,
            env_settings,
            dotenv_settings,
            env_specific,
            file_secret_settings,
        )

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
        env_file=".env",
        env_file_encoding="utf-8",
    )


def build_kafka_consumer_settings(settings: Settings):
    return build_from_settings(base=settings.kafka,
                               settings=settings,
                               prefix="kafka_consumer",
                               model=KafkaConsumerSettings)


def build_kafka_producer_settings(settings: Settings):
    return build_from_settings(base=settings.kafka,
                               settings=settings,
                               prefix="kafka_producer",
                               model=KafkaProducerSettings)


settings = Settings()

producer_kafka_settings = build_kafka_producer_settings(settings=settings)
consumer_kafka_settings = build_kafka_consumer_settings(settings=settings)
