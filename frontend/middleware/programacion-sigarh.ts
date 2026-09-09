export default defineNuxtRouteMiddleware((to) => {
  return navigateTo({
    path: '/app/admision/programacion-medica',
    query: { tenant: to.query.tenant },
  }, { replace: true })
})
