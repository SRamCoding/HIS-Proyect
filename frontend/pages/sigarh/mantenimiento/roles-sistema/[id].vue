<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Roles del Sistema</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Rol</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)">
            <UIcon name="i-heroicons-shield-check" class="w-6 h-6" style="color: var(--navy)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Rol del Sistema' }}</h1>
            <p class="page-subtitle">Actualiza los datos y permisos del rol</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" />
      </div>

      <template v-else>
        <SFormCard title="Configuracion del Rol" subtitle="Actualiza los datos del rol del sistema"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">

          <div class="form-group">
            <label class="form-label">Codigo interno</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-barcode" class="input-icon" />
              <input v-model="form.codigo" class="input-clinical font-mono-data" placeholder="Ej: ADMIN_SIGARH" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Nombre visible <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-shield-check" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Administrador SIGARH" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Panel</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-computer-desktop" class="input-icon" />
              <select v-model="form.panel" class="input-clinical">
                <option value="app">App</option>
                <option value="sigarh">SIGARH</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Modulo requerido</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-lock-closed" class="input-icon" />
              <select v-model="form.modulo_requerido" class="input-clinical">
                <option value="">Ninguno</option>
                <option v-for="m in todosModulos" :key="m.code" :value="m.code">{{ m.name }}</option>
              </select>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Descripcion</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea v-model="form.descripcion" class="input-clinical" rows="2" placeholder="Descripcion del rol y su alcance..." />
            </div>
          </div>

          <div class="form-group full-width">
            <div class="flex items-center justify-between mb-2">
              <label class="form-label" style="margin: 0">Modulos permitidos</label>
              <button type="button" class="link-btn" @click="toggleTodosModulos">
                {{ form.modulos_permitidos.length === todosModulos.length ? 'Quitar todos' : 'Seleccionar todos' }}
              </button>
            </div>
            <div class="check-catalog">
              <div v-if="!todosModulos.length" class="check-catalog-empty">No hay modulos disponibles</div>
              <label
                v-for="mod in todosModulos"
                :key="mod.code"
                class="check-catalog-item"
                :class="{ 'check-catalog-item--active': form.modulos_permitidos.includes(mod.code) }"
              >
                <input type="checkbox" :value="mod.code" v-model="form.modulos_permitidos" />
                <span>{{ mod.name }}</span>
              </label>
            </div>
            <p class="field-hint">Modulos a los que los usuarios con este rol podran acceder</p>
          </div>

          <div class="form-group full-width">
            <div class="flex items-center justify-between mb-2">
              <label class="form-label" style="margin: 0">Grupos ocupacionales permitidos</label>
              <button type="button" class="link-btn" @click="toggleTodosGrupos">
                {{ form.grupos_ocupacionales_permitidos.length === gruposOcupacionales.length ? 'Quitar todos' : 'Seleccionar todos' }}
              </button>
            </div>
            <div class="check-catalog">
              <div v-if="!gruposOcupacionales.length" class="check-catalog-empty">No hay grupos ocupacionales</div>
              <label
                v-for="g in gruposOcupacionales"
                :key="g.id"
                class="check-catalog-item"
                :class="{ 'check-catalog-item--active': form.grupos_ocupacionales_permitidos.includes(g.id) }"
              >
                <input type="checkbox" :value="g.id" v-model="form.grupos_ocupacionales_permitidos" />
                <span>{{ g.nombre }}</span>
              </label>
            </div>
            <p class="field-hint">Vacio = sin restriccion por grupo ocupacional</p>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Permisos de accion</label>
            <div class="check-catalog">
              <label
                v-for="p in PERMISOS_ACCION"
                :key="p.code"
                class="check-catalog-item"
                :class="{ 'check-catalog-item--active': form.permisos_accion.includes(p.code) }"
              >
                <input type="checkbox" :value="p.code" v-model="form.permisos_accion" />
                <span>{{ p.name }}</span>
              </label>
            </div>
            <p class="field-hint">Acciones concretas habilitadas dentro de un modulo (ver el modulo no implica poder aprobar en el)</p>
          </div>

          <div class="form-group full-width">
            <div class="status-toggle">
              <span class="toggle-label">Alcance global</span>
              <button type="button" @click="form.alcance_global = !form.alcance_global" class="toggle-switch" :class="{ 'toggle-active': form.alcance_global }">
                <span class="toggle-slider" />
              </button>
            </div>
            <p class="field-hint">Si esta apagado, un permiso como "Aprobar roles de turno" solo aplica al empleado marcado como jefe del servicio del rol</p>
          </div>

          <div class="form-group full-width">
            <div class="status-toggle">
              <span class="toggle-label">Rol Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Los roles agrupan permisos de acceso por panel', 'El codigo interno se usa en el sistema; el nombre es visible', 'El modulo requerido limita quien puede usar el rol', 'Los modulos permitidos definen el alcance del rol']" />
      <SWidgetSummary :items="[
        { label: 'Codigo', value: form.codigo, mono: true },
        { label: 'Nombre', value: form.nombre },
        { label: 'Panel', value: form.panel },
        { divider: true },
        { label: 'Modulos', value: String(form.modulos_permitidos.length) },
        { label: 'Grupos', value: String(form.grupos_ocupacionales_permitidos.length) },
        { label: 'Estado', slot: 'estado' },
      ]">
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Usa codigos en MAYUSCULAS con guion bajo (ej: SUPERVISOR_RRHH) para mantener consistencia." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

interface Modulo { id: string; code: string; name: string; category: string; is_active: boolean }
interface GrupoOcupacional { id: string; nombre: string }

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)

const loading = ref(true)
const saving = ref(false)
const error = ref('')

const todosModulos = ref<Modulo[]>([])
const gruposOcupacionales = ref<GrupoOcupacional[]>([])

const PERMISOS_ACCION = [
  { code: 'aprobar_roles_turno', name: 'Aprobar roles de turno' },
]

const form = reactive({
  codigo: '',
  nombre: '',
  panel: 'app',
  modulo_requerido: '',
  descripcion: '',
  is_active: true,
  modulos_permitidos: [] as string[],
  grupos_ocupacionales_permitidos: [] as string[],
  permisos_accion: [] as string[],
  alcance_global: false,
})

const toggleTodosModulos = () => {
  form.modulos_permitidos = form.modulos_permitidos.length === todosModulos.value.length
    ? []
    : todosModulos.value.map(m => m.code)
}

const toggleTodosGrupos = () => {
  form.grupos_ocupacionales_permitidos = form.grupos_ocupacionales_permitidos.length === gruposOcupacionales.value.length
    ? []
    : gruposOcupacionales.value.map(g => g.id)
}

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre del rol es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/roles-sistema/${id.value}`, {
      method: 'PATCH',
      body: {
        codigo: form.codigo,
        nombre: form.nombre,
        panel: form.panel,
        modulo_requerido: form.modulo_requerido || null,
        descripcion: form.descripcion || null,
        is_active: form.is_active,
        modulos_permitidos: form.modulos_permitidos,
        grupos_ocupacionales_permitidos: form.grupos_ocupacionales_permitidos,
        permisos_accion: form.permisos_accion,
        alcance_global: form.alcance_global,
      },
    })
    router.push(`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar el rol' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, modulos, grupos] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/roles-sistema/${id.value}`),
      api<Modulo[]>('/sigarh/mantenimiento/modulos-catalogo'),
      api<GrupoOcupacional[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
    ])
    todosModulos.value = modulos
    gruposOcupacionales.value = grupos
    form.codigo = data.codigo || ''
    form.nombre = data.nombre
    form.panel = data.panel
    form.modulo_requerido = data.modulo_requerido || ''
    form.descripcion = data.descripcion || ''
    form.is_active = data.is_active
    form.modulos_permitidos = data.modulos_permitidos || []
    form.grupos_ocupacionales_permitidos = data.grupos_ocupacionales_permitidos || []
    form.permisos_accion = data.permisos_accion || []
    form.alcance_global = !!data.alcance_global
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar el rol'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.link-btn {
  background: none;
  border: none;
  color: var(--teal);
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  padding: 0;
}
.link-btn:hover { text-decoration: underline; }
</style>
