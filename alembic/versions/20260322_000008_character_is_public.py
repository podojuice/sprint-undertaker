"""add is_public to characters

Revision ID: 20260322_000008
Revises: 20260319_000007
Create Date: 2026-03-22 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260322_000008"
down_revision = "20260319_000007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "characters",
        sa.Column("is_public", sa.Boolean(), nullable=False, server_default=sa.false()),
    )


def downgrade() -> None:
    op.drop_column("characters", "is_public")
