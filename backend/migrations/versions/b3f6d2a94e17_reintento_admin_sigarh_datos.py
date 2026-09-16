"""reintento_admin_sigarh_datos

Revision ID: b3f6d2a94e17
Revises: eacc05588786
Create Date: 2026-09-16 22:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3f6d2a94e17'
down_revision: Union[str, Sequence[str], None] = 'eacc05588786'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tenants', sa.Column('admin_name', sa.String(length=255), nullable=True))
    op.add_column('tenants', sa.Column('admin_email', sa.String(length=255), nullable=True))
    op.add_column('tenants', sa.Column('sigarh_name', sa.String(length=255), nullable=True))
    op.add_column('tenants', sa.Column('sigarh_email', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('tenants', 'sigarh_email')
    op.drop_column('tenants', 'sigarh_name')
    op.drop_column('tenants', 'admin_email')
    op.drop_column('tenants', 'admin_name')
