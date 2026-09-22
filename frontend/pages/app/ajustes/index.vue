<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })
const auth = useAuthStore()
const { link, gruposVisibles } = useHospitalNav()
const { preferences, storageError, defaults, save } = useHospitalPreferences()
const draft = reactive(defaults())
const success = ref('')
watch(preferences, value => Object.assign(draft, value), { immediate: true, deep: true })
watch(draft, () => { success.value = '' })
const changed = computed(() => JSON.stringify(draft) !== JSON.stringify(preferences.value))
const settingsPaths = [
  '/app/general/servicios', '/app/general/diagnosticos', '/app/general/paquetes',
  '/app/fact-config/catalogo-servicios', '/app/fact-config/catalogo-bienes-insumos',
  '/app/seguridad/empleados', '/app/auditoria/auditoria-general',
]
const managementLinks = computed(() => gruposVisibles.value.flatMap(group =>
  group.items.filter(item => settingsPaths.includes(item.path)).map(item => ({ ...item, group: group.label }))
))
function guardar() {
  if (save({ ...draft })) success.value = 'Preferencias guardadas y aplicadas.'
}
async function restablecer() {
  if (save(defaults())) {
    await nextTick()
    success.value = 'Se restablecieron las preferencias originales.'
  }
}
</script>

<template>
  <div class="hospital-settings">
    <header class="settings-heading">
      <span class="heading-icon"><UIcon name="i-heroicons-cog-6-tooth" aria-hidden="true" /></span>
      <div><h1>Ajustes</h1><p>Personaliza tu espacio de trabajo en el panel hospitalario.</p></div>
    </header>
    <div class="settings-grid">
      <section class="settings-card preferences-card" aria-labelledby="preferences-title">
        <div class="card-heading"><UIcon name="i-heroicons-adjustments-horizontal" aria-hidden="true" /><div><h2 id="preferences-title">Preferencias de visualización</h2><p>Se guardan para tu cuenta y hospital en este navegador.</p></div></div>
        <form @submit.prevent="guardar">
          <label class="preference-row"><span><strong>Menú lateral compacto</strong><small>Iniciar con el menú plegado para disponer de más espacio.</small></span><input v-model="draft.collapsedSidebar" type="checkbox" role="switch" /></label>
          <label class="preference-row"><span><strong>Tablas compactas</strong><small>Reducir el espacio entre filas para ver más registros.</small></span><input v-model="draft.compactTables" type="checkbox" role="switch" /></label>
          <label class="preference-row"><span><strong>Reducir movimiento</strong><small>Evitar animaciones y desplazamientos suaves en el panel.</small></span><input v-model="draft.reduceMotion" type="checkbox" role="switch" /></label>
          <p v-if="storageError" class="message error" role="alert">{{ storageError }}</p>
          <p v-if="success" class="message success" role="status">{{ success }}</p>
          <div class="preference-actions"><button type="submit" class="primary" :disabled="!changed && !storageError">Guardar preferencias</button><button type="button" class="secondary" @click="restablecer">Restablecer</button></div>
        </form>
      </section>
      <section class="settings-card" aria-labelledby="account-title">
        <div class="card-heading"><UIcon name="i-heroicons-user-circle" aria-hidden="true" /><div><h2 id="account-title">Mi cuenta</h2><p>Información de tu sesión actual.</p></div></div>
        <dl class="account-details"><div><dt>Nombre</dt><dd>{{ auth.user?.name || '—' }}</dd></div><div><dt>Correo</dt><dd>{{ auth.user?.email || '—' }}</dd></div><div><dt>Rol</dt><dd>{{ roleLabel(auth.user?.role) }}</dd></div></dl>
        <NuxtLink :to="link('/app/perfil')" class="account-link">Editar perfil y contraseña <UIcon name="i-heroicons-arrow-right" aria-hidden="true" /></NuxtLink>
      </section>
      <section class="settings-card management-card" aria-labelledby="management-title">
        <div class="card-heading"><UIcon name="i-heroicons-building-office-2" aria-hidden="true" /><div><h2 id="management-title">Configuración y catálogos</h2><p>Accesos disponibles según los permisos de tu cuenta.</p></div></div>
        <div v-if="managementLinks.length" class="management-links">
          <NuxtLink v-for="item in managementLinks" :key="item.path" :to="link(item.path)" class="management-link"><UIcon :name="item.icon" aria-hidden="true" /><span><strong>{{ item.label }}</strong><small>{{ item.group }}</small></span><UIcon name="i-heroicons-chevron-right" aria-hidden="true" /></NuxtLink>
        </div>
        <p v-else class="access-note">Tu cuenta no tiene accesos de configuración administrativa. Puedes gestionar tus preferencias y tu perfil desde esta pantalla.</p>
      </section>
    </div>
  </div>
</template>

<style scoped>
.hospital-settings { padding: 24px; min-height: 100%; background: #f4f8fb; color: var(--ink); }
.settings-heading { display: flex; align-items: center; gap: 16px; margin-bottom: 24px; }.heading-icon { display: grid; place-items: center; width: 46px; height: 46px; border-radius: 12px; background: #e8f0ff; color: #5288e9; flex-shrink: 0; }.heading-icon .iconify { width: 25px; height: 25px; }h1 { font-size: 24px; font-weight: 600; margin: 0; }.settings-heading p { font-size: 14px; color: var(--ink-soft); margin: 5px 0 0; }
.settings-grid { display: grid; grid-template-columns: minmax(0,1.5fr) minmax(260px,1fr); gap: 20px; max-width: 1280px; }.settings-card { padding: 24px; border: 1px solid #e1e8ef; border-radius: 12px; background: white; min-width: 0; }.card-heading { display: flex; gap: 12px; align-items: flex-start; margin-bottom: 20px; }.card-heading > .iconify { width: 22px; height: 22px; color: #608fe9; flex-shrink: 0; }h2 { font-size: 16px; font-weight: 600; margin: 0; }.card-heading p { font-size: 13px; color: var(--ink-soft); margin: 5px 0 0; }
.preference-row { display: flex; align-items: center; justify-content: space-between; gap: 20px; padding: 18px 0; border-top: 1px solid #edf1f6; cursor: pointer; }.preference-row strong { display: block; font-size: 14px; font-weight: 500; }.preference-row small { display: block; font-size: 12px; color: var(--ink-soft); margin-top: 5px; }.preference-row input { width: 20px; height: 20px; accent-color: #5288e9; flex-shrink: 0; cursor: pointer; }
.preference-actions { display: flex; flex-wrap: wrap; gap: 10px; margin-top: 16px; }button { border-radius: 8px; padding: 10px 14px; font-size: 13px; font-weight: 500; cursor: pointer; }.primary { background: #608fe9; color: white; border: 1px solid #608fe9; }.primary:hover:not(:disabled) { background: #4f7ed9; }button:disabled { opacity: .5; cursor: default; }.secondary { background: white; border: 1px solid #dce6ef; }.secondary:hover { background: #f4f8fb; }a:focus-visible, button:focus-visible, input:focus-visible { outline: 3px solid #4285f4; outline-offset: 3px; }
.message { padding: 10px 12px; border-radius: 8px; font-size: 13px; }.error { background: #fff0f2; color: #ad2b40; }.success { background: #eaf8ef; color: #1e7d4f; }
.account-details { margin: 0; }.account-details > div { margin-bottom: 18px; }dt { font-size: 12px; color: var(--ink-soft); }dd { margin: 4px 0 0; font-size: 14px; overflow-wrap: anywhere; }.account-link { display: flex; align-items: center; gap: 8px; padding-top: 16px; border-top: 1px solid #edf1f6; font-size: 13px; color: #3f72c7; }.account-link .iconify { width: 18px; height: 18px; }
.management-card { grid-column: 1 / -1; }.management-links { display: grid; grid-template-columns: repeat(3,minmax(0,1fr)); gap: 12px; }.management-link { display: flex; align-items: center; gap: 12px; padding: 16px; border: 1px solid #e1e8ef; border-radius: 8px; text-decoration: none; }.management-link:hover { background: #f7faff; border-color: #b8cdef; }.management-link > .iconify { width: 20px; height: 20px; flex-shrink: 0; color: #6082ad; }.management-link > span { flex: 1; min-width: 0; }.management-link strong { display: block; font-size: 13px; font-weight: 500; }.management-link small { font-size: 12px; color: var(--ink-soft); }.access-note { font-size: 13px; color: var(--ink-soft); }
@media(max-width: 1100px) { .settings-grid { grid-template-columns: minmax(0,1fr); }.management-links { grid-template-columns: repeat(2,minmax(0,1fr)); } }
@media(max-width: 767px) { .hospital-settings { padding: 16px; }.settings-card { padding: 18px; }.management-links { grid-template-columns: minmax(0,1fr); }.preference-actions button { width: 100%; } }
</style>
