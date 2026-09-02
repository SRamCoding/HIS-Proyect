// stores/auth.store.ts
interface User {
  sub: string
  email: string
  name: string
  role: string
  panel: 'admin' | 'app' | 'sigarh'
  tenant_id: string | null
}

interface LoginPayload {
  email: string
  password: string
  panel: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    token: null as string | null,
    refreshToken: null as string | null,
    user: null as User | null,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    panelRoute: (state) => {
      switch (state.user?.panel) {
        case 'admin': return '/admin'
        case 'app': return '/app'
        case 'sigarh': return '/sigarh'
        default: return '/login'
      }
    },
  },

  actions: {
    async login(payload: LoginPayload) {
      const config = useRuntimeConfig()
      const response = await $fetch<{
        access_token: string
        refresh_token: string
        user: User
      }>(`${config.public.apiUrl}/auth/login`, {
        method: 'POST',
        body: payload,
      })

      this.token = response.access_token
      this.refreshToken = response.refresh_token
      this.user = response.user

      return response
    },

    async refresh() {
      if (!this.refreshToken) return false
      const config = useRuntimeConfig()
      try {
        const response = await $fetch<{ access_token: string }>(
          `${config.public.apiUrl}/auth/refresh`,
          {
            method: 'POST',
            body: { refresh_token: this.refreshToken },
          }
        )
        this.token = response.access_token
        return true
      } catch {
        return false
      }
    },

    async logout() {
      const config = useRuntimeConfig()
      try {
        await $fetch(`${config.public.apiUrl}/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${this.token}` },
        })
      } catch {
        // ignore errors on logout
      }
      this.token = null
      this.refreshToken = null
      this.user = null
    },
  },

  persist: true,
})