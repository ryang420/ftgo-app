from typing import Annotated

from fastapi import APIRouter, Depends

from kitchen_service.api.dependencies import get_ticket_service
from kitchen_service.application.tickets import KitchenTicketApplicationService
from kitchen_service.schemas.tickets import KitchenTicketRead, to_ticket_read

router = APIRouter(prefix="/kitchen/tickets", tags=["kitchen-tickets"])


@router.get("", response_model=list[KitchenTicketRead])
def list_tickets(
    service: Annotated[KitchenTicketApplicationService, Depends(get_ticket_service)],
) -> list[KitchenTicketRead]:
    return [to_ticket_read(ticket) for ticket in service.list_tickets()]
