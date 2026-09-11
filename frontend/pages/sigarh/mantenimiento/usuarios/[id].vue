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
          <span style="color: var(--ink)">Editar Usuario</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-user" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.username || 'Editar Usuario' }}</h1>
            <p class="page-subtitle">{{ form.email }}</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>

      <template v-else>
        <SFormCard
          title="Datos del Usuario"
          subtitle="Actualiza los datos del usuario"
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
            <label class="form-label">Correo electronico <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-envelope" class="input-icon" />
              <input v-model="form.email" type="email" class="input-clinical" />
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Perfil <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-shield-check" class="input-icon" />
              <select v-model="form.perfil_id" class="input-clinical">
                <option value="">Seleccione un perfil</option>
                <option v-for="p in perfiles" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
            </div>
            <p class="field-hint">El rol y los modulos se toman del perfil seleccionado</p>
          </div>

          <div class="form-group">
            <label class="form-label">Nueva contrasena</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-lock-closed" class="input-icon" />
              <input v-model="form.password" type="password" class="input-clinical" placeholder="Dejar vacio para no cambiar" />
            </div>
            <ul v-if="form.password" class="pwd-checklist">
              <li :class="{ ok: pwdChecks.length }"><UIcon :name="pwdChecks.length ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> 8+ caracteres</li>
              <li :class="{ ok: pwdChecks.lower }"><UIcon :name="pwdChecks.lower ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Minúscula</li>
              <li :class="{ ok: pwdChecks.upper }"><UIcon :name="pwdChecks.upper ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Mayúscula</li>
              <li :class="{ ok: pwdChecks.digit }"><UIcon :name="pwdChecks.digit ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Número</li>
              <li :class="{ ok: pwdChecks.special }"><UIcon :name="pwdChecks.special ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Carácter especial</li>
            </ul>
            <p class="field-hint">Solo completar si desea cambiar la contrasena. Minimo 8 caracteres con mayúscula, minúscula, número y carácter especial.</p>
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

          <div class="form-group full-width">
            <div class="p-4 rounded" style="border: 1px solid var(--line); background: var(--mist)">
              <p class="text-sm font-semibold mb-1" style="color: var(--ink)">Perfil asignado</p>
              <p class="text-xs" style="color: var(--ink-soft)">
                {{ perfilSeleccionado ? perfilSeleccionado.nombre : '- Seleccione un perfil -' }}
              </p>
            </div>
          </div>

          <template #actions>
            <SFormActions
              :saving="saving"
              save-text="Guardar Cambios"
              saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/usuarios?tenant=${tenantId}`"
              @save="handleSave"
            />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="[
        'Los usuarios acceden al sistema SIGARH con su login y contrasena',
        'El perfil define los modulos y permisos del usuario',
        'Dejar contrasena vacia para no modificarla',
        'Los usuarios inactivos no pueden iniciar sesion',
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

      <SWidgetTip text="Solo completa la contrasena si deseas cambiarla. De lo contrario dejala vacia." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const perfiles = ref<any[]>([])

const form = reactive({
  username: '',
  email: '',
  password: '',
  perfil_id: '',
  is_active: true
})

const perfilSeleccionado = computed(() =>
  perfiles.value.find(p => p.id === form.perfil_id) || null
)

const pwdChecks = computed(() => ({
  length: form.password.length >= 8,
  lower: /[a-z]/.test(form.password),
  upper: /[A-Z]/.test(form.password),
  digit: /\d/.test(form.password),
  special: /[^\w\s]/.test(form.password),
}))

const handleSave = async () => {
  if (!form.username.trim()) { error.value = 'El usuario es requerido'; return }
  if (!form.email.trim()) { error.value = 'El correo es requerido'; return }
  if (form.password && !Object.values(pwdChecks.value).every(Boolean)) {
    error.value = 'La contraseña no cumple los requisitos mínimos'; return
  }
  saving.value = true
  error.value = ''
  try {
    const body: any = {
      username: form.username,
      email: form.email,
      perfil_id: form.perfil_id || null,
      is_active: form.is_active,
    }
    if (form.password) body.password = form.password
    await api(`/sigarh/mantenimiento/usuarios/${id.value}`, { method: 'PATCH', body })
    router.push(`/sigarh/mantenimiento/usuarios?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = apiErr(e, 'No se pudo guardar')
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [data, perfilesData] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/usuarios/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/perfiles-usuario'),
    ])
    form.username = data.username
    form.email = data.email
    form.perfil_id = data.perfil_id || ''
    form.is_active = data.is_active
    perfiles.value = perfilesData
  } catch (e: any) {
    error.value = apiErr(e, 'No se pudo cargar')
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.pwd-checklist {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem 0.9rem;
  list-style: none;
  margin: 0.5rem 0 0;
  padding: 0;
}
.pwd-checklist li {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.78rem;
  color: var(--ink-soft);
  transition: color 0.15s ease;
}
.pwd-checklist li.ok {
  color: var(--green, #16a34a);
  font-weight: 600;
}
</style>
