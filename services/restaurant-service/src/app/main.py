from common.api import create_base_app

from app.api.routes import restaurants_router
from app.config import get_settings
from app.domain import models  # noqa: F401
from app.infrastructure.db import init_db

settings = get_settings()
app = create_base_app(settings.service_name, api_router=restaurants_router)


@app.on_event("startup")
def create_tables() -> None:
    init_db()
