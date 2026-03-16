"""rename legacy title to deep focus

Revision ID: 20260315_000004
Revises: 20260314_000003
Create Date: 2026-03-15 15:20:00
"""

from alembic import op


revision = "20260315_000004"
down_revision = "20260314_000003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        UPDATE titles
        SET name = 'Deep Focus',
            description = '집중력 10 달성',
            condition = 'focus >= 10',
            theme_color = '#b08a2e'
        WHERE name = 'Marathon Builder'
        """
    )
    op.execute(
        """
        UPDATE titles
        SET condition = 'stability >= 3 and focus >= 3'
        WHERE name = 'Phantom Maintainer'
        """
    )


def downgrade() -> None:
    op.execute(
        """
        UPDATE titles
        SET name = 'Marathon Builder',
            description = '지구력 10 달성',
            condition = 'endurance >= 10',
            theme_color = '#b08a2e'
        WHERE name = 'Deep Focus'
        """
    )
    op.execute(
        """
        UPDATE titles
        SET condition = 'stability >= 3 and endurance >= 3'
        WHERE name = 'Phantom Maintainer'
        """
    )
