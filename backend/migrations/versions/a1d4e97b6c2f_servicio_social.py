"""servicio_social

Revision ID: a1d4e97b6c2f
Revises: f7a2c85e0b3d
Create Date: 2026-09-17 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1d4e97b6c2f'
down_revision: Union[str, Sequence[str], None] = 'f7a2c85e0b3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('servicio_social_correlativos',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('tipo', sa.String(length=30), nullable=False),
    sa.Column('valor', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('tenant_id', 'tipo'),
    )

    op.create_table('servicio_social_evaluaciones',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('atencion_medica_id', sa.UUID(), nullable=True),
    sa.Column('atencion_emergencia_id', sa.UUID(), nullable=True),
    sa.Column('hospitalizacion_id', sa.UUID(), nullable=True),
    sa.Column('trabajador_social_id', sa.UUID(), nullable=False),
    sa.Column('numero_ficha', sa.String(length=30), nullable=False),
    sa.Column('fecha_evaluacion', sa.Date(), nullable=False),
    sa.Column('tipo_vivienda', sa.String(length=30), nullable=True),
    sa.Column('clasificacion_socioeconomica', sa.String(length=20), nullable=True),
    sa.Column('red_apoyo_familiar', sa.Text(), nullable=True),
    sa.Column('factores_riesgo', sa.JSON(), nullable=True),
    sa.Column('requiere_derivacion_externa', sa.Boolean(), nullable=False),
    sa.Column('entidad_derivacion', sa.String(length=20), nullable=True),
    sa.Column('recomendaciones', sa.Text(), nullable=True),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('fecha_cierre', sa.Date(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['atencion_medica_id'], ['atenciones_medicas.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['atencion_emergencia_id'], ['atenciones_emergencia.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['hospitalizacion_id'], ['hospitalizaciones.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['trabajador_social_id'], ['sigarh_empleados.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero_ficha'),
    )
    op.create_index(op.f('ix_servicio_social_evaluaciones_tenant_id'), 'servicio_social_evaluaciones', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_servicio_social_evaluaciones_estado'), 'servicio_social_evaluaciones', ['estado'], unique=False)

    op.create_table('servicio_social_gestiones',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('evaluacion_social_id', sa.UUID(), nullable=False),
    sa.Column('fecha', sa.DateTime(), nullable=False),
    sa.Column('tipo_gestion', sa.String(length=30), nullable=False),
    sa.Column('descripcion', sa.Text(), nullable=False),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['evaluacion_social_id'], ['servicio_social_evaluaciones.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_servicio_social_gestiones_tenant_id'), 'servicio_social_gestiones', ['tenant_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_servicio_social_gestiones_tenant_id'), table_name='servicio_social_gestiones')
    op.drop_table('servicio_social_gestiones')

    op.drop_index(op.f('ix_servicio_social_evaluaciones_estado'), table_name='servicio_social_evaluaciones')
    op.drop_index(op.f('ix_servicio_social_evaluaciones_tenant_id'), table_name='servicio_social_evaluaciones')
    op.drop_table('servicio_social_evaluaciones')

    op.drop_table('servicio_social_correlativos')
