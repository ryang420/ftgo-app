from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from order_service.application.commands import CreateOrderCommand, CreateOrderLineItemCommand
from order_service.api.dependencies import get_order_service
from order_service.application.orders import OrderApplicationService
from order_service.schemas.orders import OrderCreate, OrderRead, to_order_read

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderRead])
async def list_orders(
    service: OrderApplicationService = Depends(get_order_service),
) -> list[OrderRead]:
    return [to_order_read(order) for order in service.list_orders()]


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(
    order_id: UUID,
    service: OrderApplicationService = Depends(get_order_service),
) -> OrderRead:
    order = service.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return to_order_read(order)


@router.post("", response_model=OrderRead, status_code=201)
async def create_order(
    payload: OrderCreate,
    service: OrderApplicationService = Depends(get_order_service),
) -> OrderRead:
    command = CreateOrderCommand(
        consumer_id=payload.consumer_id,
        restaurant_id=payload.restaurant_id,
        currency=payload.currency,
        line_items=[
            CreateOrderLineItemCommand(
                menu_item_id=item.menu_item_id,
                name=item.name,
                quantity=item.quantity,
                unit_price=item.unit_price,
            )
            for item in payload.line_items
        ],
    )
    return to_order_read(service.create_order(command))
