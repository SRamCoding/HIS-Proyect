"""merge heads imagenologia y accesos compartidos sigarh

Revision ID: a91d47c30b5e
Revises: f3a8c92e6d17, f94c23b6de51
Create Date: 2026-09-14 00:05:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a91d47c30b5e'
down_revision: Union[str, Sequence[str], None] = ('f3a8c92e6d17', 'f94c23b6de51')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
