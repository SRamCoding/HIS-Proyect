"""merge heads panel verde y aprovisionamiento admin

Revision ID: 8fabfac480de
Revises: e4f3bfacf4f5, ff649796d2de
Create Date: 2026-09-16 18:10:26.356378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fabfac480de'
down_revision: Union[str, Sequence[str], None] = ('e4f3bfacf4f5', 'ff649796d2de')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
