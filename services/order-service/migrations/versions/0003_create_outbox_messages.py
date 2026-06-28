"""Create order service outbox messages.

Revision ID: 0003_order_outbox
Revises: 0002_order_int_refs
Create Date: 2026-05-17 00:00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_order_outbox"
down_revision = "0002_order_int_refs"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "outbox_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("aggregate_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_id", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=200), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_outbox_messages")),
    )
    op.create_index(op.f("ix_outbox_messages_aggregate_id"), "outbox_messages", ["aggregate_id"], unique=False)
    op.create_index(op.f("ix_outbox_messages_aggregate_type"), "outbox_messages", ["aggregate_type"], unique=False)
    op.create_index(op.f("ix_outbox_messages_event_type"), "outbox_messages", ["event_type"], unique=False)
    op.create_index(op.f("ix_outbox_messages_published_at"), "outbox_messages", ["published_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_outbox_messages_published_at"), table_name="outbox_messages")
    op.drop_index(op.f("ix_outbox_messages_event_type"), table_name="outbox_messages")
    op.drop_index(op.f("ix_outbox_messages_aggregate_type"), table_name="outbox_messages")
    op.drop_index(op.f("ix_outbox_messages_aggregate_id"), table_name="outbox_messages")
    op.drop_table("outbox_messages")
