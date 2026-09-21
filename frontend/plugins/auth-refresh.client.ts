// frontend/plugins/auth-refresh.client.ts
const INACTIVIDAD_MAXIMA_MS = 30 * 60 * 1000 // 30 minutos sin interacción
const CLAVE_ULTIMA_ACTIVIDAD = 'erp-ultima-actividad'
const INTERVALO_CHEQUEO_MS = 60 * 1000 // revisa inactividad cada minuto, no cada 5
const INTERVALO_REFRESH_MS = 5 * 60 * 1000

export default defineNuxtPlugin(async () => {
  const authStore = useAuthStore()

  // La expiración del JWT no equivale a cerrar sesión por inactividad: el
  // refresco periódico de abajo mantendría la sesión viva indefinidamente
  // aunque el usuario se haya ido de la pantalla (relevante en equipos
  // compartidos). Se registra la última interacción real del usuario y,
  // si se supera el máximo, se cierra sesión (server + local) en vez de
  // refrescar. Se persiste en sessionStorage (no solo en memoria) porque un
  // F5 recrea este plugin desde cero -- sin persistirlo, recargar la página
  // reiniciaba el contador de inactividad a cero, dejando la sesión viva
  // indefinidamente con solo recargar de vez en cuando.
  const leerUltimaActividad = (): number => {
    try {
      const guardada = sessionStorage.getItem(CLAVE_ULTIMA_ACTIVIDAD)
      if (guardada) return Number(guardada)
    } catch { /* almacenamiento bloqueado: se sigue con el valor por defecto */ }
    return Date.now()
  }
  let ultimaActividad = leerUltimaActividad()
  const marcarActividad = () => {
    ultimaActividad = Date.now()
    try { sessionStorage.setItem(CLAVE_ULTIMA_ACTIVIDAD, String(ultimaActividad)) } catch { /* no crítico */ }
  }
  ;['pointerdown', 'keydown', 'scroll'].forEach((evento) => {
    window.addEventListener(evento, marcarActividad, { passive: true })
  })

  const cerrarPorInactividad = async () => {
    // authStore.logout() (no clearSession() solo) porque cerrar "por
    // inactividad" debe revocar la sesion en el servidor y borrar las
    // cookies httpOnly -- limpiar solo el estado local dejaba el
    // access/refresh token del navegador seguir siendo validos en el
    // backend hasta su expiracion natural, contradiciendo el proposito
    // mismo de un cierre por inactividad.
    await authStore.logout()
    try { sessionStorage.removeItem(CLAVE_ULTIMA_ACTIVIDAD) } catch { /* no crítico */ }
    await navigateTo('/login')
  }

  // Si la inactividad guardada ya supera el limite ANTES de intentar nada,
  // hay que cerrar la sesion ya mismo -- refrescar primero (como se hacia
  // antes) extendia la sesion tanto local como en el servidor un momento
  // antes de cerrarla, asi que recargar la pagina despues del limite
  // "revivia" una sesion que deberia haber quedado cerrada.
  if (authStore.isAuthenticated && Date.now() - ultimaActividad >= INACTIVIDAD_MAXIMA_MS) {
    await cerrarPorInactividad()
  } else if (authStore.isAuthenticated) {
    // Al arrancar la app (incluye recargar la página con F5), si la sesión
    // sigue dentro del límite de inactividad, refresca el token para traer
    // los active_modules actualizados desde la BD.
    await authStore.refresh()
  }

  // Chequeo de inactividad cada minuto: con 5 minutos, la sesión podia
  // seguir viva hasta 4:59 despues del limite real antes de cortarse.
  setInterval(() => {
    if (!authStore.isAuthenticated) return
    if (Date.now() - ultimaActividad >= INACTIVIDAD_MAXIMA_MS) cerrarPorInactividad()
  }, INTERVALO_CHEQUEO_MS)

  // Refresco periódico en segundo plano, cada 5 minutos, para que los
  // cambios de módulos se reflejen sin necesidad de recargar ni cerrar
  // sesión -- se salta si ya se superó el límite de inactividad, para no
  // revivir una sesión que el chequeo de arriba está por cerrar.
  setInterval(async () => {
    if (!authStore.isAuthenticated) return
    if (Date.now() - ultimaActividad >= INACTIVIDAD_MAXIMA_MS) return
    await authStore.refresh()
  }, INTERVALO_REFRESH_MS)
})