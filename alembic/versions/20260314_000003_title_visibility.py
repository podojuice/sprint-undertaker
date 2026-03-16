"""add title visibility

Revision ID: 20260314_000003
Revises: 20260314_000002
Create Date: 2026-03-14 16:40:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260314_000003"
down_revision = "20260314_000002"
branch_labels = None
depends_on = None


title_visibility_enum = postgresql.ENUM("PUBLIC", "HIDDEN", name="titlevisibility")
title_visibility_column_enum = postgresql.ENUM(
    "PUBLIC",
    "HIDDEN",
    name="titlevisibility",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    title_visibility_enum.create(bind, checkfirst=True)
    op.add_column(
        "titles",
        sa.Column(
            "visibility",
            title_visibility_column_enum,
            nullable=False,
            server_default="PUBLIC",
        ),
    )
    op.alter_column("titles", "visibility", server_default=None)


def downgrade() -> None:
    op.drop_column("titles", "visibility")
    bind = op.get_bind()
    title_visibility_enum.drop(bind, checkfirst=True)
