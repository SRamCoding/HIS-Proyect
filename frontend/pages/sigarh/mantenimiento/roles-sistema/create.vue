<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Roles del Sistema</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Nuevo Rol</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)">
            <UIcon name="i-heroicons-shield-check" class="w-6 h-6" style="color: var(--navy)" />
          </div>
          <div>
            <h1 class="page-title">Crear Rol del Sistema</h1>
            <p class="page-subtitle">Define un nuevo rol con permisos por panel y modulo</p>
          </div>
        </div>
      </div>

      <SFormCard title="Configuracion del Rol" subtitle="Ingresa los datos del nuevo rol del sistema"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">

        <div class="form-group">
          <label class="form-label">Codigo interno <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-barcode" class="input-icon" />
            <input v-model="form.codigo" class="input-clinical font-mono-data" placeholder="Ej: ADMIN_SIGARH" @focus="error = ''" />
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
          <div class="status-toggle">
            <span class="toggle-label">Rol Activo</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
              <span class="toggle-slider" />
            </button>
          </div>
        </div>

        <template #actions>
          <SFormActions :saving="saving" save-text="Crear Rol" saving-text="Creando..."
            :cancel-to="`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId}`"
            :show-create-another="true" @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
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
const saving = ref(false)
const error = ref('')

const todosModulos = ref<Modulo[]>([])
const gruposOcupacionales = ref<GrupoOcupacional[]>([])

const form = reactive({
  codigo: '',
  nombre: '',
  panel: 'app',
  modulo_requerido: '',
  descripcion: '',
  is_active: true,
  modulos_permitidos: [] as string[],
  grupos_ocupacionales_permitidos: [] as string[],
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

const resetForm = () => {
  Object.assign(form, {
    codigo: '', nombre: '', panel: 'app', modulo_requerido: '', descripcion: '',
    is_active: true, modulos_permitidos: [], grupos_ocupacionales_permitidos: [],
  })
}

const handleCreate = async (createAnother: boolean) => {
  if (!form.codigo.trim()) { error.value = 'El codigo interno es requerido'; return }
  if (!form.nombre.trim()) { error.value = 'El nombre visible es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/roles-sistema', {
      method: 'POST',
      body: {
        codigo: form.codigo.trim(),
        nombre: form.nombre.trim(),
        panel: form.panel,
        modulo_requerido: form.modulo_requerido || null,
        descripcion: form.descripcion || null,
        is_active: form.is_active,
        modulos_permitidos: form.modulos_permitidos,
        grupos_ocupacionales_permitidos: form.grupos_ocupacionales_permitidos,
      },
    })
    if (createAnother) { resetForm() }
    else { router.push(`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId.value}`) }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear el rol' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [modulos, grupos] = await Promise.all([
      api<Modulo[]>('/sigarh/mantenimiento/modulos-catalogo'),
      api<GrupoOcupacional[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
    ])
    todosModulos.value = modulos
    gruposOcupacionales.value = grupos
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudieron cargar los catalogos'
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
