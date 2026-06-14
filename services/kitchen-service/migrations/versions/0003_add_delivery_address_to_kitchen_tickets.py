"""Add delivery address to kitchen tickets.

Revision ID: 0003_kitchen_delivery_address
Revises: 0002_kitchen_outbox
Create Date: 2026-06-13 00:00:00
"""

import sqlalchemy as sa
from alembic import op

revision = "0003_kitchen_delivery_address"
down_revision = "0002_kitchen_outbox"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "kitchen_tickets",
        sa.Column("delivery_address", sa.String(length=500), nullable=True),
    )
    op.execute(
        "UPDATE kitchen_tickets SET delivery_address = 'Unknown' "
        "WHERE delivery_address IS NULL"
    )
    op.alter_column("kitchen_tickets", "delivery_address", nullable=False)


def downgrade() -> None:
    op.drop_column("kitchen_tickets", "delivery_address")
