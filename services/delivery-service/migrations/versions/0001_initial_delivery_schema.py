"""Initial delivery schema.

Revision ID: 0001_delivery
Revises:
Create Date: 2026-06-13 00:00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_delivery"
down_revision = None
branch_labels = None
depends_on = None


delivery_status = postgresql.ENUM(
    "PENDING_ASSIGNMENT",
    "ASSIGNED",
    "PICKED_UP",
    "DELIVERED",
    "CANCELLED",
    name="delivery_status",
    create_type=False,
)


def upgrade() -> None:
    delivery_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "deliveries",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("delivery_address", sa.String(length=500), nullable=False),
        sa.Column("status", delivery_status, nullable=False),
        sa.Column("courier_id", sa.String(length=100), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_deliveries")),
        sa.UniqueConstraint("order_id", name=op.f("uq_deliveries_order_id")),
    )
    op.create_index(op.f("ix_deliveries_order_id"), "deliveries", ["order_id"], unique=False)
    op.create_index(
        op.f("ix_deliveries_restaurant_id"),
        "deliveries",
        ["restaurant_id"],
        unique=False,
    )

    op.create_table(
        "outbox_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("aggregate_type", sa.String(length=100), nullable=False),
        sa.Column("aggregate_id", sa.String(length=100), nullable=False),
        sa.Column("event_type", sa.String(length=200), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_outbox_messages")),
    )
    op.create_index(
        op.f("ix_outbox_messages_aggregate_id"),
        "outbox_messages",
        ["aggregate_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_outbox_messages_aggregate_type"),
        "outbox_messages",
        ["aggregate_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_outbox_messages_event_type"),
        "outbox_messages",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_outbox_messages_published_at"),
        "outbox_messages",
        ["published_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_outbox_messages_published_at"), table_name="outbox_messages")
    op.drop_index(op.f("ix_outbox_messages_event_type"), table_name="outbox_messages")
    op.drop_index(op.f("ix_outbox_messages_aggregate_type"), table_name="outbox_messages")
    op.drop_index(op.f("ix_outbox_messages_aggregate_id"), table_name="outbox_messages")
    op.drop_table("outbox_messages")
    op.drop_index(op.f("ix_deliveries_restaurant_id"), table_name="deliveries")
    op.drop_index(op.f("ix_deliveries_order_id"), table_name="deliveries")
    op.drop_table("deliveries")
    delivery_status.drop(op.get_bind(), checkfirst=True)
