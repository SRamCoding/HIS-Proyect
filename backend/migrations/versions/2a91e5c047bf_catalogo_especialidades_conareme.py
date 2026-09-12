"""catálogo nacional de especialidades CONAREME

Revision ID: 2a91e5c047bf
Revises: 8d12f6c37a41
Create Date: 2026-09-11
"""

import json
from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.sigarh.rrhh.especialidades_catalogo import (
    ESPECIALIDADES,
    SUBESPECIALIDADES,
    RECOMENDADAS_POR_NIVEL,
    FUENTE,
    NORMA,
    FUENTE_URL,
    catalogo_id,
    oferta_id,
    codigo,
)

revision = "2a91e5c047bf"
down_revision = "8d12f6c37a41"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "catalogo_especialidades_salud",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("codigo", sa.String(30), nullable=False, unique=True),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("tipo", sa.String(20), nullable=False),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("requisitos", sa.Text(), nullable=True),
        sa.Column("fuente", sa.String(100), nullable=False),
        sa.Column("norma", sa.String(255), nullable=False),
        sa.Column("fuente_url", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.CheckConstraint(
            "tipo IN ('especialidad', 'subespecialidad')",
            name="ck_catalogo_especialidad_tipo",
        ),
        sa.ForeignKeyConstraint(
            ["parent_id"], ["catalogo_especialidades_salud.id"], ondelete="RESTRICT"
        ),
    )
    op.add_column(
        "sigarh_especialidades",
        sa.Column("catalogo_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_sigarh_especialidad_catalogo",
        "sigarh_especialidades",
        "catalogo_especialidades_salud",
        ["catalogo_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_unique_constraint(
        "uq_especialidad_tenant_catalogo",
        "sigarh_especialidades",
        ["tenant_id", "catalogo_id"],
    )

    catalog = sa.table(
        "catalogo_especialidades_salud",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("codigo", sa.String),
        sa.column("nombre", sa.String),
        sa.column("tipo", sa.String),
        sa.column("parent_id", postgresql.UUID(as_uuid=True)),
        sa.column("requisitos", sa.Text),
        sa.column("fuente", sa.String),
        sa.column("norma", sa.String),
        sa.column("fuente_url", sa.Text),
        sa.column("is_active", sa.Boolean),
    )
    rows = []
    for n, nombre in enumerate(ESPECIALIDADES, 1):
        rows.append(
            {
                "id": catalogo_id("especialidad", nombre),
                "codigo": codigo("especialidad", n),
                "nombre": nombre,
                "tipo": "especialidad",
                "parent_id": None,
                "requisitos": None,
                "fuente": FUENTE,
                "norma": NORMA,
                "fuente_url": FUENTE_URL,
                "is_active": True,
            }
        )
    for n, (nombre, parent, requisitos) in enumerate(SUBESPECIALIDADES, 1):
        rows.append(
            {
                "id": catalogo_id("subespecialidad", nombre),
                "codigo": codigo("subespecialidad", n),
                "nombre": nombre,
                "tipo": "subespecialidad",
                "parent_id": catalogo_id("especialidad", parent),
                "requisitos": json.dumps(requisitos, ensure_ascii=False),
                "fuente": FUENTE,
                "norma": NORMA,
                "fuente_url": FUENTE_URL,
                "is_active": True,
            }
        )
    op.bulk_insert(catalog, rows)

    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if "tenants" not in inspector.get_table_names():
        return
    tenants = bind.execute(sa.text("SELECT id, hospital_level FROM tenants")).all()
    now = datetime.utcnow()
    for tenant_id, level in tenants:
        recommended = RECOMENDADAS_POR_NIVEL.get(level, set())
        for row in rows:
            is_recommended = (
                row["tipo"] == "especialidad" and row["nombre"] in recommended
            )
            bind.execute(
                sa.text("""
                INSERT INTO sigarh_especialidades
                    (id, tenant_id, catalogo_id, nombre, codigo, descripcion,
                     is_active, created_at)
                VALUES (:id, :tenant_id, :catalogo_id, :nombre, :codigo,
                        :descripcion, :active, :created_at)
                ON CONFLICT (tenant_id, catalogo_id) DO NOTHING
            """),
                {
                    "id": oferta_id(tenant_id, row["id"]),
                    "tenant_id": tenant_id,
                    "catalogo_id": row["id"],
                    "nombre": row["nombre"],
                    "codigo": row["codigo"],
                    "descripcion": "Recomendada por categoría"
                    if is_recommended
                    else None,
                    "active": is_recommended,
                    "created_at": now,
                },
            )


def downgrade() -> None:
    op.drop_constraint(
        "uq_especialidad_tenant_catalogo", "sigarh_especialidades", type_="unique"
    )
    op.drop_constraint(
        "fk_sigarh_especialidad_catalogo", "sigarh_especialidades", type_="foreignkey"
    )
    op.drop_column("sigarh_especialidades", "catalogo_id")
    op.drop_table("catalogo_especialidades_salud")
