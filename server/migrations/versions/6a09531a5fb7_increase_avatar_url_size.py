"""increase_avatar_url_size

Revision ID: 6a09531a5fb7
Revises: ff1d41cdfaef
Create Date: 2025-10-03 15:17:58.982977

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6a09531a5fb7'
down_revision = 'ff1d41cdfaef'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Increase avatar_url column size from VARCHAR(500) to TEXT
    op.alter_column('users', 'avatar_url',
                    existing_type=sa.String(length=500),
                    type_=sa.Text(),
                    existing_nullable=True)


def downgrade() -> None:
    # Revert avatar_url column size back to VARCHAR(500)
    op.alter_column('users', 'avatar_url',
                    existing_type=sa.Text(),
                    type_=sa.String(length=500),
                    existing_nullable=True)
