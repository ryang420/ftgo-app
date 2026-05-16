from fastapi import APIRouter, FastAPI


def create_base_app(service_name: str, *, api_router: APIRouter | None = None) -> FastAPI:
    app = FastAPI(title=service_name)
    router = APIRouter()

    @router.get("/health", tags=["platform"])
    async def healthcheck() -> dict[str, str]:
        return {"status": "ok", "service": service_name}

    app.include_router(router)
    if api_router is not None:
        app.include_router(api_router)
    return app
