"""admision_lista_espera_anuncios_mensajes

Revision ID: a673102f5c2e
Revises: d4f27b18e903
Create Date: 2026-09-15 10:26:01.187423

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a673102f5c2e'
down_revision: Union[str, Sequence[str], None] = 'd4f27b18e903'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('admision_anuncios',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('titulo', sa.String(length=150), nullable=False),
    sa.Column('contenido', sa.Text(), nullable=False),
    sa.Column('publicado_por', sa.String(length=255), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admision_anuncios_tenant_id'), 'admision_anuncios', ['tenant_id'], unique=False)

    op.create_table('admision_mensajes',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('remitente_user_id', sa.UUID(), nullable=False),
    sa.Column('remitente_nombre', sa.String(length=255), nullable=True),
    sa.Column('destinatario_user_id', sa.UUID(), nullable=True),
    sa.Column('destinatario_role', sa.String(length=50), nullable=True),
    sa.Column('patient_id', sa.UUID(), nullable=True),
    sa.Column('contenido', sa.String(length=500), nullable=False),
    sa.Column('leido', sa.Boolean(), nullable=False),
    sa.Column('leido_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['destinatario_user_id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['remitente_user_id'], ['users.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admision_mensajes_created_at'), 'admision_mensajes', ['created_at'], unique=False)
    op.create_index(op.f('ix_admision_mensajes_tenant_id'), 'admision_mensajes', ['tenant_id'], unique=False)

    op.create_table('admision_lista_espera',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('tenant_id', sa.UUID(), nullable=False),
    sa.Column('patient_id', sa.UUID(), nullable=False),
    sa.Column('servicio_id', sa.UUID(), nullable=True),
    sa.Column('especialidad_id', sa.UUID(), nullable=True),
    sa.Column('cita_id', sa.UUID(), nullable=True),
    sa.Column('motivo', sa.Text(), nullable=True),
    sa.Column('prioridad', sa.String(length=20), nullable=False),
    sa.Column('estado', sa.String(length=20), nullable=False),
    sa.Column('registrado_por', sa.String(length=255), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('atendido_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['cita_id'], ['citas.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['especialidad_id'], ['sigarh_especialidades.id'], ondelete='SET NULL'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['servicio_id'], ['sigarh_servicios.id'], ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admision_lista_espera_estado'), 'admision_lista_espera', ['estado'], unique=False)
    op.create_index(op.f('ix_admision_lista_espera_tenant_id'), 'admision_lista_espera', ['tenant_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_admision_lista_espera_tenant_id'), table_name='admision_lista_espera')
    op.drop_index(op.f('ix_admision_lista_espera_estado'), table_name='admision_lista_espera')
    op.drop_table('admision_lista_espera')

    op.drop_index(op.f('ix_admision_mensajes_tenant_id'), table_name='admision_mensajes')
    op.drop_index(op.f('ix_admision_mensajes_created_at'), table_name='admision_mensajes')
    op.drop_table('admision_mensajes')

    op.drop_index(op.f('ix_admision_anuncios_tenant_id'), table_name='admision_anuncios')
    op.drop_table('admision_anuncios')
