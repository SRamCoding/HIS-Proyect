"""drop_system_roles

Revision ID: eacc05588786
Revises: a1828c843894
Create Date: 2026-09-16 12:56:41.115101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eacc05588786'
down_revision: Union[str, Sequence[str], None] = 'a1828c843894'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # app/admin/roles (SystemRole) no tenia ningun consumidor en el
    # frontend -- ni una sola pantalla lo llamaba -- y sus unicas
    # referencias en el backend (auth/seeder.py, admin/seeder_niveles.py)
    # eran imports sin usar. El sistema de roles real, con CRUD completo,
    # es RolSistema (SIGARH -> Mantenimiento -> Roles del Sistema).
    op.drop_table('system_roles')


def downgrade() -> None:
    op.create_table(
        'system_roles',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('label', sa.String(length=255), nullable=False),
        sa.Column('panel', sa.String(length=50), nullable=False),
        sa.Column('required_module', sa.String(length=100), nullable=True),
        sa.Column('allowed_modules', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('sort_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )
