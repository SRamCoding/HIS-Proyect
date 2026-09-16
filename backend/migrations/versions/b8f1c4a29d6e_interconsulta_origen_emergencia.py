"""interconsulta_origen_emergencia

Revision ID: b8f1c4a29d6e
Revises: a673102f5c2e
Create Date: 2026-09-15 11:40:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b8f1c4a29d6e'
down_revision: Union[str, Sequence[str], None] = 'a673102f5c2e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('interconsultas', sa.Column('atencion_emergencia_id', sa.UUID(), nullable=True))
    op.add_column('interconsultas', sa.Column('patient_id', sa.UUID(), nullable=True))
    op.create_unique_constraint('uq_interconsultas_atencion_emergencia_id', 'interconsultas', ['atencion_emergencia_id'])
    op.create_foreign_key('fk_interconsulta_atencion_emergencia_id', 'interconsultas', 'atenciones_emergencia', ['atencion_emergencia_id'], ['id'], ondelete='CASCADE')
    op.create_foreign_key('fk_interconsulta_patient_id', 'interconsultas', 'patients', ['patient_id'], ['id'], ondelete='RESTRICT')


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('fk_interconsulta_patient_id', 'interconsultas', type_='foreignkey')
    op.drop_constraint('fk_interconsulta_atencion_emergencia_id', 'interconsultas', type_='foreignkey')
    op.drop_constraint('uq_interconsultas_atencion_emergencia_id', 'interconsultas', type_='unique')
    op.drop_column('interconsultas', 'patient_id')
    op.drop_column('interconsultas', 'atencion_emergencia_id')
