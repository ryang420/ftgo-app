from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from delivery_service.api.dependencies import get_delivery_service
from delivery_service.application.deliveries import DeliveryApplicationService
from delivery_service.domain.models import InvalidDeliveryStatusTransitionError
from delivery_service.schemas.deliveries import (
    AssignCourierRequest,
    DeliveryRead,
    to_delivery_read,
)

router = APIRouter(prefix="/deliveries", tags=["deliveries"])


@router.get("", response_model=list[DeliveryRead])
def list_deliveries(
    service: Annotated[DeliveryApplicationService, Depends(get_delivery_service)],
) -> list[DeliveryRead]:
    return [to_delivery_read(delivery) for delivery in service.list_deliveries()]


@router.get("/{delivery_id}", response_model=DeliveryRead)
def get_delivery(
    delivery_id: UUID,
    service: Annotated[DeliveryApplicationService, Depends(get_delivery_service)],
) -> DeliveryRead:
    delivery = service.get_delivery(delivery_id)
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return to_delivery_read(delivery)


@router.post("/{delivery_id}/assign", response_model=DeliveryRead)
def assign_courier(
    delivery_id: UUID,
    body: AssignCourierRequest,
    service: Annotated[DeliveryApplicationService, Depends(get_delivery_service)],
) -> DeliveryRead:
    try:
        delivery = service.assign_courier(delivery_id, body.courier_id)
    except InvalidDeliveryStatusTransitionError as exc:
        raise _transition_conflict(exc) from exc
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return to_delivery_read(delivery)


@router.post("/{delivery_id}/pickup", response_model=DeliveryRead)
def mark_picked_up(
    delivery_id: UUID,
    service: Annotated[DeliveryApplicationService, Depends(get_delivery_service)],
) -> DeliveryRead:
    try:
        delivery = service.mark_picked_up(delivery_id)
    except InvalidDeliveryStatusTransitionError as exc:
        raise _transition_conflict(exc) from exc
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return to_delivery_read(delivery)


@router.post("/{delivery_id}/deliver", response_model=DeliveryRead)
def mark_delivered(
    delivery_id: UUID,
    service: Annotated[DeliveryApplicationService, Depends(get_delivery_service)],
) -> DeliveryRead:
    try:
        delivery = service.mark_delivered(delivery_id)
    except InvalidDeliveryStatusTransitionError as exc:
        raise _transition_conflict(exc) from exc
    if delivery is None:
        raise HTTPException(status_code=404, detail="Delivery not found")
    return to_delivery_read(delivery)


def _transition_conflict(exc: InvalidDeliveryStatusTransitionError) -> HTTPException:
    return HTTPException(
        status_code=409,
        detail={
            "message": str(exc),
            "current_status": exc.current,
            "target_status": exc.target,
        },
    )
