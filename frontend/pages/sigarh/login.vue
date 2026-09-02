<template>
  <div class="min-h-screen flex items-center justify-center" style="background: var(--mist)">
    <div class="w-full max-w-sm p-8" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div class="flex items-center gap-2 mb-6">
        <div class="w-8 h-8 rounded flex items-center justify-center" style="background: var(--teal)">
          <span class="text-xs font-bold text-white">S</span>
        </div>
        <span class="font-semibold" style="color: var(--ink)">SIGARH</span>
      </div>

      <h1 class="text-base font-semibold mb-1" style="color: var(--ink)">Iniciar sesión</h1>
      <p class="text-sm mb-6" style="color: var(--ink-soft)">Panel de Recursos Humanos</p>

      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Correo electrónico</label>
          <input
            v-model="form.email"
            type="email"
            class="input-clinical"
            placeholder="sigarh@hospital.pe"
            @keyup.enter="handleLogin"
          />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Contraseña</label>
          <input
            v-model="form.password"
            type="password"
            class="input-clinical"
            @keyup.enter="handleLogin"
          />
        </div>
      </div>

      <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">
        {{ error }}
      </div>

      <button
        class="btn-primary w-full mt-6"
        :disabled="loading"
        @click="handleLogin"
      >
        {{ loading ? 'Ingresando...' : 'Ingresar' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: false })

const { api } = useApi()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.query.tenant as string || '')

const form = reactive({
  email: '',
  password: '',
})

const loading = ref(false)
const error = ref('')

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
</script>