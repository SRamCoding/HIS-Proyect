export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore()
  if (!to.path.startsWith('/app') || !auth.isAuthenticated || auth.user?.panel !== 'app') return
  const permiso = hospitalPermiso(to.path)
  if (permiso && !hospitalPuede(auth.user.active_modules || [], permiso)) {
    return navigateTo({ path: '/app', query: to.query })
  }
})
