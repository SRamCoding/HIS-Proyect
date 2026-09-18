<script setup lang="ts">
interface Notice {
  type?: 'warning' | 'success'
  text: string
}

const props = withDefaults(defineProps<{
  email: string
  password: string
  loading?: boolean
  error?: string
  title?: string
  intro?: string
  recuperarTo?: string | null
  soporteTo?: string
  notices?: Notice[]
  variant?: 'default' | 'sigarh' | 'hospital'
}>(), {
  loading: false,
  error: '',
  title: 'Iniciar sesión',
  intro: 'Ingresa tus credenciales para acceder al sistema.',
  recuperarTo: null,
  soporteTo: '/soporte',
  notices: () => [],
  variant: 'default',
})

const emit = defineEmits<{
  'update:email': [value: string]
  'update:password': [value: string]
  submit: []
}>()

const showPassword = ref(false)
const emailValido = computed(() => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(props.email))
const soporteEsMailto = computed(() => props.soporteTo.startsWith('mailto:'))
</script>

<template>
  <form class="login-card" :class="{ 'login-card--sigarh': variant !== 'default', 'login-card--hospital': variant === 'hospital' }" :aria-busy="loading" @submit.prevent="!loading && emit('submit')">
    <h2>{{ title }}</h2>
    <p class="intro">{{ intro }}</p>

    <p
      v-for="(n, i) in notices"
      :key="i"
      class="notice-message"
      :class="{ 'notice-message--success': n.type === 'success' }"
    >
      <UIcon aria-hidden="true" :name="n.type === 'success' ? 'i-heroicons-check-circle' : 'i-heroicons-exclamation-triangle'" class="w-4 h-4 shrink-0" />
      {{ n.text }}
    </p>

    <label for="auth-email">{{ variant !== 'default' ? 'Correo institucional' : 'Correo electrónico' }}</label>
    <div class="input-wrap">
      <UIcon aria-hidden="true" name="i-heroicons-envelope" class="input-icon" />
      <input
        id="auth-email"
        :value="email"
        type="email"
        autocomplete="email"
        placeholder="nombre@hospital.pe"
        required
        @input="emit('update:email', ($event.target as HTMLInputElement).value)"
      />
      <Transition name="pop">
        <UIcon aria-hidden="true" v-if="emailValido" name="i-heroicons-check-circle" class="input-check" />
      </Transition>
    </div>

    <div class="label-row">
      <label for="auth-password">Contraseña</label>
      <NuxtLink v-if="recuperarTo" :to="recuperarTo">¿Olvidaste tu contraseña?</NuxtLink>
    </div>
    <div class="input-wrap">
      <UIcon aria-hidden="true" name="i-heroicons-lock-closed" class="input-icon" />
      <input
        id="auth-password"
        :value="password"
        :type="showPassword ? 'text' : 'password'"
        autocomplete="current-password"
        placeholder="••••••••"
        required
        class="has-toggle"
        @input="emit('update:password', ($event.target as HTMLInputElement).value)"
      />
      <button
        type="button"
        class="toggle-btn"
        :aria-label="showPassword ? 'Ocultar contraseña' : 'Ver contraseña'"
        @click="showPassword = !showPassword"
      >
        <UIcon aria-hidden="true" :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" />
      </button>
    </div>

    <Transition name="pop">
      <p v-if="error" class="error-message" role="alert">
        <UIcon aria-hidden="true" name="i-heroicons-exclamation-circle" class="w-4 h-4 shrink-0" />
        {{ error }}
      </p>
    </Transition>

    <button class="submit" type="submit" :disabled="loading">
      <UIcon aria-hidden="true" v-if="loading" name="i-heroicons-arrow-path" class="w-4 h-4 spin" />
      <span>{{ loading ? 'Ingresando…' : variant === 'sigarh' ? 'Ingresar a SIGARH' : variant === 'hospital' ? 'Ingresar al sistema' : 'Ingresar' }}</span>
      <UIcon aria-hidden="true" v-if="!loading" name="i-heroicons-arrow-right" class="w-4 h-4" />
    </button>

    <p class="help">
      ¿Necesitas ayuda?
      <a v-if="soporteEsMailto" :href="soporteTo">{{ variant === 'sigarh' ? 'Contactar a Mesa de Ayuda' : 'Contacta a soporte' }}</a>
      <NuxtLink v-else :to="soporteTo">{{ variant === 'sigarh' ? 'Contactar a Mesa de Ayuda' : 'Contacta a soporte' }}</NuxtLink>
    </p>
    <div v-if="variant !== 'default'" class="security-row" aria-label="Seguridad y soporte">
      <div><UIcon name="i-heroicons-shield-check" aria-hidden="true" /><span>Acceso seguro</span></div>
      <div><UIcon :name="variant === 'hospital' ? 'i-heroicons-circle-stack' : 'i-heroicons-lock-closed'" aria-hidden="true" /><span>{{ variant === 'hospital' ? 'Datos protegidos' : 'Datos cifrados' }}</span></div>
      <a href="https://atencionalcliente.techquk.com/" target="_blank" rel="noopener noreferrer"><UIcon name="i-heroicons-phone" aria-hidden="true" /><span>Soporte 24/7</span></a>
    </div>
  </form>
</template>

<style scoped>
.login-card {
  width: min(100%, 420px);
  color: var(--ink);
  font-family: 'IBM Plex Sans', ui-sans-serif, system-ui, sans-serif;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  padding: 40px 36px;
  animation: card-enter 0.4s ease-out;
}

@keyframes card-enter {
  from { opacity: 0; transform: translateY(8px); }
  to { opacity: 1; transform: translateY(0); }
}

.login-card h2 {
  margin: 0 0 6px;
  font-size: 24px;
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
  transition: background 0.15s ease, transform 0.15s ease;
}
.submit:hover:not(:disabled) {
  background: var(--navy-hover);
  transform: translateY(-1px);
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

.login-card--sigarh {
  width: min(100%, 620px);
  padding: clamp(28px, 3.3vw, 52px);
  border: 1px solid #e2ebf1;
  border-radius: 22px;
  background: #fff;
  box-shadow: 0 18px 55px #0b3b5a08;
  font-family: inherit;
}
.login-card--sigarh h2 { color: #081d37; font-size: clamp(27px, 2.4vw, 40px); font-weight: 700; line-height: 1.2; letter-spacing: -.04em; }
.login-card--sigarh .intro { margin: 12px 0 34px; font-size: clamp(15px, 1.3vw, 20px); line-height: 1.5; }
.login-card--sigarh label { font-size: 16px; font-weight: 600; }
.login-card--sigarh .input-wrap { margin-bottom: 26px; }
.login-card--sigarh input { height: 62px; padding-left: 58px; padding-right: 44px; border-radius: 10px; border-color: #d6e3ec; background: linear-gradient(110deg, #f5f9fd, #eaf2fe); font-size: 16px; }
.login-card--sigarh .input-icon { left: 20px; width: 25px; height: 25px; color: #09617b; }
.login-card--sigarh .toggle-btn { width: 44px; height: 44px; color: #09617b; }
.login-card--sigarh .toggle-btn :deep(svg), .login-card--sigarh .toggle-btn :deep(span) { width: 24px; height: 24px; }
.login-card--sigarh .label-row { gap: 8px; flex-wrap: wrap; }
.login-card--sigarh .label-row a { margin-bottom: 8px; font-size: 13px; color: #007f88; }
.login-card--sigarh .submit { height: 64px; border-radius: 10px; background: #0b4562; font-size: 18px; gap: 14px; }
.login-card--sigarh .submit:hover:not(:disabled) { background: #105672; }
.login-card--sigarh .help { margin: 28px 0 0; font-size: 13px; line-height: 1.7; }
.login-card--sigarh .help a { font-size: inherit; color: #007f88; }
.login-card--sigarh :is(a, button):focus-visible { outline: 3px solid #009c9a; outline-offset: 4px; }
.security-row { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); margin: 32px -24px -24px; padding: 24px 0; background: #f2f8fc; border-radius: 18px; }
.security-row > * { display: flex; flex-direction: column; align-items: center; gap: 10px; text-align: center; color: #0b4562; font-size: 13px; text-decoration: none; }
.security-row > * + * { border-left: 1px solid #c7dce9; }
.security-row :deep(.iconify) { width: 27px; height: 27px; color: #00667b; }
@media (min-width: 768px) and (max-height: 800px) {
  .login-card--sigarh { padding: 28px; }
  .login-card--sigarh .intro { margin-bottom: 22px; }
  .login-card--sigarh .input-wrap { margin-bottom: 18px; }
  .login-card--sigarh .help { margin-top: 20px; }
  .security-row { margin: 22px -10px -10px; padding: 18px 0; }
}
@media (max-width: 767px) {
  .login-card--sigarh { padding: 28px 20px; border-radius: 18px; }
  .login-card--sigarh .intro { margin-bottom: 28px; }
  .login-card--sigarh label { font-size: 14px; }
  .login-card--sigarh .label-row a { font-size: 12px; }
  .security-row { margin: 28px -8px -12px; padding: 20px 0; }
  .security-row > * { font-size: 11px; }
}
.login-card--hospital { max-width: 590px; animation: none; }
.login-card--hospital h2 { font-size: clamp(32px, 2.5vw, 42px); }
.login-card--hospital .intro { font-size: 18px; }
.login-card--hospital .security-row { position: relative; margin-top: 44px; }
.login-card--hospital .security-row::before { content: ''; position: absolute; top: -20px; left: 0; right: 0; border-top: 1px solid #e1ebf1; }
.login-card--hospital .security-row > * { color: #5b7185; }
@media (max-width: 767px) {
  .login-card--hospital { padding: 24px 20px; box-shadow: none; }
  .login-card--hospital .intro { font-size: 15px; margin-bottom: 22px; }
  .login-card--hospital .input-wrap { margin-bottom: 18px; }
  .login-card--hospital input { height: 54px; }
  .login-card--hospital .submit { height: 54px; }
  .login-card--hospital .help { margin-top: 20px; }
  .login-card--hospital .security-row { margin-top: 32px; padding: 16px 0; }
  .login-card--hospital .security-row::before { top: -16px; }
}
@media (prefers-reduced-motion: reduce) {
  .login-card { animation: none; }
  .login-card *, .pop-enter-active, .pop-leave-active { transition: none; }
}
</style>
