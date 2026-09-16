"""banco_sangre

Revision ID: f4a9d2e83b6c
Revises: e1b4c7f92a3d
Create Date: 2026-09-16 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4a9d2e83b6c'
down_revision: Union[str, Sequence[str], None] = 'e1b4c7f92a3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('banco_sangre_correlativos',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('tipo', sa.String(length=30), nullable=False),
    sa.Column('valor', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('tenant_id', 'tipo'),
    )

    op.create_table('banco_sangre_donantes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('dni', sa.String(length=15), nullable=False),
    sa.Column('nombres', sa.String(length=150), nullable=False),
    sa.Column('apellido_paterno', sa.String(length=100), nullable=False),
    sa.Column('apellido_materno', sa.String(length=100), nullable=False),
    sa.Column('fecha_nacimiento', sa.Date(), nullable=False),
    sa.Column('sexo', sa.String(length=1), nullable=False),
    sa.Column('celular', sa.String(length=15), nullable=True),
    sa.Column('correo', sa.String(length=255), nullable=True),
    sa.Column('direccion', sa.Text(), nullable=True),
    sa.Column('grupo_sanguineo', sa.String(length=2), nullable=True),
    sa.Column('factor_rh', sa.String(length=1), nullable=True),
    sa.Column('fecha_ultima_donacion', sa.Date(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('tenant_id', 'dni', name='uq_donante_tenant_dni'),
    )
    op.create_index(op.f('ix_banco_sangre_donantes_tenant_id'), 'banco_sangre_donantes', ['tenant_id'], unique=False)

    op.create_table('banco_sangre_unidades',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('donante_id', sa.UUID(), nullable=False),
    sa.Column('numero_unidad', sa.String(length=30), nullable=False),
    sa.Column('fecha_extraccion', sa.DateTime(), nullable=False),
    sa.Column('peso_kg', sa.Float(), nullable=True),
    sa.Column('hemoglobina_g_dl', sa.Float(), nullable=True),
    sa.Column('presion_sistolica', sa.Integer(), nullable=True),
    sa.Column('presion_diastolica', sa.Integer(), nullable=True),
    sa.Column('grupo_sanguineo', sa.String(length=2), nullable=False),
    sa.Column('factor_rh', sa.String(length=1), nullable=False),
    sa.Column('vih_reactivo', sa.Boolean(), nullable=True),
    sa.Column('hbsag_reactivo', sa.Boolean(), nullable=True),
    sa.Column('hcv_reactivo', sa.Boolean(), nullable=True),
    sa.Column('sifilis_reactivo', sa.Boolean(), nullable=True),
    sa.Column('chagas_reactivo', sa.Boolean(), nullable=True),
    sa.Column('tamizaje_registrado_at', sa.DateTime(), nullable=True),
    sa.Column('apto', sa.Boolean(), nullable=True),
    sa.Column('motivo_diferido', sa.Text(), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['donante_id'], ['banco_sangre_donantes.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero_unidad'),
    )
    op.create_index(op.f('ix_banco_sangre_unidades_tenant_id'), 'banco_sangre_unidades', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_banco_sangre_unidades_estado'), 'banco_sangre_unidades', ['estado'], unique=False)

    op.create_table('banco_sangre_componentes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('unidad_sangre_id', sa.UUID(), nullable=False),
    sa.Column('codigo', sa.String(length=30), nullable=False),
    sa.Column('tipo', sa.String(length=30), nullable=False),
    sa.Column('grupo_sanguineo', sa.String(length=2), nullable=False),
    sa.Column('factor_rh', sa.String(length=1), nullable=False),
    sa.Column('fecha_produccion', sa.DateTime(), nullable=False),
    sa.Column('fecha_vencimiento', sa.Date(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['unidad_sangre_id'], ['banco_sangre_unidades.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('codigo'),
    )
    op.create_index(op.f('ix_banco_sangre_componentes_tenant_id'), 'banco_sangre_componentes', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_banco_sangre_componentes_estado'), 'banco_sangre_componentes', ['estado'], unique=False)

    op.create_table('banco_sangre_solicitudes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('atencion_medica_id', sa.UUID(), nullable=True),
    sa.Column('atencion_emergencia_id', sa.UUID(), nullable=True),
    sa.Column('hospitalizacion_id', sa.UUID(), nullable=True),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('medico_solicitante_id', sa.UUID(), nullable=True),
    sa.Column('numero_solicitud', sa.String(length=30), nullable=False),
    sa.Column('tipo_componente', sa.String(length=30), nullable=False),
    sa.Column('cantidad_unidades', sa.Integer(), nullable=False),
    sa.Column('grupo_sanguineo_paciente', sa.String(length=2), nullable=False),
    sa.Column('factor_rh_paciente', sa.String(length=1), nullable=False),
    sa.Column('urgencia', sa.String(length=20), nullable=False),
    sa.Column('motivo_clinico', sa.Text(), nullable=False),
    sa.Column('estado', sa.String(length=30), nullable=False),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['atencion_medica_id'], ['atenciones_medicas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['atencion_emergencia_id'], ['atenciones_emergencia.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['hospitalizacion_id'], ['hospitalizaciones.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['medico_solicitante_id'], ['sigarh_empleados.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero_solicitud'),
    )
    op.create_index(op.f('ix_banco_sangre_solicitudes_tenant_id'), 'banco_sangre_solicitudes', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_banco_sangre_solicitudes_estado'), 'banco_sangre_solicitudes', ['estado'], unique=False)

    op.create_table('banco_sangre_solicitud_componentes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('solicitud_id', sa.UUID(), nullable=False),
    sa.Column('componente_id', sa.UUID(), nullable=False),
    sa.Column('resultado_prueba_cruzada', sa.String(length=20), nullable=False),
    sa.Column('observaciones', sa.Text(), nullable=True),
    sa.Column('prueba_cruzada_por', sa.String(length=255), nullable=True),
    sa.Column('prueba_cruzada_at', sa.DateTime(), nullable=True),
    sa.Column('dispensado', sa.Boolean(), nullable=False),
    sa.Column('dispensado_por', sa.String(length=255), nullable=True),
    sa.Column('dispensado_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['solicitud_id'], ['banco_sangre_solicitudes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['componente_id'], ['banco_sangre_componentes.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('componente_id', name='uq_componente_una_asignacion'),
    )
    op.create_index(op.f('ix_banco_sangre_solicitud_componentes_tenant_id'), 'banco_sangre_solicitud_componentes', ['tenant_id'], unique=False)

    op.create_table('banco_sangre_movimientos',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('componente_id', sa.UUID(), nullable=False),
    sa.Column('solicitud_id', sa.UUID(), nullable=True),
    sa.Column('tipo', sa.String(length=30), nullable=False),
    sa.Column('observaciones', sa.Text(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['componente_id'], ['banco_sangre_componentes.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['solicitud_id'], ['banco_sangre_solicitudes.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_banco_sangre_movimientos_tenant_id'), 'banco_sangre_movimientos', ['tenant_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_banco_sangre_movimientos_tenant_id'), table_name='banco_sangre_movimientos')
    op.drop_table('banco_sangre_movimientos')

    op.drop_index(op.f('ix_banco_sangre_solicitud_componentes_tenant_id'), table_name='banco_sangre_solicitud_componentes')
    op.drop_table('banco_sangre_solicitud_componentes')

    op.drop_index(op.f('ix_banco_sangre_solicitudes_estado'), table_name='banco_sangre_solicitudes')
    op.drop_index(op.f('ix_banco_sangre_solicitudes_tenant_id'), table_name='banco_sangre_solicitudes')
    op.drop_table('banco_sangre_solicitudes')

    op.drop_index(op.f('ix_banco_sangre_componentes_estado'), table_name='banco_sangre_componentes')
    op.drop_index(op.f('ix_banco_sangre_componentes_tenant_id'), table_name='banco_sangre_componentes')
    op.drop_table('banco_sangre_componentes')

    op.drop_index(op.f('ix_banco_sangre_unidades_estado'), table_name='banco_sangre_unidades')
    op.drop_index(op.f('ix_banco_sangre_unidades_tenant_id'), table_name='banco_sangre_unidades')
    op.drop_table('banco_sangre_unidades')

    op.drop_index(op.f('ix_banco_sangre_donantes_tenant_id'), table_name='banco_sangre_donantes')
    op.drop_table('banco_sangre_donantes')

    op.drop_table('banco_sangre_correlativos')
