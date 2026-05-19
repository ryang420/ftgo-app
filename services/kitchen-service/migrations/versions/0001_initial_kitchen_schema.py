"""Initial kitchen schema.

Revision ID: 0001_kitchen
Revises:
Create Date: 2026-05-19 00:00:00
"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0001_kitchen"
down_revision = None
branch_labels = None
depends_on = None


ticket_status = postgresql.ENUM(
    "CREATE_PENDING",
    "ACCEPTED",
    "PREPARING",
    "READY_FOR_PICKUP",
    "CANCELLED",
    name="kitchen_ticket_status",
    create_type=False,
)


def upgrade() -> None:
    ticket_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "kitchen_tickets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("status", ticket_status, nullable=False),
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
        sa.PrimaryKeyConstraint("id", name=op.f("pk_kitchen_tickets")),
        sa.UniqueConstraint("order_id", name=op.f("uq_kitchen_tickets_order_id")),
    )
    op.create_index(
        op.f("ix_kitchen_tickets_order_id"),
        "kitchen_tickets",
        ["order_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_kitchen_tickets_restaurant_id"),
        "kitchen_tickets",
        ["restaurant_id"],
        unique=False,
    )

    op.create_table(
        "kitchen_ticket_line_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("ticket_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("menu_item_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["ticket_id"],
            ["kitchen_tickets.id"],
            name=op.f("fk_kitchen_ticket_line_items_ticket_id_kitchen_tickets"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_kitchen_ticket_line_items")),
    )
    op.create_index(
        op.f("ix_kitchen_ticket_line_items_ticket_id"),
        "kitchen_ticket_line_items",
        ["ticket_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_kitchen_ticket_line_items_ticket_id"),
        table_name="kitchen_ticket_line_items",
    )
    op.drop_table("kitchen_ticket_line_items")
    op.drop_index(op.f("ix_kitchen_tickets_restaurant_id"), table_name="kitchen_tickets")
    op.drop_index(op.f("ix_kitchen_tickets_order_id"), table_name="kitchen_tickets")
    op.drop_table("kitchen_tickets")
    ticket_status.drop(op.get_bind(), checkfirst=True)
