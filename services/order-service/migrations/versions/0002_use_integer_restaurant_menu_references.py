"""Use integer restaurant and menu references.

Revision ID: 0002_order_int_refs
Revises: 0001_order
Create Date: 2026-05-17 00:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0002_order_int_refs"
down_revision = "0001_order"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(op.f("ix_order_line_items_order_id"), table_name="order_line_items")
    op.drop_table("order_line_items")

    op.execute("DELETE FROM orders")
    op.drop_index(op.f("ix_orders_restaurant_id"), table_name="orders")
    op.drop_column("orders", "restaurant_id")
    op.add_column("orders", sa.Column("restaurant_id", sa.Integer(), nullable=False))
    op.create_index(op.f("ix_orders_restaurant_id"), "orders", ["restaurant_id"], unique=False)

    op.create_table(
        "order_line_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("menu_item_id", sa.Integer(), nullable=False),
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
    op.drop_column("orders", "restaurant_id")
    op.add_column("orders", sa.Column("restaurant_id", sa.UUID(), nullable=False))
    op.create_index(op.f("ix_orders_restaurant_id"), "orders", ["restaurant_id"], unique=False)

    op.create_table(
        "order_line_items",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=False),
        sa.Column("menu_item_id", sa.UUID(), nullable=False),
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
