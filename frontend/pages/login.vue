<script setup lang="ts">
definePageMeta({ layout: false })
useHead({ title: 'Acceso administrativo · ERP Hospitalario Central' })

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
const showPassword = ref(false)
// MFA (TOTP) es obligatorio para el panel admin -- ver backend/app/auth/
// router.py. `mfaState` no-null significa "la contraseña ya se validó,
// falta el segundo factor"; `setup` distingue la primera vez (hay que
// escanear el QR) de un login normal (solo pide el código).
const mfaState = ref<{ setup: boolean; qr: string | null; secret: string | null } | null>(null)
const mfaCode = ref('')
const rememberEmail = ref(false)
const info = ref<'recovery' | 'terms' | 'privacy' | null>(null)
const infoDialog = ref<HTMLDialogElement | null>(null)
const infoTitles = { recovery: 'Recuperar acceso', terms: 'Términos de uso', privacy: 'Privacidad' }
const storageKey = 'erp-admin-remembered-email'
onMounted(() => {
  try {
    const remembered = localStorage.getItem(storageKey)
    if (remembered) { email.value = remembered; rememberEmail.value = true }
  } catch { /* El acceso funciona también con almacenamiento bloqueado. */ }
})
watch(rememberEmail, (enabled) => {
  if (!enabled) { try { localStorage.removeItem(storageKey) } catch {} }
})
async function openInfo(kind: 'recovery' | 'terms' | 'privacy') {
  info.value = kind
  await nextTick()
  infoDialog.value?.showModal()
}

async function finalizarLogin() {
  try {
    if (rememberEmail.value) localStorage.setItem(storageKey, email.value)
    else localStorage.removeItem(storageKey)
  } catch { /* No impedir el inicio de sesión por almacenamiento local. */ }
  // Punto único de "login realmente completo": lo llaman tanto signIn() (sin
  // MFA) como verificarMfa() (segundo factor ya validado) -- el toast va acá
  // para no disparar antes de tiempo cuando todavía falta el código TOTP.
  useToast().add({
    title: 'Login exitoso',
    description: `${roleLabel(authStore.user?.role)} — bienvenido, ${authStore.user?.name}`,
    color: 'success',
  })
  await navigateTo(authStore.panelRoute)
}

async function signIn() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    const response = await authStore.login({ email: email.value, password: password.value, panel: 'admin' })
    if (response.mfa_required) {
      mfaState.value = {
        setup: !!response.mfa_setup,
        qr: response.qr_png_base64 || null,
        secret: response.secret || null,
      }
    } else {
      await finalizarLogin()
    }
  } catch (e: any) {
    error.value = apiErr(e, 'No pudimos validar tus credenciales. Inténtalo nuevamente.')
  } finally {
    loading.value = false
  }
}

async function verificarMfa() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    await authStore.mfaVerify(mfaCode.value)
    await finalizarLogin()
  } catch (e: any) {
    error.value = apiErr(e, 'Código incorrecto o expirado.')
    mfaCode.value = ''
  } finally {
    loading.value = false
  }
}

function volverAlPaso1() {
  mfaState.value = null
  mfaCode.value = ''
  error.value = ''
}
</script>

<template>
  <main class="admin-access">
    <AdminLoginScene />
    <section class="access-side" aria-labelledby="access-title">
      <svg class="network-background" viewBox="0 0 680 940" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
        <defs><pattern id="admin-grid" width="64" height="64" patternUnits="userSpaceOnUse"><path d="M64 0H0V64" fill="none" stroke="white" stroke-opacity=".2" /></pattern></defs>
        <rect width="680" height="940" fill="url(#admin-grid)" />
        <g fill="none" stroke="#fff" stroke-opacity=".46"><path d="M0 110Q180 -80 390 85T680 30M0 420Q180 145 420 235T680 160M0 720Q120 490 380 565T680 710M0 920Q230 710 480 840T680 865M40 0Q135 380 45 940M235 0Q130 340 360 940M490 0Q410 340 620 940M660 0Q490 370 660 940"/><path d="M0 200L680 570M0 590L680 100M0 850L680 415"/></g>
        <g fill="#efffff"><circle v-for="(p,i) in [[48,70],[105,42],[224,25],[342,28],[548,90],[660,183],[22,408],[178,299],[383,237],[657,455],[55,640],[343,574],[660,723],[48,900],[371,868]]" :key="i" :cx="p[0]" :cy="p[1]" r="4" /></g>
      </svg>
      <div class="platform-status"><span aria-hidden="true" />Plataforma central</div>
      <div class="access-card">
        <div class="portal-label"><span><UIcon name="i-heroicons-lock-closed" aria-hidden="true" /></span>PORTAL ADMINISTRATIVO</div>
        <template v-if="!mfaState">
          <h2 id="access-title">Acceso al ERP</h2><p class="access-intro">Ingresa con tu cuenta de administración central.</p>
          <form :aria-busy="loading" @submit.prevent="signIn">
            <p v-for="(notice,i) in notices" :key="i" class="notice" :class="{success:notice.type === 'success'}" role="status">{{ notice.text }}</p>
            <div class="field-group"><label for="admin-email">Correo corporativo</label><div class="field-shell email-shell"><UIcon name="i-heroicons-envelope" aria-hidden="true" /><input id="admin-email" v-model="email" type="email" autocomplete="username" inputmode="email" spellcheck="false" autocapitalize="none" placeholder="admin@erp-hospitalario.pe" required :disabled="loading" /></div></div>
            <div class="field-group password-group"><label for="admin-password">Contraseña</label><div class="field-shell"><UIcon name="i-heroicons-lock-closed" aria-hidden="true" /><input id="admin-password" v-model="password" :type="showPassword ? 'text' : 'password'" autocomplete="current-password" placeholder="•••••••••" required :disabled="loading" /><button class="password-toggle" type="button" :aria-label="showPassword ? 'Ocultar contraseña' : 'Mostrar contraseña'" :aria-pressed="showPassword" @click="showPassword = !showPassword"><UIcon :name="showPassword ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" aria-hidden="true" /></button></div></div>
            <div class="form-options"><label class="remember" title="Recuerda solo tu correo en este dispositivo, nunca tu contraseña ni la sesión."><input v-model="rememberEmail" type="checkbox" :disabled="loading" />Recordarme<span class="sr-only">: guardar solo el correo en este dispositivo</span></label><button type="button" class="text-link" @click="openInfo('recovery')">¿Olvidaste tu contraseña?</button></div>
            <p v-if="error" class="notice error" role="alert">{{ error }}</p>
            <button class="sign-in" type="submit" :disabled="loading"><span>{{ loading ? 'Ingresando…' : 'Ingresar al sistema' }}</span><UIcon :name="loading ? 'i-heroicons-arrow-path' : 'i-heroicons-arrow-right'" :class="{ spinning: loading }" aria-hidden="true" /></button>
          </form>
        </template>

        <template v-else>
          <h2 id="access-title">Verificación en dos pasos</h2>
          <p class="access-intro">{{ mfaState.setup ? 'Configura tu app de autenticación (Google Authenticator, Authy u otra compatible con TOTP) antes de continuar.' : 'Ingresa el código de 6 dígitos de tu app de autenticación.' }}</p>
          <form :aria-busy="loading" @submit.prevent="verificarMfa">
            <div v-if="mfaState.setup" class="mfa-setup">
              <img v-if="mfaState.qr" class="mfa-qr" :src="`data:image/png;base64,${mfaState.qr}`" alt="Código QR para configurar la app de autenticación" width="180" height="180" />
              <p class="mfa-secret-label">¿No puedes escanear? Ingresa este código manualmente:</p>
              <code class="mfa-secret">{{ mfaState.secret }}</code>
            </div>
            <div class="field-group password-group">
              <label for="mfa-code">Código de verificación</label>
              <div class="field-shell"><UIcon name="i-heroicons-device-phone-mobile" aria-hidden="true" /><input id="mfa-code" v-model="mfaCode" type="text" inputmode="numeric" pattern="\d{6}" maxlength="6" autocomplete="one-time-code" placeholder="000000" required :disabled="loading" /></div>
            </div>
            <p v-if="error" class="notice error" role="alert">{{ error }}</p>
            <button class="sign-in" type="submit" :disabled="loading || mfaCode.length !== 6"><span>{{ loading ? 'Verificando…' : 'Verificar y continuar' }}</span><UIcon :name="loading ? 'i-heroicons-arrow-path' : 'i-heroicons-arrow-right'" :class="{ spinning: loading }" aria-hidden="true" /></button>
            <button type="button" class="text-link mfa-back" @click="volverAlPaso1">Volver</button>
          </form>
        </template>
        <div class="help-line"><span>¿Necesitas ayuda? <a href="https://atencionalcliente.techquk.com/" target="_blank" rel="noopener noreferrer">Contacta a soporte</a></span></div>
        <div class="security-message"><UIcon name="i-heroicons-shield-check" aria-hidden="true" /><span>Acceso administrativo seguro y protegido</span></div>
      </div>
      <footer class="access-footer"><span>© {{ new Date().getFullYear() }} ERP Hospitalario Central</span><span aria-hidden="true">·</span><button type="button" @click="openInfo('terms')">Términos de uso</button><span aria-hidden="true">·</span><button type="button" @click="openInfo('privacy')">Privacidad</button></footer>
    </section>
    <dialog ref="infoDialog" class="access-dialog" @click="($event.target === infoDialog) && infoDialog?.close()"><div v-if="info"><h2>{{ infoTitles[info] }}</h2><p v-if="info === 'recovery'">Para recuperar tu acceso administrativo, contacta con soporte y solicita el procedimiento de recuperación. No compartas tu contraseña.</p><p v-else>Solicita a la administración la versión vigente de {{ info === 'terms' ? 'los términos de uso' : 'la política de privacidad' }} de esta plataforma.</p><a href="https://atencionalcliente.techquk.com/" target="_blank" rel="noopener noreferrer">Contactar a soporte ↗</a><button type="button" class="dialog-close" autofocus @click="infoDialog?.close()">Cerrar</button></div></dialog>
  </main>
</template>

<style scoped>
.admin-access{display:grid;grid-template-columns:minmax(0,1.2fr) minmax(440px,1fr);min-height:100svh;background:#f3f6f8;font-family:Inter,Arial,sans-serif;color:#203447;line-height:1.5}
.admin-access *{box-sizing:border-box}
.access-side{position:relative;isolation:isolate;display:flex;flex-direction:column;align-items:center;gap:24px;min-width:0;min-height:100svh;padding:24px clamp(24px,3.2vw,64px);background:linear-gradient(145deg,#f8fafb,#edf2f5);border-left:1px solid #dce5eb}
.network-background{position:absolute;inset:0;width:100%;height:100%;z-index:-1;pointer-events:none;opacity:.18}
.platform-status{align-self:flex-end;display:flex;align-items:center;gap:8px;font-size:12px;font-weight:500;color:#607281}
.platform-status>span{width:7px;height:7px;border-radius:50%;background:#239b72}
.access-card{width:100%;max-width:480px;margin:auto 0;padding:32px;border:1px solid #e0e7ec;border-radius:20px;background:#fff;box-shadow:0 12px 40px #20344709,0 2px 6px #20344704}
.portal-label{display:inline-flex;align-items:center;gap:8px;color:#39767d;font-size:10px;font-weight:700;letter-spacing:.1em}
.portal-label>span{width:30px;height:30px;display:grid;place-items:center;border-radius:9px;background:#edf5f5}
.portal-label :deep(.iconify){width:17px;height:17px}
.access-card h2{font-size:34px;font-weight:750;letter-spacing:-.045em;line-height:1.15;margin:22px 0 9px;color:#172e40}
.access-intro{font-size:14px;line-height:1.6;color:#72818e;margin:0 0 27px;max-width:340px}
.field-group label{display:block;font-size:13px;font-weight:600;margin-bottom:8px;color:#314758}
.field-shell{position:relative;display:flex;align-items:center;height:50px;border:1px solid #dce3e9;border-radius:9px;background:#fafbfc;color:#7c8d9b;transition:box-shadow .18s,border-color .18s}
.field-shell:focus-within{border-color:#38868d;background:#fff;box-shadow:0 0 0 3px #38868d14}
.field-shell>:deep(.iconify){position:absolute;left:15px;width:20px;height:20px;pointer-events:none}
.field-shell input{width:100%;min-width:0;height:48px;padding:0 46px 0 44px;border:0;outline:0!important;background:transparent;color:#243b4c;font:inherit;font-size:16px;box-shadow:none}
.field-shell input::placeholder{color:#95a1ac;opacity:1}
.password-group{margin-top:19px}
.password-toggle{position:absolute;right:3px;display:grid;place-items:center;width:44px;height:44px;border:0;border-radius:7px;background:transparent;color:#7a8c9a;cursor:pointer}
.password-toggle :deep(.iconify){width:20px;height:20px}
.password-toggle:hover{background:#edf2f5}
.form-options{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;margin:20px 0 24px;font-size:12px}
.remember{display:flex;align-items:center;gap:8px;cursor:pointer;color:#637381}
.remember input{width:16px;height:16px;margin:0;accent-color:#247980;cursor:pointer}
.text-link,.access-footer button{font:inherit;cursor:pointer;background:none;border:0;padding:0}
.text-link{color:#287880;font-weight:600}
.text-link:hover,.help-line a:hover,.access-footer button:hover{text-decoration:underline}
.sign-in{display:flex;align-items:center;justify-content:center;gap:12px;width:100%;min-height:50px;padding:12px 18px;border:1px solid #226d76;border-radius:9px;background:#267781;box-shadow:0 3px 7px #1c536912;color:#fff;font:inherit;font-size:14px;font-weight:600;cursor:pointer;transition:background .18s}
.sign-in:hover:not(:disabled){background:#1e626d}
.sign-in:disabled{cursor:wait;opacity:.72}
.sign-in :deep(.iconify){width:20px;height:20px}
.help-line{margin:22px 0 20px;text-align:center;font-size:12px;line-height:1.8;color:#7d8b97}
.help-line a{color:#287880;font-weight:600;text-decoration:none}
.security-message{display:flex;align-items:center;justify-content:center;gap:8px;padding-top:18px;border-top:1px solid #edf0f3;color:#87949f;font-size:11px;text-align:center}
.security-message :deep(.iconify){width:17px;height:17px;color:#5c8b8e;flex-shrink:0}
.access-footer{display:flex;flex-wrap:wrap;justify-content:center;align-items:center;gap:8px 12px;width:100%;font-size:10px;color:#8795a0;text-align:center}
.access-footer button{color:inherit}
.mfa-setup{display:flex;flex-direction:column;align-items:center;gap:10px;margin:0 0 20px;padding:20px;border:1px solid #e0e7ec;border-radius:12px;background:#fafbfc}
.mfa-qr{width:180px;height:180px;border-radius:8px;background:#fff;padding:8px;border:1px solid #e0e7ec}
.mfa-secret-label{margin:4px 0 0;font-size:12px;color:#72818e;text-align:center}
.mfa-secret{font-family:'IBM Plex Mono',ui-monospace,monospace;font-size:13px;letter-spacing:.05em;padding:8px 12px;border-radius:7px;background:#edf2f5;color:#243b4c;word-break:break-all;text-align:center}
.mfa-back{display:block;margin:14px auto 0}
#mfa-code{letter-spacing:.3em;font-family:'IBM Plex Mono',ui-monospace,monospace;text-align:center}
.notice{padding:12px 14px;margin:0 0 18px;font-size:13px;line-height:1.5;border:1px solid #d9b967;border-radius:8px;background:#fff7dc;color:#72571e}
.notice.success{color:#146354;background:#e7faf3;border-color:#90cbb7}
.notice.error{color:#9f2636;background:#fff0f2;border-color:#ecb4bc}
.access-dialog{margin:auto;max-width:min(450px,calc(100vw - 32px));padding:30px;border:1px solid #dce3e9;border-radius:18px;color:#203447;background:#fff;box-shadow:0 20px 80px #001b4266}
.access-dialog::backdrop{background:#10263777;backdrop-filter:blur(5px)}
.access-dialog h2{font-size:24px;margin:0 0 15px}
.access-dialog p{font-size:15px;line-height:1.6}
.access-dialog a{color:#287880}
.dialog-close{display:block;margin:24px 0 0 auto;padding:9px 25px;border:0;border-radius:7px;background:#267781;color:white;cursor:pointer}
.admin-access :is(button,a,input):focus-visible{outline:3px solid #38868d;outline-offset:4px}
.spinning{animation:admin-spin 1s linear infinite}
@keyframes admin-spin{to{transform:rotate(360deg)}}
@media(min-width:961px) and (max-height:760px){
 .access-side{padding-top:16px;padding-bottom:16px;gap:16px}
 .access-card{padding:25px 30px}
 .access-card h2{margin-top:16px;font-size:30px}
 .access-intro{margin-bottom:20px}
 .password-group{margin-top:16px}
 .form-options{margin:16px 0 20px}
 .help-line{margin:16px 0}
 .security-message{padding-top:14px}
}
@media(max-width:1100px) and (min-width:961px){.access-side{padding-left:24px;padding-right:24px}.access-card{padding:28px}}
@media(max-width:960px){
 .admin-access{grid-template-columns:minmax(0,1fr);align-content:start;background:#f3f6f8}
 .access-side{min-height:0;padding:0 24px 26px;border-left:0;gap:20px;background:#f3f6f8}
 .platform-status,.network-background{display:none}
 .access-card{position:relative;margin:-16px 0 0;max-width:480px;border-radius:20px;box-shadow:0 8px 30px #20344708}
 .access-footer{margin-top:2px}
}
@media(max-width:480px){
 .access-side{padding:0 16px 22px;gap:18px}
 .access-card{padding:24px 20px;border-radius:20px}
 .access-card h2{font-size:28px;margin-top:14px}
 .access-intro{font-size:13px;margin-bottom:20px}
 .form-options{font-size:12px;margin:16px 0 20px}
 .password-group{margin-top:16px}
 .help-line{margin:18px 0 16px}
 .access-footer>span:first-child{width:100%}
 .access-footer>span:nth-child(2){display:none}
}
@media(prefers-reduced-motion:reduce){.admin-access *{animation:none!important;transition:none!important}}
</style>
