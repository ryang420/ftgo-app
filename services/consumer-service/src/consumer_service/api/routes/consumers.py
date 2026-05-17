"""Consumer API routes."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError

from consumer_service.api.dependencies import get_consumer_service
from consumer_service.application.commands import CreateConsumerAddressCommand, CreateConsumerCommand
from consumer_service.application.consumer_service import ConsumerApplicationService
from consumer_service.schemas.consumer import ConsumerCreate, ConsumerListResponse, ConsumerRead, to_consumer_read

router = APIRouter(prefix="/consumers", tags=["consumers"])


@router.get("", response_model=ConsumerListResponse)
def list_consumer_profiles(
    service: Annotated[ConsumerApplicationService, Depends(get_consumer_service)],
) -> ConsumerListResponse:
    return ConsumerListResponse(items=[to_consumer_read(consumer) for consumer in service.list_consumers()])


@router.post("", response_model=ConsumerRead, status_code=status.HTTP_201_CREATED)
def create_consumer_profile(
    payload: ConsumerCreate,
    service: Annotated[ConsumerApplicationService, Depends(get_consumer_service)],
) -> ConsumerRead:
    command = CreateConsumerCommand(
        email=str(payload.email),
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone_number=payload.phone_number,
        addresses=[
            CreateConsumerAddressCommand(
                label=address.label,
                street1=address.street1,
                street2=address.street2,
                city=address.city,
                state=address.state,
                postal_code=address.postal_code,
                country=address.country,
            )
            for address in payload.addresses
        ],
    )
    try:
        return to_consumer_read(service.create_consumer(command))
    except IntegrityError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A consumer with that email already exists.",
        ) from exc


@router.get("/{consumer_id}", response_model=ConsumerRead)
def get_consumer_profile(
    consumer_id: str,
    service: Annotated[ConsumerApplicationService, Depends(get_consumer_service)],
) -> ConsumerRead:
    consumer = service.get_consumer(consumer_id)
    if consumer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer not found.",
        )
    return to_consumer_read(consumer)
