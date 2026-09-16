"""merge heads sesion multi-agente y limpieza admin

Revision ID: e4f3bfacf4f5
Revises: b5f83c1a7e6d, d531c26e6a2c
Create Date: 2026-09-16 17:18:21.814051

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4f3bfacf4f5'
down_revision: Union[str, Sequence[str], None] = ('b5f83c1a7e6d', 'd531c26e6a2c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
