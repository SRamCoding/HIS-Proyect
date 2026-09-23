<template>
  <div class="sigarh-index-container">

    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h1 class="page-title">Hospitales</h1>
          <p class="page-subtitle">Establecimientos registrados en la plataforma</p>
        </div>
      </div>
      <NuxtLink to="/admin/hospitales/create" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Hospital
      </NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ hospitales.length }}</div>
          <div class="sigarh-stat-label">Total Hospitales</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ activos }}</div>
          <div class="sigarh-stat-label">Activos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ inactivos }}</div>
          <div class="sigarh-stat-label">Inactivos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ promedioModulos }}</div>
          <div class="sigarh-stat-label">Modulos / Hospital</div>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="searchQuery" type="text" placeholder="Buscar hospital por nombre..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button v-for="filter in filters" :key="filter.value" class="sigarh-filter-btn"
              :class="{ active: activeFilter === filter.value }" @click="activeFilter = filter.value">
              {{ filter.label }} <span class="sigarh-filter-count">{{ filter.count }}</span>
            </button>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span class="sigarh-result-count">{{ filteredHospitales.length }} resultados</span>
          <button v-if="searchQuery || activeFilter !== 'all'" @click="searchQuery = ''; activeFilter = 'all'" class="sigarh-clear-btn">Limpiar</button>
        </div>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
        <p style="color: var(--ink-soft)">Cargando hospitales...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button @click="loadHospitales" class="btn-outline">Reintentar</button>
      </div>
      <div v-else-if="!filteredHospitales.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-building-office-2" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">No hay hospitales registrados</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Comienza registrando tu primer establecimiento</p>
        </div>
        <NuxtLink to="/admin/hospitales/create" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Crear Hospital
        </NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 22%">Hospital</th>
              <th style="width: 18%">Dominio</th>
              <th style="width: 12%">Nivel</th>
              <th style="width: 18%">Modulos</th>
              <th style="width: 12%">Estado</th>
              <th style="width: 18%; text-align: right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="hospital in filteredHospitales" :key="hospital.id">
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--mist)">
                    <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" style="color: var(--navy)" />
                  </div>
                  <span class="sigarh-item-name">{{ hospital.name }}</span>
                </div>
              </td>
              <td style="font-family: monospace; color: var(--ink-soft)">{{ hospital.domain }}</td>
              <td>
                <span v-if="hospital.hospital_level" class="sigarh-code-badge"
                  :style="{ background: getLevelColor(hospital.hospital_level), color: getContrastColor(getLevelColor(hospital.hospital_level)) }">
                  {{ hospital.hospital_level }}
                </span>
                <span v-else style="color: var(--ink-soft)">-</span>
              </td>
              <td>
                <div style="display: flex; align-items: center; gap: 0.75rem">
                  <span style="font-weight: 600; color: var(--ink); min-width: 24px">{{ hospital.active_modules?.length || 0 }}</span>
                  <div style="flex: 1; height: 4px; border-radius: 2px; background: var(--mist); overflow: hidden; min-width: 60px">
                    <div style="height: 100%; border-radius: 2px; transition: width 0.6s ease" :style="{ width: getModulePercentage(hospital) + '%', background: 'var(--teal)' }" />
                  </div>
                </div>
              </td>
              <td>
                <span v-if="hospital.provisioning_status === 'pendiente'" class="badge badge--neutral" title="Creando la base de datos y los catálogos iniciales">
                  <UIcon name="i-heroicons-arrow-path" class="w-3 h-3 animate-spin" style="display: inline; vertical-align: -1px" /> Aprovisionando...
                </span>
                <span v-else-if="hospital.provisioning_status === 'error'" class="badge badge--alert" :title="hospital.provisioning_error || 'Error al aprovisionar'">
                  Error al aprovisionar
                </span>
                <span v-else class="badge" :class="hospital.is_active ? 'badge--ok' : 'badge--neutral'">
                  {{ hospital.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink v-if="hospital.provisioning_status === 'error'" :to="`/admin/hospitales/${hospital.id}/reintentar`" class="sigarh-action-btn" title="Reintentar aprovisionamiento">
                    <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" style="color: var(--amber)" />
                  </NuxtLink>
                  <button class="sigarh-action-btn" title="Ver landing" :disabled="sinBaseFisica(hospital)" @click="irA(hospital, '')">
                    <UIcon name="i-heroicons-globe-alt" class="w-4 h-4" style="color: var(--navy)" />
                  </button>
                  <button class="sigarh-action-btn" title="Panel Hospitalario" :disabled="sinBaseFisica(hospital)" @click="irA(hospital, '/app')">
                    <UIcon name="i-heroicons-squares-2x2" class="w-4 h-4" style="color: var(--teal)" />
                  </button>
                  <button class="sigarh-action-btn" title="Panel SIGARH" :disabled="sinBaseFisica(hospital)" @click="irA(hospital, '/sigarh')">
                    <UIcon name="i-heroicons-folder-open" class="w-4 h-4" style="color: var(--purple)" />
                  </button>
                  <NuxtLink :to="`/admin/hospitales/${hospital.id}`" class="sigarh-action-btn" title="Editar hospital">
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--amber)" />
                  </NuxtLink>
                  <button class="sigarh-action-btn danger" :title="hospital.is_active ? 'Desactivar' : 'Activar'"
                    :disabled="togglingId === hospital.id || sinBaseFisica(hospital)" @click="handleToggle(hospital)">
                    <UIcon v-if="togglingId === hospital.id" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                    <UIcon v-else :name="hospital.is_active ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" style="color: var(--alert)" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">
          Mostrando <strong>{{ filteredHospitales.length }}</strong> de <strong>{{ hospitales.length }}</strong> hospitales
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Hospital {
  id: string
  name: string
  domain: string
  hospital_level?: string
  active_modules: string[]
  is_active: boolean
  created_at: string
  provisioning_status?: string
  provisioning_error?: string | null
}

const { api } = useApi()

const hospitales = ref<Hospital[]>([])
const loading = ref(true)
const error = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const togglingId = ref<string | null>(null)

const levelColors: Record<string, string> = {
  'I-1': '#6b7280', 'I-2': '#6b7280', 'I-3': '#6b7280',
  'II-1': '#3b82f6', 'II-2': '#3b82f6',
  'III-1': '#8b5cf6', 'III-2': '#8b5cf6',
  'IV-1': '#ec4899', 'IV-2': '#ec4899',
}

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: hospitales.value.length },
  { label: 'Activos', value: 'active', count: activos.value },
  { label: 'Inactivos', value: 'inactive', count: inactivos.value },
])

const activos = computed(() => hospitales.value.filter(h => h.is_active).length)
const inactivos = computed(() => hospitales.value.filter(h => !h.is_active).length)

const promedioModulos = computed(() => {
  if (!hospitales.value.length) return 0
  const total = hospitales.value.reduce((sum, h) => sum + (h.active_modules?.length ?? 0), 0)
  return Math.round(total / hospitales.value.length)
})

const filteredHospitales = computed(() => {
  let result = hospitales.value
  if (activeFilter.value === 'active') result = result.filter(h => h.is_active)
  else if (activeFilter.value === 'inactive') result = result.filter(h => !h.is_active)
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(h => h.name.toLowerCase().includes(query) || h.domain.toLowerCase().includes(query))
  }
  return result
})

const getLevelColor = (level: string) => levelColors[level] || '#6b7280'

const getContrastColor = (hex: string) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#000000' : '#FFFFFF'
}

const getModulePercentage = (hospital: Hospital) => {
  const total = hospital.active_modules?.length || 0
  return Math.min((total / 20) * 100, 100)
}

const sinBaseFisica = (hospital: Hospital) =>
  hospital.provisioning_status === 'pendiente' || hospital.provisioning_status === 'error'

const irA = (hospital: Hospital, path: string) => {
  const destino = path === '/sigarh' ? '/sigarh/login' : path === '/app' ? '/app/login' : path
  // ".local" es el TLD reservado (RFC 6762) que usan los hospitales sin
  // dominio publico real todavia (aprovisionados como placeholder, ej.
  // hospital-lima.erp.local) -- nunca resuelve fuera de esta red, asi que
  // para esos casos la unica forma de entrar sigue siendo por query en el
  // dominio central. Un hospital con dominio real (ej.
  // hospital-reque.techquk.com) se abre directo ahi, SIN "?tenant=": el
  // middleware global (tenant-domain.global.ts) y el fallback por Host en
  // el backend (auth/router.py) ya resuelven el hospital por el propio
  // subdominio, igual que si alguien entrara a mano a esa URL.
  const tieneDominioReal = hospital.domain && !hospital.domain.toLowerCase().endsWith('.local')
  if (tieneDominioReal) {
    window.open(`https://${hospital.domain}${destino}`, '_blank')
    return
  }
  window.open(`${window.location.origin}${destino}?tenant=${hospital.id}`, '_blank')
}

const hayPendientes = computed(() => hospitales.value.some(h => h.provisioning_status === 'pendiente'))
let pollInterval: ReturnType<typeof setInterval> | null = null

// Mientras un hospital este "pendiente", el aprovisionamiento sigue corriendo
// en el worker de Celery en segundo plano -- sin este polling, la unica
// forma de enterarse de que ya termino era recargar la pagina a mano.
const detenerPolling = () => {
  if (pollInterval) { clearInterval(pollInterval); pollInterval = null }
}

const refrescarSilencioso = async () => {
  try { hospitales.value = await api<Hospital[]>('/admin/hospitales') }
  catch { /* un fallo puntual del polling no debe pisar el error visible de una carga explicita */ }
}

const iniciarPolling = () => {
  if (pollInterval) return
  pollInterval = setInterval(async () => {
    await refrescarSilencioso()
    if (!hayPendientes.value) detenerPolling()
  }, 5000)
}

const loadHospitales = async () => {
  loading.value = true
  error.value = ''
  try {
    hospitales.value = await api<Hospital[]>('/admin/hospitales')
    if (hayPendientes.value) iniciarPolling()
  }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}

const handleToggle = async (hospital: Hospital) => {
  togglingId.value = hospital.id
  try {
    await api(`/admin/hospitales/${hospital.id}/toggle`, { method: 'PATCH', body: { is_active: !hospital.is_active } })
    hospital.is_active = !hospital.is_active
  } catch (e: any) { error.value = apiErr(e, 'No se pudo actualizar el estado') }
  finally { togglingId.value = null }
}

onMounted(loadHospitales)
onUnmounted(detenerPolling)
</script>
