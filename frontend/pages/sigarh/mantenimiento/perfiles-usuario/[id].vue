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
        <SAccesosPanelInfo />
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
                <option value="">Seleccione un rol SIGARH</option>
                <option v-for="r in rolesSistema.filter(r => r.panel === 'sigarh' && r.is_active)" :key="r.id" :value="r.id">{{ r.nombre }}</option>
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
            <div class="flex items-center justify-between mb-2">
              <label class="form-label" style="margin: 0">Modulos con acceso</label>
              <button type="button" class="link-btn" @click="toggleTodosModulos">
                {{ todosSeleccionados ? 'Quitar todos' : 'Seleccionar todos' }}
              </button>
            </div>
            <div class="module-tree">
              <div v-if="!modulosDisponibles.length" class="check-catalog-empty">No hay modulos disponibles para el rol seleccionado</div>
              <div v-for="mod in modulosDisponibles" :key="mod.code" class="module-tree-item">
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
            <p class="field-hint">Solo se muestran los modulos/submodulos que el rol seleccionado permite.</p>
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
      <SWidgetInfo :items="['Los perfiles definen los permisos de usuario', 'Cada perfil requiere un rol SIGARH activo', 'Los modulos seleccionados determinan el acceso', 'Los perfiles inactivos no se pueden asignar']" />
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
const { puedeAdministrarSeguridad } = useSigarhPermisos()

const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)

const loading = ref(true)
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

const rolNombre = computed(() => rolesSistema.value.find(r => r.id === form.rol_sistema_id)?.nombre || '')

// El rol de sistema es el techo: el perfil solo puede pedir del rol hacia
// abajo (menos, nunca mas). "cubre" replica permiso_incluye() del backend.
const cubre = (codigos: string[], codigo: string) => {
  if (codigos.includes(codigo)) return true
  const padre = codigo.split('.')[0]
  return padre !== codigo && codigos.includes(padre)
}

const modulosDisponibles = computed(() => {
  const habilitados = todosModulos.value
  const rol = rolesSistema.value.find(r => r.id === form.rol_sistema_id)
  if (!rol || !rol.modulos_permitidos?.length) return []
  return habilitados
    .map((m: any) => ({
      ...m,
      submodulos: (m.submodulos || []).filter((s: any) => cubre(rol.modulos_permitidos, `${m.code}.${s.code}`)),
    }))
    .filter((m: any) => cubre(rol.modulos_permitidos, m.code) || m.submodulos.length > 0)
})

watch(() => form.rol_sistema_id, () => {
  const modulos = modulosDisponibles.value
  const rol = rolesSistema.value.find(r => r.id === form.rol_sistema_id)
  form.modulos_acceso = form.modulos_acceso.filter(c => cubre(rol?.modulos_permitidos || [], c) && modulos.some((m: any) => cubre([c], m.code) || m.submodulos?.some((s: any) => `${m.code}.${s.code}` === c)))
})

// --- Arbol de modulos/submodulos (igual que en Rol del Sistema) ---
const expandidos = ref<Set<string>>(new Set())

const toggleExpand = (code: string) => {
  expandidos.value.has(code) ? expandidos.value.delete(code) : expandidos.value.add(code)
  expandidos.value = new Set(expandidos.value)
}

const subSeleccionado = (mod: any, sub: any): boolean =>
  form.modulos_acceso.includes(mod.code) || form.modulos_acceso.includes(`${mod.code}.${sub.code}`)

const submodulosSeleccionados = (mod: any): any[] =>
  (mod.submodulos || []).filter((s: any) => subSeleccionado(mod, s))

const estadoModulo = (mod: any): 'all' | 'some' | 'none' => {
  if (!mod.submodulos?.length) {
    return form.modulos_acceso.includes(mod.code) ? 'all' : 'none'
  }
  const seleccionados = submodulosSeleccionados(mod).length
  if (seleccionados === 0) return 'none'
  if (seleccionados === mod.submodulos.length) return 'all'
  return 'some'
}

const toggleModulo = (mod: any) => {
  const codigosSubmodulo = (mod.submodulos || []).map((s: any) => `${mod.code}.${s.code}`)
  // Leer el estado ANTES de vaciar: leerlo despues siempre da "none" y el
  // modulo se re-marca por completo sin importar la intencion del click.
  const estabaCompleto = estadoModulo(mod) === 'all'
  form.modulos_acceso = form.modulos_acceso.filter(c => c !== mod.code && !codigosSubmodulo.includes(c))
  if (!estabaCompleto) {
    // Si el rol solo otorga submodulos puntuales (no el modulo completo), no
    // se puede mandar el codigo padre: se marcan los submodulos uno por uno.
    const rol = rolesSistema.value.find(r => r.id === form.rol_sistema_id)
    const rolPermitePadre = rol ? cubre(rol.modulos_permitidos || [], mod.code) : false
    if (rolPermitePadre || !codigosSubmodulo.length) {
      form.modulos_acceso.push(mod.code)
    } else {
      form.modulos_acceso.push(...codigosSubmodulo)
    }
  }
}

const toggleSub = (mod: any, sub: any) => {
  const codigoSub = `${mod.code}.${sub.code}`
  const yaSeleccionado = subSeleccionado(mod, sub)
  let actuales: string[]
  if (form.modulos_acceso.includes(mod.code)) {
    actuales = form.modulos_acceso.filter(c => c !== mod.code)
    const todos = (mod.submodulos || []).map((s: any) => `${mod.code}.${s.code}`)
    actuales = [...actuales, ...todos.filter((c: string) => c !== codigoSub)]
  } else {
    actuales = yaSeleccionado
      ? form.modulos_acceso.filter(c => c !== codigoSub)
      : [...form.modulos_acceso, codigoSub]
  }
  const todosCodigos = (mod.submodulos || []).map((s: any) => `${mod.code}.${s.code}`)
  const seleccionadosAhora = todosCodigos.filter((c: string) => actuales.includes(c))
  // Solo colapsar al codigo padre si el rol seleccionado realmente lo permite
  // completo; si el rol solo otorga el submodulo puntual, colapsar mandaria
  // un codigo que el backend rechaza (permiso_incluye no deja que un hijo
  // cubra a su padre).
  const rol = rolesSistema.value.find(r => r.id === form.rol_sistema_id)
  const rolPermitePadre = rol ? cubre(rol.modulos_permitidos || [], mod.code) : false
  if (todosCodigos.length && seleccionadosAhora.length === todosCodigos.length && rolPermitePadre) {
    actuales = actuales.filter((c: string) => !todosCodigos.includes(c))
    actuales.push(mod.code)
  }
  form.modulos_acceso = actuales
}

const todosSeleccionados = computed(() => modulosDisponibles.value.every((m: any) => estadoModulo(m) === 'all'))

const toggleTodosModulos = () => {
  const rol = rolesSistema.value.find(r => r.id === form.rol_sistema_id)
  form.modulos_acceso = todosSeleccionados.value ? [] : modulosDisponibles.value.flatMap((m: any) => cubre(rol?.modulos_permitidos || [], m.code) ? [m.code] : (m.submodulos || []).map((s: any) => `${m.code}.${s.code}`))
}

const handleSave = async () => {
  if (!form.rol_sistema_id) { error.value = 'Seleccione un rol SIGARH activo'; return }
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
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar el perfil') }
  finally { saving.value = false }
}

onMounted(async () => {
  if (!puedeAdministrarSeguridad.value) {
    router.replace(`/sigarh/mantenimiento/perfiles-usuario?tenant=${tenantId.value}`)
    return
  }
  try {
    const [data, roles, modulos] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/perfiles-usuario/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/roles-sistema'),
      api<any[]>('/sigarh/mantenimiento/modulos-catalogo'),
    ])
    form.nombre = data.nombre
    form.rol_sistema_id = data.rol_sistema_id || ''
    form.descripcion = data.descripcion || ''
    form.modulos_acceso = data.modulos_acceso || []
    form.is_active = data.is_active
    rolesSistema.value = roles
    todosModulos.value = modulos
  } catch (e: any) {
    error.value = apiErr(e, 'No se pudo cargar el perfil')
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
