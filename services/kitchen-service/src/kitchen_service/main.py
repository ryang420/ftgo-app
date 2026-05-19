from common.api import create_base_app

from kitchen_service.api.routes import router
from kitchen_service.config import get_settings
from kitchen_service.infrastructure.db import init_db

settings = get_settings()
app = create_base_app(settings.service_name, api_router=router)


@app.on_event("startup")
def create_tables() -> None:
    init_db()
