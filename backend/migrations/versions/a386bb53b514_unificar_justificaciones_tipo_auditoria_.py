"""unificar justificaciones: tipo, auditoria de revision

Revision ID: a386bb53b514
Revises: 74c49570f1f9
Create Date: 2026-09-09 12:18:09.123478

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a386bb53b514'
down_revision: Union[str, Sequence[str], None] = '74c49570f1f9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("sigarh_justificaciones", sa.Column("tipo", sa.String(length=20), nullable=False, server_default="justificacion"))
    op.add_column("sigarh_justificaciones", sa.Column("registrado_por", sa.String(length=255), nullable=True))
    op.add_column("sigarh_justificaciones", sa.Column("revisado_por", sa.String(length=255), nullable=True))
    op.add_column("sigarh_justificaciones", sa.Column("revisado_at", sa.DateTime(), nullable=True))
    op.add_column("sigarh_justificaciones", sa.Column("motivo_rechazo", sa.Text(), nullable=True))
    op.alter_column("sigarh_justificaciones", "tipo", server_default=None)


def downgrade() -> None:
    op.drop_column("sigarh_justificaciones", "motivo_rechazo")
    op.drop_column("sigarh_justificaciones", "revisado_at")
    op.drop_column("sigarh_justificaciones", "revisado_por")
    op.drop_column("sigarh_justificaciones", "registrado_por")
    op.drop_column("sigarh_justificaciones", "tipo")
