"""provisioning_started_at

Revision ID: a1828c843894
Revises: 768e554fcb73
Create Date: 2026-09-16 12:40:32.059164

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1828c843894'
down_revision: Union[str, Sequence[str], None] = '768e554fcb73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tenants', sa.Column('provisioning_started_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('tenants', 'provisioning_started_at')
