import uuid
from datetime import datetime

from common.db import Base
from sqlalchemy import JSON, DateTime, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column


class OutboxMessageRecord(Base):
    """Shared outbox table model. Each service must include this in its metadata."""

    __tablename__ = "outbox_messages"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    aggregate_type: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    aggregate_id: Mapped[str] = mapped_column(
        String(100), nullable=False, index=True
    )
    event_type: Mapped[str] = mapped_column(
        String(200), nullable=False, index=True
    )
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
