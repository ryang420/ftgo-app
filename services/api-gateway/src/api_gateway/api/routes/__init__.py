from fastapi import APIRouter

from api_gateway.api.routes.core_services import router as core_services_router

router = APIRouter()
router.include_router(core_services_router)
