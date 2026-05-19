from fastapi import APIRouter

from kitchen_service.api.routes.tickets import router as tickets_router

router = APIRouter()
router.include_router(tickets_router)

__all__ = ["router"]
