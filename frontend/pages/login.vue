<!-- pages/login.vue -->
<template>
  <div>
    <h1 class="text-xl font-semibold mb-1" style="color: var(--ink)">Iniciar sesión</h1>
    <p class="text-sm mb-7" style="color: var(--ink-soft)">
      Ingresa con tus credenciales institucionales.
    </p>

    <form @submit.prevent="handleLogin" class="space-y-4">
      <div>
        <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">
          Correo electrónico
        </label>
        <input
          v-model="form.email"
          type="email"
          required
          placeholder="nombre@hospital.gob.pe"
          class="input-clinical"
        />
      </div>

      <div>
        <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">
          Contraseña
        </label>
        <input
          v-model="form.password"
          type="password"
          required
          placeholder="••••••••"
          class="input-clinical"
        />
      </div>

      <div
        v-if="error"
        class="text-sm rounded px-3 py-2"
        style="background: var(--alert-soft); color: var(--alert)"
      >
        {{ error }}
      </div>

      <button type="submit" :disabled="loading" class="btn-primary w-full">
        {{ loading ? 'Ingresando…' : 'Ingresar' }}
      </button>
    </form>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const authStore = useAuthStore()
const form = reactive({ email: '', password: '', panel: 'admin' })
const error = ref('')
const loading = ref(false)

const handleLogin = async () => {
  error.value = ''
  loading.value = true
  try {
    await authStore.login(form)
    await navigateTo(authStore.panelRoute)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Credenciales inválidas'
  } finally {
    loading.value = false
  }
}
</script>