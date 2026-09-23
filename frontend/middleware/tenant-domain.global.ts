// Nuxt enruta por PATH de archivo, no por dominio: "/" y "/login" son
// siempre los mismos archivos (pages/index.vue, pages/login.vue -- el
// portal admin central) sin importar desde que Host se entre. Cada
// hospital tiene su propio subdominio (Tenant.domain, ej.
// hospital-reque.techquk.com), pero visitarlo en la raiz mostraba el
// portal admin generico en vez del login/landing de ESE hospital -- nada
// miraba el Host para decidirlo. Este middleware global resuelve el Host
// contra /auth/resolver-dominio (publica, sin auth) y redirige solo esos
// dos puntos de entrada cuando el dominio pertenece a un hospital real.
export default defineNuxtRouteMiddleware(async (to) => {
  if (to.path !== '/' && to.path !== '/login') return
  if (to.query.tenant) return // ya viene resuelto explicitamente, no repetir la consulta

  const config = useRuntimeConfig()
  const { hostname } = useRequestURL()
  const baseUrl = import.meta.server ? config.internalApiUrl : config.public.apiUrl

  try {
    const data = await $fetch<{ tenant_id: string | null }>(`${baseUrl}/auth/resolver-dominio`, {
      query: { domain: hostname },
    })
    if (!data?.tenant_id) return // dominio central o no registrado: se sigue mostrando el portal admin

    // Sin "?tenant=" en el destino de /login a proposito: el hospital ya
    // esta identificado por el propio subdominio (Host), no hace falta
    // repetirlo en la URL. app/login.vue y sigarh/login.vue (comparten el
    // mismo fallback en el backend, auth/router.py ~276-286) resuelven el
    // tenant por Host al momento de enviar el formulario si no llega
    // X-Tenant-ID -- una vez que ya estamos en el subdominio correcto, la
    // resolucion aqui en el middleware solo decidio A DONDE redirigir, no
    // hace falta que el navegador la vuelva a cargar como query visible.
    if (to.path === '/login') {
      return navigateTo('/app/login', { replace: true })
    }
    // "/" (landing publica) si necesita el id en la URL: pages/index.vue
    // no tiene el mismo fallback por Host, usa ?tenant= para pedir
    // /auth/tenant-publico/{id} y mostrar el contenido institucional real
    // de ese hospital.
    return navigateTo({ path: '/', query: { ...to.query, tenant: data.tenant_id } }, { replace: true })
  } catch {
    // Backend no disponible en este instante: no bloquear la navegacion,
    // se sigue mostrando el portal admin central por defecto.
  }
})
