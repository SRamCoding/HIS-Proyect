"""is_superadmin en users

Revision ID: 3ef65afd331c
Revises: ddd42c788f2d
Create Date: 2026-09-15 16:23:37.398530

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3ef65afd331c'
down_revision: Union[str, Sequence[str], None] = 'ddd42c788f2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'users',
        sa.Column('is_superadmin', sa.Boolean(), nullable=False, server_default='false'),
    )
    # Migra la regla anterior (comparar contra un correo fijo) a la cuenta
    # que ya exista con ese correo, si la hay.
    op.execute(
        "UPDATE users SET is_superadmin = true WHERE email = 'admin@erp.local'"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('users', 'is_superadmin')
