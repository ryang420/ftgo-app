"""Consumer API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.application.consumer_service import create_consumer, get_consumer, list_consumers
from app.infrastructure.db.session import get_db_session
from app.schemas.consumer import ConsumerCreate, ConsumerListResponse, ConsumerRead

router = APIRouter(prefix="/consumers", tags=["consumers"])


@router.get("", response_model=ConsumerListResponse)
def list_consumer_profiles(session: Session = Depends(get_db_session)) -> ConsumerListResponse:
    return ConsumerListResponse(items=list_consumers(session))


@router.post("", response_model=ConsumerRead, status_code=status.HTTP_201_CREATED)
def create_consumer_profile(
    payload: ConsumerCreate,
    session: Session = Depends(get_db_session),
) -> ConsumerRead:
    try:
        return create_consumer(session, payload)
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A consumer with that email already exists.",
        ) from exc


@router.get("/{consumer_id}", response_model=ConsumerRead)
def get_consumer_profile(
    consumer_id: str,
    session: Session = Depends(get_db_session),
) -> ConsumerRead:
    consumer = get_consumer(session, consumer_id)
    if consumer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Consumer not found.",
        )
    return consumer
