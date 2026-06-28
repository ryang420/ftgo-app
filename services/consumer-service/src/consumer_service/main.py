from common.api import create_base_app
from fastapi import FastAPI

from consumer_service.api.routes import consumers_router
from consumer_service.config import get_settings
from consumer_service.infrastructure.db import init_db


def create_app() -> FastAPI:
    settings = get_settings()
    app = create_base_app(settings.service_name, api_router=consumers_router)
    app.state.settings = settings

    @app.on_event("startup")
    def on_startup() -> None:
        init_db()

    return app


app = create_app()
