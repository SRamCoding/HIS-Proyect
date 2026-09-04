<template>
  <div class="justificacion-detail-container">
    <div class="justificacion-detail-grid">
      <!-- Main Content -->
      <div class="justificacion-detail-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/rrhh/justificaciones?tenant=${tenantId}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-document-text" class="w-3.5 h-3.5" />
              Justificaciones
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Detalle</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" :style="{ background: getEstadoColor(form.estado) + '22' }">
              <UIcon 
                :name="getEstadoIcon(form.estado)" 
                class="w-6 h-6" 
                :style="{ color: getEstadoColor(form.estado) }" 
              />
            </div>
            <div>
              <h1 class="page-title">Detalle de Justificación</h1>
              <p class="page-subtitle">
                <span class="status-badge-detail" :class="getStatusClass(form.estado)">
                  <UIcon :name="getEstadoIcon(form.estado)" class="w-3.5 h-3.5" />
                  {{ formatEstado(form.estado) }}
                </span>
                <span class="detail-date">{{ form.fecha_inicio ? formatDate(form.fecha_inicio) : '—' }}</span>
              </p>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando justificación...</p>
        </div>

        <template v-else>
          <!-- Detail Card -->
          <section class="detail-card">
            <div class="card-header">
              <div class="card-header-icon" :style="{ background: getEstadoColor(form.estado) + '22' }">
                <UIcon :name="getEstadoIcon(form.estado)" class="w-4 h-4" :style="{ color: getEstadoColor(form.estado) }" />
              </div>
              <div>
                <h3 class="card-title">Información de la Justificación</h3>
                <p class="card-subtitle">Detalles completos de la solicitud</p>
              </div>
            </div>

            <div class="detail-grid">
              <div class="detail-item">
                <span class="detail-label">Empleado</span>
                <div class="detail-value employee-value">
                  <div class="employee-avatar" :style="{ background: getEmployeeColor(form.empleado_nombre || '') }">
                    <span>{{ getInitials(form.empleado_nombre || '—') }}</span>
                  </div>
                  <span>{{ form.empleado_nombre || '—' }}</span>
                </div>
              </div>

              <div class="detail-item">
                <span class="detail-label">Motivo</span>
                <span class="detail-value">{{ form.motivo_nombre || '—' }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">Fecha de Inicio</span>
                <span class="detail-value font-mono-data">{{ form.fecha_inicio ? formatDate(form.fecha_inicio) : '—' }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">Fecha de Fin</span>
                <span class="detail-value font-mono-data">{{ form.fecha_fin ? formatDate(form.fecha_fin) : '—' }}</span>
              </div>

              <div class="detail-item full-width">
                <span class="detail-label">Descripción</span>
                <span class="detail-value description-text">{{ form.descripcion || '—' }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">Días</span>
                <span class="detail-value">{{ calcularDias(form.fecha_inicio, form.fecha_fin) }}</span>
              </div>

              <div class="detail-item">
                <span class="detail-label">Estado Actual</span>
                <span class="status-badge" :class="getStatusClass(form.estado)">
                  <UIcon :name="getEstadoIcon(form.estado)" class="w-3.5 h-3.5" />
                  {{ formatEstado(form.estado) }}
                </span>
              </div>
            </div>

            <!-- Status Update Section -->
            <div class="status-update-section">
              <h4 class="section-title">Actualizar Estado</h4>
              <div class="status-update-grid">
                <div class="form-group">
                  <label class="form-label">Nuevo Estado</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-flag" class="input-icon" />
                    <select v-model="form.estado" class="input-clinical">
                      <option value="pendiente">⏳ Pendiente</option>
                      <option value="aprobado">✅ Aprobado</option>
                      <option value="rechazado">❌ Rechazado</option>
                    </select>
                  </div>
                </div>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="error-banner">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
              {{ error }}
            </div>

            <!-- Actions -->
            <div class="detail-actions">
              <div class="action-group">
                <button 
                  class="btn-primary" 
                  :disabled="saving" 
                  @click="handleSave"
                >
                  <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                  {{ saving ? 'Guardando...' : 'Actualizar Estado' }}
                </button>
                <NuxtLink 
                  :to="`/sigarh/rrhh/justificaciones?tenant=${tenantId}`"
                  class="btn-secondary"
                >
                  <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
                  Volver al Listado
                </NuxtLink>
              </div>
            </div>
          </section>
        </template>
      </div>

      <!-- Sidebar Widgets -->
      <div class="justificacion-detail-sidebar">
        <!-- Status Widget -->
        <div class="widget widget-status">
          <div class="widget-header">
            <UIcon name="i-heroicons-information-circle" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Estado de la Solicitud</h4>
          </div>
          <div class="widget-content">
            <div class="status-display">
              <div class="status-icon-large" :style="{ background: getEstadoColor(form.estado) + '22' }">
                <UIcon :name="getEstadoIcon(form.estado)" class="w-8 h-8" :style="{ color: getEstadoColor(form.estado) }" />
              </div>
              <div class="status-info">
                <span class="status-label">Estado</span>
                <span class="status-value-large" :style="{ color: getEstadoColor(form.estado) }">
                  {{ formatEstado(form.estado) }}
                </span>
              </div>
            </div>

            <div class="status-timeline">
              <div class="timeline-item" :class="{ 'timeline-active': form.estado === 'pendiente' }">
                <div class="timeline-dot" :class="{ 'dot-active': form.estado === 'pendiente' }" />
                <span class="timeline-label">Pendiente</span>
              </div>
              <div class="timeline-line" :class="{ 'line-active': form.estado === 'aprobado' || form.estado === 'rechazado' }" />
              <div class="timeline-item" :class="{ 'timeline-active': form.estado === 'aprobado' || form.estado === 'rechazado' }">
                <div class="timeline-dot" :class="{ 'dot-active': form.estado === 'aprobado' || form.estado === 'rechazado' }" />
                <span class="timeline-label">{{ form.estado === 'rechazado' ? 'Rechazado' : 'Resuelto' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--navy)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Empleado</span>
              <span class="summary-value">{{ form.empleado_nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Motivo</span>
              <span class="summary-value">{{ form.motivo_nombre || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Días</span>
              <span class="summary-value font-mono-data">{{ calcularDias(form.fecha_inicio, form.fecha_fin) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Período</span>
              <span class="summary-value font-mono-data" style="font-size: 0.75rem;">
                {{ form.fecha_inicio ? formatDate(form.fecha_inicio) : '—' }}
                {{ form.fecha_fin ? `→ ${formatDate(form.fecha_fin)}` : '' }}
              </span>
            </div>
          </div>
        </div>

        <!-- Tip Widget -->
        <div class="widget widget-tip">
          <div class="widget-content">
            <div class="tip-content">
              <UIcon name="i-heroicons-light-bulb" class="tip-icon" style="color: var(--amber)" />
              <div>
                <p class="tip-title">Consejo</p>
                <p class="tip-text">
                  Actualiza el estado de la justificación para mantener un registro 
                  claro de las ausencias y permisos del personal.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats Widget -->
        <div class="widget widget-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Información Adicional</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Solicitud</span>
              <span class="stat-number font-mono-data" style="font-size: 0.75rem;">#{{ id }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Días solicitados</span>
              <span class="stat-number">{{ calcularDias(form.fecha_inicio, form.fecha_fin) }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Estado actual</span>
              <span class="stat-number" :style="{ color: getEstadoColor(form.estado) }">
                {{ formatEstado(form.estado) }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)

const loading = ref(true)
const saving = ref(false)
const error = ref('')

const form = reactive({
  empleado_nombre: '',
  motivo_nombre: '',
  fecha_inicio: '',
  fecha_fin: '',
  descripcion: '',
  estado: 'pendiente',
})

const getInitials = (name: string) => {
  if (!name || name === '—') return '?'
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getEmployeeColor = (name: string) => {
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

const formatDate = (date: string) => {
  if (!date) return '—'
  const d = new Date(date)
  return d.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const formatEstado = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'Pendiente',
    aprobado: 'Aprobado',
    rechazado: 'Rechazado'
  }
  return map[estado] || estado
}

const getEstadoIcon = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'i-heroicons-clock',
    aprobado: 'i-heroicons-check-circle',
    rechazado: 'i-heroicons-x-circle'
  }
  return map[estado] || 'i-heroicons-circle'
}

const getEstadoColor = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'var(--amber)',
    aprobado: 'var(--green)',
    rechazado: 'var(--alert)'
  }
  return map[estado] || 'var(--ink-soft)'
}

const getStatusClass = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'status-pendiente',
    aprobado: 'status-aprobado',
    rechazado: 'status-rechazado'
  }
  return map[estado] || 'status-default'
}

const calcularDias = (fechaInicio: string, fechaFin: string) => {
  if (!fechaInicio || !fechaFin) return '—'
  const inicio = new Date(fechaInicio)
  const fin = new Date(fechaFin)
  const diff = Math.ceil((fin.getTime() - inicio.getTime()) / (1000 * 60 * 60 * 24)) + 1
  return `${diff} día${diff > 1 ? 's' : ''}`
}

const handleSave = async () => {
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/rrhh/justificaciones/${id.value}`, {
      method: 'PATCH',
      body: { estado: form.estado }
    })
    router.push(`/sigarh/rrhh/justificaciones?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo actualizar el estado'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const data = await api<any>(`/sigarh/rrhh/justificaciones/${id.value}`)
    form.empleado_nombre = data.empleado_nombre || ''
    form.motivo_nombre = data.motivo_nombre || ''
    form.fecha_inicio = data.fecha_inicio
    form.fecha_fin = data.fecha_fin
    form.descripcion = data.descripcion || ''
    form.estado = data.estado || 'pendiente'
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar la justificación'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.justificacion-detail-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.justificacion-detail-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.justificacion-detail-main {
  min-width: 0;
}

.justificacion-detail-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Header */
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
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.status-badge-detail {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.detail-date {
  font-size: 0.8125rem;
  font-family: monospace;
}

/* Loading State */
.loading-state {
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

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Detail Card */
.detail-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.card-header-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.card-subtitle {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  margin: 0;
}

/* Detail Grid */
.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.75rem;
  border-radius: var(--radius);
  background: var(--mist);
}

.detail-label {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
}

.detail-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.employee-value {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.employee-avatar {
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

.description-text {
  white-space: pre-wrap;
  word-break: break-word;
}

/* Status Badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.8125rem;
  font-weight: 500;
}

.status-pendiente {
  background: var(--amber-soft);
  color: var(--amber);
}

.status-aprobado {
  background: var(--green-soft);
  color: var(--green);
}

.status-rechazado {
  background: var(--alert-soft);
  color: var(--alert);
}

.status-default {
  background: var(--mist);
  color: var(--ink-soft);
}

/* Status Update Section */
.status-update-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 1rem 0;
}

.status-update-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  max-width: 400px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--ink-soft);
}

.input-clinical {
  width: 100%;
  padding: 0.625rem 0.875rem;
  padding-left: 2.5rem;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.input-clinical:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
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
  margin-top: 1rem;
}

/* Actions */
.detail-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.action-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  background: var(--teal);
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: var(--teal-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink);
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--mist);
}

/* Widgets */
.widget {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  border: 1px solid var(--line);
}

.widget-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--line);
}

.widget-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.widget-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.widget-content {
  padding: 1rem 1.25rem;
}

/* Status Widget */
.status-display {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem;
  border-radius: var(--radius);
  background: var(--mist);
  margin-bottom: 1rem;
}

.status-icon-large {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.status-info {
  display: flex;
  flex-direction: column;
}

.status-label {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.status-value-large {
  font-size: 1.125rem;
  font-weight: 700;
}

/* Status Timeline */
.status-timeline {
  display: flex;
  align-items: center;
  padding: 0.5rem 0;
}

.timeline-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  opacity: 0.4;
  transition: all 0.3s ease;
}

.timeline-item.timeline-active {
  opacity: 1;
}

.timeline-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--line);
  transition: all 0.3s ease;
}

.timeline-dot.dot-active {
  background: var(--teal);
  box-shadow: 0 0 0 4px var(--teal-soft);
}

.timeline-label {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.timeline-line {
  flex: 1;
  height: 2px;
  background: var(--line);
  margin: 0 0.5rem;
  transition: all 0.3s ease;
}

.timeline-line.line-active {
  background: var(--teal);
}

/* Summary Widget */
.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
  border-bottom: 1px solid var(--line);
}

.summary-item:last-of-type {
  border-bottom: none;
}

.summary-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.summary-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  max-width: 60%;
  text-align: right;
  word-break: break-word;
}

.summary-divider {
  height: 1px;
  background: var(--line);
  margin: 0.5rem 0;
}

/* Tip Widget */
.widget-tip {
  background: var(--amber-soft);
  border-color: var(--amber-soft);
}

.tip-content {
  display: flex;
  gap: 0.75rem;
}

.tip-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.tip-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.25rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tip-text {
  font-size: 0.8125rem;
  color: var(--ink);
  margin: 0;
  line-height: 1.5;
}

/* Stats Widget */
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
}

.stat-item + .stat-item {
  border-top: 1px solid var(--line);
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.stat-number {
  font-size: 1rem;
  font-weight: 700;
  color: var(--ink);
}

/* Responsive */
@media (max-width: 1024px) {
  .justificacion-detail-grid {
    grid-template-columns: 1fr;
  }

  .justificacion-detail-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .justificacion-detail-container {
    padding: 1rem;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .justificacion-detail-sidebar {
    grid-template-columns: 1fr;
  }

  .action-group {
    flex-direction: column;
    width: 100%;
  }

  .action-group > * {
    width: 100%;
    justify-content: center;
  }

  .page-subtitle {
    flex-direction: column;
    align-items: flex-start;
  }

  .status-update-grid {
    max-width: 100%;
  }

  .status-timeline {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .status-display {
    flex-direction: column;
    text-align: center;
  }

  .summary-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .summary-value {
    max-width: 100%;
    text-align: left;
  }

  .timeline-line {
    min-width: 20px;
  }
}
</style>