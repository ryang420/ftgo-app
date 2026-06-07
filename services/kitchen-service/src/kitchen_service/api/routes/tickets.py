from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from kitchen_service.api.dependencies import get_ticket_service
from kitchen_service.application.tickets import KitchenTicketApplicationService
from kitchen_service.domain.models import InvalidKitchenTicketStatusTransitionError
from kitchen_service.schemas.tickets import (
    KitchenTicketRead,
    RejectTicketRequest,
    to_ticket_read,
)

router = APIRouter(prefix="/kitchen/tickets", tags=["kitchen-tickets"])


@router.get("", response_model=list[KitchenTicketRead])
def list_tickets(
    service: Annotated[KitchenTicketApplicationService, Depends(get_ticket_service)],
) -> list[KitchenTicketRead]:
    return [to_ticket_read(ticket) for ticket in service.list_tickets()]


@router.post("/{ticket_id}/accept", response_model=KitchenTicketRead)
def accept_ticket(
    ticket_id: UUID,
    service: Annotated[KitchenTicketApplicationService, Depends(get_ticket_service)],
) -> KitchenTicketRead:
    try:
        ticket = service.accept_ticket(ticket_id)
    except InvalidKitchenTicketStatusTransitionError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "message": str(exc),
                "current_status": exc.current,
                "target_status": exc.target,
            },
        ) from exc
    if ticket is None:
        raise HTTPException(status_code=404, detail="Kitchen ticket not found")
    return to_ticket_read(ticket)


@router.post("/{ticket_id}/reject", response_model=KitchenTicketRead)
def reject_ticket(
    ticket_id: UUID,
    service: Annotated[KitchenTicketApplicationService, Depends(get_ticket_service)],
    body: RejectTicketRequest = RejectTicketRequest(),
) -> KitchenTicketRead:
    try:
        ticket = service.reject_ticket(ticket_id, rejection_reason=body.rejection_reason)
    except InvalidKitchenTicketStatusTransitionError as exc:
        raise HTTPException(
            status_code=409,
            detail={
                "message": str(exc),
                "current_status": exc.current,
                "target_status": exc.target,
            },
        ) from exc
    if ticket is None:
        raise HTTPException(status_code=404, detail="Kitchen ticket not found")
    return to_ticket_read(ticket)


@router.post("/{ticket_id}/prepare", response_model=KitchenTicketRead)
def start_preparing(
    ticket_id: UUID,
    service: Annotated[KitchenTicketApplicationService, Depends(get_ticket_service)],
) -> KitchenTicketRead:
    try:
        ticket = service.start_preparing(ticket_id)
    except InvalidKitchenTicketStatusTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if ticket is None:
        raise HTTPException(status_code=404, detail="Kitchen ticket not found")
    return to_ticket_read(ticket)


@router.post("/{ticket_id}/ready-for-pickup", response_model=KitchenTicketRead)
def mark_ready_for_pickup(
    ticket_id: UUID,
    service: Annotated[KitchenTicketApplicationService, Depends(get_ticket_service)],
) -> KitchenTicketRead:
    try:
        ticket = service.mark_ready_for_pickup(ticket_id)
    except InvalidKitchenTicketStatusTransitionError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    if ticket is None:
        raise HTTPException(status_code=404, detail="Kitchen ticket not found")
    return to_ticket_read(ticket)
