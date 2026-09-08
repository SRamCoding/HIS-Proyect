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
  css: ['~/assets/css/main.css', '~/assets/css/sigarh-form.css', '~/assets/css/sigarh-index.css'],
app: {
  head: {
    link: [
      {
        rel: 'stylesheet',
        href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap',
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