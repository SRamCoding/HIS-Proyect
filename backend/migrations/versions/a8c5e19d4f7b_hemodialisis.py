"""hemodialisis

Revision ID: a8c5e19d4f7b
Revises: f4a9d2e83b6c
Create Date: 2026-09-16 15:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a8c5e19d4f7b'
down_revision: Union[str, Sequence[str], None] = 'f4a9d2e83b6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('hemodialisis_pacientes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('diagnostico_id', sa.UUID(), nullable=True),
    sa.Column('medico_nefrologo_id', sa.UUID(), nullable=True),
    sa.Column('fecha_ingreso_programa', sa.Date(), nullable=False),
    sa.Column('acceso_vascular_tipo', sa.String(length=30), nullable=False),
    sa.Column('fecha_creacion_acceso', sa.Date(), nullable=True),
    sa.Column('peso_seco_kg', sa.Float(), nullable=False),
    sa.Column('turno_habitual', sa.String(length=20), nullable=False),
    sa.Column('frecuencia_semanal', sa.Integer(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('fecha_estado', sa.Date(), nullable=True),
    sa.Column('observaciones', sa.Text(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['diagnostico_id'], ['sigarh_diagnosticos_cie10.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['medico_nefrologo_id'], ['sigarh_empleados.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tenant_id', 'patient_id', name='uq_hd_paciente_tenant_patient'),
    )
    op.create_index(op.f('ix_hemodialisis_pacientes_tenant_id'), 'hemodialisis_pacientes', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_hemodialisis_pacientes_estado'), 'hemodialisis_pacientes', ['estado'], unique=False)

    op.create_table('hemodialisis_sesiones',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('paciente_hemodialisis_id', sa.UUID(), nullable=False),
    sa.Column('fecha', sa.Date(), nullable=False),
    sa.Column('turno', sa.String(length=20), nullable=False),
    sa.Column('numero_maquina', sa.String(length=20), nullable=True),
    sa.Column('hora_inicio', sa.String(length=5), nullable=True),
    sa.Column('hora_fin', sa.String(length=5), nullable=True),
    sa.Column('tiempo_sesion_horas', sa.Float(), nullable=True),
    sa.Column('peso_pre_kg', sa.Float(), nullable=True),
    sa.Column('peso_post_kg', sa.Float(), nullable=True),
    sa.Column('ultrafiltracion_litros', sa.Float(), nullable=True),
    sa.Column('presion_pre_sistolica', sa.Integer(), nullable=True),
    sa.Column('presion_pre_diastolica', sa.Integer(), nullable=True),
    sa.Column('presion_post_sistolica', sa.Integer(), nullable=True),
    sa.Column('presion_post_diastolica', sa.Integer(), nullable=True),
    sa.Column('acceso_vascular_utilizado', sa.String(length=30), nullable=True),
    sa.Column('heparinizacion', sa.Boolean(), nullable=False),
    sa.Column('complicaciones', sa.Text(), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('observaciones', sa.Text(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['paciente_hemodialisis_id'], ['hemodialisis_pacientes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_hemodialisis_sesiones_tenant_id'), 'hemodialisis_sesiones', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_hemodialisis_sesiones_estado'), 'hemodialisis_sesiones', ['estado'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_hemodialisis_sesiones_estado'), table_name='hemodialisis_sesiones')
    op.drop_index(op.f('ix_hemodialisis_sesiones_tenant_id'), table_name='hemodialisis_sesiones')
    op.drop_table('hemodialisis_sesiones')

    op.drop_index(op.f('ix_hemodialisis_pacientes_estado'), table_name='hemodialisis_pacientes')
    op.drop_index(op.f('ix_hemodialisis_pacientes_tenant_id'), table_name='hemodialisis_pacientes')
    op.drop_table('hemodialisis_pacientes')
