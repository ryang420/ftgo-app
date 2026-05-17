from common.config import BaseServiceSettings
from pydantic import Field


class OrderServiceSettings(BaseServiceSettings):
    service_name: str = "order-service"
    database_url: str = Field(
        default="postgresql+psycopg://ftgo:ftgo@localhost:15432/order_db",
        validation_alias="FTGO_ORDER_DATABASE_URL",
    )
    sql_echo: bool = False
