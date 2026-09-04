# backend/migrations/versions/6e49c8636a4d_agregar_campos_avanzados_a_roles_sistema.py
"""agregar campos avanzados a roles_sistema

Revision ID: 6e49c8636a4d
Revises: a2ff13ac6ba2
Create Date: 2026-09-04 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e49c8636a4d'
down_revision: Union[str, Sequence[str], None] = 'a2ff13ac6ba2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('sigarh_roles_sistema', sa.Column('codigo', sa.String(length=100), nullable=True))
    op.add_column('sigarh_roles_sistema', sa.Column('panel', sa.String(length=50), nullable=False, server_default='sigarh'))
    op.add_column('sigarh_roles_sistema', sa.Column('modulo_requerido', sa.String(length=100), nullable=True))
    op.add_column('sigarh_roles_sistema', sa.Column('modulos_permitidos', sa.Text(), nullable=True))
    op.add_column('sigarh_roles_sistema', sa.Column('grupos_ocupacionales_permitidos', sa.Text(), nullable=True))

    # Único compuesto: el código debe ser único por hospital, no global
    op.create_index(
        'ix_sigarh_roles_sistema_tenant_codigo',
        'sigarh_roles_sistema',
        ['tenant_id', 'codigo'],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_sigarh_roles_sistema_tenant_codigo', table_name='sigarh_roles_sistema')
    op.drop_column('sigarh_roles_sistema', 'grupos_ocupacionales_permitidos')
    op.drop_column('sigarh_roles_sistema', 'modulos_permitidos')
    op.drop_column('sigarh_roles_sistema', 'modulo_requerido')
    op.drop_column('sigarh_roles_sistema', 'panel')
    op.drop_column('sigarh_roles_sistema', 'codigo')