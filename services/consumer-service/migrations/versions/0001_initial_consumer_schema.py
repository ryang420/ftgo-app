"""Initial consumer schema.

Revision ID: 0001_consumer
Revises:
Create Date: 2026-05-16 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "0001_consumer"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "consumer_profiles",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("first_name", sa.String(length=100), nullable=False),
        sa.Column("last_name", sa.String(length=100), nullable=False),
        sa.Column("phone_number", sa.String(length=32), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_consumer_profiles")),
    )
    op.create_index(op.f("ix_consumer_profiles_email"), "consumer_profiles", ["email"], unique=True)

    op.create_table(
        "consumer_addresses",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("consumer_id", sa.String(length=36), nullable=False),
        sa.Column("label", sa.String(length=50), nullable=False),
        sa.Column("street1", sa.String(length=255), nullable=False),
        sa.Column("street2", sa.String(length=255), nullable=True),
        sa.Column("city", sa.String(length=100), nullable=False),
        sa.Column("state", sa.String(length=100), nullable=False),
        sa.Column("postal_code", sa.String(length=20), nullable=False),
        sa.Column("country", sa.String(length=2), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(
            ["consumer_id"],
            ["consumer_profiles.id"],
            name=op.f("fk_consumer_addresses_consumer_id_consumer_profiles"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_consumer_addresses")),
    )
    op.create_index(
        op.f("ix_consumer_addresses_consumer_id"),
        "consumer_addresses",
        ["consumer_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_consumer_addresses_consumer_id"), table_name="consumer_addresses")
    op.drop_table("consumer_addresses")
    op.drop_index(op.f("ix_consumer_profiles_email"), table_name="consumer_profiles")
    op.drop_table("consumer_profiles")
