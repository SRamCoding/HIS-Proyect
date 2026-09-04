// frontend/plugins/auth-refresh.client.ts
export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore()

  // Al arrancar la app (incluye recargar la página con F5),
  // si hay sesión activa, refresca el token para traer
  // los active_modules actualizados desde la BD.
  if (authStore.isAuthenticated) {
    await authStore.refresh()
  }

  // Refresco periódico en segundo plano, cada 5 minutos,
  // para que los cambios de módulos se reflejen sin
  // necesidad de recargar ni cerrar sesión.
  setInterval(async () => {
    if (authStore.isAuthenticated) {
      await authStore.refresh()
    }
  }, 5 * 60 * 1000) // 5 minutos
})