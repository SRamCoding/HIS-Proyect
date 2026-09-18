?<template>
  <div class="pacientes-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-user-group" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Pacientes</h1>
          <p class="page-subtitle">Gestión de pacientes del hospital</p>
        </div>
      </div>
      <NuxtLink :to="link('/app/admision/pacientes/create')" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Paciente
      </NuxtLink>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <div class="search-card">
        <div class="search-header">
          <UIcon name="i-heroicons-magnifying-glass" class="search-header-icon" />
          <span class="search-header-title">Búsqueda de Pacientes</span>
        </div>
        <div class="search-body">
          <div class="search-input-wrapper">
            <UIcon name="i-heroicons-user" class="search-input-icon" />
            <input
              v-model="q"
              type="text"
              placeholder="DNI, Nro Historia, nombres o apellidos..."
              class="search-input"
              @keyup.enter="buscar"
            />
          </div>
          <div class="search-actions">
            <button class="btn-clear" @click="limpiar">
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
              Limpiar
            </button>
            <button class="btn-search" :disabled="cargando" @click="buscar">
              <UIcon v-if="cargando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <UIcon v-else name="i-heroicons-magnifying-glass" class="w-4 h-4" />
              {{ cargando ? 'Buscando...' : 'Buscar' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="cargando && !resultados.length" class="loading-state">
      <div class="loading-spinner">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>
      <p style="color: var(--ink-soft)">Buscando pacientes...</p>
    </div>

    <!-- Results Table -->
    <div v-if="resultados.length" class="table-card">
      <div class="table-header">
        <div class="table-header-left">
          <span class="table-title">{{ q.trim() ? 'Resultados de búsqueda' : 'Todos los pacientes' }}</span>
          <span class="table-count">{{ total }} paciente{{ total === 1 ? '' : 's' }}</span>
        </div>
      </div>
      <div class="table-responsive">
        <table class="pacientes-table">
          <thead>
            <tr>
              <th class="col-dni">
                <span class="th-content">DNI</span>
              </th>
              <th class="col-record">
                <span class="th-content">Nro Historia</span>
              </th>
              <th class="col-name">
                <span class="th-content">Nombre completo</span>
              </th>
              <th class="col-age">
                <span class="th-content">Edad</span>
              </th>
              <th class="col-insurance">
                <span class="th-content">Seguro</span>
              </th>
              <th class="col-actions">
                <span class="th-content">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in resultados"
              :key="p.id"
              class="table-row"
            >
              <td class="col-dni">
                <span class="dni-text font-mono-data">{{ p.dni || 'NN' }}</span>
              </td>
              <td class="col-record">
                <span class="record-text font-mono-data">{{ p.record_number || '—' }}</span>
              </td>
              <td class="col-name">
                <div class="name-cell">
                  <div class="patient-avatar" :style="{ background: getPatientColor(p.full_name) }">
                    <span>{{ getInitials(p.full_name) }}</span>
                  </div>
                  <span class="name-text">{{ p.full_name }}</span>
                </div>
              </td>
              <td class="col-age">
                <span class="age-badge">{{ p.age }}</span>
              </td>
              <td class="col-insurance">
                <span class="insurance-text">{{ p.insurance_type || '—' }}</span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    :to="link(`/app/admision/pacientes/${p.id}`)"
                    class="action-btn action-view"
                    title="Ver / Editar paciente"
                  >
                    <UIcon name="i-heroicons-eye" class="w-5 h-5" />
                  </NuxtLink>
                  <NuxtLink
                    :to="link(`/app/admision/pacientes/${p.id}`)"
                    class="action-btn action-edit"
                    title="Editar paciente"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-5 h-5" />
                  </NuxtLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span class="pagination-info">
          Página {{ page }} de {{ totalPages }} · {{ total }} paciente{{ total === 1 ? '' : 's' }} en total
        </span>
        <div class="pagination-controls">
          <button class="pagination-btn" :disabled="page <= 1 || cargando" @click="irPagina(page - 1)">
            <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
            Anterior
          </button>
          <button class="pagination-btn" :disabled="page >= totalPages || cargando" @click="irPagina(page + 1)">
            Siguiente
            <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!cargando" class="empty-state">
      <div class="empty-icon" style="background: var(--mist)">
        <UIcon name="i-heroicons-user-group" class="w-12 h-12" style="color: var(--ink-soft)" />
      </div>
      <h3 style="color: var(--ink)">{{ q.trim() ? 'No se encontraron pacientes' : 'No hay pacientes registrados' }}</h3>
      <p style="color: var(--ink-soft)">
        {{ q.trim() ? 'No hay pacientes que coincidan con tu búsqueda' : 'Aún no se registró ningún paciente en este hospital' }}
      </p>
      <button v-if="q.trim()" class="btn-secondary" @click="limpiar">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
        Limpiar búsqueda
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()
const { link } = useHospitalNav()

const q = ref('')
const resultados = ref<any[]>([])
const cargando = ref(false)
const error = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const getInitials = (name: string) => {
  if (!name || name === '—') return '?'
  return name
    .split(' ')
    .map((word: string) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getPatientColor = (name: string) => {
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

async function cargar() {
  const texto = q.value.trim()
  if (texto && texto.length < 2) {
    error.value = 'Ingresa al menos 2 caracteres'
    return
  }
  error.value = ''
  cargando.value = true
  try {
    const query: Record<string, any> = { page: page.value, page_size: pageSize }
    if (texto) query.q = texto
    const data = await api<{ items: any[]; total: number }>('/app/admision/buscar', { query })
    resultados.value = data.items
    total.value = data.total
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar pacientes'
  } finally {
    cargando.value = false
  }
}

function buscar() {
  page.value = 1
  cargar()
}

function irPagina(p: number) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  cargar()
}

function limpiar() {
  q.value = ''
  page.value = 1
  cargar()
}

onMounted(cargar)
</script>

<style scoped>
.pacientes-container {
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

/* Search Section */
.search-section {
  margin-bottom: 1.5rem;
}

.search-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.search-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1.25rem;
  background: var(--teal);
}

.search-header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: white;
}

.search-header-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
}

.search-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.search-input-wrapper {
  position: relative;
}

.search-input-icon {
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
  padding: 0.625rem 0.875rem 0.625rem 2.5rem;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.search-input::placeholder {
  color: var(--ink-soft);
  opacity: 0.6;
}

.search-actions {
  display: flex;
  gap: 0.625rem;
  justify-content: flex-end;
}

.btn-clear {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear:hover {
  background: var(--mist);
}

.btn-search {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-search:hover:not(:disabled) {
  background: var(--teal-dark);
}

.btn-search:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--alert-soft);
  color: var(--alert);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

/* Loading State */
.loading-state {
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

/* Table Card */
.table-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--line);
}

.table-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.table-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.table-count {
  font-size: 0.75rem;
  color: var(--ink-soft);
  background: var(--mist);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
}

/* Table Footer / Pagination */
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 1.25rem;
  border-top: 1px solid var(--line);
  flex-wrap: wrap;
}

.pagination-info {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.4375rem 0.875rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.pagination-btn:hover:not(:disabled) {
  background: var(--mist);
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.table-responsive {
  overflow-x: auto;
}

.pacientes-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.pacientes-table thead {
  background: var(--mist);
}

.pacientes-table th {
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

.pacientes-table td {
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

.col-dni { width: 12%; }
.col-record { width: 12%; }
.col-name { width: 28%; }
.col-age { width: 10%; }
.col-insurance { width: 18%; }
.col-actions { width: 20%; text-align: right; }

/* DNI */
.dni-text {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink-soft);
}

/* Record */
.record-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Name Cell */
.name-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.patient-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6875rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.name-text {
  font-weight: 500;
  color: var(--ink);
}

/* Age Badge */
.age-badge {
  display: inline-block;
  padding: 0.1875rem 0.5rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--mist);
  color: var(--ink-soft);
}

/* Insurance */
.insurance-text {
  color: var(--ink-soft);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.action-btn:hover {
  background: var(--mist);
  transform: translateY(-1px);
  box-shadow: var(--shadow-sm);
}

.action-view {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
}

.action-view:hover {
  background: var(--teal);
  border-color: var(--teal);
  color: white;
}

.action-edit {
  color: var(--amber);
  border-color: var(--amber-soft);
  background: var(--amber-soft);
}

.action-edit:hover {
  background: var(--amber);
  border-color: var(--amber);
  color: white;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state h3 {
  font-size: 1.125rem;
  margin: 0;
}

.empty-state p {
  margin: 0;
}

/* Responsive */
@media (max-width: 1024px) {
  .pacientes-container {
    padding: 1rem 1.5rem;
  }
}

@media (max-width: 768px) {
  .pacientes-container {
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

  .search-actions {
    flex-direction: column;
  }

  .btn-clear,
  .btn-search {
    justify-content: center;
  }

  .col-actions {
    min-width: 80px;
  }

  .col-name {
    min-width: 150px;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .col-dni {
    min-width: 80px;
  }
  
  .col-record {
    min-width: 90px;
  }
  
  .col-actions {
    min-width: 70px;
  }

  .action-btn {
    width: 28px;
    height: 28px;
  }

  .action-buttons {
    gap: 0.125rem;
  }

  .search-body {
    padding: 0.75rem;
  }
}
</style>