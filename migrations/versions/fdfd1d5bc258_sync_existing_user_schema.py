"""Record existing schema synchronization.

Revision ID: fdfd1d5bc258
Revises: a001_initial_schema
Create Date: 2026-08-06 21:58:16.405946
"""

from collections.abc import Sequence

revision: str = "fdfd1d5bc258"
down_revision: str | Sequence[str] | None = "a001_initial_schema"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Schema is already represented by the initial migration."""

    pass


def downgrade() -> None:
    """No additional schema changes to revert."""

    pass
