"""sis_formato_fua

Revision ID: c7e2a5f91b4d
Revises: b8f1c4a29d6e
Create Date: 2026-09-15 16:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7e2a5f91b4d'
down_revision: Union[str, Sequence[str], None] = 'b8f1c4a29d6e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('sis_correlativos',
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('tipo', sa.String(length=20), nullable=False),
    sa.Column('valor', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('tenant_id', 'tipo')
    )

    op.create_table('sis_formatos_fua',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('atencion_medica_id', sa.UUID(), nullable=True),
    sa.Column('atencion_emergencia_id', sa.UUID(), nullable=True),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('seguro_id', sa.UUID(), nullable=False),
    sa.Column('numero_fua', sa.String(length=40), nullable=False),
    sa.Column('fecha_atencion', sa.DateTime(), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('observaciones', sa.Text(), nullable=True),
    sa.Column('registrado_por', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['atencion_emergencia_id'], ['atenciones_emergencia.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['atencion_medica_id'], ['atenciones_medicas.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['seguro_id'], ['sigarh_seguros.id'], ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('atencion_emergencia_id'),
    sa.UniqueConstraint('atencion_medica_id'),
    sa.UniqueConstraint('tenant_id', 'numero_fua'),
    )
    op.create_index(op.f('ix_sis_formatos_fua_estado'), 'sis_formatos_fua', ['estado'], unique=False)
    op.create_index(op.f('ix_sis_formatos_fua_numero_fua'), 'sis_formatos_fua', ['numero_fua'], unique=False)
    op.create_index(op.f('ix_sis_formatos_fua_tenant_id'), 'sis_formatos_fua', ['tenant_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_sis_formatos_fua_tenant_id'), table_name='sis_formatos_fua')
    op.drop_index(op.f('ix_sis_formatos_fua_numero_fua'), table_name='sis_formatos_fua')
    op.drop_index(op.f('ix_sis_formatos_fua_estado'), table_name='sis_formatos_fua')
    op.drop_table('sis_formatos_fua')
    op.drop_table('sis_correlativos')
