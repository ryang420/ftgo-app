"""Initial order schema.

Revision ID: 0001_order
Revises:
Create Date: 2026-05-16 00:00:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_order"
down_revision = None
branch_labels = None
depends_on = None


order_status = postgresql.ENUM(
    "PENDING",
    "APPROVED",
    "REJECTED",
    "CANCELLED",
    name="order_status",
    create_type=False,
)


def upgrade() -> None:
    order_status.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "orders",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("consumer_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("restaurant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", order_status, nullable=False),
        sa.Column("currency", sa.String(length=3), nullable=False),
        sa.Column("total_amount", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_orders")),
    )
    op.create_index(op.f("ix_orders_consumer_id"), "orders", ["consumer_id"], unique=False)
    op.create_index(op.f("ix_orders_restaurant_id"), "orders", ["restaurant_id"], unique=False)

    op.create_table(
        "order_line_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("order_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("menu_item_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.Column("unit_price", sa.Numeric(10, 2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["order_id"],
            ["orders.id"],
            name=op.f("fk_order_line_items_order_id_orders"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_order_line_items")),
    )
    op.create_index(op.f("ix_order_line_items_order_id"), "order_line_items", ["order_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_order_line_items_order_id"), table_name="order_line_items")
    op.drop_table("order_line_items")
    op.drop_index(op.f("ix_orders_restaurant_id"), table_name="orders")
    op.drop_index(op.f("ix_orders_consumer_id"), table_name="orders")
    op.drop_table("orders")
    order_status.drop(op.get_bind(), checkfirst=True)
