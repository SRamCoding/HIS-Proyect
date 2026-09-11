export const useApi = () => {
  const authStore = useAuthStore()
  const config = useRuntimeConfig()

  const api = async <T = any>(endpoint: string, options: any = {}): Promise<T> => {
    const explicitTenant = typeof options.tenant === 'string' && options.tenant.trim()
      ? options.tenant.trim()
      : null
    const { tenant: _tenant, ...fetchOptions } = options
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(authStore.token && { Authorization: `Bearer ${authStore.token}` }),
      ...((explicitTenant || authStore.user?.tenant_id) && {
        'X-Tenant-ID': explicitTenant || authStore.user?.tenant_id as string,
      }),
      ...options.headers,
    }

    // Un 401 en /auth/login o /auth/refresh es un rechazo normal de credenciales
    // o de un refresh token vencido, no una sesión activa que expiró a mitad de
    // uso: no debe disparar logout ni redirigir, sino dejar que la propia
    // pantalla de login muestre el mensaje de error.
    const esLlamadaDeAuth = endpoint.startsWith('/auth/login') || endpoint.startsWith('/auth/refresh')

    try {
      return await $fetch<T>(`${config.public.apiUrl}${endpoint}`, {
        ...fetchOptions,
        headers,
      })
    } catch (error: any) {
      if (error?.response?.status === 401 && !esLlamadaDeAuth) {
        const refreshed = await authStore.refresh()
        if (refreshed) {
          return await $fetch<T>(`${config.public.apiUrl}${endpoint}`, {
            ...fetchOptions,
            headers: {
              ...headers,
              Authorization: `Bearer ${authStore.token}`,
            },
          })
        }
        const panel = authStore.user?.panel
        authStore.logout()
        await navigateTo(panel === 'sigarh' ? '/sigarh/login' : panel === 'app' ? '/app/login' : '/login')
      }
      throw error
    }
  }

  return { api }
}
