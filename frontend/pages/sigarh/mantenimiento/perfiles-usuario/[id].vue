<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Perfiles de Usuario</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Perfil</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--purple-soft)">
            <UIcon name="i-heroicons-user-group" class="w-6 h-6" style="color: var(--purple)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Perfil de Usuario' }}</h1>
            <p class="page-subtitle">Actualiza los datos y permisos del perfil</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--purple)" />
      </div>

      <template v-else>
        <SFormCard title="Configuracion del Perfil" subtitle="Actualiza los datos del perfil de usuario"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--purple-soft)" icon-color="var(--purple)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-user-group" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Administrador, Supervisor, Consultor" />
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Rol del Sistema</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-shield-check" class="input-icon" />
              <select v-model="form.rol_sistema_id" class="input-clinical">
                <option value="">Sin rol</option>
                <option v-for="r in rolesSistema" :key="r.id" :value="r.id">{{ r.nombre }}</option>
              </select>
            </div>
            <p class="field-hint">Rol base para el perfil</p>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Descripcion</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea v-model="form.descripcion" class="input-clinical" rows="2" placeholder="Descripcion del perfil y sus responsabilidades..." />
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Modulos con acceso</label>
            <div class="check-catalog">
              <div v-if="!todosModulos.length" class="check-catalog-empty">No hay modulos disponibles</div>
              <label
                v-for="code in todosModulos"
                :key="code"
                class="check-catalog-item"
                :class="{ 'check-catalog-item--active': form.modulos_acceso.includes(code) }"
              >
                <input type="checkbox" :value="code" v-model="form.modulos_acceso" />
                <span>{{ formatModulo(code) }}</span>
              </label>
            </div>
            <p class="field-hint">Selecciona los modulos a los que tendra acceso este perfil</p>
          </div>

          <div class="form-group full-width">
            <div class="status-toggle">
              <span class="toggle-label">Perfil Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
            <p class="field-hint">Los perfiles inactivos no estaran disponibles</p>
          </div>

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Los perfiles definen los permisos de usuario', 'Pueden estar asociados a un rol del sistema', 'Los modulos seleccionados determinan el acceso', 'Los perfiles inactivos no se pueden asignar']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Rol', value: rolNombre || 'Sin rol' },
        { divider: true },
        { label: 'Modulos', value: String(form.modulos_acceso.length) },
        { label: 'Estado', slot: 'estado' },
      ]">
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Asigna solo los modulos necesarios para cada perfil, siguiendo el principio de minimo privilegio." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)

const loading = ref(true)
const saving = ref(false)
const error = ref('')
const rolesSistema = ref<any[]>([])

const form = reactive({
  nombre: '',
  rol_sistema_id: '',
  descripcion: '',
  modulos_acceso: [] as string[],
  is_active: true,
})

const todosModulos = computed(() =>
  authStore.user?.active_modules?.filter((m: string) => m.startsWith('sigarh_')) || []
)

const formatModulo = (code: string) =>
  code.replace('sigarh_', '').replace(/_/g, ' ').replace(/\b\w/g, (c: string) => c.toUpperCase())

const rolNombre = computed(() => rolesSistema.value.find(r => r.id === form.rol_sistema_id)?.nombre || '')

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre del perfil es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/perfiles-usuario/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        rol_sistema_id: form.rol_sistema_id || null,
        descripcion: form.descripcion || null,
        modulos_acceso: form.modulos_acceso,
        is_active: form.is_active,
      },
    })
    router.push(`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar el perfil' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, roles] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/perfiles-usuario/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/roles-sistema'),
    ])
    form.nombre = data.nombre
    form.rol_sistema_id = data.rol_sistema_id || ''
    form.descripcion = data.descripcion || ''
    form.modulos_acceso = data.modulos_acceso || []
    form.is_active = data.is_active
    rolesSistema.value = roles
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar el perfil'
  } finally {
    loading.value = false
  }
})
</script>
