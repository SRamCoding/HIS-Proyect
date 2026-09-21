<!-- pages/sigarh/login.vue -->
<script setup lang="ts">
definePageMeta({ layout: 'sigarh-auth' })

const { api } = useApi()
const authStore = useAuthStore()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => (route.query.tenant as string) || '')

const notices = computed(() => {
  if (route.query.aviso === 'logout_sin_confirmar') {
    return [{
      type: 'warning' as const,
      text: 'Se cerró la sesión en este navegador, pero el servidor no pudo confirmar la revocación. Si usaste un equipo compartido, cambia tu contraseña por seguridad.',
    }]
  }
  return []
})

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
        panel: 'sigarh',
      },
    })

    // El access_token y el refresh_token ya llegaron como cookies httpOnly
    // (ver backend/app/auth/router.py) -- no hay nada que leer del body ni
    // guardar en el store aparte de los datos del usuario.
    authStore.user = response.user

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
    :error="error"
    :notices="notices"
    recuperar-to="/sigarh/recuperar"
    @submit="handleLogin"
  />
</template>
