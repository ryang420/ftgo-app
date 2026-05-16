from functools import lru_cache

from common.config import BaseServiceSettings


class ConsumerServiceSettings(BaseServiceSettings):
    service_name: str = "consumer-service"
    database_url: str = "postgresql+psycopg://ftgo:ftgo@localhost:5432/consumer_db"
    sql_echo: bool = False


@lru_cache(maxsize=1)
def get_settings() -> ConsumerServiceSettings:
    return ConsumerServiceSettings()
