<template>
  <div class="programacion-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Programación Médica</h1>
          <p class="page-subtitle">Consulta Externa · Gestión de citas médicas</p>
        </div>
      </div>
    </div>

    <div class="source-banner">
      <UIcon name="i-heroicons-information-circle" class="w-5 h-5 shrink-0" />
      <span>Las jornadas se generan desde los roles aprobados en SIGARH. Los médicos, guardias, horarios y días se validan allí.</span>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Programaciones -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
        <div class="stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ programaciones.length }}</span>
          <span class="stat-label">Total Programaciones</span>
        </div>
      </div>

      <!-- Activas -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ activas }}</span>
          <span class="stat-label">Activas</span>
        </div>
      </div>

      <!-- Inactivas -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ inactivas }}</span>
          <span class="stat-label">Inactivas</span>
        </div>
      </div>

      <!-- Especialidades -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
        <div class="stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-star" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ especialidadesCount }}</span>
          <span class="stat-label">Especialidades</span>
        </div>
      </div>
    </div>

    <!-- Filter Section -->
    <div class="filter-section">
      <div class="filter-card">
        <div class="filter-header">
          <UIcon name="i-heroicons-funnel" class="filter-header-icon" />
          <span class="filter-header-title">Filtros</span>
        </div>
        <div class="filter-body">
          <div class="filter-group">
            <div class="filter-item">
              <label class="filter-label">Periodo</label>
              <div class="input-wrapper-small" style="min-width: 100px">
                <select v-model.number="anio" class="input-clinical-small" style="padding-left: 0.625rem" @change="cargar">
                  <option v-for="y in anios" :key="y" :value="y">{{ y }}</option>
                </select>
              </div>
              <div class="input-wrapper-small" style="min-width: 130px">
                <select v-model.number="mes" class="input-clinical-small" style="padding-left: 0.625rem" @change="cargar">
                  <option v-for="(m, i) in MESES" :key="i" :value="i + 1">{{ m }}</option>
                </select>
              </div>
            </div>
            <div class="filter-item">
              <label class="filter-label">Servicio</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-building-office-2" class="input-icon-small" />
                <select v-model="filtroServicio" class="input-clinical-small" @change="cargar">
                  <option value="">Todos</option>
                  <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                </select>
              </div>
            </div>
            <div class="filter-item">
              <label class="filter-label">Especialidad</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-star" class="input-icon-small" />
                <select v-model="filtroEspecialidad" class="input-clinical-small" @change="cargar">
                  <option value="">Todas</option>
                  <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
                </select>
              </div>
            </div>
            <div class="filter-item">
              <label class="filter-label">Estado</label>
              <div class="input-wrapper-small" style="min-width: 130px">
                <select v-model="filtroEstado" class="input-clinical-small" style="padding-left: 0.625rem" @change="cargar">
                  <option value="">Todos</option>
                  <option value="activo">Activa</option>
                  <option value="inactivo">Inactiva</option>
                </select>
              </div>
            </div>
            <div class="filter-item">
              <label class="filter-label">Código</label>
              <div class="input-wrapper-small" style="min-width: 130px">
                <UIcon name="i-heroicons-hashtag" class="input-icon-small" />
                <input v-model="filtroCodigo" type="text" class="input-clinical-small" placeholder="N°" @input="onCodigoInput" />
              </div>
            </div>
            <button class="btn-clear-filter" @click="limpiarFiltros">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
              Limpiar
            </button>
          </div>
          <div class="filter-result">
            <span class="result-count">{{ programaciones.length }} resultados</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="cargando" class="loading-state">
      <div class="loading-spinner">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>
      <p style="color: var(--ink-soft)">Cargando programaciones médicas...</p>
    </div>

    <!-- Error Message -->
    <div v-else-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Table -->
    <div v-else-if="programaciones.length" class="table-card">
      <div class="table-header">
        <div class="table-header-left">
          <span class="table-title">Programaciones Registradas</span>
          <span class="table-count">{{ programaciones.length }} programaciones</span>
        </div>
      </div>
      <div class="table-responsive">
        <table class="programacion-table">
          <thead>
            <tr>
              <th><span class="th-content">Código</span></th>
              <th class="col-medico"><span class="th-content">Médico</span></th>
              <th class="col-especialidad"><span class="th-content">Especialidad</span></th>
              <th><span class="th-content">Servicio</span></th>
              <th class="col-fecha"><span class="th-content">Fecha</span></th>
              <th class="col-turno"><span class="th-content">Turno</span></th>
              <th class="col-hora"><span class="th-content">Hora</span></th>
              <th><span class="th-content">Modalidad</span></th>
              <th><span class="th-content">Origen</span></th>
              <th class="col-estado"><span class="th-content">Estado</span></th>
              <th class="col-actions"><span class="th-content">Acciones</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="p in programaciones" :key="p.id" class="table-row">
              <td><span class="fecha-text font-mono-data">{{ p.codigo || '—' }}</span></td>
              <td class="col-medico">
                <div class="medico-cell">
                  <div class="medico-avatar" :style="{ background: getMedicoColor(p.medico_nombre) }">
                    <span>{{ getInitials(p.medico_nombre) }}</span>
                  </div>
                  <span class="medico-name">{{ p.medico_nombre }}</span>
                </div>
              </td>
              <td class="col-especialidad">
                <span class="especialidad-badge" :style="{ background: getEspecialidadColor(p.especialidad_nombre) + '22', color: getEspecialidadColor(p.especialidad_nombre) }">
                  {{ p.especialidad_nombre }}
                </span>
              </td>
              <td><span class="fecha-text">{{ p.servicio_nombre || '—' }}</span></td>
              <td class="col-fecha">
                <span class="fecha-text font-mono-data">{{ formatFecha(p.fecha) }}</span>
              </td>
              <td class="col-turno">
                <span class="turno-badge" :class="p.turno === 'MAÑANA' ? 'turno-manana' : p.turno === 'TARDE' ? 'turno-tarde' : 'turno-noche'">
                  <UIcon :name="getTurnoIcon(p.turno)" class="w-3.5 h-3.5" />
                  {{ p.turno }}
                </span>
              </td>
              <td class="col-hora">
                <span class="hora-text font-mono-data">{{ p.hora_inicio }} - {{ p.hora_fin }}</span>
              </td>
              <td>
                <span class="status-badge" :class="p.modalidad === 'VIRTUAL' ? 'status-active' : 'status-inactive'">
                  {{ p.modalidad === 'VIRTUAL' ? 'Virtual' : 'Presencial' }}
                </span>
              </td>
              <td>
                <span class="status-badge" :class="p.origen === 'SIGARH' ? 'status-active' : 'status-inactive'">
                  {{ p.origen === 'SIGARH' ? 'Rol SIGARH' : 'Manual' }}
                </span>
              </td>
              <td class="col-estado">
                <span class="status-badge" :class="p.estado === 'activo' ? 'status-active' : 'status-inactive'">
                  <span class="status-dot" :class="p.estado === 'activo' ? 'dot-active' : 'dot-inactive'" />
                  {{ p.estado === 'activo' ? 'Activa' : 'Inactiva' }}
                </span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    :to="link(`/app/admision/programacion-medica/${p.id}?mode=view`)"
                    class="action-btn action-view"
                    title="Ver detalle"
                  >
                    <UIcon name="i-heroicons-eye" class="w-4 h-4" />
                  </NuxtLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!cargando" class="empty-state">
      <div class="empty-icon" style="background: var(--mist)">
        <UIcon name="i-heroicons-calendar-days" class="w-12 h-12" style="color: var(--ink-soft)" />
      </div>
      <h3 style="color: var(--ink)">No hay programaciones registradas</h3>
      <p style="color: var(--ink-soft)">Crea y aprueba un rol con actividad de Consulta Externa en SIGARH.</p>
     
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()
const { link } = useHospitalNav()

const MESES = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const hoy = new Date()
const anios = Array.from({ length: 5 }, (_, i) => hoy.getFullYear() - 2 + i)

const especialidades = ref<any[]>([])
const servicios = ref<any[]>([])
const programaciones = ref<any[]>([])
const filtroEspecialidad = ref('')
const filtroServicio = ref('')
const filtroEstado = ref('')
const filtroCodigo = ref('')
const anio = ref(hoy.getFullYear())
const mes = ref(hoy.getMonth() + 1)
const cargando = ref(false)
const error = ref('')

let codigoTimer: any
const onCodigoInput = () => { clearTimeout(codigoTimer); codigoTimer = setTimeout(cargar, 400) }
const limpiarFiltros = () => {
  filtroEspecialidad.value = ''; filtroServicio.value = ''; filtroEstado.value = ''; filtroCodigo.value = ''
  anio.value = hoy.getFullYear(); mes.value = hoy.getMonth() + 1
  cargar()
}

const activas = computed(() => programaciones.value.filter(p => p.estado === 'activo').length)
const inactivas = computed(() => programaciones.value.filter(p => p.estado !== 'activo').length)
const especialidadesCount = computed(() => {
  const unique = new Set(programaciones.value.map(p => p.especialidad_id))
  return unique.size
})

const getInitials = (name: string) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((word: string) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getMedicoColor = (name: string) => {
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

const getEspecialidadColor = (name: string) => {
  const colors = [
    'var(--teal)',
    'var(--purple)',
    'var(--navy)',
    'var(--amber)',
    'var(--green)',
    'var(--pink)',
    'var(--blue)',
    'var(--orange)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const getTurnoIcon = (turno: string) => {
  const map: Record<string, string> = {
    'MAÑANA': 'i-heroicons-sun',
    'TARDE': 'i-heroicons-cloud',
    'NOCHE': 'i-heroicons-moon'
  }
  return map[turno] || 'i-heroicons-clock'
}

const formatFecha = (fecha: string) => {
  if (!fecha) return '—'
  const d = new Date(fecha)
  return d.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (filtroEspecialidad.value) params.set('especialidad_id', filtroEspecialidad.value)
    if (filtroServicio.value) params.set('servicio_id', filtroServicio.value)
    if (filtroEstado.value) params.set('estado', filtroEstado.value)
    if (filtroCodigo.value) params.set('codigo', filtroCodigo.value)
    if (anio.value) params.set('anio', String(anio.value))
    if (mes.value) params.set('mes', String(mes.value))
    const query = params.toString() ? `?${params.toString()}` : ''
    programaciones.value = await api(`/app/consulta-externa/programacion-medica${query}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar programaciones'
  } finally {
    cargando.value = false
  }
}

onMounted(async () => {
  try {
    const [esp, serv] = await Promise.all([
      api('/app/consulta-externa/programacion-medica/especialidades'),
      api('/app/consulta-externa/programacion-medica/servicios'),
    ])
    especialidades.value = esp
    servicios.value = serv
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar catálogos'
  }
  await cargar()
})
</script>

<style scoped>
.programacion-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

.source-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  padding: 0.9rem 1rem;
  border: 1px solid var(--teal);
  border-radius: 12px;
  color: var(--teal);
  background: var(--teal-soft);
  font-size: 0.875rem;
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

/* Widgets Grid */
.widgets-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
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

/* Filter Section */
.filter-section {
  margin-bottom: 1.5rem;
}

.filter-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1.25rem;
  background: var(--mist);
  border-bottom: 1px solid var(--line);
}

.filter-header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--ink-soft);
}

.filter-header-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.filter-body {
  padding: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  flex: 1;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  white-space: nowrap;
}

.input-wrapper-small {
  position: relative;
  min-width: 200px;
}

.input-icon-small {
  position: absolute;
  left: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  width: 0.875rem;
  height: 0.875rem;
  color: var(--ink-soft);
}

.input-clinical-small {
  width: 100%;
  padding: 0.375rem 0.625rem 0.375rem 2rem;
  border-radius: 6px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.8125rem;
  transition: all 0.2s ease;
}

.input-clinical-small:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.btn-clear-filter {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-filter:hover {
  background: var(--mist);
}

.filter-result {
  display: flex;
  align-items: center;
}

.result-count {
  font-size: 0.8125rem;
  color: var(--ink-soft);
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

.table-responsive {
  overflow-x: auto;
}

.programacion-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.programacion-table thead {
  background: var(--mist);
}

.programacion-table th {
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

.programacion-table td {
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

.col-medico { width: 18%; }
.col-especialidad { width: 16%; }
.col-fecha { width: 12%; }
.col-turno { width: 12%; }
.col-hora { width: 14%; }
.col-estado { width: 13%; }
.col-actions { width: 15%; text-align: right; }

/* Medico Cell */
.medico-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.medico-avatar {
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

.medico-name {
  font-weight: 500;
  color: var(--ink);
}

/* Especialidad Badge */
.especialidad-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

/* Fecha */
.fecha-text {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Turno Badge */
.turno-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
}

.turno-manana {
  background: var(--amber-soft);
  color: var(--amber);
}

.turno-tarde {
  background: var(--blue-soft);
  color: var(--blue);
}

.turno-noche {
  background: var(--navy-soft);
  color: var(--navy);
}

/* Hora */
.hora-text {
  font-size: 0.8125rem;
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

.action-view:hover {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
}

.action-edit:hover {
  color: var(--amber);
  border-color: var(--amber-soft);
  background: var(--amber-soft);
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
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .programacion-container {
    padding: 1rem 1.5rem;
  }

  .filter-body {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    flex-direction: column;
    align-items: stretch;
  }

  .input-wrapper-small {
    min-width: auto;
  }

  .filter-result {
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .programacion-container {
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

  .col-actions {
    min-width: 80px;
  }

  .col-medico {
    min-width: 140px;
  }

  .table-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }
}

@media (max-width: 480px) {
  .widgets-grid {
    grid-template-columns: 1fr;
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

  .filter-body {
    padding: 0.75rem;
  }
}
</style>
