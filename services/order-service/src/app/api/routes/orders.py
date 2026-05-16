from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_order_service
from app.application.orders import OrderApplicationService
from app.schemas.orders import OrderCreate, OrderRead

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderRead])
async def list_orders(
    service: OrderApplicationService = Depends(get_order_service),
) -> list[OrderRead]:
    return [OrderRead.model_validate(order) for order in service.list_orders()]


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: UUID,
    service: OrderApplicationService = Depends(get_order_service),
) -> OrderRead:
    order = service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return OrderRead.model_validate(order)


@router.post("", response_model=OrderRead, status_code=201)
async def create_order(
    payload: OrderCreate,
    service: OrderApplicationService = Depends(get_order_service),
) -> OrderRead:
    return OrderRead.model_validate(service.create_order(payload))
