"""session_version en users

Revision ID: ddd42c788f2d
Revises: 59d39034b508
Create Date: 2026-09-15 16:11:20.013208

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ddd42c788f2d'
down_revision: Union[str, Sequence[str], None] = '59d39034b508'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('session_version', sa.Integer(), nullable=False, server_default='0'),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'session_version')
