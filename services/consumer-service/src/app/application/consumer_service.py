"""Application service helpers for consumer workflows."""

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.domain.models import ConsumerAddress, ConsumerProfile
from app.schemas.consumer import ConsumerCreate


def list_consumers(session: Session) -> list[ConsumerProfile]:
    """Return all consumers with their addresses."""

    statement = (
        select(ConsumerProfile)
        .options(selectinload(ConsumerProfile.addresses))
        .order_by(ConsumerProfile.created_at.desc())
    )
    return list(session.scalars(statement).all())


def get_consumer(session: Session, consumer_id: str) -> ConsumerProfile | None:
    """Return a single consumer by identifier."""

    statement = (
        select(ConsumerProfile)
        .options(selectinload(ConsumerProfile.addresses))
        .where(ConsumerProfile.id == consumer_id)
    )
    return session.scalar(statement)


def create_consumer(session: Session, payload: ConsumerCreate) -> ConsumerProfile:
    """Create a consumer profile and any initial addresses."""

    consumer = ConsumerProfile(
        email=str(payload.email),
        first_name=payload.first_name,
        last_name=payload.last_name,
        phone_number=payload.phone_number,
        addresses=[
            ConsumerAddress(
                label=address.label,
                street1=address.street1,
                street2=address.street2,
                city=address.city,
                state=address.state,
                postal_code=address.postal_code,
                country=address.country.upper(),
            )
            for address in payload.addresses
        ],
    )
    session.add(consumer)
    session.commit()
    session.refresh(consumer)
    return get_consumer(session, consumer.id) or consumer
