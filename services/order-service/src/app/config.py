from common.config import BaseServiceSettings


class OrderServiceSettings(BaseServiceSettings):
    service_name: str = "order-service"
    database_url: str = "postgresql+psycopg://ftgo:ftgo@localhost:5432/order_db"
    sql_echo: bool = False
