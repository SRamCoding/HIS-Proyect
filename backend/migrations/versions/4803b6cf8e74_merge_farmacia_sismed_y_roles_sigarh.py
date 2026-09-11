"""merge farmacia sismed y roles sigarh

Revision ID: 4803b6cf8e74
Revises: 4168b3a941c7, 9b7e2a1c4d60
Create Date: 2026-09-10 11:19:29.370033

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4803b6cf8e74'
down_revision: Union[str, Sequence[str], None] = ('4168b3a941c7', '9b7e2a1c4d60')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
