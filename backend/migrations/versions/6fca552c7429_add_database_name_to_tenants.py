"""add database_name to tenants

Revision ID: 6fca552c7429
Revises: c5c503da0eea
Create Date: 2026-09-10 12:12:47.414470

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '6fca552c7429'
down_revision: Union[str, Sequence[str], None] = 'c5c503da0eea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('tenants', sa.Column('database_name', sa.String(length=100), nullable=True))
    op.create_unique_constraint(None, 'tenants', ['database_name'])


def downgrade() -> None:
    op.drop_constraint(None, 'tenants', type_='unique')
    op.drop_column('tenants', 'database_name')