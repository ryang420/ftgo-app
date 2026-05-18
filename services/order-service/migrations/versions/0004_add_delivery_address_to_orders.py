"""add delivery_address to orders

Revision ID: 0004
Revises: 0003_order_outbox
Create Date: 2025-05-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0004"
down_revision: Union[str, None] = "0003_order_outbox"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "orders",
        sa.Column("delivery_address", sa.String(length=500), nullable=True),
    )
    # Backfill existing rows with a default value
    op.execute("UPDATE orders SET delivery_address = 'Unknown' WHERE delivery_address IS NULL")
    # Make it non-nullable after backfill
    op.alter_column("orders", "delivery_address", nullable=False)


def downgrade() -> None:
    op.drop_column("orders", "delivery_address")
