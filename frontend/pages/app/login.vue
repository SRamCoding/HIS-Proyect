<!-- frontend/pages/app/login.vue -->
<script setup lang="ts">
definePageMeta({ layout: 'hospital-auth' })

const { api } = useApi()
const authStore = useAuthStore()
const router = useRouter()

const { tenantId, hospital, pending, brandingError } = useHospitalBranding()
const loginDisabled = computed(() => pending.value || !!brandingError.value || hospital.value?.is_active === false)

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

const handleLogin = async () => {
  if (loading.value || loginDisabled.value) return
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

    // El access_token y el refresh_token ya llegaron como cookies httpOnly
    // (ver backend/app/auth/router.py) -- no hay nada que leer del body ni
    // guardar en el store aparte de los datos del usuario.
    authStore.user = response.user

    useToast().add({
      title: 'Login exitoso',
      description: `${roleLabel(response.user?.role)} — bienvenido, ${response.user?.name}`,
      color: 'success',
    })

    const resolvedTenant = response.user?.tenant_id || tenantId.value
    router.push(resolvedTenant ? `/app?tenant=${resolvedTenant}` : '/app')
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
    :disabled="loginDisabled"
    :error="error"
    intro="Accede al sistema de gestión hospitalaria"
    :recuperar-to="tenantId ? `/app/recuperar?tenant=${tenantId}` : '/app/recuperar'"
    @submit="handleLogin"
  />
</template>
