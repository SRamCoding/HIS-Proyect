// composables/useApi.ts
export const useApi = () => {
  const authStore = useAuthStore()
  const config = useRuntimeConfig()

  const api = async <T = any>(endpoint: string, options: any = {}): Promise<T> => {
    try {
      return await $fetch<T>(`${config.public.apiUrl}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...(authStore.token && { Authorization: `Bearer ${authStore.token}` }),
          ...options.headers,
        },
      })
    } catch (error: any) {
      if (error?.response?.status === 401) {
        const refreshed = await authStore.refresh()
        if (refreshed) {
          return await $fetch<T>(`${config.public.apiUrl}${endpoint}`, {
            ...options,
            headers: {
              'Content-Type': 'application/json',
              Authorization: `Bearer ${authStore.token}`,
              ...options.headers,
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