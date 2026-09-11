<!-- frontend/pages/app/login.vue -->
<template>
  <div class="flex" style="position: fixed; inset: 0; font-family: var(--font-sans, 'Inter', sans-serif)">

    <div
      class="hidden lg:block relative overflow-hidden"
      style="width: 60%; background: #dfeef9"
    >
      <img
        src="/sigarh.png"
        alt="Panel Hospitalario"
        class="w-full h-full object-cover"
        style="
          mask-image: linear-gradient(to right, black 0%, black 88%, transparent 100%);
          -webkit-mask-image: linear-gradient(to right, black 0%, black 88%, transparent 100%);
        "
      />
    </div>

    <div
      class="relative flex flex-col items-center justify-between w-full lg:w-[40%] overflow-hidden"
      style="background-image: url('/fondo.png'); background-size: cover; background-position: center; background-color: #dfeef9;"
    >
      <svg width="28" height="28" viewBox="0 0 28 28" class="absolute top-6 left-1/2 -translate-x-1/2 pointer-events-none" style="opacity: 0.4">
        <rect x="11" y="0" width="6" height="28" rx="2" fill="#c3cedb" />
        <rect x="0" y="11" width="28" height="6" rx="2" fill="#c3cedb" />
      </svg>

      <svg width="120" height="120" viewBox="0 0 120 120" class="absolute top-10 right-0 pointer-events-none" style="opacity: 0.5">
        <g fill="#c3cedb">
          <circle cx="10" cy="10" r="2" /><circle cx="30" cy="10" r="2" /><circle cx="50" cy="10" r="2" /><circle cx="70" cy="10" r="2" /><circle cx="90" cy="10" r="2" />
          <circle cx="10" cy="30" r="2" /><circle cx="30" cy="30" r="2" /><circle cx="50" cy="30" r="2" /><circle cx="70" cy="30" r="2" /><circle cx="90" cy="30" r="2" />
          <circle cx="10" cy="50" r="2" /><circle cx="30" cy="50" r="2" /><circle cx="50" cy="50" r="2" /><circle cx="70" cy="50" r="2" /><circle cx="90" cy="50" r="2" />
          <circle cx="10" cy="70" r="2" /><circle cx="30" cy="70" r="2" /><circle cx="50" cy="70" r="2" /><circle cx="70" cy="70" r="2" /><circle cx="90" cy="70" r="2" />
          <circle cx="10" cy="90" r="2" /><circle cx="30" cy="90" r="2" /><circle cx="50" cy="90" r="2" /><circle cx="70" cy="90" r="2" /><circle cx="90" cy="90" r="2" />
        </g>
      </svg>

      <svg width="420" height="260" viewBox="0 0 420 260" class="absolute bottom-0 left-0 pointer-events-none" style="opacity: 0.5">
        <polygon points="0,260 0,120 260,260" fill="#dbe4ee" />
      </svg>

      <div class="flex-1 flex items-center justify-center w-full px-4 relative z-10">
        <div
          class="w-full max-w-[480px] px-10 py-9"
          style="background: #ffffff; border-radius: 20px; box-shadow: 0 20px 50px -12px rgba(15, 42, 67, 0.15)"
        >
          <div class="flex items-center gap-2 mb-8 lg:hidden">
            <div
              class="w-6 h-6 rounded-full flex items-center justify-center shrink-0"
              style="background: #123a52"
            >
              <UIcon name="i-heroicons-plus" class="w-3.5 h-3.5 text-white" />
            </div>
            <span class="text-[15px] font-semibold" style="color: #111827">ERP Hospitalario</span>
          </div>

          <h1
            class="text-[32px] leading-tight mb-2"
            style="color: #111827; font-family: 'Lora', serif; font-weight: 500"
          >
            Iniciar sesión
          </h1>
          <p class="text-[15px] leading-snug mb-8" style="color: #64748b">
            Ingresa tus credenciales para acceder al panel hospitalario.
          </p>

          <div class="space-y-5">
            <div>
              <label class="block text-sm font-semibold mb-2" style="color: #111827">Correo electrónico</label>
              <div class="relative">
                <UIcon
                  name="i-heroicons-envelope"
                  class="w-4.5 h-4.5 absolute pointer-events-none"
                  style="color: #94a3b8; left: 14px; top: 50%; transform: translateY(-50%)"
                />
                <input
                  v-model="form.email"
                  type="email"
                  class="login-input"
                  placeholder="nombre@hospital.pe"
                  @keyup.enter="handleLogin"
                />
              </div>
            </div>

            <div>
              <div class="flex items-center justify-between mb-2">
                <label class="text-sm font-semibold" style="color: #111827">Contraseña</label>
                <NuxtLink to="/app/recuperar" class="text-sm font-medium hover:underline" style="color: #0f766e">
                  ¿Olvidaste tu contraseña?
                </NuxtLink>
              </div>
              <div class="relative">
                <UIcon
                  name="i-heroicons-lock-closed"
                  class="w-4.5 h-4.5 absolute pointer-events-none"
                  style="color: #94a3b8; left: 14px; top: 50%; transform: translateY(-50%)"
                />
                <input
                  v-model="form.password"
                  :type="showPassword ? 'text' : 'password'"
                  class="login-input"
                  style="padding-right: 2.75rem"
                  placeholder="Ingresa tu contraseña"
                  @keyup.enter="handleLogin"
                />
                <button
                  type="button"
                  class="absolute"
                  style="color: #94a3b8; right: 14px; top: 50%; transform: translateY(-50%)"
                  @click="showPassword = !showPassword"
                >
                  <UIcon :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4.5 h-4.5" />
                </button>
              </div>
            </div>
          </div>

          <div
            v-if="error"
            class="mt-4 text-sm rounded-lg px-3.5 py-2.5 flex items-center gap-2"
            style="background: #fef2f2; color: #b91c1c"
          >
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ error }}
          </div>

          <button
            class="w-full mt-7 py-3.5 rounded-xl text-[15px] font-semibold text-white flex items-center justify-center gap-2 transition-opacity disabled:opacity-70"
            style="background: #123a52"
            :disabled="loading"
            @click="handleLogin"
          >
            <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            <template v-else>
              Ingresar
              <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
            </template>
          </button>

          <p class="text-center text-sm mt-6" style="color: #64748b">
            ¿Necesitas ayuda?
            <NuxtLink to="/soporte" class="font-semibold hover:underline" style="color: #0f766e">
              Contacta a soporte
            </NuxtLink>
          </p>
        </div>
      </div>

      <div class="relative z-10 pb-8 text-center">
        <div class="flex items-center justify-center gap-6 text-sm mb-2" style="color: #94a3b8">
          <span class="flex items-center gap-1.5">
            <UIcon name="i-heroicons-shield-check" class="w-4 h-4" />
            Datos cifrados
          </span>
          <span class="flex items-center gap-1.5">
            <UIcon name="i-heroicons-server" class="w-4 h-4" />
            Infraestructura en la nube
          </span>
          <span class="flex items-center gap-1.5">
            <UIcon name="i-heroicons-clock" class="w-4 h-4" />
            Soporte 24/7
          </span>
        </div>
        <p class="text-xs" style="color: #cbd5e1">
          © 2026 ERP Hospitalario · <NuxtLink to="/terminos" class="hover:underline">Términos de uso</NuxtLink> · <NuxtLink to="/privacidad" class="hover:underline">Privacidad</NuxtLink>
        </p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

useHead({
  link: [
    { rel: 'preconnect', href: 'https://fonts.googleapis.com' },
    { rel: 'preconnect', href: 'https://fonts.gstatic.com', crossorigin: '' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Lora:wght@400;500;600&family=Inter:wght@400;500;600;700&display=swap' },
  ],
})

const { api } = useApi()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => (route.query.tenant as string) || '')

const form = reactive({
  email: '',
  password: '',
})

const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

onUnmounted(() => {
  document.documentElement.style.overflow = ''
  document.body.style.overflow = ''
})

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api<any>('/auth/login', {
      method: 'POST',
      tenant: tenantId.value,
      body: {
        email: form.email,
        password: form.password,
        panel: 'app',
      },
    })

    authStore.token = response.access_token
    authStore.refreshToken = response.refresh_token
    authStore.user = response.user

    router.push(`/app?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = apiErr(e, 'Credenciales incorrectas')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-input {
  width: 100%;
  height: 46px;
  padding-left: 2.75rem;
  padding-right: 1rem;
  border-radius: 10px;
  border: 1px solid #e2e8f0;
  background: #ffffff;
  font-size: 14px;
  color: #111827;
  outline: none;
  transition: border-color 0.15s;
}
.login-input::placeholder {
  color: #94a3b8;
}
.login-input:focus {
  border-color: #123a52;
}
</style>

<style>
html,
body {
  margin: 0;
  padding: 0;
  overflow: hidden;
}
</style>