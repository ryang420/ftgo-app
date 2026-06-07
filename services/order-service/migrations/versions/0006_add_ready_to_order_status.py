"""add READY to order_status enum

Revision ID: 0006
Revises: 0005
Create Date: 2025-06-07 00:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0006"
down_revision: Union[str, None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'READY'")


def downgrade() -> None:
    # Removing an enum value in PostgreSQL requires recreating the type.
    # Omitted for simplicity; coordinate with a full rollback plan if needed.
    pass
