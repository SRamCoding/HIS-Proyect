# backend/migrations/versions/a2ff13ac6ba2_agregar_tenant_id_a_patients.py
"""agregar tenant_id a patients

Revision ID: a2ff13ac6ba2
Revises: f43ee115cbbc
Create Date: 2026-09-04 15:03:13.133489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a2ff13ac6ba2'
down_revision: Union[str, Sequence[str], None] = 'f43ee115cbbc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # 1. Agregar la columna tenant_id (tabla vacía, así que se puede NOT NULL directo)
    op.add_column('patients', sa.Column('tenant_id', sa.UUID(), nullable=False))
    op.create_index(op.f('ix_patients_tenant_id'), 'patients', ['tenant_id'], unique=False)

    # 2. Quitar el índice único global del DNI (un mismo DNI ya no puede
    #    ser único en todo el sistema, solo dentro de un mismo hospital)
    op.drop_index(op.f('ix_patients_dni'), table_name='patients')

    # 3. Crear índice normal (no único) para dni, y un índice único compuesto
    #    (tenant_id, dni) para que el DNI sea único por hospital
    op.create_index(op.f('ix_patients_dni'), 'patients', ['dni'], unique=False)
    op.create_index(
        'ix_patients_tenant_id_dni',
        'patients',
        ['tenant_id', 'dni'],
        unique=True,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_patients_tenant_id_dni', table_name='patients')
    op.drop_index(op.f('ix_patients_dni'), table_name='patients')
    op.create_index(op.f('ix_patients_dni'), 'patients', ['dni'], unique=True)
    op.drop_index(op.f('ix_patients_tenant_id'), table_name='patients')
    op.drop_column('patients', 'tenant_id')