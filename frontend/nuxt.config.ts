export default defineNuxtConfig({
  components: [{ path: "~/components", pathPrefix: false }],
  srcDir: '.',
  compatibilityDate: '2026-09-02',
  devtools: { enabled: true },
  modules: [
    '@nuxt/ui',
    '@pinia/nuxt',
    '@pinia-plugin-persistedstate/nuxt',
  ],
  css: ['~/assets/css/main.css', '~/assets/css/sigarh-form.css', '~/assets/css/sigarh-index.css', '~/assets/css/sigarh-wizard.css', '~/assets/css/sigarh-table.css', '~/assets/css/hospital-theme.css'],
app: {
  head: {
    viewport: 'width=device-width, initial-scale=1',
    link: [
      {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap',
      },
    ],
  },
},
runtimeConfig: {
  // Solo accesible en el servidor (Nitro/SSR). El build en producción usa
  // NUXT_PUBLIC_API_URL=/api (ruta relativa que Apache proxea al backend),
  // pero una ruta relativa no se puede resolver durante el renderizado en
  // servidor (no hay origen de navegador) y termina fetcheando contra el
  // propio proceso de Nitro, que no tiene rutas /api. Por eso el SSR usa
  // esta URL absoluta directa al backend en vez de config.public.apiUrl.
  internalApiUrl: process.env.NUXT_INTERNAL_API_URL || 'http://127.0.0.1:8010',
  public: {
    apiUrl: process.env.NUXT_PUBLIC_API_URL || 'http://localhost:8000',
    tenantDomain: process.env.NUXT_PUBLIC_TENANT_DOMAIN || 'techquk.com',
  },
},
  routeRules: {
    '/admin/**': { ssr: false },
    '/app/**': { ssr: false },
    '/sigarh/**': { ssr: false },
    '/portal/**': { ssr: false },
  },
})
