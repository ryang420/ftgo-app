from fastapi import FastAPI

from common.api import create_base_app

from app.api.routes import consumers_router
from app.config import get_settings
from app.infrastructure.db import init_db


def create_app() -> FastAPI:
    settings = get_settings()
    app = create_base_app(settings.service_name, api_router=consumers_router)
    app.state.settings = settings

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    return app


app = create_app()
