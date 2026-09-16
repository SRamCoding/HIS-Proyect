<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="listPath" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
            <UIcon name="i-heroicons-users" class="w-3.5 h-3.5" />
            {{ isAdminView ? 'Administradores' : 'Usuarios por Hospital' }}
          </NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar</span>
        </div>
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <div class="page-header-icon" :style="{ background: form.is_active ? 'var(--teal-soft)' : 'var(--mist)' }">
              <UIcon name="i-heroicons-user" class="w-6 h-6" :style="{ color: form.is_active ? 'var(--teal)' : 'var(--ink-soft)' }" />
            </div>
            <div>
              <h1 class="page-title">{{ form.name || 'Editar Usuario' }}</h1>
              <p class="page-subtitle">{{ form.email }}</p>
            </div>
          </div>
          <button class="btn-danger" @click="showDeleteModal = true">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar
          </button>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>

      <div v-else-if="isSigarhAccount" class="form-card">
        <div class="flex items-start gap-3 p-4" style="background: var(--mist); border-radius: var(--radius)">
          <UIcon name="i-heroicons-information-circle" class="w-5 h-5 shrink-0" style="color: var(--ink-soft)" />
          <div>
            <p style="color: var(--ink); font-weight: 500">Esta es una cuenta SIGARH</p>
            <p class="field-hint" style="margin-top: 0.25rem">
              Las cuentas de SIGARH (usuario, rol y permisos) se editan desde
              SIGARH → Mantenimiento → Usuarios. Desde Admin solo puedes
              activarla/desactivarla o eliminarla desde el listado.
            </p>
          </div>
        </div>
      </div>

      <template v-else>
        <SFormCard
          title="Datos del Usuario"
          subtitle="Actualiza la información de la cuenta"
          icon="i-heroicons-identification"
          icon-bg="var(--teal-soft)"
          icon-color="var(--teal)"
          :error="saveError"
        >
          <div class="form-group full-width">
            <label class="form-label">Nombre Completo <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-user" class="input-icon" />
              <input v-model="form.name" class="input-clinical" placeholder="Ej: Juan Pérez" :class="{ 'input-error': errors.name }" />
            </div>
            <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Correo Electrónico <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-envelope" class="input-icon" />
              <input v-model="form.email" type="email" class="input-clinical" placeholder="usuario@hospital.pe" :class="{ 'input-error': errors.email }" />
            </div>
            <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">Nueva Contraseña</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-key" class="input-icon" />
              <input v-model="form.password" type="password" class="input-clinical" placeholder="Dejar vacío para no cambiar" :class="{ 'input-error': errors.password }" />
            </div>
            <ul v-if="form.password" class="pwd-checklist">
              <li :class="{ ok: pwdChecks.length }"><UIcon :name="pwdChecks.length ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> 8+ caracteres</li>
              <li :class="{ ok: pwdChecks.lower }"><UIcon :name="pwdChecks.lower ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Minúscula</li>
              <li :class="{ ok: pwdChecks.upper }"><UIcon :name="pwdChecks.upper ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Mayúscula</li>
              <li :class="{ ok: pwdChecks.digit }"><UIcon :name="pwdChecks.digit ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Número</li>
              <li :class="{ ok: pwdChecks.special }"><UIcon :name="pwdChecks.special ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Carácter especial</li>
            </ul>
            <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">Confirmar Contraseña</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-shield-check" class="input-icon" />
              <input v-model="form.password_confirm" type="password" class="input-clinical" placeholder="Confirmar contraseña" :class="{ 'input-error': errors.password_confirm }" />
            </div>
            <span v-if="errors.password_confirm" class="error-message">{{ errors.password_confirm }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">Rol <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-briefcase" class="input-icon" />
              <select v-model="form.role" class="input-clinical" :class="{ 'input-error': errors.role }">
                <option value="administrador">Administrativo</option>
                <option value="medico">Médico</option>
                <option value="enfermera">Enfermera</option>
                <option value="farmaceutico">Farmacéutico</option>
                <option value="laboratorista">Laboratorista</option>
                <option value="cajero">Cajero</option>
                <option value="tuasis">TUASIS</option>
                <option value="sigarh">SIGARH</option>
              </select>
            </div>
            <span v-if="errors.role" class="error-message">{{ errors.role }}</span>
          </div>

          <div class="form-group">
            <label class="form-label">Panel <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-squares-2x2" class="input-icon" />
              <input class="input-clinical" disabled :value="isAdminView ? 'Admin ERP' : 'Panel Hospitalario'" />
            </div>
            <span class="field-hint" v-if="!isAdminView">Las cuentas de SIGARH se gestionan desde SIGARH → Mantenimiento → Usuarios.</span>
          </div>

          <div v-if="!isAdminView" class="form-group">
            <label class="form-label">Hospital</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-building-office-2" class="input-icon" />
              <select v-model="form.tenant_id" class="input-clinical">
                <option value="">Sin hospital</option>
                <option v-for="h in hospitales" :key="h.id" :value="h.id">{{ h.name }}</option>
              </select>
            </div>
          </div>

          <div class="form-group full-width">
            <div class="status-toggle">
              <span class="toggle-label">Usuario Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <template #actions>
            <SFormActions
              :saving="saving"
              save-text="Guardar Cambios"
              saving-text="Guardando..."
              :cancel-to="listPath"
              @save="handleSave"
            />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="[
        'Los cambios de rol o panel se aplican de inmediato',
        'Dejar la contraseña vacía para no modificarla',
        'Los usuarios inactivos no pueden iniciar sesión',
        'No puedes desactivar ni eliminar tu propia cuenta',
      ]" />

      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.name },
        { label: 'Correo', value: form.email },
        { divider: true },
        { label: 'Rol', value: formatRol(form.role) },
        { label: 'Panel', value: formatPanel(form.panel) },
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

      <SWidgetTip text="Solo completa la contraseña si deseas cambiarla. De lo contrario déjala vacía." />
    </template>
  </SFormLayout>

  <!-- Delete Confirmation Modal -->
  <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
    <div class="modal-content" style="background: var(--paper); border-radius: var(--radius-lg)">
      <div class="modal-header">
        <div class="modal-icon" style="background: var(--alert-soft)">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" style="color: var(--alert)" />
        </div>
        <h3 class="modal-title">Confirmar Eliminación</h3>
      </div>
      <p class="modal-body">
        ¿Estás seguro de que deseas eliminar al usuario <strong>{{ form.name }}</strong>?
        <br>
        <span style="color: var(--ink-soft); font-size: 0.875rem">Esta acción no se puede deshacer.</span>
      </p>
      <div v-if="deleteError" class="error-banner">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
        {{ deleteError }}
      </div>
      <div class="modal-footer">
        <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
        <button class="btn-danger" :disabled="deleting" @click="handleDelete">
          <UIcon name="i-heroicons-trash" class="w-4 h-4" />
          {{ deleting ? 'Eliminando...' : 'Eliminar' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Hospital {
  id: string
  name: string
  domain: string
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const id = computed(() => route.params.id as string)
const isAdminView = computed(() => route.query.tipo === 'admin')
const listPath = computed(() => isAdminView.value ? '/admin/usuarios?tipo=admin' : '/admin/usuarios')

const loading = ref(true)
const saving = ref(false)
const saveError = ref('')
const hospitales = ref<Hospital[]>([])

const showDeleteModal = ref(false)
const deleting = ref(false)
const deleteError = ref('')
const isSigarhAccount = ref(false)

const form = reactive({
  name: '',
  email: '',
  password: '',
  password_confirm: '',
  role: 'administrador',
  panel: 'app',
  tenant_id: '',
  is_active: true,
})

const errors = reactive({
  name: '',
  email: '',
  password: '',
  password_confirm: '',
  role: '',
})

const pwdChecks = computed(() => ({
  length: form.password.length >= 8,
  lower: /[a-z]/.test(form.password),
  upper: /[A-Z]/.test(form.password),
  digit: /\d/.test(form.password),
  special: /[^\w\s]/.test(form.password),
}))

const formatRol = (role: string) => {
  const map: Record<string, string> = {
    administrador: 'Administrativo', medico: 'Médico', enfermera: 'Enfermera',
    farmaceutico: 'Farmacéutico', laboratorista: 'Laboratorista', cajero: 'Cajero',
    tuasis: 'TUASIS', sigarh: 'SIGARH', admin: 'Admin ERP',
  }
  return map[role] || role
}

const formatPanel = (panel: string) => {
  const map: Record<string, string> = { admin: 'Admin ERP', app: 'Hospitalario', sigarh: 'SIGARH' }
  return map[panel] || panel
}

const validateForm = (): boolean => {
  errors.name = !form.name ? 'El nombre es requerido' : ''
  errors.email = !form.email ? 'El correo es requerido' : ''
  errors.password = (form.password && !Object.values(pwdChecks.value).every(Boolean))
    ? 'La contraseña no cumple los requisitos mínimos'
    : ''
  errors.password_confirm = form.password && form.password !== form.password_confirm ? 'Las contraseñas no coinciden' : ''
  errors.role = !form.role ? 'El rol es requerido' : ''

  return !(errors.name || errors.email || errors.password || errors.password_confirm || errors.role)
}

const handleSave = async () => {
  if (!validateForm()) return

  saving.value = true
  saveError.value = ''
  try {
    const body: any = {
      name: form.name,
      email: form.email,
      role: form.role,
      panel: isAdminView.value ? 'admin' : form.panel,
      tenant_id: form.tenant_id || null,
      is_active: form.is_active,
    }
    if (form.password) body.password = form.password

    const tenantQs = form.tenant_id ? `?tenant_id=${form.tenant_id}` : ''
    await api(`/admin/usuarios/${id.value}${tenantQs}`, { method: 'PATCH', body })
    router.push(listPath.value)
  } catch (e: any) {
    saveError.value = apiErr(e, 'No se pudo guardar los cambios')
  } finally {
    saving.value = false
  }
}

const handleDelete = async () => {
  deleting.value = true
  deleteError.value = ''
  try {
    const tenantQs = form.tenant_id ? `?tenant_id=${form.tenant_id}` : ''
    await api(`/admin/usuarios/${id.value}${tenantQs}`, { method: 'DELETE' })
    router.push(listPath.value)
  } catch (e: any) {
    deleteError.value = apiErr(e, 'No se pudo eliminar el usuario')
  } finally {
    deleting.value = false
  }
}

onMounted(async () => {
  try {
    // Antes esto descargaba /usuarios/con-hospital COMPLETO (todos los
    // hospitales) solo para encontrar un usuario por id. Si la lista ya
    // conocia su tenant_id (viene en la URL, ver editUser en index.vue) se
    // pide directo a ese hospital; si no, el backend igual lo resuelve
    // (recorriendo, como antes) via el mismo endpoint dedicado.
    const tenantIdQuery = (route.query.tenant_id as string) || ''
    const usuarioUrl = tenantIdQuery
      ? `/admin/usuarios/${id.value}?tenant_id=${tenantIdQuery}`
      : `/admin/usuarios/${id.value}`
    const [user, hospitals] = await Promise.all([
      api<any>(usuarioUrl),
      api<Hospital[]>('/admin/hospitales'),
    ])
    form.name = user.name
    form.email = user.email
    form.role = user.role
    form.panel = user.panel
    form.tenant_id = user.tenant_id || ''
    form.is_active = user.is_active
    isSigarhAccount.value = user.account_type === 'sigarh'
    hospitales.value = hospitals
  } catch (e: any) {
    saveError.value = apiErr(e, 'No se pudo cargar el usuario')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>

.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--alert);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}
.btn-danger:hover:not(:disabled) { background: var(--alert-dark); }
.btn-danger:disabled { opacity: 0.6; cursor: not-allowed; }

.modal-content { max-width: 480px; width: 100%; padding: 1.5rem; box-shadow: var(--shadow-lg); }
.modal-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1.25rem; }

.modal-body { margin-bottom: 1.25rem; color: var(--ink); }

</style>
