<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Perfiles de Usuario</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Nuevo Perfil</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--purple-soft)">
            <UIcon name="i-heroicons-user-group" class="w-6 h-6" style="color: var(--purple)" />
          </div>
          <div>
            <h1 class="page-title">Crear Perfil de Usuario</h1>
            <p class="page-subtitle">Define un nuevo perfil con permisos especificos</p>
          </div>
        </div>
      </div>

      <SFormCard title="Configuracion del Perfil" subtitle="Ingresa los datos del nuevo perfil de usuario"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--purple-soft)" icon-color="var(--purple)" :error="error">

        <div class="form-group full-width">
          <label class="form-label">Nombre <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-user-group" class="input-icon" />
            <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Administrador, Supervisor, Consultor" @focus="error = ''" />
          </div>
        </div>

        <div class="form-group full-width">
          <label class="form-label">Rol del Sistema</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-shield-check" class="input-icon" />
            <select v-model="form.rol_sistema_id" class="input-clinical">
              <option value="">Sin rol</option>
              <option v-for="r in rolesDisponibles" :key="r.id" :value="r.id">{{ r.nombre }}</option>
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
            <div v-if="!modulosDisponibles.length" class="check-catalog-empty">No hay modulos disponibles</div>
            <label
              v-for="mod in modulosDisponibles"
              :key="mod.code"
              class="check-catalog-item"
              :class="{ 'check-catalog-item--active': form.modulos_acceso.includes(mod.code) }"
            >
              <input type="checkbox" :value="mod.code" v-model="form.modulos_acceso" />
              <span>{{ mod.name }}</span>
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
          <SFormActions :saving="saving" save-text="Crear Perfil" saving-text="Creando..."
            :cancel-to="`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId}`"
            :show-create-another="true" @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
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

const saving = ref(false)
const error = ref('')
const rolesSistema = ref<any[]>([])
const todosModulos = ref<any[]>([])

const form = reactive({
  nombre: '',
  rol_sistema_id: '',
  descripcion: '',
  modulos_acceso: [] as string[],
  is_active: true,
})

const rolesDisponibles = computed(() =>
  rolesSistema.value.filter(r =>
    r.is_active && (!r.modulo_requerido || authStore.user?.active_modules?.includes(r.modulo_requerido))
  )
)

const modulosDisponibles = computed(() => {
  let base = todosModulos.value.filter(m => authStore.user?.active_modules?.includes(m.code))
  const rol = rolesSistema.value.find(r => r.id === form.rol_sistema_id)
  if (rol && rol.modulos_permitidos?.length) {
    base = base.filter(m => rol.modulos_permitidos.includes(m.code))
  }
  return base
})

const rolNombre = computed(() => rolesSistema.value.find(r => r.id === form.rol_sistema_id)?.nombre || '')

watch(() => form.rol_sistema_id, () => {
  const codigosValidos = modulosDisponibles.value.map(m => m.code)
  form.modulos_acceso = form.modulos_acceso.filter(m => codigosValidos.includes(m))
})

const handleCreate = async (createAnother: boolean) => {
  if (!form.nombre.trim()) { error.value = 'El nombre del perfil es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/perfiles-usuario', {
      method: 'POST',
      tenant: tenantId.value,
      body: {
        nombre: form.nombre,
        rol_sistema_id: form.rol_sistema_id || null,
        descripcion: form.descripcion || null,
        modulos_acceso: form.modulos_acceso,
        is_active: form.is_active,
      },
    })
    if (createAnother) {
      Object.assign(form, { nombre: '', rol_sistema_id: '', descripcion: '', modulos_acceso: [], is_active: true })
    } else {
      router.push(`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId.value}`)
    }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear el perfil' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [roles, modulos] = await Promise.all([
      api('/sigarh/mantenimiento/roles-sistema'),
      api('/sigarh/mantenimiento/modulos-catalogo'),
    ])
    rolesSistema.value = roles
    todosModulos.value = modulos
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar catalogos'
  }
})
</script>
