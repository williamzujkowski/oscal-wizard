"""add workspace owner id

Revision ID: 0004_add_workspace_owner_id
Revises: 0003_add_workspace_updated_at
Create Date: 2026-01-20T07:45:44-05:00

"""
import sqlalchemy as sa

from alembic import op

revision = "0004_add_workspace_owner_id"
down_revision = "0003_add_workspace_updated_at"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workspaces",
        sa.Column("owner_id", sa.String(length=36), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("workspaces", "owner_id")
