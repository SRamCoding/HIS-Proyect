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
    // Se incrementa en cada clearSession(). refresh() lo captura antes de
    // esperar al backend y descarta su propia respuesta si ya cambio: sin
    // esto, una renovacion en vuelo que llega DESPUES de un logout (la
    // respuesta llega tarde, por lentitud de red) volvia a poner token/user
    // en el store, resucitando localmente una sesion que el usuario ya
    // habia cerrado en esta pestaña.
    sessionGeneration: 0,
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
      const generacion = this.sessionGeneration
      const config = useRuntimeConfig()
      try {
        const response = await $fetch<{ access_token: string; user: User }>(
          `${config.public.apiUrl}/auth/refresh`,
          {
            method: 'POST',
            body: { refresh_token: this.refreshToken },
          }
        )
        if (this.sessionGeneration !== generacion) return false
        this.token = response.access_token
        if (response.user) this.user = response.user
        return true
      } catch {
        if (this.sessionGeneration === generacion) this.clearSession()
        return false
      }
    },
    updateUser(cambios: Partial<Pick<User, 'name' | 'email'>>) {
      if (this.user) this.user = { ...this.user, ...cambios }
    },
    clearSession() {
      this.sessionGeneration++
      this.token = null
      this.refreshToken = null
      this.user = null
    },
    async logout() {
      const config = useRuntimeConfig()
      const token = this.token
      // La sesion local se limpia YA, antes de esperar al servidor: en un
      // equipo compartido no hay que dejar la pantalla con datos visibles
      // mientras cuelga una peticion sin limite de tiempo. El token
      // capturado arriba se conserva solo para este intento de revocacion,
      // best-effort, con un tope explicito (la libreria no pone uno por
      // defecto).
      this.clearSession()
      try {
        await $fetch(`${config.public.apiUrl}/auth/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
          timeout: 5000,
        })
        return true
      } catch {
        // El backend responde error si no pudo confirmar la revocacion del
        // lado del servidor (o la peticion no llego a tiempo): el token
        // viejo puede seguir siendo valido hasta que expire por su cuenta.
        return false
      }
    },
  },
  // Cada pestaña mantiene su propia sesión. Esto permite usar Admin, App y
  // SIGARH simultáneamente sin que el último login sobrescriba a los demás.
  persist: {
    storage: persistedState.sessionStorage,
  },
})
