"""notificaciones admin

Revision ID: 59d39034b508
Revises: c43e8129fa02
Create Date: 2026-09-15 15:10:18.020056

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '59d39034b508'
down_revision: Union[str, Sequence[str], None] = 'c43e8129fa02'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'notificaciones_admin',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('titulo', sa.String(length=255), nullable=False),
        sa.Column('cuerpo', sa.Text(), nullable=True),
        sa.Column('nivel', sa.String(length=20), nullable=False),
        sa.Column('link', sa.String(length=500), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.execute(
        """
        INSERT INTO notificaciones_admin (id, titulo, cuerpo, nivel, link, is_read, created_at)
        VALUES (
            gen_random_uuid(),
            'Notificaciones activadas',
            'La campana del panel ya esta conectada: aqui apareceran los hospitales creados, errores de aprovisionamiento y cuentas nuevas.',
            'info',
            NULL,
            false,
            now()
        )
        """
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('notificaciones_admin')
