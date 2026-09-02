export default defineNuxtConfig({
  srcDir: '.',
  compatibilityDate: '2026-09-02',
  devtools: { enabled: true },
  modules: [
    '@nuxt/ui',
    '@pinia/nuxt',
    '@pinia-plugin-persistedstate/nuxt',
  ],
  css: ['~/assets/css/main.css'],
  app: {
    head: {
      link: [
        {
          rel: 'stylesheet',
          href: 'https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap',
        },
      ],
    },
  },
runtimeConfig: {
  public: {
    apiUrl: 'http://localhost:8000',
  },
},
  routeRules: {
    '/admin/**': { ssr: false },
    '/app/**': { ssr: false },
    '/sigarh/**': { ssr: false },
    '/portal/**': { ssr: false },
  },
})