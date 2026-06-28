from __future__ import annotations

from uuid import uuid4

from common.db import TimestampedModel
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship


class ConsumerProfileRecord(TimestampedModel):
    __tablename__ = "consumer_profiles"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email: Mapped[str] = mapped_column(String(320), unique=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str | None] = mapped_column(String(32), nullable=True)
    addresses: Mapped[list[ConsumerAddressRecord]] = relationship(
        back_populates="consumer",
        cascade="all, delete-orphan",
    )


class ConsumerAddressRecord(TimestampedModel):
    __tablename__ = "consumer_addresses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid4()))
    consumer_id: Mapped[str] = mapped_column(
        ForeignKey("consumer_profiles.id", ondelete="CASCADE"),
        index=True,
    )
    label: Mapped[str] = mapped_column(String(50))
    street1: Mapped[str] = mapped_column(String(255))
    street2: Mapped[str | None] = mapped_column(String(255), nullable=True)
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(100))
    postal_code: Mapped[str] = mapped_column(String(20))
    country: Mapped[str] = mapped_column(String(2), default="US")
    consumer: Mapped[ConsumerProfileRecord] = relationship(back_populates="addresses")
