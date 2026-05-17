from functools import lru_cache

from common.config import BaseServiceSettings
from pydantic import Field


class ConsumerServiceSettings(BaseServiceSettings):
    service_name: str = "consumer-service"
    database_url: str = Field(
        default="postgresql+psycopg://ftgo:ftgo@localhost:15432/consumer_db",
        validation_alias="FTGO_CONSUMER_DATABASE_URL",
    )
    sql_echo: bool = False


@lru_cache(maxsize=1)
def get_settings() -> ConsumerServiceSettings:
    return ConsumerServiceSettings()
