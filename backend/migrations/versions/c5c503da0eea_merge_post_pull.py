"""merge post-pull

Revision ID: c5c503da0eea
Revises: 4803b6cf8e74, e7a914c02f65
Create Date: 2026-09-10 12:12:36.041584

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5c503da0eea'
down_revision: Union[str, Sequence[str], None] = ('4803b6cf8e74', 'e7a914c02f65')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
