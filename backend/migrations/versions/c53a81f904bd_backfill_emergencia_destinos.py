"""backfill emergencia destinos

Revision ID: c53a81f904bd
Revises: b42e7d9a1c30
"""
from typing import Sequence, Union

from alembic import op


revision: str = "c53a81f904bd"
down_revision: Union[str, None] = "b42e7d9a1c30"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        INSERT INTO emergencia_destinos
            (id, tenant_id, atencion_id, destino, estado, observacion, created_at, resolved_at)
        SELECT
            gen_random_uuid(), a.tenant_id, a.id, a.destino_atencion,
            CASE WHEN a.destino_atencion IN ('AMBULATORIA', 'ALTA', 'FALLECIDO')
                 THEN 'completado' ELSE 'pendiente' END,
            NULL, COALESCE(a.firmado_at, a.created_at),
            CASE WHEN a.destino_atencion IN ('AMBULATORIA', 'ALTA', 'FALLECIDO')
                 THEN COALESCE(a.firmado_at, a.created_at) ELSE NULL END
        FROM atenciones_emergencia a
        WHERE a.estado = 'firmado'
        ON CONFLICT (atencion_id) DO NOTHING
    """)


def downgrade() -> None:
    op.execute("""
        DELETE FROM emergencia_destinos d
        USING atenciones_emergencia a
        WHERE d.atencion_id = a.id AND d.created_at = COALESCE(a.firmado_at, a.created_at)
    """)
