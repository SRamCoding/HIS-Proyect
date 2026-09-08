<template>
  <div class="emergencia-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--alert-soft)">
          <UIcon name="i-heroicons-heart" class="w-5 h-5" style="color: var(--alert)" />
        </div>
        <div>
          <h1 class="page-title">Admisión de Emergencia</h1>
          <p class="page-subtitle">Gestión de admisiones de emergencia</p>
        </div>
      </div>
      <NuxtLink :to="link('/app/emergencia/admisiones/create')" class="btn-primary" style="background: var(--alert)">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nueva Admisión
      </NuxtLink>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Admisiones -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
        <div class="stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-document-text" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ admisiones.length }}</span>
          <span class="stat-label">Total Admisiones</span>
        </div>
      </div>

      <!-- Admitidos -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
        <div class="stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ admitidos }}</span>
          <span class="stat-label">Admitidos</span>
        </div>
      </div>

      <!-- En Triaje -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ enTriaje }}</span>
          <span class="stat-label">En Triaje</span>
        </div>
      </div>

      <!-- Atendidos -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-badge" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ atendidos }}</span>
          <span class="stat-label">Atendidos</span>
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
              placeholder="Buscar por paciente o cuenta..."
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
              <span class="filter-count" :style="{ background: activeFilter === filter.value ? 'var(--alert)' : 'var(--mist)' }">
                {{ filter.count }}
              </span>
            </button>
          </div>
        </div>
        <div class="toolbar-right">
          <span class="result-count">{{ admisionesFiltradas.length }} resultados</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="cargando" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--alert)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando admisiones...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="cargar">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="admisionesFiltradas.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-heart" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay admisiones registradas</h3>
        <p style="color: var(--ink-soft)">Comienza registrando una nueva admisión de emergencia</p>
        <NuxtLink :to="link('/app/emergencia/admisiones/create')" class="btn-primary" style="background: var(--alert)">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Nueva Admisión
        </NuxtLink>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="emergencia-table">
          <thead>
            <tr>
              <th class="col-cuenta">
                <span class="th-content">Cuenta</span>
              </th>
              <th class="col-hc">
                <span class="th-content">HC</span>
              </th>
              <th class="col-paciente">
                <span class="th-content">Paciente</span>
              </th>
              <th class="col-servicio">
                <span class="th-content">Servicio</span>
              </th>
              <th class="col-triaje">
                <span class="th-content">Triaje</span>
              </th>
              <th class="col-estado">
                <span class="th-content">Estado</span>
              </th>
              <th class="col-actions">
                <span class="th-content">Acción</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="a in admisionesFiltradas"
              :key="a.id"
              class="table-row"
            >
              <td class="col-cuenta">
                <span class="cuenta-text font-mono-data">{{ a.numero_cuenta }}</span>
              </td>
              <td class="col-hc">
                <span class="hc-text font-mono-data">{{ a.paciente_hc || '—' }}</span>
              </td>
              <td class="col-paciente">
                <div class="paciente-cell">
                  <div class="paciente-avatar" :style="{ background: getColorPaciente(a.paciente_nombre) }">
                    <span>{{ getInitials(a.paciente_nombre) }}</span>
                  </div>
                  <span class="paciente-text">{{ a.paciente_nombre }}</span>
                </div>
              </td>
              <td class="col-servicio">
                <span class="servicio-text">{{ a.servicio_emergencia || '—' }}</span>
              </td>
              <td class="col-triaje">
                <span class="triaje-badge" :class="a.paso_triaje ? 'triaje-completado' : 'triaje-pendiente'">
                  <UIcon :name="a.paso_triaje ? 'i-heroicons-check-circle' : 'i-heroicons-clock'" class="w-3.5 h-3.5" />
                  {{ a.paso_triaje ? 'Completado' : 'Pendiente' }}
                </span>
              </td>
              <td class="col-estado">
                <span class="estado-badge" :class="getEstadoClass(a.estado)">
                  <span class="estado-dot" :class="getEstadoDot(a.estado)" />
                  {{ formatearEstado(a.estado) }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    v-if="!a.paso_triaje"
                    :to="link(`/app/emergencia/triaje/${a.id}`)"
                    class="action-btn action-triaje"
                    title="Realizar Triaje"
                  >
                    <UIcon name="i-heroicons-clipboard-document-list" class="w-4 h-4" />
                  </NuxtLink>
                  <NuxtLink
                    v-else
                    :to="link(`/app/emergencia/atencion/${a.id}`)"
                    class="action-btn action-atencion"
                    title="Iniciar Atención"
                  >
                    <UIcon name="i-heroicons-heart" class="w-4 h-4" />
                  </NuxtLink>
                  <NuxtLink
                    :to="link(`/app/emergencia/admisiones/${a.id}`)"
                    class="action-btn action-view"
                    title="Ver admisión"
                  >
                    <UIcon name="i-heroicons-eye" class="w-4 h-4" />
                  </NuxtLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Footer -->
      <div v-if="admisionesFiltradas.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ admisionesFiltradas.length }}</strong> de <strong>{{ admisiones.length }}</strong> admisiones
          <span v-if="admisionesFiltradas.length < admisiones.length">(filtrados)</span>
        </span>
        <div class="footer-actions">
          <button
            v-if="admisionesFiltradas.length < admisiones.length || search || activeFilter !== 'all'"
            class="btn-secondary btn-sm"
            @click="clearFilters"
          >
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()
const { link } = useHospitalNav()

interface Admision {
  id: number
  numero_cuenta: string
  paciente_hc: string | null
  paciente_nombre: string
  servicio_emergencia: string
  paso_triaje: boolean
  estado: 'admitido' | 'en_triaje' | 'atendido'
}

const admisiones = ref<Admision[]>([])
const filtroEstado = ref('')
const search = ref('')
const activeFilter = ref('all')
const cargando = ref(false)
const error = ref('')

const admitidos = computed(() => admisiones.value.filter(a => a.estado === 'admitido').length)
const enTriaje = computed(() => admisiones.value.filter(a => a.estado === 'en_triaje').length)
const atendidos = computed(() => admisiones.value.filter(a => a.estado === 'atendido').length)

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: admisiones.value.length },
  { label: 'Admitidos', value: 'admitido', count: admitidos.value },
  { label: 'En Triaje', value: 'en_triaje', count: enTriaje.value },
  { label: 'Atendidos', value: 'atendido', count: atendidos.value },
])

const admisionesFiltradas = computed(() => {
  let result = admisiones.value

  // Filter by estado (from dropdown)
  if (filtroEstado.value) {
    result = result.filter(a => a.estado === filtroEstado.value)
  }

  // Filter by status (from chips)
  if (activeFilter.value !== 'all') {
    result = result.filter(a => a.estado === activeFilter.value)
  }

  // Filter by search
  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(a =>
      a.paciente_nombre.toLowerCase().includes(q) ||
      a.numero_cuenta.toLowerCase().includes(q) ||
      (a.paciente_hc && a.paciente_hc.toLowerCase().includes(q))
    )
  }

  return result
})

const getInitials = (name: string) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getColorPaciente = (name: string) => {
  const colors = [
    'var(--teal-soft)',
    'var(--purple-soft)',
    'var(--navy-soft)',
    'var(--amber-soft)',
    'var(--green-soft)',
    'var(--pink-soft)',
    'var(--blue-soft)',
    'var(--orange-soft)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const formatearEstado = (estado: string) => {
  const map: Record<string, string> = {
    admitido: 'Admitido',
    en_triaje: 'En Triaje',
    atendido: 'Atendido'
  }
  return map[estado] || estado
}

const getEstadoClass = (estado: string) => {
  const map: Record<string, string> = {
    admitido: 'estado-admitido',
    en_triaje: 'estado-triaje',
    atendido: 'estado-atendido'
  }
  return map[estado] || 'estado-default'
}

const getEstadoDot = (estado: string) => {
  const map: Record<string, string> = {
    admitido: 'dot-admitido',
    en_triaje: 'dot-triaje',
    atendido: 'dot-atendido'
  }
  return map[estado] || 'dot-default'
}

const clearFilters = () => {
  search.value = ''
  activeFilter.value = 'all'
  filtroEstado.value = ''
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const params = filtroEstado.value ? `?estado=${filtroEstado.value}` : ''
    admisiones.value = await api(`/app/emergencia/admisiones${params}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar admisiones'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.emergencia-container {
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
  border-color: var(--alert);
  box-shadow: 0 0 0 3px var(--alert-soft);
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
  background: var(--alert-soft);
  border-color: var(--alert);
  color: var(--alert);
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
  background: var(--alert);
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

.emergencia-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.emergencia-table thead {
  background: var(--mist);
}

.emergencia-table th {
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

.emergencia-table td {
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

.col-cuenta { width: 12%; }
.col-hc { width: 10%; }
.col-paciente { width: 20%; }
.col-servicio { width: 15%; }
.col-triaje { width: 13%; }
.col-estado { width: 15%; }
.col-actions { width: 15%; text-align: right; }

/* Cuenta */
.cuenta-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* HC */
.hc-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Paciente Cell */
.paciente-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.paciente-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.paciente-text {
  font-weight: 500;
  color: var(--ink);
}

/* Servicio */
.servicio-text {
  color: var(--ink-soft);
}

/* Triaje Badge */
.triaje-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.triaje-completado {
  background: var(--green-soft);
  color: var(--green);
}

.triaje-pendiente {
  background: var(--amber-soft);
  color: var(--amber);
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

.estado-admitido {
  background: var(--teal-soft);
  color: var(--teal);
}

.estado-triaje {
  background: var(--amber-soft);
  color: var(--amber);
}

.estado-atendido {
  background: var(--green-soft);
  color: var(--green);
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

.dot-admitido {
  background: var(--teal);
}

.dot-triaje {
  background: var(--amber);
}

.dot-atendido {
  background: var(--green);
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

.action-triaje:hover {
  color: var(--amber);
  border-color: var(--amber-soft);
  background: var(--amber-soft);
}

.action-atencion:hover {
  color: var(--alert);
  border-color: var(--alert-soft);
  background: var(--alert-soft);
}

.action-view:hover {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
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

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .emergencia-container {
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
  .emergencia-container {
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

  .col-paciente {
    min-width: 160px;
  }

  .col-actions {
    min-width: 100px;
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

  .emergencia-table td,
  .emergencia-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }

  .col-actions {
    min-width: 90px;
  }

  .action-buttons {
    gap: 0.125rem;
  }

  .action-btn {
    width: 28px;
    height: 28px;
  }
}
</style>