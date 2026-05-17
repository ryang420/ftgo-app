from functools import lru_cache

from common.config import BaseServiceSettings
from pydantic import Field


class RestaurantServiceSettings(BaseServiceSettings):
    service_name: str = "restaurant-service"
    database_url: str = Field(
        default="postgresql+psycopg://ftgo:ftgo@localhost:15432/restaurant_db",
        validation_alias="FTGO_RESTAURANT_DATABASE_URL",
    )
    sql_echo: bool = False


@lru_cache
def get_settings() -> RestaurantServiceSettings:
    return RestaurantServiceSettings()
