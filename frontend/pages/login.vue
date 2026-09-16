<script setup lang="ts">
definePageMeta({ layout: 'auth' })

const authStore = useAuthStore()
const route = useRoute()
const avisoLogout = computed(() => route.query.aviso === 'logout_sin_confirmar')
const avisoPasswordCambiada = computed(() => route.query.aviso === 'password_cambiada')

const email = ref('')
const password = ref('')
const showPassword = ref(false)
const loading = ref(false)
const error = ref('')

const emailValido = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.value))

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
  <form class="login-card" @submit.prevent="signIn">
    <div class="form-brand">
      <span class="form-brand__icon"><UIcon name="i-heroicons-plus" class="w-3 h-3" /></span>
      ERP Hospitalario
    </div>
    <h2>Iniciar sesión</h2>
    <p class="intro">Ingresa tus credenciales para acceder al sistema.</p>

    <p v-if="avisoLogout" class="notice-message">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      Se cerró la sesión en este navegador, pero el servidor no pudo confirmar la revocación. Si usaste un equipo compartido, cambia tu contraseña por seguridad.
    </p>

    <p v-if="avisoPasswordCambiada" class="notice-message notice-message--success">
      <UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />
      Tu contraseña se actualizó correctamente. Vuelve a iniciar sesión con tu nueva contraseña.
    </p>

    <label for="email">Correo electrónico</label>
    <div class="input-wrap">
      <UIcon name="i-heroicons-envelope" class="input-icon" />
      <input
        id="email"
        v-model="email"
        type="email"
        autocomplete="email"
        placeholder="nombre@hospital.pe"
        required
      />
      <Transition name="pop">
        <UIcon v-if="emailValido" name="i-heroicons-check-circle" class="input-check" />
      </Transition>
    </div>

    <div class="label-row">
      <label for="password">Contraseña</label>
      <a href="#" @click.prevent>¿Olvidaste tu contraseña?</a>
    </div>
    <div class="input-wrap">
      <UIcon name="i-heroicons-lock-closed" class="input-icon" />
      <input
        id="password"
        v-model="password"
        :type="showPassword ? 'text' : 'password'"
        autocomplete="current-password"
        placeholder="••••••••"
        required
        class="has-toggle"
      />
      <button
        type="button"
        class="toggle-btn"
        :aria-label="showPassword ? 'Ocultar contraseña' : 'Ver contraseña'"
        @click="showPassword = !showPassword"
      >
        <UIcon :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" />
      </button>
    </div>

    <Transition name="pop">
      <p v-if="error" class="error-message">
        <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 shrink-0" />
        {{ error }}
      </p>
    </Transition>

    <button class="submit" type="submit" :disabled="loading">
      <UIcon v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 spin" />
      <span>{{ loading ? 'Ingresando…' : 'Ingresar' }}</span>
      <UIcon v-if="!loading" name="i-heroicons-arrow-right" class="w-4 h-4" />
    </button>

    <p class="help">¿Necesitas ayuda? <a href="mailto:soporte@hospital.pe">Contacta a soporte</a></p>
  </form>
</template>

<style scoped>
.login-card {
  width: min(100%, 460px);
  color: var(--ink);
  font-family: 'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif;
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 44px 44px;
  animation: card-enter 0.5s ease-out;
}

@keyframes card-enter {
  from { opacity: 0; transform: translateY(14px); }
  to { opacity: 1; transform: translateY(0); }
}

.form-brand {
  display: flex;
  align-items: center;
  gap: 6px;
  color: var(--navy);
  font-size: 13px;
  font-weight: 750;
}
.form-brand__icon {
  display: inline-grid;
  place-items: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  background: var(--navy);
  color: white;
}
.login-card h2 {
  margin: 26px 0 6px;
  font-size: 26px;
  letter-spacing: -.03em;
  color: var(--ink);
}
.intro {
  margin: 0 0 28px;
  color: var(--ink-soft);
  font-size: 13px;
}
.login-card label {
  display: block;
  margin: 0 0 8px;
  color: var(--ink);
  font-size: 12px;
  font-weight: 650;
}
.input-wrap {
  position: relative;
  margin-bottom: 20px;
}
.input-wrap input {
  box-sizing: border-box;
  width: 100%;
  height: 48px;
  border: 1px solid var(--line);
  border-radius: var(--radius);
  outline: 0;
  padding: 0 14px 0 42px;
  color: var(--ink);
  background: var(--paper);
  font: inherit;
  font-size: 13px;
  transition: border-color .2s ease, box-shadow .2s ease;
}
.input-wrap input.has-toggle {
  padding-right: 44px;
}
.input-wrap input:hover {
  border-color: #bacbd0;
}
.input-wrap input:focus {
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}
.input-icon {
  position: absolute;
  top: 50%;
  left: 14px;
  width: 18px;
  height: 18px;
  color: var(--ink-soft);
  pointer-events: none;
  transform: translateY(-50%);
  transition: color 0.2s ease;
}
.input-wrap input:focus ~ .input-icon {
  color: var(--teal);
}
.input-check {
  position: absolute;
  top: 50%;
  right: 14px;
  width: 18px;
  height: 18px;
  color: var(--ok);
  transform: translateY(-50%);
}
.label-row {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
}
.label-row a, .help a {
  color: var(--teal);
  text-decoration: none;
  font-size: 11px;
  font-weight: 600;
}
.label-row a:hover, .help a:hover {
  text-decoration: underline;
}
.toggle-btn {
  position: absolute;
  top: 50%;
  right: 6px;
  width: 34px;
  height: 34px;
  display: grid;
  place-items: center;
  border: 0;
  border-radius: 8px;
  background: none;
  color: var(--ink-soft);
  cursor: pointer;
  transform: translateY(-50%);
  transition: background 0.15s ease, color 0.15s ease;
}
.toggle-btn:hover {
  background: var(--mist);
  color: var(--teal);
}
.error-message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: -6px 0 16px;
  padding: 10px 12px;
  border-radius: var(--radius);
  background: var(--alert-soft);
  color: var(--alert);
  font-size: 12px;
  line-height: 1.4;
}
.notice-message {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  margin: 0 0 20px;
  padding: 10px 12px;
  border-radius: var(--radius);
  background: var(--amber-soft);
  color: var(--amber);
  font-size: 12px;
  line-height: 1.4;
}
.notice-message--success {
  background: var(--green-soft, #ecfdf5);
  color: var(--green, #16a34a);
}
.submit {
  width: 100%;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border: 0;
  border-radius: var(--radius);
  background: var(--navy);
  color: #fff;
  font: inherit;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  box-shadow: 0 5px 12px rgba(11, 95, 168, 0.22);
  transition: background 0.15s ease, transform 0.15s ease, box-shadow 0.15s ease;
}
.submit:hover:not(:disabled) {
  background: var(--navy-hover);
  transform: translateY(-1px);
  box-shadow: 0 8px 16px rgba(11, 95, 168, 0.28);
}
.submit:active:not(:disabled) {
  transform: translateY(0);
}
.submit:disabled {
  cursor: wait;
  opacity: .72;
}
.spin {
  animation: spin 0.8s linear infinite;
}
@keyframes spin {
  to { transform: rotate(360deg); }
}
.help {
  margin: 22px 0 0;
  text-align: center;
  color: var(--ink-soft);
  font-size: 11px;
}

.pop-enter-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.pop-enter-from {
  opacity: 0;
  transform: scale(0.85);
}
.pop-leave-active {
  transition: opacity 0.15s ease;
}
.pop-leave-to {
  opacity: 0;
}
</style>