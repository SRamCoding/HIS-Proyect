"""merge admin_solo_lectura y hc_dni_alias

Revision ID: c82bb97158ff
Revises: d2e3f4a5b6c7, d4e5f6a7b8c9
Create Date: 2026-09-23 14:51:32.914099

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c82bb97158ff'
down_revision: Union[str, Sequence[str], None] = ('d2e3f4a5b6c7', 'd4e5f6a7b8c9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
