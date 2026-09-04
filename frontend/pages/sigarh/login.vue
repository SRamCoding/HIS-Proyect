<!-- pages/sigarh/login.vue -->
<template>
  <div class="h-screen w-screen overflow-hidden flex" style="background: var(--mist)">

    <!-- Panel izquierdo: imagen a sangre completa -->
    <div class="hidden lg:block lg:w-[56%] h-full shrink-0">
      <img
        src="/sigarh.png"
        alt="Sistema Integral de Gestión y Administración de Recursos Humanos"
        class="w-full h-full object-cover block"
      />
    </div>

    <!-- Panel derecho: card completa con fondo decorativo -->
    <div class="flex-1 min-h-0 flex items-center justify-center p-4 lg:p-6 relative overflow-hidden">

      <!-- Cruces decorativas de fondo -->
      <svg class="absolute inset-0 w-full h-full pointer-events-none" style="opacity: 0.5" xmlns="http://www.w3.org/2000/svg">
        <g fill="var(--line)">
          <g transform="translate(60,50)"><rect x="-4" y="-16" width="8" height="32" rx="2"/><rect x="-16" y="-4" width="32" height="8" rx="2"/></g>
          <g transform="translate(90%,15%)" style="transform-box: fill-box"><rect x="-6" y="-22" width="12" height="44" rx="3"/><rect x="-22" y="-6" width="44" height="12" rx="3"/></g>
          <g transform="translate(85%,85%)" style="transform-box: fill-box"><rect x="-5" y="-18" width="10" height="36" rx="2"/><rect x="-18" y="-5" width="36" height="10" rx="2"/></g>
          <g transform="translate(8%,88%)"><rect x="-3.5" y="-13" width="7" height="26" rx="2"/><rect x="-13" y="-3.5" width="26" height="7" rx="2"/></g>
        </g>
      </svg>

      <div
        class="relative z-10 w-full max-w-lg px-9 py-8"
        style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)"
      >
        <!-- Logo SIGARH -->
        <div class="flex items-center gap-2.5 mb-7">
          <div
            class="w-9 h-9 rounded-lg flex items-center justify-center shrink-0"
            style="background: linear-gradient(135deg, var(--teal) 0%, var(--navy) 100%)"
          >
            <span class="text-sm font-bold text-white">S</span>
          </div>
          <span class="text-lg font-bold tracking-tight" style="color: var(--navy)">SIGARH</span>
        </div>

        <!-- Título -->
        <h1 class="text-2xl font-bold leading-tight mb-1.5" style="color: var(--navy)">Iniciar sesión</h1>
        <p class="text-sm leading-snug mb-7" style="color: var(--ink-soft)">
          Sistema Integral de Gestión y Administración de Recursos Humanos
        </p>

        <!-- Formulario -->
        <div class="space-y-4">
          <div>
            <label class="block text-xs font-semibold mb-1.5" style="color: var(--ink)">Correo electrónico</label>
            <div class="relative">
              <UIcon
                name="i-heroicons-envelope"
                class="w-4.5 h-4.5 absolute pointer-events-none"
                style="color: var(--ink-soft); left: 14px; top: 50%; transform: translateY(-50%)"
              />
              <input
                v-model="form.email"
                type="email"
                class="input-clinical"
                style="padding-left: 2.75rem"
                placeholder="tu.correo@hospital.pe"
                @keyup.enter="handleLogin"
              />
            </div>
          </div>

          <div>
            <label class="block text-xs font-semibold mb-1.5" style="color: var(--ink)">Contraseña</label>
            <div class="relative">
              <UIcon
                name="i-heroicons-lock-closed"
                class="w-4.5 h-4.5 absolute pointer-events-none"
                style="color: var(--ink-soft); left: 14px; top: 50%; transform: translateY(-50%)"
              />
              <input
                v-model="form.password"
                :type="showPassword ? 'text' : 'password'"
                class="input-clinical"
                style="padding-left: 2.75rem; padding-right: 2.75rem"
                placeholder="Ingresa tu contraseña"
                @keyup.enter="handleLogin"
              />
              <button
                type="button"
                class="absolute"
                style="color: var(--ink-soft); right: 14px; top: 50%; transform: translateY(-50%)"
                @click="showPassword = !showPassword"
              >
                <UIcon :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4.5 h-4.5" />
              </button>
            </div>
          </div>

          <div class="flex items-center justify-between pt-1">
            <label class="flex items-center gap-2 text-sm cursor-pointer select-none" style="color: var(--ink)">
              <input type="checkbox" v-model="form.remember" class="checkbox-clinical" />
              Recordarme
            </label>
            <NuxtLink to="/sigarh/recuperar" class="text-sm font-medium hover:underline" style="color: var(--teal)">
              ¿Olvidaste tu contraseña?
            </NuxtLink>
          </div>
        </div>

        <!-- Error -->
        <div
          v-if="error"
          class="mt-4 text-sm rounded-lg px-3.5 py-2.5 flex items-center gap-2"
          style="background: var(--alert-soft); color: var(--alert)"
        >
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
          {{ error }}
        </div>

        <!-- Botón principal -->
        <button
          class="w-full mt-6 py-3 rounded-lg text-sm font-semibold text-white flex items-center justify-center gap-2 transition-opacity disabled:opacity-70"
          style="background: linear-gradient(90deg, var(--teal) 0%, var(--navy) 100%)"
          :disabled="loading"
          @click="handleLogin"
        >
          <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
          <template v-else>
            Ingresar
            <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
          </template>
        </button>

        <!-- Divisor -->
        <div class="flex items-center gap-3 my-5">
          <div class="flex-1 h-px" style="background: var(--line)" />
          <span class="text-xs shrink-0" style="color: var(--ink-soft)">o continúa con</span>
          <div class="flex-1 h-px" style="background: var(--line)" />
        </div>

        <!-- Microsoft -->
        <button
          class="w-full py-3 rounded-lg text-sm font-medium flex items-center justify-center gap-2.5 transition-colors hover:bg-black/[0.02]"
          style="border: 1px solid var(--line); color: var(--ink)"
          type="button"
          @click="handleMicrosoftLogin"
        >
          <svg width="16" height="16" viewBox="0 0 21 21" xmlns="http://www.w3.org/2000/svg">
            <rect x="1" y="1" width="9" height="9" fill="#f25022" />
            <rect x="11" y="1" width="9" height="9" fill="#7fba00" />
            <rect x="1" y="11" width="9" height="9" fill="#00a4ef" />
            <rect x="11" y="11" width="9" height="9" fill="#ffb900" />
          </svg>
          Iniciar sesión con Microsoft
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { api } = useApi()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => (route.query.tenant as string) || '')

const form = reactive({
  email: '',
  password: '',
  remember: false,
})

const loading = ref(false)
const error = ref('')
const showPassword = ref(false)

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api<any>('/auth/login', {
      method: 'POST',
      body: {
        email: form.email,
        password: form.password,
        panel: 'sigarh',
      },
    })

    authStore.token = response.access_token
    authStore.refreshToken = response.refresh_token
    authStore.user = response.user

    router.push(`/sigarh?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Credenciales incorrectas'
  } finally {
    loading.value = false
  }
}

const handleMicrosoftLogin = () => {
  // TODO: integrar flujo OAuth de Microsoft
}
</script>

<style scoped>
.checkbox-clinical {
  width: 16px;
  height: 16px;
  border-radius: 4px;
  border: 1px solid var(--line);
  accent-color: var(--teal);
  cursor: pointer;
}
</style>