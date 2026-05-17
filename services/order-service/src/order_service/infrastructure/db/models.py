import uuid
from datetime import datetime
from decimal import Decimal

from common.db import Base
from sqlalchemy import JSON, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from order_service.domain.models import OrderStatus


class OrderRecord(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    consumer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    restaurant_id: Mapped[int] = mapped_column(nullable=False, index=True)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus, name="order_status"),
        default=OrderStatus.PENDING,
        nullable=False,
    )
    currency: Mapped[str] = mapped_column(String(3), default="USD", nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    line_items: Mapped[list["OrderLineItemRecord"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )


class OrderLineItemRecord(Base):
    __tablename__ = "order_line_items"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    menu_item_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)
    unit_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    order: Mapped[OrderRecord] = relationship(back_populates="line_items")


class OutboxMessageRecord(Base):
    __tablename__ = "outbox_messages"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    aggregate_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    aggregate_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    event_type: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
