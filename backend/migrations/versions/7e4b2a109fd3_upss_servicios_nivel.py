"""UPSS y servicios por categoría hospitalaria

Revision ID: 7e4b2a109fd3
Revises: 41ca78d3f802
Create Date: 2026-09-11
"""

from datetime import datetime
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.sigarh.mantenimiento.upss_catalogo import (
    UPSS,
    SERVICIOS,
    ESPECIALIDADES_SERVICIO,
    RECOMENDADAS,
    FUENTE,
    NORMA,
    FUENTE_URL,
    stable_id,
)

revision = "7e4b2a109fd3"
down_revision = "41ca78d3f802"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "sigarh_upss",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True
        ),
        sa.Column("codigo", sa.String(30), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("tipo_atencion", sa.String(30), nullable=False),
        sa.Column("fuente", sa.String(100), nullable=True),
        sa.Column("norma", sa.String(255), nullable=True),
        sa.Column("fuente_url", sa.Text(), nullable=True),
        sa.Column(
            "recomendada_nivel", sa.Boolean(), nullable=False, server_default=sa.false()
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()
        ),
        sa.UniqueConstraint("tenant_id", "codigo", name="uq_upss_tenant_codigo"),
        sa.CheckConstraint(
            "tipo_atencion IN ('atencion_directa','atencion_soporte')",
            name="ck_upss_tipo_atencion",
        ),
    )
    op.add_column(
        "sigarh_servicios",
        sa.Column("es_base", sa.Boolean(), nullable=False, server_default=sa.false()),
    )
    op.create_table(
        "sigarh_servicio_upss",
        sa.Column(
            "servicio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sigarh_servicios.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "upss_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sigarh_upss.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    op.create_table(
        "sigarh_servicio_especialidades",
        sa.Column(
            "servicio_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sigarh_servicios.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column(
            "especialidad_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("sigarh_especialidades.id", ondelete="CASCADE"),
            primary_key=True,
        ),
    )
    bind = op.get_bind()
    if "tenants" not in sa.inspect(bind).get_table_names():
        return
    for tenant_id, level in bind.execute(
        sa.text("SELECT id, hospital_level FROM tenants")
    ):
        _seed(bind, tenant_id, level)


def _seed(bind, tenant_id, level) -> None:
    active_codes = RECOMENDADAS.get(level, set())
    now = datetime.utcnow()
    for code, name, care_type in UPSS:
        bind.execute(
            sa.text("""INSERT INTO sigarh_upss
            (id,tenant_id,codigo,nombre,tipo_atencion,fuente,norma,fuente_url,recomendada_nivel,is_active,created_at)
            VALUES (:id,:tid,:code,:name,:care,:source,:norm,:url,:recommended,:active,:now)
            ON CONFLICT (tenant_id,codigo) DO NOTHING"""),
            {
                "id": stable_id("upss", tenant_id, code),
                "tid": tenant_id,
                "code": code,
                "name": name,
                "care": care_type,
                "source": FUENTE,
                "norm": NORMA,
                "url": FUENTE_URL,
                "recommended": code in active_codes,
                "active": code in active_codes,
                "now": now,
            },
        )
    for code, name, upss_codes in SERVICIOS:
        sid = stable_id("service", tenant_id, code)
        active = any(upss in active_codes for upss in upss_codes)
        bind.execute(
            sa.text("""INSERT INTO sigarh_servicios
            (id,tenant_id,nombre,codigo,descripcion,tiempo_atencion_min,is_active,es_base,created_at,updated_at)
            VALUES (:id,:tid,:name,:code,:description,15,:active,true,:now,:now)
            ON CONFLICT DO NOTHING"""),
            {
                "id": sid,
                "tid": tenant_id,
                "name": name,
                "code": code,
                "description": "Servicio asistencial base vinculado a UPSS",
                "active": active,
                "now": now,
            },
        )
        for upss_code in upss_codes:
            bind.execute(
                sa.text("""INSERT INTO sigarh_servicio_upss (servicio_id,upss_id)
                VALUES (:sid,:uid) ON CONFLICT DO NOTHING"""),
                {"sid": sid, "uid": stable_id("upss", tenant_id, upss_code)},
            )
        for specialty in ESPECIALIDADES_SERVICIO.get(code, []):
            bind.execute(
                sa.text("""INSERT INTO sigarh_servicio_especialidades
                (servicio_id,especialidad_id)
                SELECT :sid,e.id FROM sigarh_especialidades e
                WHERE e.tenant_id=:tid AND e.nombre=:name AND e.tipo='especialidad'
                ON CONFLICT DO NOTHING"""),
                {"sid": sid, "tid": tenant_id, "name": specialty},
            )


def downgrade() -> None:
    op.drop_table("sigarh_servicio_especialidades")
    op.drop_table("sigarh_servicio_upss")
    op.drop_column("sigarh_servicios", "es_base")
    op.drop_table("sigarh_upss")
