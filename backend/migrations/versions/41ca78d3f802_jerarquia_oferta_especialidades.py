"""jerarquía en la oferta hospitalaria de especialidades

Revision ID: 41ca78d3f802
Revises: 2a91e5c047bf
Create Date: 2026-09-11
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "41ca78d3f802"
down_revision = "2a91e5c047bf"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "sigarh_especialidades",
        sa.Column("tipo", sa.String(20), nullable=False, server_default="especialidad"),
    )
    op.add_column(
        "sigarh_especialidades",
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_check_constraint(
        "ck_sigarh_especialidad_tipo",
        "sigarh_especialidades",
        "tipo IN ('especialidad', 'subespecialidad')",
    )
    op.create_foreign_key(
        "fk_sigarh_especialidad_parent",
        "sigarh_especialidades",
        "sigarh_especialidades",
        ["parent_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.execute("""
        UPDATE sigarh_especialidades e
        SET tipo = c.tipo
        FROM catalogo_especialidades_salud c
        WHERE e.catalogo_id = c.id
    """)
    op.execute("""
        UPDATE sigarh_especialidades child
        SET parent_id = parent.id
        FROM catalogo_especialidades_salud child_catalog,
             sigarh_especialidades parent
        WHERE child.catalogo_id = child_catalog.id
          AND child_catalog.parent_id = parent.catalogo_id
          AND child.tenant_id = parent.tenant_id
    """)
    op.create_index(
        "ix_sigarh_especialidades_parent_id", "sigarh_especialidades", ["parent_id"]
    )


def downgrade() -> None:
    op.drop_index(
        "ix_sigarh_especialidades_parent_id",
        table_name="sigarh_especialidades",
    )
    op.drop_constraint(
        "fk_sigarh_especialidad_parent", "sigarh_especialidades", type_="foreignkey"
    )
    op.drop_constraint(
        "ck_sigarh_especialidad_tipo", "sigarh_especialidades", type_="check"
    )
    op.drop_column("sigarh_especialidades", "parent_id")
    op.drop_column("sigarh_especialidades", "tipo")
