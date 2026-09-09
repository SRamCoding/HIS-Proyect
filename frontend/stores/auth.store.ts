// stores/auth.store.ts
interface User {
  id: string
  email: string
  name: string
  role: string
  panel: 'admin' | 'app' | 'sigarh' | 'portal'
  tenant_id: string | null
  active_modules: string[]  // ← línea 8: módulos activos del tenant
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
    // ← línea 23: helper para verificar si el módulo está activo
    hasModule: (state) => (moduleCode: string) => {
      return state.user?.active_modules?.includes(moduleCode) ?? false
    },
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
        const response = await $fetch<{ access_token: string; user: User }>(
          `${config.public.apiUrl}/auth/refresh`,
          {
            method: 'POST',
            body: { refresh_token: this.refreshToken },
          }
        )
        this.token = response.access_token
        if (response.user) this.user = response.user
        return true
      } catch {
        this.clearSession()
        return false
      }
    },
    clearSession() {
      this.token = null
      this.refreshToken = null
      this.user = null
    },
    async logout() {
      const config = useRuntimeConfig()
      try {
        await $fetch(`${config.public.apiUrl}/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${this.token}` },
        })
      } catch {}
      this.clearSession()
    },
  },
  // Cada pestaña mantiene su propia sesión. Esto permite usar Admin, App y
  // SIGARH simultáneamente sin que el último login sobrescriba a los demás.
  persist: {
    storage: persistedState.sessionStorage,
  },
})
