"""Integridad y permisos de mantenimiento sin eliminar ni fusionar datos existentes.

Revision ID: e7a914c02f65
Revises: a3c5e8f1d92b, d4a91f6c2b70
"""
from alembic import op
import sqlalchemy as sa

revision = "e7a914c02f65"
down_revision = ("a3c5e8f1d92b", "d4a91f6c2b70")
branch_labels = None
depends_on = None

TABLES = ["departamentos", "servicios", "dependencias", "tipos_trabajador", "tipos_guardia",
          "niveles_remunerativos", "horarios_guardia", "grupos_ocupacionales", "tipos_actividad",
          "actividades", "guardias_valorizadas", "roles_sistema", "perfiles_usuario", "usuarios"]
CODES = [t for t in TABLES if t not in {"horarios_guardia", "guardias_valorizadas", "perfiles_usuario", "usuarios"}]
SECURITY = {"roles_sistema", "perfiles_usuario", "usuarios"}


def upgrade():
    for suffix in TABLES:
        if suffix not in {"departamentos", "servicios", "usuarios"}:
            op.add_column("sigarh_" + suffix, sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()))
    op.add_column("sigarh_usuarios", sa.Column("session_version", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("sigarh_horarios_guardia", sa.Column("duracion_minutos", sa.Integer(), nullable=True))
    op.alter_column("sigarh_horarios_guardia", "horas_totales", type_=sa.Float(), existing_type=sa.Integer())
    op.execute("""
        UPDATE sigarh_horarios_guardia
        SET duracion_minutos = ((EXTRACT(EPOCH FROM hora_fin::time) - EXTRACT(EPOCH FROM hora_inicio::time))::integer + 86400) % 86400 / 60,
            horas_totales = (((EXTRACT(EPOCH FROM hora_fin::time) - EXTRACT(EPOCH FROM hora_inicio::time))::integer + 86400) % 86400) / 3600.0
        WHERE hora_inicio ~ '^([01][0-9]|2[0-3]):[0-5][0-9]$'
          AND hora_fin ~ '^([01][0-9]|2[0-3]):[0-5][0-9]$' AND hora_inicio <> hora_fin
    """)
    op.execute("""ALTER TABLE sigarh_horarios_guardia ADD CONSTRAINT ck_horario_minutos
        CHECK (NOT is_active OR (duracion_minutos BETWEEN 1 AND 1439 AND duracion_minutos IS NOT NULL)) NOT VALID""")
    op.alter_column("sigarh_guardias_valorizadas", "valor", type_=sa.Numeric(12, 2), existing_type=sa.Float(), postgresql_using="round(valor::numeric, 2)")
    op.add_column("sigarh_guardias_valorizadas", sa.Column("moneda", sa.String(3), nullable=False, server_default="PEN"))
    for name in ("vigencia_desde", "vigencia_hasta"):
        op.add_column("sigarh_guardias_valorizadas", sa.Column(name, sa.Date(), nullable=True))
    op.add_column("sigarh_guardias_valorizadas", sa.Column("sustento", sa.Text(), nullable=True))
    op.execute("""ALTER TABLE sigarh_guardias_valorizadas ADD CONSTRAINT ck_guardia_valor
        CHECK (NOT is_active OR valor > 0) NOT VALID""")
    op.execute("""ALTER TABLE sigarh_guardias_valorizadas ADD CONSTRAINT ck_guardia_vigencia
        CHECK (vigencia_hasta IS NULL OR (vigencia_desde IS NOT NULL AND vigencia_hasta >= vigencia_desde)) NOT VALID""")
    op.add_column("sigarh_actividades", sa.Column("genera_agenda", sa.Boolean(), nullable=False, server_default="false"))
    op.execute("""UPDATE sigarh_actividades SET genera_agenda = requiere_consultorio OR lower(trim(nombre)) IN
        ('consulta externa', 'atencion ambulatoria', 'atención ambulatoria')""")
    op.add_column("sigarh_roles_turno", sa.Column("created_by_id", sa.UUID(), nullable=True))
    # Solo resolver autoría cuando la identidad histórica es inequívoca dentro del hospital.
    op.execute("""UPDATE sigarh_roles_turno r SET created_by_id = u.id FROM sigarh_usuarios u
        WHERE r.tenant_id = u.tenant_id AND (r.created_by = u.username OR r.created_by = u.email)
        AND (SELECT count(*) FROM sigarh_usuarios x WHERE x.tenant_id=r.tenant_id
             AND (r.created_by=x.username OR r.created_by=x.email))=1""")
    # Versiones antiguas concedían aprobación global masivamente. Registrar y revocar
    # exactamente esa concesión; un administrador deberá asignarla explícitamente.
    op.execute("""INSERT INTO audit_logs (id, tenant_id, action, model, model_id, description, old_values, new_values, created_at)
        SELECT gen_random_uuid(), tenant_id, 'permissions_reset', 'RolSistema', id::text,
        'Retiro de concesión global heredada; requiere asignación explícita',
        json_build_object('permisos_accion', permisos_accion, 'alcance_global', alcance_global),
        json_build_object('permisos_accion', '[]', 'alcance_global', false), now()
        FROM sigarh_roles_sistema WHERE alcance_global=true AND permisos_accion='["aprobar_roles_turno"]'""")
    op.execute("""UPDATE sigarh_roles_sistema SET permisos_accion='[]', alcance_global=false
        WHERE alcance_global=true AND permisos_accion='["aprobar_roles_turno"]'""")
    op.execute("""ALTER TABLE sigarh_grupos_ocupacionales ADD CONSTRAINT fk_grupo_catalogo
        FOREIGN KEY (tipo_grupo_id) REFERENCES sigarh_catalogos(id) ON DELETE RESTRICT NOT VALID""")
    # No se corrigen duplicados silenciosamente: los índices fallan y revierte toda
    # la migración. El preflight documentado permite regularizar antes del despliegue.
    for suffix in TABLES:
        table = "sigarh_" + suffix
        if suffix not in {"usuarios", "guardias_valorizadas"}:
            op.execute(f'CREATE UNIQUE INDEX uq_mant_{suffix}_nombre ON {table} (tenant_id, lower(trim(nombre)))')
        if suffix in CODES:
            op.execute(f"CREATE UNIQUE INDEX uq_mant_{suffix}_codigo ON {table} (tenant_id, lower(trim(codigo))) WHERE codigo IS NOT NULL AND trim(codigo) <> ''")
    for field in ("username", "email"):
        op.execute(f'CREATE UNIQUE INDEX uq_mant_usuarios_{field} ON sigarh_usuarios (lower(trim({field})))')
    # Todas las referencias deben compartir hospital. Se comprueba en API y BD.
    op.execute("""
    CREATE FUNCTION mantenimiento_referencias() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE rel record; ref uuid; valido boolean;
    BEGIN
      FOR rel IN SELECT a.attname AS campo, c.confrelid::regclass AS destino
        FROM pg_constraint c JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=c.conkey[1]
        JOIN pg_attribute target ON target.attrelid=c.confrelid AND target.attname='tenant_id'
        WHERE c.contype='f' AND c.conrelid=TG_RELID AND array_length(c.conkey,1)=1
      LOOP
        ref := (to_jsonb(NEW)->>rel.campo)::uuid;
        IF ref IS NOT NULL THEN
          EXECUTE format('SELECT EXISTS (SELECT 1 FROM %s WHERE id=$1 AND tenant_id=$2)', rel.destino)
            INTO valido USING ref, NEW.tenant_id;
          IF NOT valido THEN RAISE EXCEPTION 'Referencia fuera del hospital: %', rel.campo USING ERRCODE='23514'; END IF;
        END IF;
      END LOOP;
      RETURN NEW;
    END $$;
    """)
    op.execute("""
    CREATE FUNCTION mantenimiento_proteger_catalogo() RETURNS trigger LANGUAGE plpgsql AS $$
    DECLARE rel record; utilizado boolean;
    BEGIN
      IF TG_OP='UPDATE' AND (to_jsonb(NEW)-'updated_at'-'descripcion')=(to_jsonb(OLD)-'updated_at'-'descripcion') THEN RETURN NEW; END IF;
      FOR rel IN SELECT c.conrelid::regclass AS origen, a.attname AS campo
        FROM pg_constraint c JOIN pg_attribute a ON a.attrelid=c.conrelid AND a.attnum=c.conkey[1]
        WHERE c.contype='f' AND c.confrelid=TG_RELID AND array_length(c.conkey,1)=1
      LOOP
        EXECUTE format('SELECT EXISTS (SELECT 1 FROM %s WHERE %I=$1)', rel.origen, rel.campo)
          INTO utilizado USING OLD.id;
        IF utilizado THEN RAISE EXCEPTION 'Catálogo utilizado; conserve el registro y cree una nueva versión' USING ERRCODE='23503'; END IF;
      END LOOP;
      IF TG_OP='DELETE' THEN RETURN OLD; ELSE RETURN NEW; END IF;
    END $$;
    """)
    for suffix in TABLES:
        table = "sigarh_" + suffix
        op.execute(f'CREATE TRIGGER mantenimiento_referencias BEFORE INSERT OR UPDATE ON {table} FOR EACH ROW EXECUTE FUNCTION mantenimiento_referencias()')
        if suffix not in SECURITY:
            op.execute(f'CREATE TRIGGER mantenimiento_proteger BEFORE UPDATE OR DELETE ON {table} FOR EACH ROW EXECUTE FUNCTION mantenimiento_proteger_catalogo()')


def downgrade():
    # No restaura permisos globales ni elimina auditoría histórica.
    for suffix in TABLES:
        table = "sigarh_" + suffix
        op.execute(f'DROP TRIGGER IF EXISTS mantenimiento_referencias ON {table}')
        op.execute(f'DROP TRIGGER IF EXISTS mantenimiento_proteger ON {table}')
        for field in ("nombre", "codigo"):
            op.execute(f'DROP INDEX IF EXISTS uq_mant_{suffix}_{field}')
    for field in ("username", "email"):
        op.execute(f'DROP INDEX IF EXISTS uq_mant_usuarios_{field}')
    op.execute('DROP FUNCTION mantenimiento_referencias()')
    op.execute('DROP FUNCTION mantenimiento_proteger_catalogo()')
    op.drop_constraint('fk_grupo_catalogo', 'sigarh_grupos_ocupacionales', type_='foreignkey')
    op.drop_column('sigarh_roles_turno', 'created_by_id')
    op.drop_column('sigarh_actividades', 'genera_agenda')
    op.drop_constraint('ck_guardia_valor', 'sigarh_guardias_valorizadas')
    op.drop_constraint('ck_guardia_vigencia', 'sigarh_guardias_valorizadas')
    for name in ('moneda', 'vigencia_desde', 'vigencia_hasta', 'sustento'):
        op.drop_column('sigarh_guardias_valorizadas', name)
    op.alter_column('sigarh_guardias_valorizadas', 'valor', type_=sa.Float())
    op.drop_constraint('ck_horario_minutos', 'sigarh_horarios_guardia')
    op.drop_column('sigarh_horarios_guardia', 'duracion_minutos')
    # Conservar Float evita destruir duraciones fraccionarias en un rollback.
    op.drop_column('sigarh_usuarios', 'session_version')
    for suffix in TABLES:
        if suffix not in {'departamentos', 'servicios', 'usuarios'}:
            op.drop_column('sigarh_' + suffix, 'updated_at')
