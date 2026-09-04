<!-- frontend/pages/admin/auditoria/hospital.vue -->
<template>
  <div class="auditoria-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h1 class="page-title">Auditoría por Hospital</h1>
          <p class="page-subtitle">
            Registro de acciones de un hospital específico, incluyendo ambos paneles: SIGARH y Administrativo.
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" :disabled="!tenantId" @click="refreshData">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': refreshing }" />
          Refrescar
        </button>
        <button class="btn-secondary" :disabled="!tenantId" @click="exportData">
          <UIcon name="i-heroicons-arrow-down-tray" class="w-4 h-4" />
          Exportar
        </button>
      </div>
    </div>

    <!-- Selector de hospital -->
    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1.25rem 1.5rem; margin-bottom: 1.5rem;">
      <label class="detail-label" style="display:block; margin-bottom: 0.5rem;">Selecciona un hospital</label>
      <select
        v-model="tenantId"
        class="search-input"
        style="max-width: 400px; border: 1px solid var(--line); background: var(--paper);"
        @change="onTenantChange"
      >
        <option value="" disabled>Elige un hospital...</option>
        <option v-for="h in hospitales" :key="h.id" :value="h.id">
          {{ h.name }} ({{ h.domain }})
        </option>
      </select>
    </div>

    <!-- Si no hay hospital seleccionado -->
    <div v-if="!tenantId" class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card);">
      <div class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-building-office-2" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">Selecciona un hospital</h3>
        <p style="color: var(--ink-soft)">Elige un hospital arriba para ver su auditoría</p>
      </div>
    </div>

    <template v-else>
      <!-- Widgets -->
      <div class="widgets-grid">
        <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
          <div class="stat-icon" style="background: var(--navy-soft)">
            <UIcon name="i-heroicons-clipboard-document-list" class="w-5 h-5" style="color: var(--navy)" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ logs.length }}</span>
            <span class="stat-label">Total Eventos</span>
          </div>
        </div>

        <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
          <div class="stat-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ todayEvents }}</span>
            <span class="stat-label">Eventos Hoy</span>
          </div>
        </div>

        <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
          <div class="stat-icon" style="background: var(--purple-soft)">
            <UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--purple)" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ uniqueUsers }}</span>
            <span class="stat-label">Usuarios Activos</span>
          </div>
        </div>

        <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
          <div class="stat-icon" style="background: var(--amber-soft)">
            <UIcon name="i-heroicons-fire" class="w-5 h-5" style="color: var(--amber)" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ topAction }}</span>
            <span class="stat-label">Acción Más Frecuente</span>
          </div>
        </div>
      </div>

      <!-- Tabla -->
      <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
        <div class="table-toolbar">
          <div class="toolbar-left">
            <div class="search-wrapper">
              <UIcon name="i-heroicons-magnifying-glass" class="search-icon" />
              <input
                v-model="searchQuery"
                type="text"
                placeholder="Buscar por usuario, acción o descripción..."
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
            <span class="result-count">{{ filteredLogs.length }} resultados</span>
          </div>
        </div>

        <div v-if="loading" class="table-loading">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando registros de auditoría...</p>
        </div>

        <div v-else-if="error" class="table-error">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
          <p style="color: var(--alert)">{{ error }}</p>
          <button class="btn-secondary" @click="refreshData">Reintentar</button>
        </div>

        <div v-else-if="filteredLogs.length === 0" class="table-empty">
          <div class="empty-icon" style="background: var(--mist)">
            <UIcon name="i-heroicons-clipboard-document-list" class="w-12 h-12" style="color: var(--ink-soft)" />
          </div>
          <h3 style="color: var(--ink)">No hay registros de auditoría</h3>
          <p style="color: var(--ink-soft)">Los eventos de este hospital aparecerán aquí</p>
        </div>

        <div v-else class="table-responsive">
          <table class="auditoria-table">
            <thead>
              <tr>
                <th class="col-date"><span class="th-content">Fecha</span></th>
                <th class="col-user"><span class="th-content">Usuario</span></th>
                <th class="col-action"><span class="th-content">Acción</span></th>
                <th class="col-type"><span class="th-content">Tipo</span></th>
                <th class="col-model"><span class="th-content">Sobre</span></th>
                <th class="col-ip"><span class="th-content">IP</span></th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="log in paginatedLogs"
                :key="log.id"
                class="table-row"
                @click="openModal(log)"
              >
                <td class="col-date">
                  <div class="date-cell">
                    <span class="date-day">{{ formatDateDay(log.created_at) }}</span>
                    <span class="date-time">{{ formatDateTime(log.created_at) }}</span>
                  </div>
                </td>
                <td class="col-user">
                  <div class="user-cell">
                    <div class="user-avatar" :style="{ background: getUserColor(log.user_name || 'Sistema') }">
                      <span>{{ getUserInitials(log.user_name || 'S') }}</span>
                    </div>
                    <span class="user-name">{{ log.user_name || 'Sistema' }}</span>
                  </div>
                </td>
                <td class="col-action">
                  <span class="action-text">{{ log.description || log.action }}</span>
                </td>
                <td class="col-type">
                  <span class="type-badge" :class="getTypeClass(log.action)">
                    <UIcon :name="getTypeIcon(log.action)" class="w-3.5 h-3.5" />
                    {{ log.action }}
                  </span>
                </td>
                <td class="col-model">
                  <span class="model-text">{{ log.model || '—' }}</span>
                </td>
                <td class="col-ip">
                  <span class="ip-text font-mono-data">{{ log.ip_address || '—' }}</span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="filteredLogs.length > 0" class="table-footer">
          <span class="footer-info">
            Mostrando <strong>{{ paginatedLogs.length }}</strong> de <strong>{{ filteredLogs.length }}</strong> registros
            <span v-if="filteredLogs.length < logs.length">(filtrados)</span>
          </span>
          <div class="footer-actions">
            <button
              v-if="filteredLogs.length < logs.length || searchQuery || activeFilter !== 'all'"
              class="btn-secondary btn-sm"
              @click="clearFilters"
            >
              Limpiar filtros
            </button>
            <div class="pagination">
              <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
                <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
              </button>
              <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
              <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
                <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </template>

    <!-- Modal de detalle -->
    <div v-if="showModal" class="modal-overlay" @click.self="showModal = false">
      <div class="modal-content" style="background: var(--paper); border-radius: var(--radius-lg)">
        <div class="modal-header">
          <div class="modal-icon" :style="{ background: getTypeColor(selectedLog?.action || '') + '22' }">
            <UIcon
              :name="getTypeIcon(selectedLog?.action || '')"
              class="w-6 h-6"
              :style="{ color: getTypeColor(selectedLog?.action || '') }"
            />
          </div>
          <div>
            <h3 class="modal-title">Detalle del Evento</h3>
            <p class="modal-subtitle">{{ formatDateFull(selectedLog?.created_at || '') }}</p>
          </div>
          <button class="modal-close" @click="showModal = false">
            <UIcon name="i-heroicons-x-mark" class="w-5 h-5" style="color: var(--ink-soft)" />
          </button>
        </div>
        <div class="modal-body">
          <div class="detail-grid">
            <div class="detail-item">
              <span class="detail-label">Usuario</span>
              <span class="detail-value">{{ selectedLog?.user_name || 'Sistema' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Acción</span>
              <span class="type-badge" :class="getTypeClass(selectedLog?.action || '')">
                <UIcon :name="getTypeIcon(selectedLog?.action || '')" class="w-3.5 h-3.5" />
                {{ selectedLog?.action }}
              </span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">Descripción</span>
              <span class="detail-value">{{ selectedLog?.description || selectedLog?.action || '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">Modelo</span>
              <span class="detail-value">{{ selectedLog?.model || '—' }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">IP Address</span>
              <span class="detail-value font-mono-data">{{ selectedLog?.ip_address || '—' }}</span>
            </div>
            <div class="detail-item full-width">
              <span class="detail-label">ID</span>
              <span class="detail-value font-mono-data" style="font-size: 0.75rem; color: var(--ink-soft)">{{ selectedLog?.id }}</span>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showModal = false">Cerrar</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface AuditLog {
  id: string
  user_name: string | null
  tenant_name: string | null
  action: string
  model: string | null
  description: string | null
  ip_address: string | null
  created_at: string
}

interface Hospital {
  id: string
  name: string
  domain: string
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const hospitales = ref<Hospital[]>([])
const tenantId = ref<string>((route.query.tenant as string) || '')

const logs = ref<AuditLog[]>([])
const loading = ref(true)
const refreshing = ref(false)
const error = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const currentPage = ref(1)
const perPage = 15
const showModal = ref(false)
const selectedLog = ref<AuditLog | null>(null)

const actionTypes = ['login', 'logout', 'login_failed', 'created', 'updated', 'deleted']

const filters = computed(() => {
  const counts: Record<string, number> = {}
  actionTypes.forEach(type => {
    counts[type] = logs.value.filter(l => l.action === type).length
  })
  counts['all'] = logs.value.length

  return [
    { label: 'Todos', value: 'all', count: counts['all'] },
    { label: 'Login', value: 'login', count: counts['login'] || 0 },
    { label: 'Logout', value: 'logout', count: counts['logout'] || 0 },
    { label: 'Creados', value: 'created', count: counts['created'] || 0 },
    { label: 'Actualizados', value: 'updated', count: counts['updated'] || 0 },
    { label: 'Eliminados', value: 'deleted', count: counts['deleted'] || 0 },
  ]
})

const todayEvents = computed(() => {
  const today = new Date().toDateString()
  return logs.value.filter(l => new Date(l.created_at).toDateString() === today).length
})

const uniqueUsers = computed(() => {
  return new Set(logs.value.map(l => l.user_name).filter(Boolean)).size
})

const topAction = computed(() => {
  if (!logs.value.length) return '—'
  const counts: Record<string, number> = {}
  logs.value.forEach(l => {
    counts[l.action] = (counts[l.action] || 0) + 1
  })
  let maxAction = ''
  let maxCount = 0
  Object.entries(counts).forEach(([action, count]) => {
    if (count > maxCount) {
      maxCount = count
      maxAction = action
    }
  })
  return maxAction || '—'
})

const filteredLogs = computed(() => {
  let result = logs.value

  if (activeFilter.value !== 'all') {
    result = result.filter(l => l.action === activeFilter.value)
  }

  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(l =>
      l.user_name?.toLowerCase().includes(query) ||
      l.action?.toLowerCase().includes(query) ||
      l.description?.toLowerCase().includes(query) ||
      l.model?.toLowerCase().includes(query)
    )
  }

  return result
})

const totalPages = computed(() => Math.ceil(filteredLogs.value.length / perPage))

const paginatedLogs = computed(() => {
  const start = (currentPage.value - 1) * perPage
  return filteredLogs.value.slice(start, start + perPage)
})

const formatDateDay = (date: string) => {
  return new Date(date).toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const formatDateTime = (date: string) => {
  return new Date(date).toLocaleTimeString('es-PE', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const formatDateFull = (date: string) => {
  return new Date(date).toLocaleString('es-PE', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

const getUserInitials = (name: string) => {
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getUserColor = (name: string) => {
  const colors = [
    'var(--teal-soft)',
    'var(--purple-soft)',
    'var(--navy-soft)',
    'var(--amber-soft)',
    'var(--green-soft)',
    'var(--pink-soft)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const getTypeClass = (action: string) => {
  const map: Record<string, string> = {
    login: 'type-login',
    logout: 'type-logout',
    login_failed: 'type-failed',
    created: 'type-created',
    updated: 'type-updated',
    deleted: 'type-deleted',
  }
  return map[action] || 'type-default'
}

const getTypeIcon = (action: string) => {
  const map: Record<string, string> = {
    login: 'i-heroicons-arrow-right-on-rectangle',
    logout: 'i-heroicons-arrow-left-on-rectangle',
    login_failed: 'i-heroicons-x-circle',
    created: 'i-heroicons-plus-circle',
    updated: 'i-heroicons-pencil-circle',
    deleted: 'i-heroicons-trash',
  }
  return map[action] || 'i-heroicons-circle'
}

const getTypeColor = (action: string) => {
  const map: Record<string, string> = {
    login: 'var(--teal)',
    logout: 'var(--ink-soft)',
    login_failed: 'var(--alert)',
    created: 'var(--green)',
    updated: 'var(--amber)',
    deleted: 'var(--alert)',
  }
  return map[action] || 'var(--ink-soft)'
}

const openModal = (log: AuditLog) => {
  selectedLog.value = log
  showModal.value = true
}

const clearFilters = () => {
  searchQuery.value = ''
  activeFilter.value = 'all'
  currentPage.value = 1
}

const onTenantChange = () => {
  router.replace({ query: { ...route.query, tenant: tenantId.value } })
  currentPage.value = 1
  loadLogs()
}

const refreshData = async () => {
  refreshing.value = true
  await loadLogs()
  refreshing.value = false
}

const exportData = () => {
  const headers = ['Fecha', 'Usuario', 'Acción', 'Descripción', 'Modelo', 'IP']
  const rows = filteredLogs.value.map(l => [
    formatDateFull(l.created_at),
    l.user_name || 'Sistema',
    l.action,
    l.description || '',
    l.model || '',
    l.ip_address || ''
  ])

  const csv = [headers.join(','), ...rows.map(r => r.join(','))].join('\n')
  const blob = new Blob([csv], { type: 'text/csv' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `auditoria_hospital_${tenantId.value}_${new Date().toISOString().slice(0,10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

const loadHospitales = async () => {
  try {
    hospitales.value = await api<Hospital[]>('/admin/hospitales')
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar la lista de hospitales'
  }
}

const loadLogs = async () => {
  if (!tenantId.value) {
    logs.value = []
    return
  }
  loading.value = true
  error.value = ''
  try {
    logs.value = await api<AuditLog[]>(`/admin/auditoria/hospital/${tenantId.value}?limit=1000`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadHospitales()
  if (tenantId.value) {
    await loadLogs()
  } else {
    loading.value = false
  }
})
</script>

<style scoped>
.auditoria-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: flex-start;
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
  margin-top: 0.125rem;
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
  max-width: 600px;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
  flex-shrink: 0;
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

.btn-secondary:hover:not(:disabled) {
  background: var(--mist);
}

.btn-secondary:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

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

.table-responsive {
  overflow-x: auto;
}

.auditoria-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.auditoria-table thead {
  background: var(--mist);
}

.auditoria-table th {
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

.auditoria-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
}

.table-row {
  transition: background 0.15s ease;
  cursor: pointer;
}

.table-row:hover {
  background: var(--mist);
}

.col-date { width: 15%; }
.col-user { width: 16%; }
.col-action { width: 25%; }
.col-type { width: 12%; }
.col-model { width: 14%; }
.col-ip { width: 18%; }

.date-cell {
  display: flex;
  flex-direction: column;
}

.date-day {
  font-size: 0.8125rem;
  color: var(--ink);
}

.date-time {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  font-family: monospace;
}

.user-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.user-name {
  font-weight: 500;
  color: var(--ink);
}

.action-text {
  color: var(--ink);
  font-size: 0.8125rem;
}

.type-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.1875rem 0.625rem;
  border-radius: 20px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.type-login { background: var(--teal-soft); color: var(--teal); }
.type-logout { background: var(--mist); color: var(--ink-soft); }
.type-failed { background: var(--alert-soft); color: var(--alert); }
.type-created { background: var(--green-soft); color: var(--green); }
.type-updated { background: var(--amber-soft); color: var(--amber); }
.type-deleted { background: var(--alert-soft); color: var(--alert); }
.type-default { background: var(--mist); color: var(--ink-soft); }

.model-text {
  color: var(--ink-soft);
  font-size: 0.8125rem;
}

.ip-text {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

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
  align-items: center;
  gap: 0.75rem;
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.page-btn:hover:not(:disabled) {
  background: var(--mist);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  padding: 0 0.5rem;
}

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
  max-width: 520px;
  width: 100%;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1rem;
  position: relative;
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

.modal-subtitle {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

.modal-close {
  position: absolute;
  top: -0.25rem;
  right: -0.25rem;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--mist);
}

.modal-body {
  margin-bottom: 1.5rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.detail-item.full-width {
  grid-column: 1 / -1;
}

.detail-label {
  display: block;
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin-bottom: 0.25rem;
}

.detail-value {
  font-size: 0.875rem;
  color: var(--ink);
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

@media (max-width: 1200px) {
  .widgets-grid { grid-template-columns: repeat(2, 1fr); }
}

@media (max-width: 1024px) {
  .auditoria-container { padding: 1rem 1.5rem; }
  .page-header { flex-direction: column; }
  .header-actions { width: 100%; }
  .header-actions .btn-secondary { flex: 1; justify-content: center; }
  .table-toolbar { flex-direction: column; align-items: stretch; }
  .toolbar-left { flex-direction: column; align-items: stretch; }
  .search-wrapper { max-width: none; }
}

@media (max-width: 768px) {
  .auditoria-container { padding: 1rem; }
  .widgets-grid { grid-template-columns: 1fr 1fr; }
  .filter-group { flex-wrap: wrap; }
  .col-ip { min-width: 100px; }
  .col-action { min-width: 150px; }
  .table-footer { flex-direction: column; align-items: stretch; gap: 0.75rem; }
  .footer-actions { flex-wrap: wrap; justify-content: space-between; }
  .pagination { margin-left: auto; }
}

@media (max-width: 480px) {
  .widgets-grid { grid-template-columns: 1fr; }
  .filter-chip { font-size: 0.6875rem; padding: 0.25rem 0.5rem; }
  .table-responsive { margin: 0 -0.5rem; }
  .auditoria-table td,
  .auditoria-table th { padding: 0.5rem 0.625rem; font-size: 0.8125rem; }
  .col-date { min-width: 100px; }
  .col-user { min-width: 100px; }
  .detail-grid { grid-template-columns: 1fr; }
  .modal-content { margin: 1rem; }
}
</style>