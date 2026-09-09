"""config_farmacia: campos sismed/cadena_frio, obligatorios y longitudes

Revision ID: 4168b3a941c7
Revises: 9430c47ab7a6
Create Date: 2026-09-09 16:23:00.629958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4168b3a941c7'
down_revision: Union[str, Sequence[str], None] = '9430c47ab7a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # sigarh_medicamentos: campos nuevos
    op.add_column("sigarh_medicamentos", sa.Column("precio_referencia_sismed", sa.Float(), nullable=True))
    op.add_column("sigarh_medicamentos", sa.Column("temperatura_min", sa.Integer(), nullable=True))
    op.add_column("sigarh_medicamentos", sa.Column("temperatura_max", sa.Integer(), nullable=True))
    # obligatorios (tablas vacías: server_default temporal y se retira)
    op.alter_column("sigarh_medicamentos", "nombre_generico", existing_type=sa.String(255), nullable=False, server_default="")
    op.alter_column("sigarh_medicamentos", "nombre_generico", server_default=None)
    op.alter_column("sigarh_medicamentos", "condicion_venta", existing_type=sa.String(50), type_=sa.String(30), nullable=False, server_default="sin_receta")
    op.alter_column("sigarh_medicamentos", "condicion_venta", server_default=None)
    op.alter_column("sigarh_medicamentos", "unidad", existing_type=sa.String(50), type_=sa.String(20), nullable=False, server_default="unidad")
    op.alter_column("sigarh_medicamentos", "unidad", server_default=None)
    # longitudes
    op.alter_column("sigarh_medicamentos", "dci", existing_type=sa.String(255), type_=sa.String(150))
    op.alter_column("sigarh_medicamentos", "forma_farmaceutica", existing_type=sa.String(100), type_=sa.String(50))
    op.alter_column("sigarh_medicamentos", "via_administracion", existing_type=sa.String(100), type_=sa.String(30))
    op.alter_column("sigarh_medicamentos", "codigo_atc", existing_type=sa.String(50), type_=sa.String(10))
    op.alter_column("sigarh_medicamentos", "numero_registro_sanitario", existing_type=sa.String(100), type_=sa.String(50))
    op.alter_column("sigarh_medicamentos", "laboratorio_fabricante", existing_type=sa.String(255), type_=sa.String(150))
    op.create_foreign_key("sigarh_medicamentos_tipo_producto_id_fkey", "sigarh_medicamentos", "sigarh_catalogos", ["tipo_producto_id"], ["id"], ondelete="SET NULL")

    # sigarh_almacenes: longitudes + unicidad de codigo
    op.alter_column("sigarh_almacenes", "codigo", existing_type=sa.String(50), type_=sa.String(20))
    op.alter_column("sigarh_almacenes", "nombre", existing_type=sa.String(255), type_=sa.String(100))
    op.alter_column("sigarh_almacenes", "tipo", existing_type=sa.String(50), type_=sa.String(30))
    op.alter_column("sigarh_almacenes", "fuente_financiamiento", existing_type=sa.String(100), type_=sa.String(30))
    op.create_unique_constraint("uq_sigarh_almacenes_tenant_codigo", "sigarh_almacenes", ["tenant_id", "codigo"])


def downgrade() -> None:
    op.drop_constraint("uq_sigarh_almacenes_tenant_codigo", "sigarh_almacenes", type_="unique")
    op.alter_column("sigarh_almacenes", "fuente_financiamiento", type_=sa.String(100))
    op.alter_column("sigarh_almacenes", "tipo", type_=sa.String(50))
    op.alter_column("sigarh_almacenes", "nombre", type_=sa.String(255))
    op.alter_column("sigarh_almacenes", "codigo", type_=sa.String(50))

    op.drop_constraint("sigarh_medicamentos_tipo_producto_id_fkey", "sigarh_medicamentos", type_="foreignkey")
    op.alter_column("sigarh_medicamentos", "laboratorio_fabricante", type_=sa.String(255))
    op.alter_column("sigarh_medicamentos", "numero_registro_sanitario", type_=sa.String(100))
    op.alter_column("sigarh_medicamentos", "codigo_atc", type_=sa.String(50))
    op.alter_column("sigarh_medicamentos", "via_administracion", type_=sa.String(100))
    op.alter_column("sigarh_medicamentos", "forma_farmaceutica", type_=sa.String(100))
    op.alter_column("sigarh_medicamentos", "unidad", type_=sa.String(50), nullable=True)
    op.alter_column("sigarh_medicamentos", "dci", type_=sa.String(255))
    op.alter_column("sigarh_medicamentos", "condicion_venta", type_=sa.String(50), nullable=True)
    op.alter_column("sigarh_medicamentos", "nombre_generico", nullable=True)
    op.drop_column("sigarh_medicamentos", "temperatura_max")
    op.drop_column("sigarh_medicamentos", "temperatura_min")
    op.drop_column("sigarh_medicamentos", "precio_referencia_sismed")
