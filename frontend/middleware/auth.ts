// middleware/auth.ts
export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore()

  const panelSolicitado = to.path.startsWith('/sigarh')
    ? 'sigarh'
    : to.path.startsWith('/app')
      ? 'app'
      : to.path.startsWith('/admin')
        ? 'admin'
        : null
  const loginPanel = panelSolicitado === 'sigarh'
    ? '/sigarh/login'
    : panelSolicitado === 'app'
      ? '/app/login'
      : '/login'

  if (!authStore.isAuthenticated && to.path !== '/login') {
    return navigateTo(loginPanel)
  }

  if (panelSolicitado && authStore.user?.panel !== panelSolicitado) {
    authStore.clearSession()
    return navigateTo(loginPanel)
  }

  if (authStore.isAuthenticated && to.path === '/login') {
    return navigateTo(authStore.panelRoute)
  }
})
