"""merge heads categoria personal y database name

Revision ID: dc2b4ceb7cdd
Revises: 6fca552c7429, f2a6c19b7d84
Create Date: 2026-09-11 09:49:22.052792

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc2b4ceb7cdd'
down_revision: Union[str, Sequence[str], None] = ('6fca552c7429', 'f2a6c19b7d84')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
