from functools import lru_cache

from common.config import BaseServiceSettings


class RestaurantServiceSettings(BaseServiceSettings):
    service_name: str = "restaurant-service"
    database_url: str = "postgresql+psycopg://ftgo:ftgo@localhost:5432/restaurant_db"
    sql_echo: bool = False


@lru_cache
def get_settings() -> RestaurantServiceSettings:
    return RestaurantServiceSettings()
