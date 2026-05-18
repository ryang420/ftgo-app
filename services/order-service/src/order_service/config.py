from common.config import BaseServiceSettings
from pydantic import Field


class OrderServiceSettings(BaseServiceSettings):
    service_name: str = "order-service"
    database_url: str = Field(
        default="postgresql+psycopg://ftgo:ftgo@localhost:15432/order_db",
        validation_alias="FTGO_ORDER_DATABASE_URL",
    )
    amqp_url: str = Field(
        default="amqp://ftgo:ftgo@localhost:5672/",
        validation_alias="FTGO_AMQP_URL",
    )
    restaurant_service_url: str = Field(
        default="http://localhost:8002",
        validation_alias="FTGO_RESTAURANT_SERVICE_URL",
    )
    consumer_service_url: str = Field(
        default="http://localhost:8001",
        validation_alias="FTGO_CONSUMER_SERVICE_URL",
    )
    upstream_timeout_seconds: float = Field(
        default=10.0,
        validation_alias="FTGO_UPSTREAM_TIMEOUT_SECONDS",
    )
    sql_echo: bool = False
