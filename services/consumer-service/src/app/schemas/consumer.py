"""Pydantic schemas for consumer-service APIs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.models import ConsumerAddress, ConsumerProfile


class ConsumerAddressCreate(BaseModel):
    label: str = Field(min_length=1, max_length=50)
    street1: str = Field(min_length=1, max_length=255)
    street2: str | None = Field(default=None, max_length=255)
    city: str = Field(min_length=1, max_length=100)
    state: str = Field(min_length=1, max_length=100)
    postal_code: str = Field(min_length=1, max_length=20)
    country: str = Field(default="US", min_length=2, max_length=2)


class ConsumerCreate(BaseModel):
    email: EmailStr
    first_name: str = Field(min_length=1, max_length=100)
    last_name: str = Field(min_length=1, max_length=100)
    phone_number: str | None = Field(default=None, max_length=32)
    addresses: list[ConsumerAddressCreate] = Field(default_factory=list)


class ConsumerAddressRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    label: str
    street1: str
    street2: str | None
    city: str
    state: str
    postal_code: str
    country: str
    created_at: datetime


class ConsumerRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: EmailStr
    first_name: str
    last_name: str
    phone_number: str | None
    created_at: datetime
    updated_at: datetime
    addresses: list[ConsumerAddressRead] = Field(default_factory=list)


class ConsumerListResponse(BaseModel):
    items: list[ConsumerRead]


def to_consumer_address_read(address: ConsumerAddress) -> ConsumerAddressRead:
    return ConsumerAddressRead(
        id=address.id,
        label=address.label,
        street1=address.street1,
        street2=address.street2,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        country=address.country,
        created_at=address.created_at,
    )


def to_consumer_read(consumer: ConsumerProfile) -> ConsumerRead:
    return ConsumerRead(
        id=consumer.id,
        email=consumer.email,
        first_name=consumer.first_name,
        last_name=consumer.last_name,
        phone_number=consumer.phone_number,
        created_at=consumer.created_at,
        updated_at=consumer.updated_at,
        addresses=[to_consumer_address_read(address) for address in consumer.addresses],
    )
