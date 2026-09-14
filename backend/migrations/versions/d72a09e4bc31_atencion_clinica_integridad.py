"""Expediente por consulta, prestaciones y atribucion de cierre."""
from alembic import op
import sqlalchemy as sa
revision = "d72a09e4bc31"
down_revision = "c43e8129fa02"
branch_labels = None
depends_on = None

def upgrade():
    op.add_column("users", sa.Column("empleado_id", sa.UUID(), nullable=True))
    op.create_foreign_key("fk_user_empleado", "users", "sigarh_empleados", ["empleado_id"], ["id"], ondelete="SET NULL")
    for campo, tipo in [("enfermedad_actual", sa.Text()), ("antecedentes_snapshot", sa.JSON()), ("prestaciones", sa.JSON()), ("cierre_evidencia", sa.JSON())]:
        op.add_column("atenciones_medicas", sa.Column(campo, tipo, nullable=True))
    # No reconstruimos antecedentes ni firma de consultas antiguas.
    for destino in ("FARMACIA", "LABORATORIO", "IMAGEN", "INTERCONSULTA"):
        op.execute(sa.text("UPDATE atenciones_medicas SET prestaciones = :prestaciones WHERE destino_atencion = :destino").bindparams(sa.bindparam("prestaciones", value=[destino], type_=sa.JSON()), destino=destino))
    op.execute("UPDATE atenciones_medicas SET destino_atencion = 'ALTA' WHERE destino_atencion IN ('FARMACIA','LABORATORIO','IMAGEN','INTERCONSULTA') AND estado = 'borrador'")

def downgrade():
    for campo in ("cierre_evidencia", "prestaciones", "antecedentes_snapshot", "enfermedad_actual"):
        op.drop_column("atenciones_medicas", campo)
    op.drop_constraint("fk_user_empleado", "users", type_="foreignkey")
    op.drop_column("users", "empleado_id")
