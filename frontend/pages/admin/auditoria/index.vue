<template>
  <div class="auditoria-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-clipboard-document-list" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h1 class="page-title">Auditoría del ERP</h1>
          <p class="page-subtitle">
            Registro de acciones a nivel de todo el sistema: creación/edición de hospitales, catálogo de módulos, e inicios de sesión.
          </p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="refreshData">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': refreshing }" />
          Refrescar
        </button>
        <button class="btn-secondary" @click="exportData">
          <UIcon name="i-heroicons-arrow-down-tray" class="w-4 h-4" />
          Exportar
        </button>
      </div>
    </div>

    <div v-if="fallbackPendientes > 0 || fallbackPendientesEmergencia > 0" class="form-card" style="padding: 0.875rem 1.25rem; margin-bottom: 1rem; display: flex; align-items: center; gap: 0.75rem; background: var(--alert-soft); border-color: var(--alert);">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5 shrink-0" style="color: var(--alert)" />
      <div style="flex: 1">
        <p v-if="fallbackPendientes > 0" style="color: var(--alert); font-size: 0.875rem; margin: 0">
          {{ fallbackPendientes }} evento{{ fallbackPendientes === 1 ? '' : 's' }} de auditoría no se pudo{{ fallbackPendientes === 1 ? '' : 'ieron' }} registrar y espera{{ fallbackPendientes === 1 ? '' : 'n' }} reintento.
        </p>
        <p v-if="fallbackPendientesEmergencia > 0" style="color: var(--alert); font-size: 0.875rem; margin: 0; font-weight: 600">
          {{ fallbackPendientesEmergencia }} evento{{ fallbackPendientesEmergencia === 1 ? '' : 's' }} atrapado{{ fallbackPendientesEmergencia === 1 ? '' : 's' }} en el archivo de emergencia (la BD central estuvo inalcanzable).
        </p>
        <p v-if="fallbackUltimoReintento" style="color: var(--ink-soft); font-size: 0.8125rem; margin: 0.25rem 0 0">
          Último reintento: {{ fallbackUltimoReintento.recuperados }} recuperado{{ fallbackUltimoReintento.recuperados === 1 ? '' : 's' }}<span v-if="fallbackUltimoReintento.errores > 0">, {{ fallbackUltimoReintento.errores }} con error real (revisar logs del backend)</span>.
        </p>
      </div>
      <button class="btn-secondary" :disabled="reintentandoFallback" @click="reintentarFallback">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': reintentandoFallback }" />
        Reintentar ahora
      </button>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Events -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
        <div class="stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-clipboard-document-list" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ logs.length }}</span>
          <span class="stat-label">Total Eventos</span>
        </div>
      </div>

      <!-- Today's Events -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
        <div class="stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ todayEvents }}</span>
          <span class="stat-label">Eventos Hoy</span>
        </div>
      </div>

      <!-- Unique Users -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
        <div class="stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ uniqueUsers }}</span>
          <span class="stat-label">Usuarios Activos</span>
        </div>
      </div>

      <!-- Top Action -->
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

    <!-- Main Table Card -->
    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
      <!-- Table Header with Search & Filters -->
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
          <span class="result-count">{{ total }} resultados</span>
        </div>
      </div>

      <!-- Loading State -->
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando registros de auditoría...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="refreshData">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="logs.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-clipboard-document-list" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay registros de auditoría</h3>
        <p style="color: var(--ink-soft)">Los eventos del sistema aparecerán aquí</p>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="auditoria-table">
          <thead>
            <tr>
              <th class="col-date">
                <span class="th-content">Fecha</span>
              </th>
              <th class="col-user">
                <span class="th-content">Usuario</span>
              </th>
              <th class="col-action">
                <span class="th-content">Acción</span>
              </th>
              <th class="col-type">
                <span class="th-content">Tipo</span>
              </th>
              <th class="col-model">
                <span class="th-content">Sobre</span>
              </th>
              <th class="col-ip">
                <span class="th-content">IP</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="log in logs"
              :key="log.id"
              class="table-row"
              tabindex="0"
              role="button"
              :aria-label="`Ver detalle del evento: ${log.description || log.action}`"
              @click="openModal(log)"
              @keydown.enter="openModal(log)"
              @keydown.space.prevent="openModal(log)"
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

      <!-- Table Footer with Pagination -->
      <div v-if="total > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ logs.length }}</strong> de <strong>{{ total }}</strong> registros
        </span>
        <div class="footer-actions">
          <button
            v-if="searchQuery || activeFilter !== 'all'"
            class="btn-secondary btn-sm"
            @click="clearFilters"
          >
            Limpiar filtros
          </button>
          <div class="pagination">
            <button
              class="page-btn"
              :disabled="currentPage === 1"
              @click="currentPage--"
            >
              <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
            </button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button
              class="page-btn"
              :disabled="currentPage === totalPages"
              @click="currentPage++"
            >
              <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Log Details Modal -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal" @keydown.esc="closeModal">
      <div
        ref="modalContentRef"
        class="modal-content"
        style="background: var(--paper); border-radius: var(--radius-lg)"
        role="dialog"
        aria-modal="true"
        aria-labelledby="audit-modal-title"
        tabindex="-1"
      >
        <div class="modal-header">
          <div class="modal-icon" :style="{ background: getTypeColor(selectedLog?.action || '') + '22' }">
            <UIcon
              :name="getTypeIcon(selectedLog?.action || '')"
              class="w-6 h-6"
              :style="{ color: getTypeColor(selectedLog?.action || '') }"
            />
          </div>
          <div>
            <h3 id="audit-modal-title" class="modal-title">Detalle del Evento</h3>
            <p class="modal-subtitle">{{ formatDateFull(selectedLog?.created_at || '') }}</p>
          </div>
          <button class="modal-close" @click="closeModal">
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
          <div v-if="selectedLog?.old_values || selectedLog?.new_values" class="log-diff-section">
            <div class="detail-grid">
              <div>
                <p class="detail-label">Valores anteriores</p>
                <pre class="log-diff">{{ pretty(selectedLog?.old_values) }}</pre>
              </div>
              <div>
                <p class="detail-label">Valores nuevos</p>
                <pre class="log-diff">{{ pretty(selectedLog?.new_values) }}</pre>
              </div>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="closeModal">Cerrar</button>
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
  old_values: Record<string, any> | null
  new_values: Record<string, any> | null
  ip_address: string | null
  created_at: string
}

const { api } = useApi()

interface Resumen {
  total: number
  eventos_hoy: number
  usuarios_unicos: number
  accion_mas_frecuente: string | null
  por_accion: Record<string, number>
}

// Antes se traian hasta 1000 filas de una vez y busqueda/filtro/paginacion
// pasaban enteros en el navegador sobre ese lote -- el historial real, mas
// alla de esas primeras filas, era invisible. Ahora cada cambio de pagina,
// busqueda o filtro le pide al servidor exactamente esa porcion (ver
// GET /admin/auditoria) y los widgets salen de un agregado aparte
// (GET /admin/auditoria/resumen) que si ve TODO el historial, no solo la
// pagina cargada.
const logs = ref<AuditLog[]>([])
const total = ref(0)
const resumen = ref<Resumen>({ total: 0, eventos_hoy: 0, usuarios_unicos: 0, accion_mas_frecuente: null, por_accion: {} })
const loading = ref(true)
const refreshing = ref(false)
const error = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const currentPage = ref(1)
const perPage = 15
const showModal = ref(false)
const selectedLog = ref<AuditLog | null>(null)
const modalContentRef = ref<HTMLElement | null>(null)
// Guarda que fila/elemento tenia el foco antes de abrir el modal -- sin
// esto, al cerrar con teclado (Escape o el boton Cerrar) el foco se pierde
// y salta al inicio del documento en vez de volver a donde estaba el
// usuario.
let elementoAntesDelModal: HTMLElement | null = null

const filters = computed(() => {
  const counts = resumen.value.por_accion || {}
  return [
    { label: 'Todos', value: 'all', count: resumen.value.total },
    { label: 'Login', value: 'login', count: counts['login'] || 0 },
    { label: 'Logout', value: 'logout', count: counts['logout'] || 0 },
    { label: 'Creados', value: 'created', count: counts['created'] || 0 },
    { label: 'Actualizados', value: 'updated', count: counts['updated'] || 0 },
    { label: 'Eliminados', value: 'deleted', count: counts['deleted'] || 0 },
  ]
})

const todayEvents = computed(() => resumen.value.eventos_hoy)
const uniqueUsers = computed(() => resumen.value.usuarios_unicos)
const topAction = computed(() => resumen.value.accion_mas_frecuente || '—')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage)))

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
  elementoAntesDelModal = document.activeElement as HTMLElement | null
  selectedLog.value = log
  showModal.value = true
  // El modal recien se monta en el DOM despues de este tick -- sin
  // nextTick, modalContentRef.value todavia apunta al render anterior (o
  // null) y el foco no se mueve.
  nextTick(() => modalContentRef.value?.focus())
}

const closeModal = () => {
  showModal.value = false
  elementoAntesDelModal?.focus()
}

const pretty = (val: Record<string, any> | null | undefined) => {
  if (!val) return '(vacío)'
  return JSON.stringify(val, null, 2)
}

const clearFilters = () => {
  searchQuery.value = ''
  activeFilter.value = 'all'
  currentPage.value = 1
  loadData()
}

const refreshData = async () => {
  refreshing.value = true
  await Promise.all([loadData(), loadResumen()])
  refreshing.value = false
}

// Exporta solo la pagina visible -- para el historial completo esta
// Reportes > Exportar Datos, que ya trae proteccion contra inyeccion de
// formulas de Excel/Sheets (ver pages/admin/reportes/exportar.vue).
const celdaSegura = (v: string) => /^[=+\-@\t]/.test(v) ? `'${v}` : v
const exportData = () => {
  const headers = ['Fecha', 'Usuario', 'Acción', 'Descripción', 'Modelo', 'IP']
  const rows = logs.value.map(l => [
    formatDateFull(l.created_at),
    l.user_name || 'Sistema',
    l.action,
    l.description || '',
    l.model || '',
    l.ip_address || ''
  ])

  const csv = [headers, ...rows]
    .map(r => r.map(v => `"${celdaSegura(String(v ?? '')).replace(/"/g, '""')}"`).join(','))
    .join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `auditoria_pagina_${currentPage.value}_${new Date().toISOString().slice(0,10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

const loadData = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams({
      only_global: 'true',
      limit: String(perPage),
      offset: String((currentPage.value - 1) * perPage),
    })
    if (searchQuery.value.trim()) params.set('q', searchQuery.value.trim())
    if (activeFilter.value !== 'all') params.set('action', activeFilter.value)
    const resp = await api<{ items: AuditLog[]; total: number }>(`/admin/auditoria?${params}`)
    logs.value = resp.items
    total.value = resp.total
  } catch (e: any) {
    error.value = apiErr(e, 'Error de conexión')
  } finally {
    loading.value = false
  }
}

const loadResumen = async () => {
  try {
    resumen.value = await api<Resumen>('/admin/auditoria/resumen?only_global=true')
  } catch {
    // los widgets no son criticos: si fallan, se quedan en sus valores por defecto
  }
}

const fallbackPendientes = ref(0)
// Eventos atrapados en el archivo de emergencia (ver
// _FALLBACK_ARCHIVO_ULTIMO_RECURSO en backend/app/core/audit.py) -- solo
// aparece si la BD central estuvo totalmente inalcanzable en algun
// momento. Antes esta pantalla solo leia `pendientes` (la tabla), asi que
// podia mostrar 0 pendientes aunque hubiera eventos atascados aca.
const fallbackPendientesEmergencia = ref(0)
const reintentandoFallback = ref(false)
// Resultado del ultimo reintento manual: solo se conoce justo despues de
// llamar a /fallback/reintentar (no hay un contador persistente de errores
// en el backend), asi que se limpia en cada carga de estado nueva.
const fallbackUltimoReintento = ref<{ recuperados: number; errores: number } | null>(null)

const loadFallbackEstado = async () => {
  try {
    const r = await api<{ pendientes: number; pendientes_emergencia: number }>('/admin/auditoria/fallback')
    fallbackPendientes.value = r.pendientes
    fallbackPendientesEmergencia.value = r.pendientes_emergencia
  } catch {
    // no bloquea el resto de la pantalla si falla esta consulta puntual
  }
}

const reintentarFallback = async () => {
  reintentandoFallback.value = true
  fallbackUltimoReintento.value = null
  try {
    const r = await api<{ recuperados: number; errores: number }>('/admin/auditoria/fallback/reintentar', { method: 'POST' })
    fallbackUltimoReintento.value = { recuperados: r.recuperados, errores: r.errores }
    await Promise.all([loadFallbackEstado(), loadData(), loadResumen()])
  } catch {
    // si el reintento mismo falla, el contador se vuelve a pedir igual
    await loadFallbackEstado()
  } finally {
    reintentandoFallback.value = false
  }
}

let searchDebounce: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, () => {
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => { currentPage.value = 1; loadData() }, 400)
})
watch(activeFilter, () => { currentPage.value = 1; loadData() })
watch(currentPage, () => loadData())

onMounted(() => {
  loadData()
  loadResumen()
  loadFallbackEstado()
})
</script>

<style scoped>

/* Page Header */

/* Widgets Grid */

/* Table Card */

/* Table States */

/* Table Styles */

/* Date Cell */

/* User Cell */

/* Action Text */

/* Type Badge */

/* Model Text */

/* IP Text */

/* Table Footer */

/* Modal */

.modal-content {
  max-width: 520px;
  width: 100%;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .auditoria-container {
    padding: 1rem 1.5rem;
  }

  .page-header {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
  }

  .header-actions .btn-secondary {
    flex: 1;
    justify-content: center;
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
  .auditoria-container {
    padding: 1rem;
  }

  .widgets-grid {
    grid-template-columns: 1fr 1fr;
  }

  .filter-group {
    flex-wrap: wrap;
  }

  .col-ip {
    min-width: 100px;
  }

  .col-action {
    min-width: 150px;
  }

  .table-footer {
    flex-direction: column;
    align-items: stretch;
    gap: 0.75rem;
  }

  .footer-actions {
    flex-wrap: wrap;
    justify-content: space-between;
  }

  .pagination {
    margin-left: auto;
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

  .auditoria-table td,
  .auditoria-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }

  .col-date {
    min-width: 100px;
  }

  .col-user {
    min-width: 100px;
  }

  .detail-grid {
    grid-template-columns: 1fr;
  }

  .modal-content {
    margin: 1rem;
  }
}
</style>