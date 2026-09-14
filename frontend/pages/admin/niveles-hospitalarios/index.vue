<template>
  <div class="sigarh-index-container">

    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-building-library" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Niveles Hospitalarios</h1>
          <p class="page-subtitle">Niveles MINSA con sus modulos por defecto</p>
        </div>
      </div>
      <NuxtLink to="/admin/niveles-hospitalarios/create" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Nivel
      </NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ niveles.length }}</div>
          <div class="sigarh-stat-label">Total Niveles</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ activeCount }}</div>
          <div class="sigarh-stat-label">Activos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ inactiveCount }}</div>
          <div class="sigarh-stat-label">Inactivos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ totalModules }}</div>
          <div class="sigarh-stat-label">Modulos Configurados</div>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="searchQuery" type="text" placeholder="Buscar nivel..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button v-for="filter in filters" :key="filter.value" class="sigarh-filter-btn"
              :class="{ active: activeFilter === filter.value }" @click="activeFilter = filter.value">
              {{ filter.label }} <span class="sigarh-filter-count">{{ filter.count }}</span>
            </button>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span class="sigarh-result-count">{{ filteredNiveles.length }} resultados</span>
          <button v-if="searchQuery || activeFilter !== 'all'" @click="searchQuery = ''; activeFilter = 'all'" class="sigarh-clear-btn">Limpiar</button>
        </div>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
        <p style="color: var(--ink-soft)">Cargando niveles hospitalarios...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button @click="fetchData" class="btn-outline">Reintentar</button>
      </div>
      <div v-else-if="!filteredNiveles.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-building-library" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">No hay niveles registrados</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Comienza creando tu primer nivel hospitalario</p>
        </div>
        <NuxtLink to="/admin/niveles-hospitalarios/create" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Crear Nivel
        </NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 12%">Codigo</th>
              <th style="width: 20%">Nombre</th>
              <th style="width: 30%">Modulos</th>
              <th style="width: 8%">Orden</th>
              <th style="width: 12%">Estado</th>
              <th style="width: 18%; text-align: right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="nivel in filteredNiveles" :key="nivel.id" style="cursor: pointer" @click="navigateToEdit(nivel.id)">
              <td>
                <span class="sigarh-code-badge" :style="{ background: nivel.color || '#6B7280', color: getContrastColor(nivel.color || '#6B7280') }">
                  {{ nivel.code }}
                </span>
              </td>
              <td>
                <div class="sigarh-item-cell">
                  <div style="width: 10px; height: 10px; border-radius: 50%; border: 1px solid var(--line); flex-shrink: 0" :style="{ background: nivel.color || '#6B7280' }" />
                  <span class="sigarh-item-name">{{ nivel.name }}</span>
                </div>
              </td>
              <td>
                <div style="display: flex; flex-direction: column; gap: 0.375rem">
                  <div style="display: flex; align-items: center; gap: 0.5rem">
                    <span style="font-weight: 600; color: var(--ink)">{{ getTotalModules(nivel) }}</span>
                    <span style="font-size: 0.75rem; color: var(--ink-soft)">
                      App: {{ nivel.default_modules?.app?.length || 0 }} · SIGARH: {{ nivel.default_modules?.sigarh?.length || 0 }}
                    </span>
                  </div>
                  <div style="display: flex; height: 4px; border-radius: 2px; overflow: hidden; background: var(--mist)">
                    <div style="height: 100%; transition: width 0.6s ease" :style="{ width: getModulePercentage(nivel, 'app') + '%', background: 'var(--teal)' }" />
                    <div style="height: 100%; transition: width 0.6s ease" :style="{ width: getModulePercentage(nivel, 'sigarh') + '%', background: 'var(--navy)' }" />
                  </div>
                </div>
              </td>
              <td>
                <span class="sigarh-code-badge" style="background: var(--mist); color: var(--ink-soft)">{{ nivel.sort_order }}</span>
              </td>
              <td>
                <span class="badge" :class="nivel.is_active ? 'badge--ok' : 'badge--neutral'">
                  {{ nivel.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td style="text-align: right">
                <div class="sigarh-actions" @click.stop>
                  <NuxtLink :to="`/admin/niveles-hospitalarios/${nivel.id}`" class="sigarh-action-btn" title="Editar nivel">
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" />
                  </NuxtLink>
                  <button class="sigarh-action-btn" :title="nivel.is_active ? 'Desactivar' : 'Activar'" @click="toggleStatus(nivel)">
                    <UIcon :name="nivel.is_active ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" style="color: var(--amber)" />
                  </button>
                  <button class="sigarh-action-btn danger" title="Eliminar nivel" @click="confirmDelete(nivel)">
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">
          Mostrando <strong>{{ filteredNiveles.length }}</strong> de <strong>{{ niveles.length }}</strong> niveles
        </div>
      </div>
    </div>

    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-content" style="background: var(--paper); border-radius: var(--radius-lg)">
        <div class="modal-header">
          <div class="modal-icon" style="background: var(--alert-soft)">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" style="color: var(--alert)" />
          </div>
          <h3 class="modal-title">Confirmar Eliminacion</h3>
        </div>
        <p class="modal-body">
          Estas seguro de eliminar el nivel <strong>{{ nivelToDelete?.name }}</strong>?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta accion no se puede deshacer y eliminara todas las configuraciones asociadas.
          </span>
        </p>
        <div class="modal-footer">
          <button class="btn-outline" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-primary" style="background: var(--alert)" @click="deleteNivel">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Nivel {
  id: number
  code: string
  name: string
  color: string
  sort_order: number
  is_active: boolean
  default_modules?: { app: string[]; sigarh: string[] }
}

const { api } = useApi()
const router = useRouter()

const niveles = ref<Nivel[]>([])
const loading = ref(true)
const error = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const showDeleteModal = ref(false)
const nivelToDelete = ref<Nivel | null>(null)

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: niveles.value.length },
  { label: 'Activos', value: 'active', count: activeCount.value },
  { label: 'Inactivos', value: 'inactive', count: inactiveCount.value },
])

const activeCount = computed(() => niveles.value.filter(n => n.is_active).length)
const inactiveCount = computed(() => niveles.value.filter(n => !n.is_active).length)
const totalModules = computed(() => niveles.value.reduce((acc, n) => {
  const app = n.default_modules?.app?.length || 0
  const sigarh = n.default_modules?.sigarh?.length || 0
  return acc + app + sigarh
}, 0))

const filteredNiveles = computed(() => {
  let result = niveles.value
  if (activeFilter.value === 'active') result = result.filter(n => n.is_active)
  else if (activeFilter.value === 'inactive') result = result.filter(n => !n.is_active)
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(n => n.code.toLowerCase().includes(query) || n.name.toLowerCase().includes(query))
  }
  return result
})

const getTotalModules = (nivel: Nivel) => (nivel.default_modules?.app?.length || 0) + (nivel.default_modules?.sigarh?.length || 0)

const getModulePercentage = (nivel: Nivel, type: 'app' | 'sigarh') => {
  const total = getTotalModules(nivel)
  if (total === 0) return 0
  return Math.round(((nivel.default_modules?.[type]?.length || 0) / total) * 100)
}

const getContrastColor = (hex: string) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#000000' : '#FFFFFF'
}

const navigateToEdit = (id: number) => router.push(`/admin/niveles-hospitalarios/${id}`)

const toggleStatus = async (nivel: Nivel) => {
  try {
    await api(`/admin/niveles-hospitalarios/${nivel.id}`, { method: 'PATCH', body: { is_active: !nivel.is_active } })
    nivel.is_active = !nivel.is_active
  } catch (e: any) { error.value = e?.data?.detail || 'Error al actualizar el estado' }
}

const confirmDelete = (nivel: Nivel) => { nivelToDelete.value = nivel; showDeleteModal.value = true }

const deleteNivel = async () => {
  if (!nivelToDelete.value) return
  try {
    await api(`/admin/niveles-hospitalarios/${nivelToDelete.value.id}`, { method: 'DELETE' })
    niveles.value = niveles.value.filter(n => n.id !== nivelToDelete.value?.id)
    showDeleteModal.value = false
    nivelToDelete.value = null
  } catch (e: any) { error.value = e?.data?.detail || 'Error al eliminar el nivel' }
}

const fetchData = async () => {
  loading.value = true
  error.value = ''
  try { niveles.value = await api<Nivel[]>('/admin/niveles-hospitalarios') }
  catch (e: any) { error.value = e?.data?.detail || 'Error de conexion' }
  finally { loading.value = false }
}

onMounted(fetchData)
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}
.modal-content { max-width: 420px; width: 100%; padding: 1.5rem; box-shadow: var(--shadow-lg); }
.modal-header { display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem; }
.modal-icon { width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.modal-title { font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0; }
.modal-body { color: var(--ink); margin-bottom: 1.5rem; line-height: 1.6; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; }
</style>
