"""Create initial database schema.

Revision ID: a001_initial_schema
Revises:
Create Date: 2026-08-06
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "a001_initial_schema"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create the complete initial database schema."""

    op.create_table(
        "system_info",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "system_name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "version",
            sa.String(length=20),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_system_info_id"),
        "system_info",
        ["id"],
        unique=False,
    )

    op.create_table(
        "users",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "full_name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "hashed_password",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "is_email_verified",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "email_verification_token",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "email_verification_expires_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "password_reset_token",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "password_reset_expires_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.Column(
            "profile_image",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_users_id"),
        "users",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_users_email"),
        "users",
        ["email"],
        unique=True,
    )

    op.create_index(
        op.f("ix_users_email_verification_token"),
        "users",
        ["email_verification_token"],
        unique=True,
    )

    op.create_index(
        op.f("ix_users_password_reset_token"),
        "users",
        ["password_reset_token"],
        unique=True,
    )

    op.create_table(
        "revoked_tokens",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "token",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "revoked_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("token"),
    )

    op.create_index(
        op.f("ix_revoked_tokens_id"),
        "revoked_tokens",
        ["id"],
        unique=False,
    )

    op.create_table(
        "activity_logs",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "action",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        op.f("ix_activity_logs_id"),
        "activity_logs",
        ["id"],
        unique=False,
    )

    op.create_table(
        "user_sessions",
        sa.Column(
            "id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_email",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "refresh_token",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "device_name",
            sa.String(length=255),
            nullable=False,
        ),
        sa.Column(
            "ip_address",
            sa.String(length=45),
            nullable=False,
        ),
        sa.Column(
            "user_agent",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "last_activity",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "logged_out_at",
            sa.DateTime(),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("refresh_token"),
    )

    op.create_index(
        op.f("ix_user_sessions_id"),
        "user_sessions",
        ["id"],
        unique=False,
    )

    op.create_index(
        op.f("ix_user_sessions_user_email"),
        "user_sessions",
        ["user_email"],
        unique=False,
    )


def downgrade() -> None:
    """Remove the complete database schema."""

    op.drop_index(
        op.f("ix_user_sessions_user_email"),
        table_name="user_sessions",
    )
    op.drop_index(
        op.f("ix_user_sessions_id"),
        table_name="user_sessions",
    )
    op.drop_table("user_sessions")

    op.drop_index(
        op.f("ix_activity_logs_id"),
        table_name="activity_logs",
    )
    op.drop_table("activity_logs")

    op.drop_index(
        op.f("ix_revoked_tokens_id"),
        table_name="revoked_tokens",
    )
    op.drop_table("revoked_tokens")

    op.drop_index(
        op.f("ix_users_password_reset_token"),
        table_name="users",
    )
    op.drop_index(
        op.f("ix_users_email_verification_token"),
        table_name="users",
    )
    op.drop_index(
        op.f("ix_users_email"),
        table_name="users",
    )
    op.drop_index(
        op.f("ix_users_id"),
        table_name="users",
    )
    op.drop_table("users")

    op.drop_index(
        op.f("ix_system_info_id"),
        table_name="system_info",
    )
    op.drop_table("system_info")
