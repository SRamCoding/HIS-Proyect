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

    // El access_token y el refresh_token ya llegaron como cookies httpOnly
    // (ver backend/app/auth/router.py) -- no hay nada que leer del body ni
    // guardar en el store aparte de los datos del usuario.
    authStore.user = response.user

    useToast().add({
      title: 'Login exitoso',
      description: `${roleLabel(response.user?.role)} — bienvenido, ${response.user?.name}`,
      color: 'success',
    })

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
