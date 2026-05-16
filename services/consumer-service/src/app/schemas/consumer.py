"""Pydantic schemas for consumer-service APIs."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field


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
