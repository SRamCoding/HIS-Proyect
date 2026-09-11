"""categoria_personal en tipos_trabajador y grupos_ocupacionales, para
validar qué personal puede agregarse a cada categoría de rol de turno.

Revision ID: f2a6c19b7d84
Revises: e7a914c02f65
Create Date: 2026-09-10 18:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "f2a6c19b7d84"
down_revision = "e7a914c02f65"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("sigarh_tipos_trabajador", sa.Column("categoria_personal", sa.String(30), nullable=True))
    op.add_column("sigarh_grupos_ocupacionales", sa.Column("categoria_personal", sa.String(30), nullable=True))
    op.execute("""
        ALTER TABLE sigarh_tipos_trabajador ADD CONSTRAINT ck_tt_categoria_personal
        CHECK (categoria_personal IS NULL OR categoria_personal IN
            ('medicos','otros_profesionales','residentes','tecnicos','internos'))
    """)
    op.execute("""
        ALTER TABLE sigarh_grupos_ocupacionales ADD CONSTRAINT ck_go_categoria_personal
        CHECK (categoria_personal IS NULL OR categoria_personal IN
            ('medicos','otros_profesionales','residentes','tecnicos','internos'))
    """)


def downgrade() -> None:
    op.drop_constraint("ck_tt_categoria_personal", "sigarh_tipos_trabajador")
    op.drop_constraint("ck_go_categoria_personal", "sigarh_grupos_ocupacionales")
    op.drop_column("sigarh_tipos_trabajador", "categoria_personal")
    op.drop_column("sigarh_grupos_ocupacionales", "categoria_personal")
