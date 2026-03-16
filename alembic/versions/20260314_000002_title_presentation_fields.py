"""add title presentation fields

Revision ID: 20260314_000002
Revises: 20260314_000001
Create Date: 2026-03-14 16:20:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260314_000002"
down_revision = "20260314_000001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "titles",
        sa.Column("theme_color", sa.String(length=32), nullable=False, server_default="#b34c24"),
    )
    op.add_column("titles", sa.Column("active_start_at", sa.DateTime(timezone=True), nullable=True))
    op.add_column("titles", sa.Column("active_end_at", sa.DateTime(timezone=True), nullable=True))

    op.execute(
        """
        UPDATE titles
        SET theme_color = CASE name
            WHEN 'Code Berserker' THEN '#d2643f'
            WHEN 'Reliable Operator' THEN '#2f7a8c'
            WHEN 'Marathon Builder' THEN '#b08a2e'
            ELSE '#b34c24'
        END
        """
    )
    op.alter_column("titles", "theme_color", server_default=None)


def downgrade() -> None:
    op.drop_column("titles", "active_end_at")
    op.drop_column("titles", "active_start_at")
    op.drop_column("titles", "theme_color")
