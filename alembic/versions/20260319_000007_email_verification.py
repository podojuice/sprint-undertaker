"""add email verification

Revision ID: 20260319_000007
Revises: 20260317_000006
Create Date: 2026-03-19 00:00:00
"""

from alembic import op
import sqlalchemy as sa


revision = "20260319_000007"
down_revision = "20260317_000006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_verified", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.execute("""
        CREATE TYPE codetype AS ENUM ('email_verification', 'password_reset');
        CREATE TABLE email_codes (
            id          SERIAL PRIMARY KEY,
            email       VARCHAR(255) NOT NULL,
            code        VARCHAR(6) NOT NULL,
            type        codetype NOT NULL,
            expires_at  TIMESTAMPTZ NOT NULL,
            used_at     TIMESTAMPTZ,
            created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
        );
        CREATE INDEX ix_email_codes_email ON email_codes (email);
    """)


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS email_codes")
    op.execute("DROP TYPE IF EXISTS codetype")
    op.drop_column("users", "is_verified")
