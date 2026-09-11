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
              {{ todosSeleccionados ? 'Quitar todos' : 'Seleccionar todos' }}
            </button>
          </div>
          <div class="module-tree">
            <div v-if="!todosModulos.length" class="check-catalog-empty">No hay modulos disponibles</div>
            <div v-for="mod in todosModulos" :key="mod.code" class="module-tree-item">
              <div class="module-tree-row">
                <button
                  v-if="mod.submodulos?.length"
                  type="button"
                  class="module-tree-expand"
                  @click="toggleExpand(mod.code)"
                >
                  <UIcon :name="expandidos.has(mod.code) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'" class="w-3.5 h-3.5" />
                </button>
                <span v-else class="module-tree-expand-spacer" />
                <label class="check-catalog-item module-tree-label" :class="{ 'check-catalog-item--active': estadoModulo(mod) !== 'none' }">
                  <input
                    type="checkbox"
                    :checked="estadoModulo(mod) === 'all'"
                    :indeterminate.prop="estadoModulo(mod) === 'some'"
                    @change="toggleModulo(mod)"
                  />
                  <span>{{ mod.name }}</span>
                  <span v-if="mod.submodulos?.length" class="module-tree-count">
                    {{ submodulosSeleccionados(mod).length }}/{{ mod.submodulos.length }}
                  </span>
                </label>
              </div>
              <div v-if="mod.submodulos?.length && expandidos.has(mod.code)" class="module-tree-children">
                <label
                  v-for="sub in mod.submodulos"
                  :key="sub.code"
                  class="check-catalog-item"
                  :class="{ 'check-catalog-item--active': subSeleccionado(mod, sub) }"
                >
                  <input type="checkbox" :checked="subSeleccionado(mod, sub)" @change="toggleSub(mod, sub)" />
                  <span>{{ sub.label }}</span>
                </label>
              </div>
            </div>
          </div>
          <p class="field-hint">Modulos a los que los usuarios con este rol podran acceder. Puedes limitar el acceso a submodulos especificos dentro de cada modulo.</p>
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

interface Submodulo { code: string; label: string }
interface Modulo { id: string; code: string; name: string; category: string; is_active: boolean; submodulos?: Submodulo[] }
interface GrupoOcupacional { id: string; nombre: string }

const { api } = useApi()
const route = useRoute()
const router = useRouter()
const { puedeAdministrarSeguridad } = useSigarhPermisos()

const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')

const todosModulos = ref<Modulo[]>([])
const gruposOcupacionales = ref<GrupoOcupacional[]>([])

const PERMISOS_ACCION = [
  { code: 'aprobar_roles_turno', name: 'Aprobar roles de turno' },
  { code: 'administrar_mantenimiento', name: 'Administrar Mantenimiento (crear/editar catalogos)' },
  { code: 'administrar_seguridad', name: 'Administrar Seguridad (crear/editar/eliminar Usuarios, Perfiles y Roles del Sistema; sin esto solo puede verlos)' },
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

// --- Arbol de modulos/submodulos permitidos ---
// form.modulos_permitidos guarda strings sueltos: o el codigo completo del
// modulo ("sigarh_recursos_humanos" = todos sus submodulos, ver
// permiso_incluye() en el backend) o codigos puntuales de submodulo
// ("sigarh_recursos_humanos.empleados").
const expandidos = ref<Set<string>>(new Set())

const toggleExpand = (code: string) => {
  expandidos.value.has(code) ? expandidos.value.delete(code) : expandidos.value.add(code)
  expandidos.value = new Set(expandidos.value)
}

const subSeleccionado = (mod: Modulo, sub: Submodulo): boolean =>
  form.modulos_permitidos.includes(mod.code) || form.modulos_permitidos.includes(`${mod.code}.${sub.code}`)

const submodulosSeleccionados = (mod: Modulo): Submodulo[] =>
  (mod.submodulos || []).filter(s => subSeleccionado(mod, s))

const estadoModulo = (mod: Modulo): 'all' | 'some' | 'none' => {
  if (!mod.submodulos?.length) {
    return form.modulos_permitidos.includes(mod.code) ? 'all' : 'none'
  }
  const seleccionados = submodulosSeleccionados(mod).length
  if (seleccionados === 0) return 'none'
  if (seleccionados === mod.submodulos.length) return 'all'
  return 'some'
}

const toggleModulo = (mod: Modulo) => {
  const codigosSubmodulo = (mod.submodulos || []).map(s => `${mod.code}.${s.code}`)
  // Sea cual sea el estado actual (todo/parcial/nada), un click en el
  // checkbox del modulo alterna entre "todo" y "nada" completos. El estado
  // se debe leer ANTES de vaciar el array: si se lee despues siempre da
  // "none" y el modulo se vuelve a marcar por completo sin importar la
  // intencion real del click.
  const estabaCompleto = estadoModulo(mod) === 'all'
  form.modulos_permitidos = form.modulos_permitidos.filter(c => c !== mod.code && !codigosSubmodulo.includes(c))
  if (!estabaCompleto) {
    form.modulos_permitidos.push(mod.code)
  }
}

const toggleSub = (mod: Modulo, sub: Submodulo) => {
  const codigoSub = `${mod.code}.${sub.code}`
  const yaSeleccionado = subSeleccionado(mod, sub)
  let actuales: string[]
  if (form.modulos_permitidos.includes(mod.code)) {
    // Estaba con el codigo padre (todos): lo abrimos a la lista explicita
    // de submodulos y le quitamos el que se esta desmarcando.
    actuales = form.modulos_permitidos.filter(c => c !== mod.code)
    const todos = (mod.submodulos || []).map(s => `${mod.code}.${s.code}`)
    actuales = [...actuales, ...todos.filter(c => c !== codigoSub)]
  } else {
    actuales = yaSeleccionado
      ? form.modulos_permitidos.filter(c => c !== codigoSub)
      : [...form.modulos_permitidos, codigoSub]
  }
  // Si con esto quedaron todos los submodulos del modulo, colapsar al
  // codigo del modulo completo (mas simple y ya cubre nuevos submodulos futuros).
  const todosCodigos = (mod.submodulos || []).map(s => `${mod.code}.${s.code}`)
  const seleccionadosAhora = todosCodigos.filter(c => actuales.includes(c))
  if (todosCodigos.length && seleccionadosAhora.length === todosCodigos.length) {
    actuales = actuales.filter(c => !todosCodigos.includes(c))
    actuales.push(mod.code)
  }
  form.modulos_permitidos = actuales
}

const todosSeleccionados = computed(() => todosModulos.value.every(m => estadoModulo(m) === 'all'))

const toggleTodosModulos = () => {
  form.modulos_permitidos = todosSeleccionados.value ? [] : todosModulos.value.map(m => m.code)
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
    permisos_accion: [], alcance_global: false,
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
        permisos_accion: form.permisos_accion,
        alcance_global: form.alcance_global,
      },
    })
    if (createAnother) { resetForm() }
    else { router.push(`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId.value}`) }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear el rol' }
  finally { saving.value = false }
}

onMounted(async () => {
  if (!puedeAdministrarSeguridad.value) {
    router.replace(`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId.value}`)
    return
  }
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

.module-tree {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  padding: 0.5rem;
  max-height: 320px;
  overflow-y: auto;
}
.module-tree-item + .module-tree-item {
  border-top: 1px solid var(--line);
  margin-top: 0.25rem;
  padding-top: 0.25rem;
}
.module-tree-row {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.module-tree-expand {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  flex-shrink: 0;
  background: none;
  border: none;
  cursor: pointer;
  color: var(--ink-soft);
}
.module-tree-expand-spacer {
  display: inline-block;
  width: 20px;
  flex-shrink: 0;
}
.module-tree-label {
  flex: 1;
  border: none !important;
  padding: 0.25rem 0.5rem !important;
}
.module-tree-count {
  margin-left: auto;
  font-size: 0.6875rem;
  color: var(--ink-soft);
  font-family: monospace;
}
.module-tree-children {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  padding-left: 1.75rem;
  margin-top: 0.125rem;
}
</style>
