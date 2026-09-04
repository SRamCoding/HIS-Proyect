<template>
  <div class="catalogos-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-list-bullet" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Catálogos</h1>
          <p class="page-subtitle">Catálogos genéricos del sistema</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/infraestructura/catalogos/create?tenant=${tenant}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Catálogo
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Items -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
        <div class="stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-list-bullet" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ lista.length }}</span>
          <span class="stat-label">Total Elementos</span>
        </div>
      </div>

      <!-- Active Items -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ activos }}</span>
          <span class="stat-label">Activos</span>
        </div>
      </div>

      <!-- Inactive Items -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ inactivos }}</span>
          <span class="stat-label">Inactivos</span>
        </div>
      </div>

      <!-- Categories Count -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
        <div class="stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-tag" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ categoriasActivas }}</span>
          <span class="stat-label">Categorías</span>
        </div>
      </div>
    </div>

    <!-- Main Table Card -->
    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
      <!-- Table Header with Search & Filters -->
      <div class="table-toolbar">
        <div class="toolbar-left">
          <div class="search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="search-icon" />
            <input
              v-model="search"
              type="text"
              placeholder="Buscar por nombre o código..."
              class="search-input"
              style="border: 1px solid var(--line); background: var(--paper)"
            />
          </div>
          <div class="filter-group">
            <button
              v-for="filter in filters"
              :key="filter.value"
              class="filter-chip"
              :class="{ 'filter-chip--active': activeFilter === filter.value }"
              @click="activeFilter = filter.value"
            >
              {{ filter.label }}
              <span class="filter-count" :style="{ background: activeFilter === filter.value ? 'var(--teal)' : 'var(--mist)' }">
                {{ filter.count }}
              </span>
            </button>
          </div>
        </div>
        <div class="toolbar-right">
          <span class="result-count">{{ listaFiltrada.length }} resultados</span>
        </div>
      </div>

      <!-- Categorías Tabs -->
      <div class="categorias-tabs">
        <button
          @click="categoriaActiva = ''"
          class="tab-btn"
          :class="categoriaActiva === '' ? 'tab-btn--active' : ''"
        >
          Todos
        </button>
        <button
          v-for="cat in CATEGORIAS"
          :key="cat"
          @click="categoriaActiva = cat"
          class="tab-btn"
          :class="categoriaActiva === cat ? 'tab-btn--active' : ''"
        >
          {{ formatCategoria(cat) }}
        </button>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando catálogos...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="cargar">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="listaFiltrada.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-list-bullet" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay elementos registrados</h3>
        <p style="color: var(--ink-soft)">Comienza registrando un nuevo elemento en el catálogo</p>
        <NuxtLink :to="`/sigarh/infraestructura/catalogos/create?tenant=${tenant}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Nuevo Catálogo
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="catalogos-table">
          <thead>
            <tr>
              <th class="col-categoria">
                <span class="th-content">Categoría</span>
              </th>
              <th class="col-codigo">
                <span class="th-content">Código</span>
              </th>
              <th class="col-nombre">
                <span class="th-content">Nombre</span>
              </th>
              <th class="col-descripcion">
                <span class="th-content">Descripción</span>
              </th>
              <th class="col-orden">
                <span class="th-content">Orden</span>
              </th>
              <th class="col-status">
                <span class="th-content">Estado</span>
              </th>
              <th class="col-actions">
                <span class="th-content">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="item in listaFiltrada"
              :key="item.id"
              class="table-row"
            >
              <td class="col-categoria">
                <span class="categoria-badge">{{ formatCategoria(item.categoria) }}</span>
              </td>
              <td class="col-codigo">
                <span class="codigo-text font-mono-data">{{ item.codigo }}</span>
              </td>
              <td class="col-nombre">
                <span class="nombre-text">{{ item.nombre }}</span>
              </td>
              <td class="col-descripcion">
                <span class="descripcion-text">{{ item.descripcion || '—' }}</span>
              </td>
              <td class="col-orden">
                <span class="orden-text">{{ item.orden }}</span>
              </td>
              <td class="col-status">
                <span class="status-badge" :class="item.is_active ? 'status-active' : 'status-inactive'">
                  <span class="status-dot" :class="item.is_active ? 'dot-active' : 'dot-inactive'" />
                  {{ item.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    :to="`/sigarh/infraestructura/catalogos/${item.id}?tenant=${tenant}`"
                    class="action-btn action-edit"
                    title="Editar catálogo"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
                  </NuxtLink>
                  <button
                    class="action-btn action-delete"
                    title="Eliminar catálogo"
                    @click="confirmarEliminar(item)"
                  >
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Footer -->
      <div v-if="listaFiltrada.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ listaFiltrada.length }}</strong> de <strong>{{ lista.length }}</strong> elementos
          <span v-if="listaFiltrada.length < lista.length">(filtrados)</span>
        </span>
        <div class="footer-actions">
          <button
            v-if="listaFiltrada.length < lista.length || search || activeFilter !== 'all' || categoriaActiva"
            class="btn-secondary btn-sm"
            @click="clearFilters"
          >
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>

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
          ¿Estás seguro de que deseas eliminar el catálogo <strong>{{ itemToDelete?.nombre }}</strong>?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta acción no se puede deshacer y eliminará todos los datos asociados.
          </span>
        </p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-danger" @click="deleteItem">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Catálogos' })

const { $api } = useNuxtApp()
const route = useRoute()

const tenant = route.query.tenant as string

interface CatalogoItem {
  id: number
  categoria: string
  codigo: string
  nombre: string
  descripcion: string | null
  orden: number
  is_active: boolean
}

const CATEGORIAS = [
  'tipos_documento', 'tipos_servicio', 'modalidades_atencion',
  'estados_cita', 'tipos_diagnostico', 'tipos_alta',
  'procedencia_emergencia', 'tipos_grupo_ocupacional', 'metodos_pago',
  'tipos_producto', 'estados_emergencia', 'destino_atencion',
  'tipos_comprobante', 'estados_comprobante',
]

const lista = ref<CatalogoItem[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const activeFilter = ref('all')
const categoriaActiva = ref('')
const showDeleteModal = ref(false)
const itemToDelete = ref<CatalogoItem | null>(null)

const activos = computed(() => lista.value.filter(i => i.is_active).length)
const inactivos = computed(() => lista.value.filter(i => !i.is_active).length)
const categoriasActivas = computed(() => {
  const cats = new Set(lista.value.map(i => i.categoria))
  return cats.size
})

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: lista.value.length },
  { label: 'Activos', value: 'active', count: activos.value },
  { label: 'Inactivos', value: 'inactive', count: inactivos.value },
])

const listaFiltrada = computed(() => {
  let result = lista.value

  // Filter by categoria
  if (categoriaActiva.value) {
    result = result.filter(i => i.categoria === categoriaActiva.value)
  }

  // Filter by status
  if (activeFilter.value === 'active') {
    result = result.filter(i => i.is_active)
  } else if (activeFilter.value === 'inactive') {
    result = result.filter(i => !i.is_active)
  }

  // Filter by search
  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(i =>
      i.nombre.toLowerCase().includes(q) ||
      i.codigo.toLowerCase().includes(q) ||
      i.categoria.toLowerCase().includes(q)
    )
  }

  return result
})

const formatCategoria = (categoria: string) => {
  return categoria
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (l) => l.toUpperCase())
}

const clearFilters = () => {
  search.value = ''
  activeFilter.value = 'all'
  categoriaActiva.value = ''
}

const confirmarEliminar = (item: CatalogoItem) => {
  itemToDelete.value = item
  showDeleteModal.value = true
}

const deleteItem = async () => {
  if (!itemToDelete.value) return
  try {
    await $api(`/sigarh/infraestructura/catalogos/${itemToDelete.value.id}`, {
      method: 'DELETE',
      tenant
    })
    lista.value = lista.value.filter(i => i.id !== itemToDelete.value?.id)
    showDeleteModal.value = false
    itemToDelete.value = null
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar el catálogo'
  }
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    const q = categoriaActiva.value ? `?categoria=${categoriaActiva.value}` : ''
    lista.value = await $api(`/sigarh/infraestructura/catalogos${q}`, { tenant })
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar los catálogos'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
watch(categoriaActiva, cargar)
</script>

<style scoped>
.catalogos-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
  line-height: 1.2;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--teal-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--mist);
}

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

.btn-danger:hover {
  background: var(--alert-dark);
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

/* Widgets Grid */
.widgets-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

.stat-widget {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.stat-widget:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Table Card */
.table-card {
  overflow: hidden;
}

.table-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  flex: 1;
}

.search-wrapper {
  position: relative;
  min-width: 200px;
  flex: 1;
  max-width: 300px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--ink-soft);
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.filter-group {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-chip:hover {
  background: var(--mist);
}

.filter-chip--active {
  background: var(--teal-soft);
  border-color: var(--teal);
  color: var(--teal);
}

.filter-count {
  padding: 0.0625rem 0.375rem;
  border-radius: 10px;
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--ink-soft);
  background: var(--mist);
  transition: all 0.2s ease;
}

.filter-chip--active .filter-count {
  background: var(--teal);
  color: white;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.result-count {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Categorías Tabs */
.categorias-tabs {
  display: flex;
  gap: 0.375rem;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
  background: var(--mist);
}

.tab-btn {
  padding: 0.3125rem 0.75rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.tab-btn:hover {
  background: var(--paper);
  color: var(--ink);
}

.tab-btn--active {
  background: var(--teal);
  color: white;
  border-color: var(--teal);
}

/* Table States */
.table-loading,
.table-error,
.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-empty h3 {
  font-size: 1.125rem;
  margin: 0;
}

.table-empty p {
  margin: 0;
}

/* Table Styles */
.table-responsive {
  overflow-x: auto;
}

.catalogos-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.catalogos-table thead {
  background: var(--mist);
}

.catalogos-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--ink-soft);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--line);
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.catalogos-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
}

.table-row {
  transition: background 0.15s ease;
}

.table-row:hover {
  background: var(--mist);
}

.col-categoria { width: 13%; }
.col-codigo { width: 10%; }
.col-nombre { width: 22%; }
.col-descripcion { width: 22%; }
.col-orden { width: 8%; }
.col-status { width: 12%; }
.col-actions { width: 13%; text-align: right; }

/* Categoria Badge */
.categoria-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
  background: var(--teal-soft);
  color: var(--teal);
}

/* Codigo */
.codigo-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Nombre */
.nombre-text {
  font-weight: 500;
  color: var(--ink);
}

/* Descripción */
.descripcion-text {
  color: var(--ink-soft);
  font-size: 0.8125rem;
}

/* Orden */
.orden-text {
  color: var(--ink-soft);
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-active {
  background: var(--green-soft);
  color: var(--green);
}

.status-inactive {
  background: var(--mist);
  color: var(--ink-soft);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-active {
  background: var(--green);
}

.dot-inactive {
  background: var(--ink-soft);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.25rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.action-btn:hover {
  background: var(--mist);
}

.action-edit:hover {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
}

.action-delete:hover {
  color: var(--alert);
  border-color: var(--alert-soft);
  background: var(--alert-soft);
}

/* Table Footer */
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  border-top: 1px solid var(--line);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.footer-info {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.footer-actions {
  display: flex;
  gap: 0.5rem;
}

/* Modal */
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

.modal-content {
  max-width: 420px;
  width: 100%;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.modal-body {
  color: var(--ink);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .catalogos-container {
    padding: 1rem 1.5rem;
  }

  .table-toolbar {
    flex-direction: column;
    align-items: stretch;
  }

  .toolbar-left {
    flex-direction: column;
    align-items: stretch;
  }

  .search-wrapper {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .catalogos-container {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-header .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .widgets-grid {
    grid-template-columns: 1fr 1fr;
  }

  .filter-group {
    flex-wrap: wrap;
  }

  .categorias-tabs {
    overflow-x: auto;
    flex-wrap: nowrap;
    padding: 0.5rem 1rem;
  }

  .col-categoria {
    min-width: 100px;
  }

  .col-codigo {
    min-width: 90px;
  }

  .col-actions {
    min-width: 80px;
  }
}

@media (max-width: 480px) {
  .widgets-grid {
    grid-template-columns: 1fr;
  }

  .filter-chip {
    font-size: 0.6875rem;
    padding: 0.25rem 0.5rem;
  }

  .table-responsive {
    margin: 0 -0.5rem;
  }

  .catalogos-table td,
  .catalogos-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }

  .col-actions {
    min-width: 70px;
  }

  .action-buttons {
    gap: 0.125rem;
  }

  .action-btn {
    width: 28px;
    height: 28px;
  }

  .modal-content {
    margin: 1rem;
  }
}
</style>