from common.api import create_base_app

from app.api.routes import router
from app.config import OrderServiceSettings
import app.infrastructure.db.models  # noqa: F401
from app.infrastructure.db import init_db

settings = OrderServiceSettings()
app = create_base_app(settings.service_name, api_router=router)


@app.on_event("startup")
def create_tables() -> None:
    init_db()
