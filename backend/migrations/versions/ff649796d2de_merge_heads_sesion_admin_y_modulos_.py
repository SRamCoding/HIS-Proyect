"""merge heads sesion admin y modulos clinicos

Revision ID: ff649796d2de
Revises: b3f6d2a94e17, b5f83c1a7e6d
Create Date: 2026-09-16 17:50:03.228962

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ff649796d2de'
down_revision: Union[str, Sequence[str], None] = ('b3f6d2a94e17', 'b5f83c1a7e6d')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
