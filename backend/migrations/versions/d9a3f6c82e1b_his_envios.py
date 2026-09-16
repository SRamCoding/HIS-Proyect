"""his_envios

Revision ID: d9a3f6c82e1b
Revises: c7e2a5f91b4d
Create Date: 2026-09-15 17:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9a3f6c82e1b'
down_revision: Union[str, Sequence[str], None] = 'c7e2a5f91b4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('his_envios',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('periodo', sa.String(length=7), nullable=False),
    sa.Column('fecha_desde', sa.Date(), nullable=False),
    sa.Column('fecha_hasta', sa.Date(), nullable=False),
    sa.Column('total_registros', sa.Integer(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('fecha_envio', sa.DateTime(), nullable=True),
    sa.Column('observaciones', sa.Text(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tenant_id', 'periodo'),
    )
    op.create_index(op.f('ix_his_envios_estado'), 'his_envios', ['estado'], unique=False)
    op.create_index(op.f('ix_his_envios_tenant_id'), 'his_envios', ['tenant_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_his_envios_tenant_id'), table_name='his_envios')
    op.drop_index(op.f('ix_his_envios_estado'), table_name='his_envios')
    op.drop_table('his_envios')
