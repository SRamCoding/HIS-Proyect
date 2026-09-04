<template>
  <div class="camas-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-bed" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Camas</h1>
          <p class="page-subtitle">Panel de camas del hospital</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/infraestructura-hosp/camas/create?tenant=${tenant}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nueva Cama
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Camas -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
        <div class="stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-bed" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ lista.length }}</span>
          <span class="stat-label">Total Camas</span>
        </div>
      </div>

      <!-- Disponibles -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ disponibles }}</span>
          <span class="stat-label">Disponibles</span>
        </div>
      </div>

      <!-- Ocupadas -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--alert)">
        <div class="stat-icon" style="background: var(--alert-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--alert)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ ocupadas }}</span>
          <span class="stat-label">Ocupadas</span>
        </div>
      </div>

      <!-- En Mantenimiento + Reservadas -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ mantenimiento + reservadas }}</span>
          <span class="stat-label">Mantenimiento / Reservadas</span>
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
              placeholder="Buscar por código, nombre o sala..."
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

      <!-- Loading State -->
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando camas...</p>
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
          <UIcon name="i-heroicons-bed" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay camas registradas</h3>
        <p style="color: var(--ink-soft)">Comienza registrando la primera cama del hospital</p>
        <NuxtLink :to="`/sigarh/infraestructura-hosp/camas/create?tenant=${tenant}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Nueva Cama
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="camas-table">
          <thead>
            <tr>
              <th class="col-codigo">
                <span class="th-content">Código</span>
              </th>
              <th class="col-nombre">
                <span class="th-content">Nombre</span>
              </th>
              <th class="col-sala">
                <span class="th-content">Sala</span>
              </th>
              <th class="col-piso">
                <span class="th-content">Piso</span>
              </th>
              <th class="col-tipo">
                <span class="th-content">Tipo</span>
              </th>
              <th class="col-estado">
                <span class="th-content">Estado</span>
              </th>
              <th class="col-actions">
                <span class="th-content">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="c in listaFiltrada"
              :key="c.id"
              class="table-row"
            >
              <td class="col-codigo">
                <span class="codigo-text font-mono-data">{{ c.codigo }}</span>
              </td>
              <td class="col-nombre">
                <div class="nombre-cell">
                  <div class="nombre-icon" :style="{ background: getEstadoColor(c.estado) + '22' }">
                    <UIcon name="i-heroicons-bed" class="w-4 h-4" :style="{ color: getEstadoColor(c.estado) }" />
                  </div>
                  <span class="nombre-text">{{ c.nombre }}</span>
                </div>
              </td>
              <td class="col-sala">
                <span class="sala-text">{{ c.sala_texto || '—' }}</span>
              </td>
              <td class="col-piso">
                <span class="piso-text">{{ c.piso_texto || '—' }}</span>
              </td>
              <td class="col-tipo">
                <span class="tipo-badge">{{ formatearTipo(c.tipo_cama) || '—' }}</span>
              </td>
              <td class="col-estado">
                <span class="estado-badge" :class="getEstadoClass(c.estado)">
                  <span class="estado-dot" :class="getEstadoDot(c.estado)" />
                  {{ formatearEstado(c.estado) }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    :to="`/sigarh/infraestructura-hosp/camas/${c.id}?tenant=${tenant}`"
                    class="action-btn action-edit"
                    title="Editar cama"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
                  </NuxtLink>
                  <button
                    class="action-btn action-delete"
                    title="Eliminar cama"
                    @click="confirmarEliminar(c)"
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
          Mostrando <strong>{{ listaFiltrada.length }}</strong> de <strong>{{ lista.length }}</strong> camas
          <span v-if="listaFiltrada.length < lista.length">(filtrados)</span>
        </span>
        <div class="footer-actions">
          <button
            v-if="listaFiltrada.length < lista.length || search || activeFilter !== 'all'"
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
          ¿Estás seguro de que deseas eliminar la cama <strong>{{ itemToDelete?.nombre }}</strong>?
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
definePageMeta({ layout: 'sigarh', title: 'Camas' })

const { $api } = useNuxtApp()
const route = useRoute()

const tenant = route.query.tenant as string

interface Cama {
  id: number
  codigo: string
  nombre: string
  sala_texto: string | null
  piso_texto: string | null
  tipo_cama: string | null
  estado: 'DISPONIBLE' | 'OCUPADA' | 'MANTENIMIENTO' | 'RESERVADA'
}

const lista = ref<Cama[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const activeFilter = ref('all')
const showDeleteModal = ref(false)
const itemToDelete = ref<Cama | null>(null)

const disponibles = computed(() => lista.value.filter(c => c.estado === 'DISPONIBLE').length)
const ocupadas = computed(() => lista.value.filter(c => c.estado === 'OCUPADA').length)
const mantenimiento = computed(() => lista.value.filter(c => c.estado === 'MANTENIMIENTO').length)
const reservadas = computed(() => lista.value.filter(c => c.estado === 'RESERVADA').length)

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: lista.value.length },
  { label: 'Disponibles', value: 'DISPONIBLE', count: disponibles.value },
  { label: 'Ocupadas', value: 'OCUPADA', count: ocupadas.value },
  { label: 'Mantenimiento', value: 'MANTENIMIENTO', count: mantenimiento.value },
  { label: 'Reservadas', value: 'RESERVADA', count: reservadas.value },
])

const listaFiltrada = computed(() => {
  let result = lista.value

  // Filter by estado
  if (activeFilter.value !== 'all') {
    result = result.filter(c => c.estado === activeFilter.value)
  }

  // Filter by search
  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(c =>
      c.codigo.toLowerCase().includes(q) ||
      c.nombre.toLowerCase().includes(q) ||
      (c.sala_texto && c.sala_texto.toLowerCase().includes(q))
    )
  }

  return result
})

const formatearEstado = (estado: string) => {
  const map: Record<string, string> = {
    DISPONIBLE: 'Disponible',
    OCUPADA: 'Ocupada',
    MANTENIMIENTO: 'Mantenimiento',
    RESERVADA: 'Reservada'
  }
  return map[estado] || estado
}

const formatearTipo = (tipo: string) => {
  const map: Record<string, string> = {
    ADULTO: 'Adulto',
    PEDIÁTRICO: 'Pediátrico',
    UCI: 'UCI',
    NEONATAL: 'Neonatal',
    MATERNIDAD: 'Maternidad',
    OBSERVACIÓN: 'Observación'
  }
  return map[tipo] || tipo
}

const getEstadoColor = (estado: string) => {
  const map: Record<string, string> = {
    DISPONIBLE: 'var(--green)',
    OCUPADA: 'var(--alert)',
    MANTENIMIENTO: 'var(--amber)',
    RESERVADA: 'var(--purple)'
  }
  return map[estado] || 'var(--ink-soft)'
}

const getEstadoClass = (estado: string) => {
  const map: Record<string, string> = {
    DISPONIBLE: 'estado-disponible',
    OCUPADA: 'estado-ocupada',
    MANTENIMIENTO: 'estado-mantenimiento',
    RESERVADA: 'estado-reservada'
  }
  return map[estado] || 'estado-default'
}

const getEstadoDot = (estado: string) => {
  const map: Record<string, string> = {
    DISPONIBLE: 'dot-disponible',
    OCUPADA: 'dot-ocupada',
    MANTENIMIENTO: 'dot-mantenimiento',
    RESERVADA: 'dot-reservada'
  }
  return map[estado] || 'dot-default'
}

const clearFilters = () => {
  search.value = ''
  activeFilter.value = 'all'
}

const confirmarEliminar = (item: Cama) => {
  itemToDelete.value = item
  showDeleteModal.value = true
}

const deleteItem = async () => {
  if (!itemToDelete.value) return
  try {
    await $api(`/sigarh/infraestructura-hosp/camas/${itemToDelete.value.id}`, {
      method: 'DELETE',
      tenant
    })
    lista.value = lista.value.filter(c => c.id !== itemToDelete.value?.id)
    showDeleteModal.value = false
    itemToDelete.value = null
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar la cama'
  }
}

async function cargar() {
  loading.value = true
  error.value = ''
  try {
    lista.value = await $api('/sigarh/infraestructura-hosp/camas', { tenant })
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar las camas'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.camas-container {
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

.camas-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.camas-table thead {
  background: var(--mist);
}

.camas-table th {
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

.camas-table td {
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

.col-codigo { width: 10%; }
.col-nombre { width: 20%; }
.col-sala { width: 15%; }
.col-piso { width: 12%; }
.col-tipo { width: 12%; }
.col-estado { width: 16%; }
.col-actions { width: 15%; text-align: right; }

/* Código */
.codigo-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Nombre Cell */
.nombre-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.nombre-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.nombre-text {
  font-weight: 500;
  color: var(--ink);
}

/* Sala y Piso */
.sala-text,
.piso-text {
  color: var(--ink-soft);
}

/* Tipo Badge */
.tipo-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
  background: var(--navy-soft);
  color: var(--navy);
}

/* Estado Badge */
.estado-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.estado-disponible {
  background: var(--green-soft);
  color: var(--green);
}

.estado-ocupada {
  background: var(--alert-soft);
  color: var(--alert);
}

.estado-mantenimiento {
  background: var(--amber-soft);
  color: var(--amber);
}

.estado-reservada {
  background: var(--purple-soft);
  color: var(--purple);
}

.estado-default {
  background: var(--mist);
  color: var(--ink-soft);
}

.estado-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-disponible {
  background: var(--green);
}

.dot-ocupada {
  background: var(--alert);
}

.dot-mantenimiento {
  background: var(--amber);
}

.dot-reservada {
  background: var(--purple);
}

.dot-default {
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
  .camas-container {
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
  .camas-container {
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

  .col-nombre {
    min-width: 160px;
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

  .camas-table td,
  .camas-table th {
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