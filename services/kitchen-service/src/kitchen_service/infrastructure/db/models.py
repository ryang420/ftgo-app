import uuid
from datetime import datetime

from common.db import Base
from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from kitchen_service.domain.models import KitchenTicketStatus


class KitchenTicketRecord(Base):
    __tablename__ = "kitchen_tickets"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        nullable=False,
        unique=True,
        index=True,
    )
    restaurant_id: Mapped[int] = mapped_column(nullable=False, index=True)
    status: Mapped[KitchenTicketStatus] = mapped_column(
        Enum(KitchenTicketStatus, name="kitchen_ticket_status"),
        default=KitchenTicketStatus.CREATE_PENDING,
        nullable=False,
    )
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

    line_items: Mapped[list["KitchenTicketLineItemRecord"]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
    )


class KitchenTicketLineItemRecord(Base):
    __tablename__ = "kitchen_ticket_line_items"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("kitchen_tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    menu_item_id: Mapped[int] = mapped_column(nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(nullable=False)

    ticket: Mapped[KitchenTicketRecord] = relationship(back_populates="line_items")
