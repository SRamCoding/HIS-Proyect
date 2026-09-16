"""medicina_fisica

Revision ID: c2f7b83e6a1d
Revises: a8c5e19d4f7b
Create Date: 2026-09-16 18:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2f7b83e6a1d'
down_revision: Union[str, Sequence[str], None] = 'a8c5e19d4f7b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('medicina_fisica_programas',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('nombre', sa.String(length=150), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=True),
    sa.Column('duracion_sesion_minutos', sa.Integer(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tenant_id', 'nombre', name='uq_mf_programa_tenant_nombre'),
    )
    op.create_index(op.f('ix_medicina_fisica_programas_tenant_id'), 'medicina_fisica_programas', ['tenant_id'], unique=False)

    op.create_table('medicina_fisica_tecnologo_programa',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('programa_id', sa.UUID(), nullable=False),
    sa.Column('empleado_id', sa.UUID(), nullable=False),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['programa_id'], ['medicina_fisica_programas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['empleado_id'], ['sigarh_empleados.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('programa_id', 'empleado_id', name='uq_mf_tecnologo_programa'),
    )
    op.create_index(op.f('ix_medicina_fisica_tecnologo_programa_tenant_id'), 'medicina_fisica_tecnologo_programa', ['tenant_id'], unique=False)

    op.create_table('medicina_fisica_programaciones',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('programa_id', sa.UUID(), nullable=False),
    sa.Column('tecnologo_id', sa.UUID(), nullable=False),
    sa.Column('fecha', sa.Date(), nullable=False),
    sa.Column('turno', sa.String(length=20), nullable=False),
    sa.Column('hora_inicio', sa.String(length=5), nullable=False),
    sa.Column('hora_fin', sa.String(length=5), nullable=False),
    sa.Column('tiempo_sesion_minutos', sa.Integer(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('motivo_bloqueo', sa.Text(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['programa_id'], ['medicina_fisica_programas.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['tecnologo_id'], ['sigarh_empleados.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_medicina_fisica_programaciones_tenant_id'), 'medicina_fisica_programaciones', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_medicina_fisica_programaciones_estado'), 'medicina_fisica_programaciones', ['estado'], unique=False)

    op.create_table('medicina_fisica_sesiones',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('programacion_mf_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('hora_inicio', sa.String(length=5), nullable=False),
    sa.Column('hora_fin', sa.String(length=5), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('escala_dolor_eva', sa.Integer(), nullable=True),
    sa.Column('actividades_realizadas', sa.Text(), nullable=True),
    sa.Column('evolucion', sa.Text(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['programacion_mf_id'], ['medicina_fisica_programaciones.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_medicina_fisica_sesiones_tenant_id'), 'medicina_fisica_sesiones', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_medicina_fisica_sesiones_estado'), 'medicina_fisica_sesiones', ['estado'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_medicina_fisica_sesiones_estado'), table_name='medicina_fisica_sesiones')
    op.drop_index(op.f('ix_medicina_fisica_sesiones_tenant_id'), table_name='medicina_fisica_sesiones')
    op.drop_table('medicina_fisica_sesiones')

    op.drop_index(op.f('ix_medicina_fisica_programaciones_estado'), table_name='medicina_fisica_programaciones')
    op.drop_index(op.f('ix_medicina_fisica_programaciones_tenant_id'), table_name='medicina_fisica_programaciones')
    op.drop_table('medicina_fisica_programaciones')

    op.drop_index(op.f('ix_medicina_fisica_tecnologo_programa_tenant_id'), table_name='medicina_fisica_tecnologo_programa')
    op.drop_table('medicina_fisica_tecnologo_programa')

    op.drop_index(op.f('ix_medicina_fisica_programas_tenant_id'), table_name='medicina_fisica_programas')
    op.drop_table('medicina_fisica_programas')
