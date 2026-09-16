"""provisioning status en tenants

Revision ID: d531c26e6a2c
Revises: 3ef65afd331c
Create Date: 2026-09-15 16:55:43.002213

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd531c26e6a2c'
down_revision: Union[str, Sequence[str], None] = '3ef65afd331c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        'tenants',
        sa.Column('provisioning_status', sa.String(length=20), nullable=False, server_default='listo'),
    )
    op.add_column(
        'tenants',
        sa.Column('provisioning_error', sa.Text(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('tenants', 'provisioning_error')
    op.drop_column('tenants', 'provisioning_status')
