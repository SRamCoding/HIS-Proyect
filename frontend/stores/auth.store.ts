// stores/auth.store.ts
interface User {
  id: string
  email: string
  name: string
  role: string
  empleado_id?: string | null
  perfil_hospital_id?: string | null
  panel: 'admin' | 'app' | 'sigarh' | 'portal'
  tenant_id: string | null
  active_modules: string[]  // ← línea 8: módulos activos del tenant
}

interface LoginPayload {
  email: string
  password: string
  panel: string
}

interface LoginResult {
  user?: User
  mfa_required?: boolean
  mfa_setup?: boolean
  otpauth_uri?: string | null
  qr_png_base64?: string | null
  secret?: string | null
}

// Fuera del store: varias peticiones en paralelo que reciben 401 al mismo
// tiempo disparaban cada una su propio refresh() con el MISMO refresh token
// vigente. Como el backend ahora rota el refresh token en cada renovación
// (ver backend/app/core/refresh_tracking.py), la segunda petición en
// llegar presentaría un token ya gastado por la primera -- el backend lo
// trata como reuso de un token robado y revoca toda la sesión. Se comparte
// una única promesa en vuelo entre todos los llamadores de esta pestaña
// para que solo se dispare una petición real de refresh a la vez.
let refrescoEnVuelo: Promise<'ok' | 'invalid' | 'error'> | null = null

export const useAuthStore = defineStore('auth', {
  state: () => ({
    // access_token y refresh_token YA NO viven aca: el backend los manda
    // como cookies httpOnly (ver backend/app/auth/router.py), invisibles
    // para JS a proposito. Guardarlos tambien en este store (persistido en
    // sessionStorage) los volvia legibles por cualquier script del mismo
    // origen -- si algun otro modulo tuviera una vulnerabilidad XSS, ese
    // script podia robar la sesion administrativa completa. `user` no es
    // sensible en ese sentido (nombre/correo/rol, no credenciales) y sigue
    // aca porque la UI lo necesita sincronicamente sin otra peticion.
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
    // Ya no hay token en JS para chequear: `user` es la unica señal
    // disponible de que el login (o un refresh) se completo con exito.
    isAuthenticated: (state) => !!state.user,
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
      // credentials: 'include' es lo que hace que el navegador GUARDE las
      // cookies Set-Cookie de esta respuesta (access_token/refresh_token/
      // csrf_token) aunque el backend este en otro puerto/origen (local:
      // :3000 -> :8000; en produccion, mismo origen via Apache).
      const response = await $fetch<LoginResult>(`${config.public.apiUrl}/auth/login`, {
        method: 'POST',
        credentials: 'include',
        body: payload,
      })
      // Panel admin: la contraseña sola ya no basta (MFA obligatorio, ver
      // backend/app/auth/router.py). Si mfa_required viene true, todavia
      // no hay sesion real -- el llamador debe pedir el codigo TOTP y
      // llamar a mfaVerify() antes de que `user` quede seteado.
      if (!response.mfa_required && response.user) this.user = response.user
      return response
    },
    // Segundo paso del login admin: confirma el codigo TOTP (setup o
    // verify, ver backend) y recien ahi obtiene la sesion real.
    async mfaVerify(code: string) {
      const config = useRuntimeConfig()
      const response = await $fetch<{ user: User }>(`${config.public.apiUrl}/auth/mfa/verify`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'X-CSRF-Token': leerCsrfToken() || '' },
        body: { code },
      })
      this.user = response.user
      return response
    },
    // Devuelve 'ok' | 'invalid' | 'error' en vez de un booleano: un booleano
    // no distingue "el refresh token fue rechazado, cierra sesión" de "hubo
    // un problema de red, reintenta después" -- los llamadores (useApi,
    // el plugin de refresco periódico) necesitan tratar cada caso distinto,
    // si no, cualquier caída temporal termina forzando un logout igual.
    async refresh(): Promise<'ok' | 'invalid' | 'error'> {
      if (refrescoEnVuelo) return refrescoEnVuelo
      refrescoEnVuelo = this._refreshReal()
      try {
        return await refrescoEnVuelo
      } finally {
        refrescoEnVuelo = null
      }
    },
    async _refreshReal(): Promise<'ok' | 'invalid' | 'error'> {
      if (!this.user) return 'invalid'
      const panel = this.user.panel
      // refrescoEnVuelo (arriba) solo coordina dentro de ESTA pestaña -- el
      // backend rota el refresh token por SESIÓN (sid), y todas las
      // pestañas del mismo panel comparten la misma cookie de sesión
      // (ver auth/router.py). Dos pestañas refrescando a la vez son,
      // para el backend, dos renovaciones concurrentes con el MISMO
      // token viejo: una gana la reserva atómica, la otra se rechaza como
      // reuso y fuerza a revocar toda la sesión -- un logout sorpresivo en
      // la otra pestaña por algo que no fue un ataque. La Web Locks API
      // (soportada en navegadores modernos) serializa la llamada de red
      // real entre pestañas del mismo panel: la que pierde la carrera
      // simplemente espera su turno y refresca DESPUÉS con la cookie ya
      // actualizada por la primera, en vez de competir por el mismo token.
      const ejecutar = () => this._refreshReq(panel)
      if (typeof navigator !== 'undefined' && 'locks' in navigator) {
        return await (navigator as any).locks.request(`erp-refresh-${panel}`, ejecutar)
      }
      return await ejecutar()
    },
    async _refreshReq(panel: string): Promise<'ok' | 'invalid' | 'error'> {
      const generacion = this.sessionGeneration
      const config = useRuntimeConfig()
      try {
        const response = await $fetch<{ user: User }>(`${config.public.apiUrl}/auth/refresh`, {
          method: 'POST',
          credentials: 'include',
          // El refresh_token va en la cookie httpOnly del panel (no hace
          // falta mandarlo en el body), pero SI hay que decir cual panel:
          // las cookies estan nombradas por panel (access_token_admin,
          // access_token_app, ...) para que este mismo navegador pueda
          // tener sesiones simultaneas en pestañas de paneles distintos, y
          // el backend no tiene otra forma de saber cual usar aca.
          body: { panel },
          headers: { 'X-CSRF-Token': leerCsrfToken() || '' },
        })
        if (this.sessionGeneration !== generacion) return 'invalid'
        if (response.user) this.user = response.user
        return 'ok'
      } catch (e: any) {
        // Solo un rechazo explícito del refresh token (401) significa que
        // la sesión ya no es válida. Un error de red, timeout o caída
        // temporal del backend (sin respuesta, o 5xx) no debe borrar la
        // sesión local -- el usuario seguiría con su token de acceso
        // vigente hasta que sí llegue un refresh exitoso o un 401 real.
        const status = e?.response?.status ?? e?.status
        if (status === 401) {
          if (this.sessionGeneration === generacion) this.clearSession()
          return 'invalid'
        }
        return 'error'
      }
    },
    updateUser(cambios: Partial<Pick<User, 'name' | 'email'>>) {
      if (this.user) this.user = { ...this.user, ...cambios }
    },
    clearSession() {
      this.sessionGeneration++
      this.user = null
    },
    async logout() {
      const config = useRuntimeConfig()
      const panel = this.user?.panel
      // La sesion local se limpia YA, antes de esperar al servidor: en un
      // equipo compartido no hay que dejar la pantalla con datos visibles
      // mientras cuelga una peticion sin limite de tiempo. Las cookies
      // httpOnly de sesion, en cambio, solo el backend puede borrarlas
      // (Set-Cookie con Max-Age=0) -- este intento es best-effort, con un
      // tope explicito (la libreria no pone uno por defecto). `panel` se
      // captura ANTES de limpiar la sesion local porque clearSession()
      // borra `user`, y el backend necesita saber cual cookie limpiar.
      this.clearSession()
      try {
        await $fetch(`${config.public.apiUrl}/auth/logout`, {
          method: 'POST',
          credentials: 'include',
          query: panel ? { panel } : undefined,
          headers: { 'X-CSRF-Token': leerCsrfToken() || '' },
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
  // Este store (con `user`) sigue siendo por pestaña via sessionStorage,
  // pero la sesion REAL vive en las cookies httpOnly del backend, que SI
  // son compartidas por todo el navegador (no por pestaña). Lo que permite
  // usar Admin, App y SIGARH simultaneamente sin pisarse es que cada panel
  // tiene su propia cookie nombrada (access_token_admin, access_token_app,
  // ...) -- dos pestañas del MISMO panel (dos pestañas de admin, por
  // ejemplo) SI comparten la misma cookie de sesion.
  persist: {
    storage: persistedState.sessionStorage,
  },
})
