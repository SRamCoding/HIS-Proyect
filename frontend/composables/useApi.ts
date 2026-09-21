const METODOS_MUTANTES = new Set(['POST', 'PUT', 'PATCH', 'DELETE'])

export const useApi = () => {
  const authStore = useAuthStore()
  const config = useRuntimeConfig()

  // En SSR, config.public.apiUrl suele ser una ruta relativa (p.ej. "/api")
  // que Apache proxea al backend; Nitro no tiene ese origen de navegador para
  // resolverla, así que en servidor se usa la URL absoluta directa al backend.
  const baseUrl = import.meta.server ? config.internalApiUrl : config.public.apiUrl

  const api = async <T = any>(endpoint: string, options: any = {}): Promise<T> => {
    const explicitTenant = typeof options.tenant === 'string' && options.tenant.trim()
      ? options.tenant.trim()
      : null
    const { tenant: _tenant, ...fetchOptions } = options
    const metodo = (fetchOptions.method || 'GET').toUpperCase()
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      // La sesión viaja en la cookie httpOnly del panel (ver
      // backend/app/auth/router.py), no en un header manual -- por eso
      // `credentials: 'include'` más abajo, no un Authorization aquí.
      ...(METODOS_MUTANTES.has(metodo) && { 'X-CSRF-Token': leerCsrfToken() || '' }),
      ...((explicitTenant || authStore.user?.tenant_id) && {
        'X-Tenant-ID': explicitTenant || authStore.user?.tenant_id as string,
      }),
      ...(authStore.user?.panel && { 'X-Panel': authStore.user.panel }),
      ...options.headers,
    }

    // Un 401 en /auth/login o /auth/refresh es un rechazo normal de credenciales
    // o de un refresh token vencido, no una sesión activa que expiró a mitad de
    // uso: no debe disparar logout ni redirigir, sino dejar que la propia
    // pantalla de login muestre el mensaje de error.
    const esLlamadaDeAuth = endpoint.startsWith('/auth/login') || endpoint.startsWith('/auth/refresh')

    try {
      return await $fetch<T>(`${baseUrl}${endpoint}`, {
        ...fetchOptions,
        credentials: 'include',
        headers,
      })
    } catch (error: any) {
      if (error?.response?.status === 401 && !esLlamadaDeAuth) {
        const resultado = await authStore.refresh()
        if (resultado === 'ok') {
          // El refresh rota la cookie csrf_token (ver _set_csrf_cookie en
          // el backend) -- reusar el header CSRF armado ANTES de refrescar
          // reenvia un valor ya vencido, y el reintento moriria con 403 en
          // vez de la mutacion real. Se reconstruye con el valor actual.
          const headersReintento = {
            ...headers,
            ...(METODOS_MUTANTES.has(metodo) && { 'X-CSRF-Token': leerCsrfToken() || '' }),
          }
          return await $fetch<T>(`${baseUrl}${endpoint}`, {
            ...fetchOptions,
            credentials: 'include',
            headers: headersReintento,
          })
        }
        // 'error' (red, timeout, 5xx) no es un rechazo de sesión: forzar
        // logout aca anulaba la proteccion de refresh() contra caidas
        // temporales -- el token de acceso sigue siendo el mismo de antes,
        // esta peticion puntual falla, pero la sesion local se conserva
        // para que el usuario pueda seguir trabajando o reintentar.
        if (resultado === 'invalid') {
          const panel = authStore.user?.panel
          authStore.logout()
          await navigateTo(panel === 'sigarh' ? '/sigarh/login' : panel === 'app' ? '/app/login' : '/login')
        }
      }
      throw error
    }
  }

  return { api }
}
