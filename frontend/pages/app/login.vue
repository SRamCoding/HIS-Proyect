<!-- frontend/pages/app/login.vue -->
<script setup lang="ts">
definePageMeta({ layout: 'hospital-auth' })

const { api } = useApi()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => (route.query.tenant as string) || '')

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await api<any>('/auth/login', {
      method: 'POST',
      tenant: tenantId.value,
      body: {
        email: email.value,
        password: password.value,
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

<template>
  <AuthLoginForm
    variant="hospital"
    title="Bienvenido"
    v-model:email="email"
    v-model:password="password"
    :loading="loading"
    :error="error"
    intro="Accede al sistema de gestión hospitalaria"
    recuperar-to="/app/recuperar"
    @submit="handleLogin"
  />
</template>
