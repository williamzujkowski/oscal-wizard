"""add workspace updated_at

Revision ID: 0003_add_workspace_updated_at
Revises: 0002_create_workspaces
Create Date: 2026-01-20T06:46:39-05:00

"""
from alembic import op
import sqlalchemy as sa

revision = "0003_add_workspace_updated_at"
down_revision = "0002_create_workspaces"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "workspaces",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    op.drop_column("workspaces", "updated_at")
