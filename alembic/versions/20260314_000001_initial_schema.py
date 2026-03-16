"""initial schema

Revision ID: 20260314_000001
Revises:
Create Date: 2026-03-14 14:30:00
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260314_000001"
down_revision = None
branch_labels = None
depends_on = None


org_role_enum = postgresql.ENUM("OWNER", "MEMBER", name="orgrole")
org_role_column_enum = postgresql.ENUM(
    "OWNER",
    "MEMBER",
    name="orgrole",
    create_type=False,
)
provider_enum = postgresql.ENUM("CLAUDE_CODE", "CODEX", "CURSOR", "AIDER", name="provider")
provider_column_enum = postgresql.ENUM(
    "CLAUDE_CODE",
    "CODEX",
    "CURSOR",
    "AIDER",
    name="provider",
    create_type=False,
)
installation_status_enum = postgresql.ENUM(
    "ACTIVE",
    "DISABLED",
    name="installationstatus",
)
installation_status_column_enum = postgresql.ENUM(
    "ACTIVE",
    "DISABLED",
    name="installationstatus",
    create_type=False,
)
title_type_enum = postgresql.ENUM("PERSONAL", "GUILD", name="titletype")
title_type_column_enum = postgresql.ENUM(
    "PERSONAL",
    "GUILD",
    name="titletype",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    org_role_enum.create(bind, checkfirst=True)
    provider_enum.create(bind, checkfirst=True)
    installation_status_enum.create(bind, checkfirst=True)
    title_type_enum.create(bind, checkfirst=True)

    op.create_table(
        "organizations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "titles",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=100), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("type", title_type_column_enum, nullable=False),
        sa.Column("condition", sa.Text(), nullable=False),
    )

    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(length=255), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("organization_id", sa.Integer(), sa.ForeignKey("organizations.id"), nullable=True),
        sa.Column("org_role", org_role_column_enum, nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_foreign_key(
        "fk_organizations_owner_id_users",
        "organizations",
        "users",
        ["owner_id"],
        ["id"],
    )

    op.create_table(
        "characters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, unique=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("class", sa.String(length=50), nullable=False),
        sa.Column("level", sa.Integer(), nullable=False),
        sa.Column("exp", sa.Integer(), nullable=False),
        sa.Column("impl", sa.Integer(), nullable=False),
        sa.Column("focus", sa.Integer(), nullable=False),
        sa.Column("efficiency", sa.Integer(), nullable=False),
        sa.Column("versatility", sa.Integer(), nullable=False),
        sa.Column("stability", sa.Integer(), nullable=False),
        sa.Column("endurance", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "provider_installations",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("provider", provider_column_enum, nullable=False),
        sa.Column("installation_name", sa.String(length=255), nullable=False),
        sa.Column("api_key", sa.String(length=255), nullable=False, unique=True),
        sa.Column("status", installation_status_column_enum, nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "activity_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("installation_id", sa.Integer(), sa.ForeignKey("provider_installations.id"), nullable=False),
        sa.Column("provider", provider_column_enum, nullable=False),
        sa.Column("session_id", sa.String(length=255), nullable=True),
        sa.Column("canonical_event_type", sa.String(length=100), nullable=False),
        sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "user_titles",
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), primary_key=True),
        sa.Column("title_id", sa.Integer(), sa.ForeignKey("titles.id"), primary_key=True),
        sa.Column("earned_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("user_titles")
    op.drop_table("activity_events")
    op.drop_table("provider_installations")
    op.drop_table("characters")
    op.drop_constraint("fk_organizations_owner_id_users", "organizations", type_="foreignkey")
    op.drop_table("users")
    op.drop_table("titles")
    op.drop_table("organizations")

    bind = op.get_bind()
    title_type_enum.drop(bind, checkfirst=True)
    installation_status_enum.drop(bind, checkfirst=True)
    provider_enum.drop(bind, checkfirst=True)
    org_role_enum.drop(bind, checkfirst=True)
