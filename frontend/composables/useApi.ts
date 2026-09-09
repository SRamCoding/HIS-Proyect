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

    try {
      return await $fetch<T>(`${config.public.apiUrl}${endpoint}`, {
        ...fetchOptions,
        headers,
      })
    } catch (error: any) {
      if (error?.response?.status === 401) {
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
        authStore.logout()
        await navigateTo('/login')
      }
      throw error
    }
  }

  return { api }
}
