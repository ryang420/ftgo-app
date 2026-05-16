from fastapi import APIRouter

from .orders import router as orders_router

router = APIRouter()
router.include_router(orders_router)
