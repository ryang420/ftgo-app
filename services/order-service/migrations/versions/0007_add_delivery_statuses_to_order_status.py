"""Add delivery statuses to order status.

Revision ID: 0007
Revises: 0006
Create Date: 2026-06-13 00:00:00
"""

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'DELIVERY_ASSIGNED'")
    op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'OUT_FOR_DELIVERY'")
    op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'DELIVERED'")


def downgrade() -> None:
    pass
