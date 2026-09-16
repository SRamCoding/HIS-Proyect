"""epidemiologia_fichas

Revision ID: f7a2c85e0b3d
Revises: e3b8f61a9c4d
Create Date: 2026-09-17 11:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f7a2c85e0b3d'
down_revision: Union[str, Sequence[str], None] = 'e3b8f61a9c4d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('epidemiologia_correlativos',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('tipo', sa.String(length=30), nullable=False),
    sa.Column('valor', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('tenant_id', 'tipo'),
    )

    op.create_table('epidemiologia_fichas',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('atencion_medica_id', sa.UUID(), nullable=True),
    sa.Column('atencion_emergencia_id', sa.UUID(), nullable=True),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('diagnostico_cie10_id', sa.UUID(), nullable=True),
    sa.Column('medico_notificante_id', sa.UUID(), nullable=False),
    sa.Column('numero_ficha', sa.String(length=30), nullable=False),
    sa.Column('tipo_ficha', sa.String(length=20), nullable=False),
    sa.Column('fecha_notificacion', sa.Date(), nullable=False),
    sa.Column('datos_clinicos', sa.JSON(), nullable=False),
    sa.Column('estado_envio', sa.String(length=20), nullable=False),
    sa.Column('fecha_envio', sa.DateTime(), nullable=True),
    sa.Column('observaciones', sa.Text(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['atencion_medica_id'], ['atenciones_medicas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['atencion_emergencia_id'], ['atenciones_emergencia.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['diagnostico_cie10_id'], ['sigarh_diagnosticos_cie10.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['medico_notificante_id'], ['sigarh_empleados.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero_ficha'),
    sa.UniqueConstraint('atencion_medica_id', 'tipo_ficha', name='uq_ficha_epi_atencion_medica_tipo'),
    sa.UniqueConstraint('atencion_emergencia_id', 'tipo_ficha', name='uq_ficha_epi_atencion_emergencia_tipo'),
    )
    op.create_index(op.f('ix_epidemiologia_fichas_tenant_id'), 'epidemiologia_fichas', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_epidemiologia_fichas_tipo_ficha'), 'epidemiologia_fichas', ['tipo_ficha'], unique=False)
    op.create_index(op.f('ix_epidemiologia_fichas_estado_envio'), 'epidemiologia_fichas', ['estado_envio'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_epidemiologia_fichas_estado_envio'), table_name='epidemiologia_fichas')
    op.drop_index(op.f('ix_epidemiologia_fichas_tipo_ficha'), table_name='epidemiologia_fichas')
    op.drop_index(op.f('ix_epidemiologia_fichas_tenant_id'), table_name='epidemiologia_fichas')
    op.drop_table('epidemiologia_fichas')
    op.drop_table('epidemiologia_correlativos')
