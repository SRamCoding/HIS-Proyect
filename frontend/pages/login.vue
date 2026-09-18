<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const authStore = useAuthStore()
const route = useRoute()

const notices = computed(() => {
  const items: { type?: 'warning' | 'success'; text: string }[] = []
  if (route.query.aviso === 'logout_sin_confirmar') {
    items.push({
      type: 'warning',
      text: 'Se cerró la sesión en este navegador, pero el servidor no pudo confirmar la revocación. Si usaste un equipo compartido, cambia tu contraseña por seguridad.',
    })
  }
  if (route.query.aviso === 'password_cambiada') {
    items.push({ type: 'success', text: 'Tu contraseña se actualizó correctamente. Vuelve a iniciar sesión con tu nueva contraseña.' })
  }
  return items
})

const email = ref('')
const password = ref('')
const loading = ref(false)
const error = ref('')

async function signIn() {
  loading.value = true
  error.value = ''
  try {
    await authStore.login({ email: email.value, password: password.value, panel: 'admin' })
    await navigateTo(authStore.panelRoute)
  } catch (e: any) {
    error.value = apiErr(e, 'No pudimos validar tus credenciales. Inténtalo nuevamente.')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <AuthLoginForm
    v-model:email="email"
    v-model:password="password"
    :loading="loading"
    :error="error"
    :notices="notices"
    soporte-to="mailto:soporte@hospital.pe"
    @submit="signIn"
  />
</template>
