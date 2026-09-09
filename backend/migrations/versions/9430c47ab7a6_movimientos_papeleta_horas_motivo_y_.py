"""movimientos: papeleta horas/motivo y auditoria en cambio-turno

Revision ID: 9430c47ab7a6
Revises: a386bb53b514
Create Date: 2026-09-09 12:30:22.716836

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9430c47ab7a6'
down_revision: Union[str, Sequence[str], None] = 'a386bb53b514'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # sigarh_papeletas: motivo libre + N° doc + horas + auditoría
    op.add_column("sigarh_papeletas", sa.Column("motivo", sa.String(length=50), nullable=True))
    op.add_column("sigarh_papeletas", sa.Column("numero_documento", sa.String(length=50), nullable=True))
    op.add_column("sigarh_papeletas", sa.Column("hora_salida", sa.String(length=5), nullable=True))
    op.add_column("sigarh_papeletas", sa.Column("hora_retorno", sa.String(length=5), nullable=True))
    op.add_column("sigarh_papeletas", sa.Column("registrado_por", sa.String(length=255), nullable=True))
    op.add_column("sigarh_papeletas", sa.Column("revisado_por", sa.String(length=255), nullable=True))
    op.add_column("sigarh_papeletas", sa.Column("revisado_at", sa.DateTime(), nullable=True))
    op.add_column("sigarh_papeletas", sa.Column("motivo_rechazo", sa.Text(), nullable=True))
    op.drop_constraint("sigarh_papeletas_motivo_id_fkey", "sigarh_papeletas", type_="foreignkey")
    op.drop_column("sigarh_papeletas", "motivo_id")

    # sigarh_cambios_turno: auditoría de revisión
    op.add_column("sigarh_cambios_turno", sa.Column("registrado_por", sa.String(length=255), nullable=True))
    op.add_column("sigarh_cambios_turno", sa.Column("revisado_por", sa.String(length=255), nullable=True))
    op.add_column("sigarh_cambios_turno", sa.Column("revisado_at", sa.DateTime(), nullable=True))
    op.add_column("sigarh_cambios_turno", sa.Column("motivo_rechazo", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("sigarh_cambios_turno", "motivo_rechazo")
    op.drop_column("sigarh_cambios_turno", "revisado_at")
    op.drop_column("sigarh_cambios_turno", "revisado_por")
    op.drop_column("sigarh_cambios_turno", "registrado_por")

    op.add_column("sigarh_papeletas", sa.Column("motivo_id", sa.dialects.postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key("sigarh_papeletas_motivo_id_fkey", "sigarh_papeletas", "sigarh_motivos_justificacion", ["motivo_id"], ["id"], ondelete="SET NULL")
    op.drop_column("sigarh_papeletas", "motivo_rechazo")
    op.drop_column("sigarh_papeletas", "revisado_at")
    op.drop_column("sigarh_papeletas", "revisado_por")
    op.drop_column("sigarh_papeletas", "registrado_por")
    op.drop_column("sigarh_papeletas", "hora_retorno")
    op.drop_column("sigarh_papeletas", "hora_salida")
    op.drop_column("sigarh_papeletas", "numero_documento")
    op.drop_column("sigarh_papeletas", "motivo")
