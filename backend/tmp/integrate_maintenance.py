from pathlib import Path
import re

def edit(path, fn):
    p=Path(path); p.write_text(fn(p.read_text(encoding='utf-8-sig')), encoding='utf-8')

# Autenticación de SIGARH y refresh contra la cuenta actual, nunca contra claims antiguos.
p=Path('backend/app/auth/router.py'); src=p.read_text(encoding='utf-8-sig')
start=src.index('    # Si el panel es sigarh')
end=src.index('    result = await db.execute(\n        select(User)',start)
src=src[:start]+'''    if data.panel == "sigarh":
        from sqlalchemy import func, or_
        from app.sigarh.mantenimiento.security import contexto_sigarh
        identifier = data.email.strip().lower()
        matches = (await db.scalars(select(UsuarioSigarh).where(or_(
            func.lower(UsuarioSigarh.email) == identifier,
            func.lower(UsuarioSigarh.username) == identifier,
        )).limit(2))).all()
        if len(matches) != 1 or not verify_password(data.password, matches[0].password):
            raise HTTPException(401, "Credenciales incorrectas o identificador ambiguo")
        token_data = await contexto_sigarh(db, matches[0])
        return _respuesta_sesion(token_data)

'''+src[end:]
pos=src.index('    result = await db.execute(',src.index('async def refresh_token'))
end=src.index('\n\n@router.post("/logout")',pos)
src=src[:pos]+'''    from app.sigarh.mantenimiento.security import usuario_actual
    token_data = await usuario_actual(db, payload)
    if token_data.get("auth_source") != "sigarh":
        from app.tenants.hospitales.models import TenantModule
        active_modules = []
        if token_data.get("tenant_id"):
            import uuid
            active_modules = list((await db.scalars(select(TenantModule.module_code).where(
                TenantModule.tenant_id == uuid.UUID(token_data["tenant_id"]), TenantModule.is_active.is_(True),
            ))).all())
        token_data["active_modules"] = active_modules
    return _respuesta_sesion(token_data)


def _respuesta_sesion(token_data):
    claims = {k: v for k, v in token_data.items() if k not in {"exp", "type", "iat", "nbf"}}
    return TokenResponse(access_token=create_access_token(claims), refresh_token=create_refresh_token(claims),
                         user={"id": claims["sub"], **claims})
'''+src[end:]
src=src.replace('from fastapi import APIRouter, Depends, HTTPException, status, Request','from fastapi import APIRouter, Depends, HTTPException, status, Request\nfrom app.core.dependencies import get_current_user')
start=src.index('@router.post("/logout")'); end=src.index('\n\nasync def _log_audit',start)
src=src[:start]+'''@router.post("/logout")
async def logout(request: Request, db: AsyncSession = Depends(get_db), user=Depends(get_current_user)):
    if user.get("auth_source") == "sigarh":
        import uuid
        cuenta = await db.scalar(select(UsuarioSigarh).where(UsuarioSigarh.id == uuid.UUID(user["sub"])).with_for_update())
        if cuenta:
            cuenta.session_version += 1
    await _log_audit(db, user["sub"], user.get("name"), user.get("tenant_id"), "logout",
                     model="UsuarioSigarh" if user.get("auth_source") == "sigarh" else "User",
                     description="Cierre de sesión", ip_address=request.client.host if request.client else None)
    return {"ok": True}
'''+src[end:]
p.write_text(src,encoding='utf-8')
edit('backend/app/auth/schemas.py',lambda s:s.replace('    active_modules: list[str] = []','    active_modules: list[str] = []\n    permisos_accion: list[str] = []\n    perfil_id: str | None = None\n    empleado_id: str | None = None\n    alcance_global: bool = False'))
# El control de módulo SIGARH usa la sesión revalidada.
edit('backend/app/tenants/entitlements.py',lambda s:s.replace('        # Obtener tenant_id del JWT o del header X-Tenant-ID','        if current_user.get("panel") == "sigarh" and module_code not in current_user.get("active_modules", []):\n            raise HTTPException(403, detail="Su perfil no permite este módulo")\n\n        # Obtener tenant_id del JWT o del header X-Tenant-ID'))
# Auditoría temporal uniforme en los 14 modelos.
p=Path('backend/app/sigarh/mantenimiento/models.py'); src=p.read_text(encoding='utf-8-sig')
parts=re.split(r'(?=^class )',src,flags=re.M)
for i,part in enumerate(parts):
    if part.startswith('class ') and 'updated_at:' not in part:
        part=part.replace('    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)', '    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)\n    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)')
    parts[i]=part
p.write_text(''.join(parts),encoding='utf-8')
# Identidad estable para la separación de funciones.
edit('backend/app/sigarh/creacion_roles/models.py', lambda s:s.replace('    created_by: Mapped[str | None]', '    created_by_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)\n    created_by: Mapped[str | None]'))
edit('backend/app/sigarh/creacion_roles/router.py',lambda s:s.replace('data, _nombre(current_user))','data, _nombre(current_user), uuid.UUID(current_user["sub"]))'))
edit('backend/app/sigarh/creacion_roles/service.py',lambda s:s.replace('data, usuario: str | None) -> dict:', 'data, usuario: str | None, usuario_id: uuid.UUID | None = None) -> dict:').replace('        created_by=usuario,','        created_by=usuario,\n        created_by_id=usuario_id,').replace('    if bool(getattr(act, "requiere_consultorio", False)):', '    if bool(getattr(act, "genera_agenda", False)):').replace('    return (getattr(act, "nombre", "") or "").strip().lower() in _NOMBRES_CONSULTA_EXTERNA','    return False').replace('return bool(empleado and empleado.es_jefe_servicio', 'return bool(empleado and empleado.is_active and empleado.es_jefe_servicio'))
edit('backend/app/sigarh/roles_pendientes/service.py', lambda s:s.replace('    if revisor and rol.created_by and revisor == rol.created_by:', '    if not rol.created_by_id:\n        raise ReglaNegocioError("El rol antiguo requiere identificar a su elaborador antes de aprobarse.")\n    if str(rol.created_by_id) == str(current_user.get("sub")):'))
# Generación de agenda explícita; la migración preserva el comportamiento anterior.
edit('backend/app/hospital/consulta_externa/service.py', lambda s:re.sub(r'or_\(\s*Actividad.requiere_consultorio == True,\s*func.lower\(Actividad.nombre\).in_\(\("consulta externa", "atencion ambulatoria", "atención ambulatoria"\)\),\s*\)', 'Actividad.genera_agenda == True', s))
# Quitar concesiones indiscriminadas también para instalaciones nuevas.
p=Path('backend/migrations/versions/a3c5e8f1d92b_permiso_aprobar_roles_turno.py'); s=p.read_text(encoding='utf-8-sig')
start=s.index('    # Migración retrocompatible:');end=s.index('    # sigarh_usuarios.empleado_id',start)
s=s[:start]+'    # Los permisos se asignan explícitamente por Administración ERP.\n\n'+s[end:];p.write_text(s,encoding='utf-8')
