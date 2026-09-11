// Permisos de accion del Rol del Sistema (independientes del acceso a
// modulos/submodulos): controlan si se puede crear/editar/eliminar en las
// pantallas de seguridad (Usuarios, Perfiles de Usuario, Roles del Sistema).
// Ver backend/app/sigarh/mantenimiento/router.py::autorizar().
export const useSigarhPermisos = () => {
  const authStore = useAuthStore()
  const permisosAccion = computed(() => authStore.user?.permisos_accion ?? [])
  const tienePermiso = (codigo: string) => permisosAccion.value.includes(codigo)
  const puedeAdministrarSeguridad = computed(() => tienePermiso('administrar_seguridad'))
  const puedeAdministrarMantenimiento = computed(() => tienePermiso('administrar_mantenimiento'))
  return { tienePermiso, puedeAdministrarSeguridad, puedeAdministrarMantenimiento }
}
