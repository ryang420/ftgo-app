"""add PREPARING to order_status enum

Revision ID: 0005
Revises: 0004
Create Date: 2025-06-07 00:00:00.000000

"""

from collections.abc import Sequence
from typing import Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE order_status ADD VALUE IF NOT EXISTS 'PREPARING'")


def downgrade() -> None:
    # Removing an enum value in PostgreSQL requires recreating the type.
    # Omitted for simplicity; coordinate with a full rollback plan if needed.
    pass
