from fastapi import APIRouter

from delivery_service.api.routes.deliveries import router as deliveries_router

router = APIRouter()
router.include_router(deliveries_router)

__all__ = ["router"]
