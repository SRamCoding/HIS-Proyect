"""firma_electronica

Revision ID: d6e91a4c7f2b
Revises: c2f7b83e6a1d
Create Date: 2026-09-16 20:00:00.000000

Incluye ademas dos columnas que le faltaban a atenciones_emergencia para
tener la misma trazabilidad de firma que atenciones_medicas ya tenia
(firmado_por_id, cierre_evidencia) -- necesarias para que la Bandeja de
Firma Electronica pueda registrar la evidencia de ambos tipos de documento
por igual.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd6e91a4c7f2b'
down_revision: Union[str, Sequence[str], None] = 'c2f7b83e6a1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('atenciones_emergencia', sa.Column('firmado_por_id', sa.UUID(), nullable=True))
    op.add_column('atenciones_emergencia', sa.Column('cierre_evidencia', sa.JSON(), nullable=True))
    op.create_foreign_key('fk_atenciones_emergencia_firmado_por_id', 'atenciones_emergencia',
        'sigarh_empleados', ['firmado_por_id'], ['id'], ondelete='SET NULL')

    op.create_table('firma_electronica_registros',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('documento_tipo', sa.String(length=30), nullable=False),
    sa.Column('documento_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('firmante_id', sa.UUID(), nullable=False),
    sa.Column('firmante_nombre', sa.String(length=255), nullable=False),
    sa.Column('numero_colegiatura', sa.String(length=50), nullable=True),
    sa.Column('sha256', sa.String(length=64), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['firmante_id'], ['sigarh_empleados.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_firma_electronica_registros_tenant_id'), 'firma_electronica_registros', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_firma_electronica_registros_documento_tipo'), 'firma_electronica_registros', ['documento_tipo'], unique=False)
    op.create_index(op.f('ix_firma_electronica_registros_documento_id'), 'firma_electronica_registros', ['documento_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_firma_electronica_registros_documento_id'), table_name='firma_electronica_registros')
    op.drop_index(op.f('ix_firma_electronica_registros_documento_tipo'), table_name='firma_electronica_registros')
    op.drop_index(op.f('ix_firma_electronica_registros_tenant_id'), table_name='firma_electronica_registros')
    op.drop_table('firma_electronica_registros')

    op.drop_constraint('fk_atenciones_emergencia_firmado_por_id', 'atenciones_emergencia', type_='foreignkey')
    op.drop_column('atenciones_emergencia', 'cierre_evidencia')
    op.drop_column('atenciones_emergencia', 'firmado_por_id')
