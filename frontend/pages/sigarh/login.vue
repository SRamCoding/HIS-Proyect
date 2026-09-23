<!-- pages/sigarh/login.vue -->
<script setup lang="ts">
definePageMeta({ layout: 'sigarh-auth' })

const { api } = useApi()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const { tenantId, hospital, pending, brandingError } = useHospitalBranding()
const loginDisabled = computed(() => pending.value || !!brandingError.value || hospital.value?.is_active === false)

const notices = computed(() => {
  if (route.query.aviso === 'logout_sin_confirmar') {
    return [{
      type: 'warning' as const,
      text: 'Se cerró la sesión en este navegador, pero el servidor no pudo confirmar la revocación. Si usaste un equipo compartido, cambia tu contraseña por seguridad.',
    }]
  }
  if (route.query.aviso === 'password_cambiada') {
    return [{ type: 'success' as const, text: 'Tu contraseña se actualizó correctamente. Vuelve a iniciar sesión con tu nueva contraseña.' }]
  }
  return []
})

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
        panel: 'sigarh',
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

    const resolvedTenant = tenantId.value || response.user?.tenant_id || ''
    router.push(resolvedTenant ? `/sigarh?tenant=${resolvedTenant}` : '/sigarh')
  } catch (e: any) {
    error.value = apiErr(e, 'Credenciales incorrectas')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLoginForm
    variant="sigarh"
    title="Bienvenido a SIGARH"
    intro="Accede con tus credenciales institucionales"
    v-model:email="email"
    v-model:password="password"
    :loading="loading"
    :disabled="loginDisabled"
    :error="error"
    :notices="notices"
    :recuperar-to="tenantId ? `/sigarh/recuperar?tenant=${tenantId}` : '/sigarh/recuperar'"
    @submit="handleLogin"
  />
</template>
