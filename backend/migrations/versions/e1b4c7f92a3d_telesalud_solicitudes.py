"""telesalud_solicitudes

Revision ID: e1b4c7f92a3d
Revises: d9a3f6c82e1b
Create Date: 2026-09-15 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'e1b4c7f92a3d'
down_revision: Union[str, Sequence[str], None] = 'd9a3f6c82e1b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('telesalud_solicitudes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('especialidad_id', sa.UUID(), nullable=True),
    sa.Column('cita_id', sa.UUID(), nullable=True),
    sa.Column('motivo', sa.Text(), nullable=False),
    sa.Column('medio_preferido', sa.String(length=20), nullable=False),
    sa.Column('contacto', sa.String(length=100), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('motivo_rechazo', sa.Text(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('atendido_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['especialidad_id'], ['sigarh_especialidades.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['cita_id'], ['citas.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('cita_id'),
    )
    op.create_index(op.f('ix_telesalud_solicitudes_estado'), 'telesalud_solicitudes', ['estado'], unique=False)
    op.create_index(op.f('ix_telesalud_solicitudes_tenant_id'), 'telesalud_solicitudes', ['tenant_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_telesalud_solicitudes_tenant_id'), table_name='telesalud_solicitudes')
    op.drop_index(op.f('ix_telesalud_solicitudes_estado'), table_name='telesalud_solicitudes')
    op.drop_table('telesalud_solicitudes')
