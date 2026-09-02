// middleware/panel.ts
export default defineNuxtRouteMiddleware((to) => {
  const authStore = useAuthStore()
  if (!authStore.user) return

  const panelPrefixes: Record<string, string> = {
    admin: '/admin',
    app: '/app',
    sigarh: '/sigarh',
  }

  const userPrefix = panelPrefixes[authStore.user.panel]
  const isProtectedRoute = Object.values(panelPrefixes).some((p) => to.path.startsWith(p))

  if (isProtectedRoute && userPrefix && !to.path.startsWith(userPrefix)) {
    return navigateTo(userPrefix)
  }
})