from common.api import create_base_app

from restaurant_service.api.routes import router
from restaurant_service.config import get_settings
from restaurant_service.infrastructure.db import init_db

settings = get_settings()
app = create_base_app(settings.service_name, api_router=router)


@app.on_event("startup")
def create_tables() -> None:
    init_db()
