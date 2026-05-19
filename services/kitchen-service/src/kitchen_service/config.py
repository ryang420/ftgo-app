from functools import lru_cache

from common.config import BaseServiceSettings
from pydantic import Field


class KitchenServiceSettings(BaseServiceSettings):
    service_name: str = "kitchen-service"
    database_url: str = Field(
        default="postgresql+psycopg://ftgo:ftgo@localhost:15432/kitchen_db",
        validation_alias="FTGO_KITCHEN_DATABASE_URL",
    )
    amqp_url: str = Field(
        default="amqp://ftgo:ftgo@localhost:5672/",
        validation_alias="FTGO_AMQP_URL",
    )
    sql_echo: bool = False


@lru_cache(maxsize=1)
def get_settings() -> KitchenServiceSettings:
    return KitchenServiceSettings()
