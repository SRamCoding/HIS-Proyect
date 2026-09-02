export const useApi = () => {
  const authStore = useAuthStore()
  const config = useRuntimeConfig()

  const api = async <T = any>(endpoint: string, options: any = {}): Promise<T> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(authStore.token && { Authorization: `Bearer ${authStore.token}` }),
      ...(authStore.user?.tenant_id && { 'X-Tenant-ID': authStore.user.tenant_id }),
      ...options.headers,
    }

    try {
      return await $fetch<T>(`${config.public.apiUrl}${endpoint}`, {
        ...options,
        headers,
      })
    } catch (error: any) {
      if (error?.response?.status === 401) {
        const refreshed = await authStore.refresh()
        if (refreshed) {
          return await $fetch<T>(`${config.public.apiUrl}${endpoint}`, {
            ...options,
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