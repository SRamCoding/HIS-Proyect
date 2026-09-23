"""notificaciones_sigarh

Revision ID: e5f6a7b8c9d0
Revises: c82bb97158ff
Create Date: 2026-09-23 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e5f6a7b8c9d0'
down_revision: Union[str, Sequence[str], None] = 'c82bb97158ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('notificaciones_sigarh',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('cuerpo', sa.Text(), nullable=True),
        sa.Column('nivel', sa.String(length=20), nullable=False),
        sa.Column('link', sa.String(length=500), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('notificaciones_sigarh')
