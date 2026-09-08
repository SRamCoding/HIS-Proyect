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
            <p class="page-subtitle">Define un nuevo usuario para el sistema SIGARH</p>
          </div>
        </div>
      </div>

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
          <p class="field-hint">Se genera automáticamente con el DNI</p>
        </div>

        <div class="form-group">
          <label class="form-label">Correo electrónico <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-envelope" class="input-icon" />
            <input v-model="form.email" type="email" class="input-clinical" placeholder="usuario@hospital.pe" />
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
          <p class="field-hint">El rol y los módulos se toman del perfil seleccionado</p>
        </div>

        <div class="form-group">
          <label class="form-label">Contraseña</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-lock-closed" class="input-icon" />
            <input v-model="form.password" type="password" class="input-clinical" placeholder="Por defecto: DNI del empleado" />
          </div>
          <p class="field-hint">Si no ingresa, se usará el DNI del empleado</p>
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
        'La contraseña por defecto es el DNI del empleado',
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

      <SWidgetTip text="Usa el DNI del empleado como nombre de usuario para facilitar el acceso y la identificación en el sistema." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.query.tenant as string || '')
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

const handleCreate = async (createAnother: boolean) => {
  if (!form.username.trim()) { error.value = 'El usuario es requerido'; return }
  if (!form.email.trim()) { error.value = 'El correo es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/usuarios', {
      method: 'POST',
      body: { ...form, perfil_id: form.perfil_id || null, password: form.password || form.username }
    })
    if (createAnother) {
      Object.assign(form, { username: '', email: '', password: '', perfil_id: '', is_active: true })
    } else {
      router.push(`/sigarh/mantenimiento/usuarios?tenant=${tenantId.value}`)
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo crear'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  perfiles.value = await api<any[]>('/sigarh/mantenimiento/perfiles-usuario')
})
</script>