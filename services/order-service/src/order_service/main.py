from common.api import create_base_app

import order_service.infrastructure.db.models  # noqa: F401
from order_service.api.routes import router
from order_service.config import OrderServiceSettings
from order_service.infrastructure.db import init_db

settings = OrderServiceSettings()
app = create_base_app(settings.service_name, api_router=router)


@app.on_event("startup")
def create_tables() -> None:
    init_db()
