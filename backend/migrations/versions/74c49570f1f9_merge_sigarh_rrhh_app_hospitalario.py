"""merge sigarh rrhh + app hospitalario

Revision ID: 74c49570f1f9
Revises: 3df7fd60dc0a, c53a81f904bd
Create Date: 2026-09-09 11:10:24.744360

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '74c49570f1f9'
down_revision: Union[str, Sequence[str], None] = ('3df7fd60dc0a', 'c53a81f904bd')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
