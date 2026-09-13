from alembic import op
import sqlalchemy as sa
revision = "c43e8129fa02"
down_revision = "0c824b51ab69"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("sigarh_empleados", sa.Column("jornada_mensual_horas", sa.Integer(), nullable=True))
    op.add_column("sigarh_empleados", sa.Column("jornada_sustento", sa.String(255), nullable=True))
    op.create_check_constraint("ck_empleado_jornada_medica", "sigarh_empleados", "jornada_mensual_horas BETWEEN 1 AND 150")

def downgrade():
    op.drop_constraint("ck_empleado_jornada_medica", "sigarh_empleados", type_="check")
    op.drop_column("sigarh_empleados", "jornada_sustento")
    op.drop_column("sigarh_empleados", "jornada_mensual_horas")
