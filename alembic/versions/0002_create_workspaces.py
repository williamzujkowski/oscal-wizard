"""create workspaces table

Revision ID: 0002_create_workspaces
Revises: 0001_create_users
Create Date: 2026-01-19T21:13:26-05:00

"""
import sqlalchemy as sa

from alembic import op

revision = "0002_create_workspaces"
down_revision = "0001_create_users"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "workspaces",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("system_id", sa.String(length=64), nullable=False),
        sa.Column("data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("workspaces")
