"""Profesiones y colegiatura del personal de salud

Revision ID: 9b6e3a721c44
Revises: 7e4b2a109fd3
Create Date: 2026-09-11
"""

from datetime import datetime

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from app.sigarh.mantenimiento.profesiones_catalogo import (
    FUENTE, FUENTE_URL, GRUPOS, PROFESIONES, stable_id,
)

revision = "9b6e3a721c44"
down_revision = "7e4b2a109fd3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "sigarh_profesiones",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False, index=True),
        sa.Column("grupo_ocupacional_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nombre", sa.String(255), nullable=False),
        sa.Column("codigo", sa.String(20), nullable=False),
        sa.Column("descripcion", sa.Text(), nullable=True),
        sa.Column("codigo_colegio", sa.String(10), nullable=True),
        sa.Column("colegio_profesional", sa.String(255), nullable=True),
        sa.Column("categoria_personal", sa.String(30), nullable=True),
        sa.Column("fuente", sa.String(255), nullable=True),
        sa.Column("fuente_url", sa.Text(), nullable=True),
        sa.Column("es_base", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["grupo_ocupacional_id"], ["sigarh_grupos_ocupacionales.id"], ondelete="RESTRICT"),
        sa.UniqueConstraint("tenant_id", "codigo", name="uq_profesion_tenant_codigo"),
        sa.UniqueConstraint("tenant_id", "nombre", name="uq_profesion_tenant_nombre"),
    )
    op.add_column("sigarh_empleados", sa.Column("profesion_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("sigarh_empleados", sa.Column("numero_colegiatura", sa.String(50), nullable=True))
    op.add_column("sigarh_empleados", sa.Column("habilitado_colegio", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.create_foreign_key("fk_empleado_profesion", "sigarh_empleados", "sigarh_profesiones", ["profesion_id"], ["id"], ondelete="SET NULL")

    bind = op.get_bind()
    if "tenants" in sa.inspect(bind).get_table_names():
        for tenant_id in bind.execute(sa.text("SELECT id FROM tenants")):
            seed(bind, tenant_id[0])


def seed(bind, tenant_id):
    now = datetime.utcnow()
    for code, name, category in GRUPOS:
        gid = stable_id("group", tenant_id, code)
        bind.execute(sa.text("""INSERT INTO sigarh_grupos_ocupacionales
            (id,tenant_id,nombre,codigo,descripcion,categoria_personal,is_active,created_at,updated_at)
            VALUES (:id,:tid,:name,:code,:description,:category,true,:now,:now)
            ON CONFLICT DO NOTHING"""), {"id": gid, "tid": tenant_id, "name": name, "code": code,
            "description": "Grupo ocupacional base del sector salud", "category": category, "now": now})
    for code, name, group_code, college_code, college, category in PROFESIONES:
        bind.execute(sa.text("""INSERT INTO sigarh_profesiones
            (id,tenant_id,grupo_ocupacional_id,nombre,codigo,codigo_colegio,
             colegio_profesional,categoria_personal,fuente,fuente_url,es_base,is_active,created_at,updated_at)
            VALUES (:id,:tid,:gid,:name,:code,:college_code,:college,:category,:source,:url,true,true,:now,:now)
            ON CONFLICT DO NOTHING"""), {
            "id": stable_id("profession", tenant_id, code), "tid": tenant_id,
            "gid": stable_id("group", tenant_id, group_code), "name": name, "code": code,
            "college_code": college_code, "college": college, "category": category,
            "source": FUENTE, "url": FUENTE_URL, "now": now,
        })
    bind.execute(sa.text("""UPDATE sigarh_empleados SET
        numero_colegiatura=numero_cmp WHERE tenant_id=:tid
        AND numero_colegiatura IS NULL AND numero_cmp IS NOT NULL"""), {"tid": tenant_id})



def downgrade():
    op.drop_constraint("fk_empleado_profesion", "sigarh_empleados", type_="foreignkey")
    op.drop_column("sigarh_empleados", "habilitado_colegio")
    op.drop_column("sigarh_empleados", "numero_colegiatura")
    op.drop_column("sigarh_empleados", "profesion_id")
    op.drop_table("sigarh_profesiones")
