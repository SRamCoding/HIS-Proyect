"""salud_ambiental_defunciones

Revision ID: e3b8f61a9c4d
Revises: d6e91a4c7f2b
Create Date: 2026-09-17 09:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3b8f61a9c4d'
down_revision: Union[str, Sequence[str], None] = 'd6e91a4c7f2b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('salud_ambiental_correlativos',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('tipo', sa.String(length=30), nullable=False),
    sa.Column('valor', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('tenant_id', 'tipo'),
    )

    op.create_table('salud_ambiental_certificados_defuncion',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('atencion_emergencia_id', sa.UUID(), nullable=True),
    sa.Column('hospitalizacion_id', sa.UUID(), nullable=True),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('medico_certificador_id', sa.UUID(), nullable=False),
    sa.Column('numero_certificado', sa.String(length=30), nullable=False),
    sa.Column('fecha_defuncion', sa.DateTime(), nullable=False),
    sa.Column('lugar_defuncion', sa.String(length=255), nullable=False),
    sa.Column('tipo_muerte', sa.String(length=20), nullable=False),
    sa.Column('causa_a_id', sa.UUID(), nullable=False),
    sa.Column('causa_b_id', sa.UUID(), nullable=True),
    sa.Column('causa_c_id', sa.UUID(), nullable=True),
    sa.Column('causa_d_id', sa.UUID(), nullable=True),
    sa.Column('requiere_necropsia_legal', sa.Boolean(), nullable=False),
    sa.Column('estado_envio', sa.String(length=20), nullable=False),
    sa.Column('fecha_envio', sa.DateTime(), nullable=True),
    sa.Column('observaciones', sa.Text(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['atencion_emergencia_id'], ['atenciones_emergencia.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['hospitalizacion_id'], ['hospitalizaciones.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['medico_certificador_id'], ['sigarh_empleados.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['causa_a_id'], ['sigarh_diagnosticos_cie10.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['causa_b_id'], ['sigarh_diagnosticos_cie10.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['causa_c_id'], ['sigarh_diagnosticos_cie10.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['causa_d_id'], ['sigarh_diagnosticos_cie10.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('numero_certificado'),
    sa.UniqueConstraint('atencion_emergencia_id', name='uq_certdef_atencion_emergencia'),
    sa.UniqueConstraint('hospitalizacion_id', name='uq_certdef_hospitalizacion'),
    )
    op.create_index(op.f('ix_salud_ambiental_certificados_defuncion_tenant_id'), 'salud_ambiental_certificados_defuncion', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_salud_ambiental_certificados_defuncion_estado_envio'), 'salud_ambiental_certificados_defuncion', ['estado_envio'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_salud_ambiental_certificados_defuncion_estado_envio'), table_name='salud_ambiental_certificados_defuncion')
    op.drop_index(op.f('ix_salud_ambiental_certificados_defuncion_tenant_id'), table_name='salud_ambiental_certificados_defuncion')
    op.drop_table('salud_ambiental_certificados_defuncion')
    op.drop_table('salud_ambiental_correlativos')
