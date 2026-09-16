"""procedimientos

Revision ID: b5f83c1a7e6d
Revises: a1d4e97b6c2f
Create Date: 2026-09-17 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5f83c1a7e6d'
down_revision: Union[str, Sequence[str], None] = 'a1d4e97b6c2f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('procedimientos_correlativos',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('tipo', sa.String(length=30), nullable=False),
    sa.Column('valor', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('tenant_id', 'tipo'),
    )

    op.create_table('procedimientos_asignaciones',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('tiempo_procedimiento_id', sa.UUID(), nullable=False),
    sa.Column('empleado_id', sa.UUID(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['tiempo_procedimiento_id'], ['sigarh_tiempos_procedimientos.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['empleado_id'], ['sigarh_empleados.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tiempo_procedimiento_id', 'empleado_id', name='uq_proc_asignacion'),
    )
    op.create_index(op.f('ix_procedimientos_asignaciones_tenant_id'), 'procedimientos_asignaciones', ['tenant_id'], unique=False)

    op.create_table('procedimientos_atenciones',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('atencion_medica_id', sa.UUID(), nullable=True),
    sa.Column('atencion_emergencia_id', sa.UUID(), nullable=True),
    sa.Column('hospitalizacion_id', sa.UUID(), nullable=True),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('tiempo_procedimiento_id', sa.UUID(), nullable=False),
    sa.Column('empleado_ejecutor_id', sa.UUID(), nullable=False),
    sa.Column('numero_atencion', sa.String(length=30), nullable=False),
    sa.Column('fecha_hora', sa.DateTime(), nullable=False),
    sa.Column('consentimiento_informado', sa.Boolean(), nullable=False),
    sa.Column('hallazgos', sa.Text(), nullable=True),
    sa.Column('complicaciones', sa.Text(), nullable=True),
    sa.Column('motivo_cancelacion', sa.Text(), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['atencion_medica_id'], ['atenciones_medicas.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['atencion_emergencia_id'], ['atenciones_emergencia.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['hospitalizacion_id'], ['hospitalizaciones.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['tiempo_procedimiento_id'], ['sigarh_tiempos_procedimientos.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['empleado_ejecutor_id'], ['sigarh_empleados.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero_atencion'),
    )
    op.create_index(op.f('ix_procedimientos_atenciones_tenant_id'), 'procedimientos_atenciones', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_procedimientos_atenciones_estado'), 'procedimientos_atenciones', ['estado'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_procedimientos_atenciones_estado'), table_name='procedimientos_atenciones')
    op.drop_index(op.f('ix_procedimientos_atenciones_tenant_id'), table_name='procedimientos_atenciones')
    op.drop_table('procedimientos_atenciones')

    op.drop_index(op.f('ix_procedimientos_asignaciones_tenant_id'), table_name='procedimientos_asignaciones')
    op.drop_table('procedimientos_asignaciones')

    op.drop_table('procedimientos_correlativos')
