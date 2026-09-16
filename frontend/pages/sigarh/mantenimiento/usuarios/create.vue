<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/usuarios?tenant=${tenantId}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
            <UIcon name="i-heroicons-users" class="w-3.5 h-3.5" />
            Usuarios
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Nuevo Usuario</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-user-plus" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">Crear Usuario</h1>
            <p class="page-subtitle">Crea una cuenta para SIGARH o el panel hospitalario</p>
          </div>
        </div>
      </div>

      <SAccesosPanelInfo />
      <SFormCard
        title="Datos del Usuario"
        subtitle="Ingresa los datos del nuevo usuario"
        icon="i-heroicons-cog-6-tooth"
        icon-bg="var(--teal-soft)"
        icon-color="var(--teal)"
        :error="error"
      >
        <div class="form-group">
          <label class="form-label">Usuario (login) <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-user" class="input-icon" />
            <input v-model="form.username" class="input-clinical" placeholder="Ej: jperez" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Correo electrónico <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-envelope" class="input-icon" />
            <input v-model="form.email" type="email" class="input-clinical" placeholder="usuario@hospital.pe" />
          </div>
        </div>

        <SSeguridadEmpleado v-model="form.empleado_id" />
<div class="form-group full-width">
          <label class="form-label">Perfil <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-shield-check" class="input-icon" />
            <select v-model="form.perfil_id" class="input-clinical">
              <option value="">Seleccione un perfil</option>
              <option v-for="p in perfiles.filter(p => p.is_active)" :key="p.id" :value="p.id">{{ p.nombre }} ({{ p.panel === 'app' ? 'Hospitalario' : 'SIGARH' }})</option>
            </select>
          </div>
          <p class="field-hint">El rol y los módulos se toman del perfil seleccionado</p>
        </div>

        <div class="form-group full-width">
          <label class="form-label">Contraseña <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-lock-closed" class="input-icon" />
            <input v-model="form.password" :type="verPassword ? 'text' : 'password'" class="input-clinical" placeholder="Mínimo 8 caracteres" />
          </div>
          <div class="flex items-center gap-3 mt-1.5">
            <button type="button" class="link-btn" @click="generarPassword">Generar contraseña segura</button>
            <button type="button" class="link-btn" @click="verPassword = !verPassword">{{ verPassword ? 'Ocultar' : 'Mostrar' }}</button>
          </div>
          <ul class="pwd-checklist">
            <li :class="{ ok: pwdChecks.length }"><UIcon :name="pwdChecks.length ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> 8+ caracteres</li>
            <li :class="{ ok: pwdChecks.lower }"><UIcon :name="pwdChecks.lower ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Minúscula</li>
            <li :class="{ ok: pwdChecks.upper }"><UIcon :name="pwdChecks.upper ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Mayúscula</li>
            <li :class="{ ok: pwdChecks.digit }"><UIcon :name="pwdChecks.digit ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Número</li>
            <li :class="{ ok: pwdChecks.special }"><UIcon :name="pwdChecks.special ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Carácter especial</li>
          </ul>
          <p class="field-hint">No puede ser igual al usuario ni al correo. Compártela con el usuario por un canal seguro; no vuelve a mostrarse.</p>
        </div>

        <div class="form-group">
          <label class="form-label">Estado</label>
          <div class="status-toggle">
            <span class="toggle-label">Usuario Activo</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
              <span class="toggle-slider" />
            </button>
          </div>
        </div>

        <!-- Preview perfil -->
        <div class="form-group full-width">
          <div class="p-4 rounded" style="border: 1px solid var(--line); background: var(--mist)">
            <p class="text-sm font-semibold mb-1" style="color: var(--ink)">Perfil asignado</p>
            <p class="text-xs" style="color: var(--ink-soft)">
              {{ perfilSeleccionado ? perfilSeleccionado.nombre : '— Seleccione un perfil —' }}
            </p>
          </div>
        </div>

        <template #actions>
          <SFormActions
            :saving="saving"
            save-text="Crear Usuario"
            saving-text="Creando..."
            :cancel-to="`/sigarh/mantenimiento/usuarios?tenant=${tenantId}`"
            :show-create-another="true"
            @save="handleCreate(false)"
            @save-another="handleCreate(true)"
          />
        </template>
      </SFormCard>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="[
        'Los usuarios acceden al sistema SIGARH con su login y contraseña',
        'El perfil define los módulos y permisos del usuario',
        'La contraseña es obligatoria y debe tener al menos 12 caracteres',
        'Los usuarios inactivos no pueden iniciar sesión',
      ]" />

      <SWidgetSummary :items="[
        { label: 'Usuario', value: form.username },
        { label: 'Correo', value: form.email },
        { divider: true },
        { label: 'Perfil', value: perfilSeleccionado?.nombre },
        { divider: true },
        { label: 'Estado', slot: 'estado' },
      ]">
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>

      <SWidgetTip text="Usa 'Generar contraseña segura' para crear una contraseña aleatoria de 16 caracteres y cópiala antes de guardar: no se muestra de nuevo." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()
const { puedeAdministrarSeguridad } = useSigarhPermisos()

const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const perfiles = ref<any[]>([])

const form = reactive({
  username: '',
  email: '',
  password: '',
  perfil_id: '',
  panel: 'sigarh',
  empleado_id: '',
  is_active: true
})
const verPassword = ref(false)

const perfilSeleccionado = computed(() =>
  perfiles.value.find(p => p.id === form.perfil_id) || null
)

watch(() => form.perfil_id, () => { const p = perfiles.value.find(p => p.id === form.perfil_id); if (p) form.panel = p.panel || 'sigarh' })

const pwdChecks = computed(() => ({
  length: form.password.length >= 8,
  lower: /[a-z]/.test(form.password),
  upper: /[A-Z]/.test(form.password),
  digit: /\d/.test(form.password),
  special: /[^\w\s]/.test(form.password),
}))
const pwdValida = computed(() => Object.values(pwdChecks.value).every(Boolean))

const generarPassword = () => {
  const grupos = ['ABCDEFGHJKLMNPQRSTUVWXYZ', 'abcdefghijkmnpqrstuvwxyz', '23456789', '!@#$%*?']
  const bytes = new Uint32Array(16)
  crypto.getRandomValues(bytes)
  const chars = Array.from(bytes, b => grupos[b % grupos.length][b % grupos[b % grupos.length].length])
  // Garantiza al menos un caracter de cada grupo exigido por el backend.
  grupos.forEach((g, i) => { chars[i] = g[bytes[i] % g.length] })
  form.password = chars.sort(() => Math.random() - 0.5).join('')
  verPassword.value = true
}

const handleCreate = async (createAnother: boolean) => {
  if (!form.username.trim()) { error.value = 'El usuario es requerido'; return }
  if (!form.email.trim()) { error.value = 'El correo es requerido'; return }
  if (!form.perfil_id) { error.value = 'El perfil es requerido'; return }
  if (!pwdValida.value) { error.value = 'La contraseña no cumple los requisitos mínimos'; return }
  if ([form.username.toLowerCase(), form.email.toLowerCase()].includes(form.password.toLowerCase())) {
    error.value = 'La contraseña no puede ser igual al usuario ni al correo'; return
  }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/usuarios', {
      method: 'POST',
      body: { ...form, empleado_id: form.empleado_id || null, perfil_id: form.perfil_id || null }
    })
    if (createAnother) {
      Object.assign(form, { username: '', email: '', password: '', perfil_id: '', is_active: true })
      verPassword.value = false
    } else {
      router.push(`/sigarh/mantenimiento/usuarios?tenant=${tenantId.value}`)
    }
  } catch (e: any) {
    error.value = apiErr(e, 'No se pudo crear')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  if (!puedeAdministrarSeguridad.value) {
    router.replace(`/sigarh/mantenimiento/usuarios?tenant=${tenantId.value}`)
    return
  }
  perfiles.value = await api<any[]>('/sigarh/mantenimiento/perfiles-usuario')
})
</script>

<style scoped>

</style>
