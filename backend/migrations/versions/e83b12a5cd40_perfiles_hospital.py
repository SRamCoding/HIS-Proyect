"""Perfiles de acceso del panel hospitalario, independientes de SIGARH."""
from alembic import op
import sqlalchemy as sa
revision = "e83b12a5cd40"
down_revision = "d72a09e4bc31"
branch_labels = None
depends_on = None

def upgrade():
    op.create_table("hospital_perfiles",
        sa.Column("id", sa.UUID(), primary_key=True),
        sa.Column("tenant_id", sa.UUID(), nullable=False, index=True),
        sa.Column("nombre", sa.String(150), nullable=False),
        sa.Column("role", sa.String(100), nullable=False),
        sa.Column("modulos", sa.JSON(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False))
    op.add_column("users", sa.Column("perfil_hospital_id", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_user_perfil_hospital", "users", "hospital_perfiles", ["perfil_hospital_id"], ["id"], ondelete="RESTRICT")

def downgrade():
    op.drop_constraint("fk_user_perfil_hospital", "users", type_="foreignkey")
    op.drop_column("users", "perfil_hospital_id")
    op.drop_table("hospital_perfiles")
