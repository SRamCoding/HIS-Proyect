"""citas: índice único parcial para evitar doble reserva del mismo cupo

Revision ID: bfbf93125c47
Revises: d4a91f6c2b70
Create Date: 2026-09-10 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "bfbf93125c47"
down_revision: Union[str, Sequence[str], None] = "d4a91f6c2b70"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Si ya existen citas duplicadas sobre un mismo cupo (bug previo sin este
    # índice), cancela los duplicados más recientes antes de crear el índice
    # para que la migración no falle.
    op.execute("""
        UPDATE citas c
        SET estado = 'cancelada'
        WHERE c.estado <> 'cancelada'
          AND c.id IN (
              SELECT id FROM (
                  SELECT id, ROW_NUMBER() OVER (
                      PARTITION BY programacion_medica_id, hora_inicio
                      ORDER BY created_at, id
                  ) AS rn
                  FROM citas
                  WHERE estado <> 'cancelada'
              ) ranked
              WHERE ranked.rn > 1
          )
    """)
    op.execute("""
        CREATE UNIQUE INDEX ux_citas_cupo_activo ON citas (programacion_medica_id, hora_inicio)
        WHERE estado <> 'cancelada'
    """)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ux_citas_cupo_activo")
