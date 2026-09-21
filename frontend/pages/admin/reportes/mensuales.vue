<template>
  <div class="auditoria-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-chart-bar" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Reporte Mensual del Sistema</h1>
          <p class="page-subtitle">Resumen de actividad del sistema por período.</p>
        </div>
      </div>
    </div>

    <!-- Filtros -->
    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1.25rem 1.5rem; margin-bottom: 1.5rem; display: flex; flex-wrap: wrap; align-items: end; gap: 1rem;">
      <div>
        <label class="detail-label">Hospital</label>
        <select v-model="tenantFilter" class="input-clinical" @change="cargar">
          <option value="">Todos los hospitales</option>
          <option v-for="h in hospitalesOpciones" :key="h.id" :value="h.id">{{ h.hospital_name }}</option>
        </select>
      </div>
      <div>
        <label class="detail-label">Mes</label>
        <select v-model="mes" class="input-clinical" @change="cargar">
          <option v-for="(nombre, i) in meses" :key="i" :value="String(i + 1).padStart(2, '0')">{{ nombre }}</option>
        </select>
      </div>
      <div>
        <label class="detail-label">Año</label>
        <select v-model="anio" class="input-clinical" @change="cargar">
          <option v-for="y in anios" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="table-loading" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg);">
      <div class="loading-spinner">
        <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
      </div>
      <p style="color: var(--ink-soft)">Cargando reporte...</p>
    </div>
    <div v-else-if="error" class="table-error" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg);">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
      <p style="color: var(--alert)">{{ error }}</p>
    </div>

    <template v-else-if="data">
      <!-- KPIs principales -->
      <div class="widgets-grid">
        <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--navy)">
          <div class="stat-icon" style="background: var(--navy-soft)">
            <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--navy)" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ data.total_hospitales_activos }}</span>
            <span class="stat-label">Hospitales Activos <span class="scope-tag scope-tag--actual">hoy</span></span>
          </div>
        </div>
        <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
          <div class="stat-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-user-plus" class="w-5 h-5" style="color: var(--teal)" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ data.pacientes_nuevos_total }}</span>
            <span class="stat-label">Pacientes Nuevos <span class="scope-tag scope-tag--periodo">del mes</span></span>
          </div>
        </div>
        <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
          <div class="stat-icon" style="background: var(--purple-soft)">
            <UIcon name="i-heroicons-plus-circle" class="w-5 h-5" style="color: var(--purple)" />
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ data.hospitales_registrados_periodo.length }}</span>
            <span class="stat-label">Hospitales Registrados <span class="scope-tag scope-tag--periodo">del mes</span></span>
          </div>
        </div>
        <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
          <div class="stat-icon" style="background: var(--amber-soft)">
            <UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--amber)" />
          </div>
          <div class="stat-content">
            <span class="stat-value" :style="data.usuarios_centrales_registrados === null ? { color: 'var(--ink-soft)', fontSize: '1.1rem' } : {}">
              {{ data.usuarios_centrales_registrados === null ? 'No aplica' : data.usuarios_centrales_registrados }}
            </span>
            <span class="stat-label">
              Usuarios Centrales Nuevos <span class="scope-tag scope-tag--periodo">del mes</span>
              <span v-if="data.usuarios_centrales_registrados === null" class="ip-text" style="display: block; font-weight: 400; text-transform: none;">no pertenecen a un hospital puntual</span>
            </span>
          </div>
        </div>
      </div>

      <!-- Aclaracion de alcance: que es "estado actual" y que es "del mes" -->
      <div v-if="data.es_estado_actual" class="report-note">
        <strong>Nota:</strong> "Hospitales Activos" y las columnas Usuarios/Módulos/Estado de la tabla reflejan el estado <strong>actual</strong> del sistema, no como estaba durante {{ meses[Number(mes) - 1] }} de {{ anio }}. Solo "Pacientes Nuevos", "Hospitales Registrados" y "Registrado" son datos reales de ese período.
        <span v-if="data.pacientes_solo_hospitales_activos"> "Pacientes Nuevos" tampoco incluye hospitales que hoy están inactivos, aunque hayan tenido pacientes reales en {{ meses[Number(mes) - 1] }}: si se desactiva un hospital, el total de meses pasados puede cambiar.</span>
      </div>

      <!-- Aviso de datos parciales: algún hospital no respondió -->
      <div v-if="data.es_parcial" class="report-note" style="background: var(--alert-soft); border-color: var(--alert); color: var(--alert);">
        <strong>Dato parcial:</strong> se pudo consultar {{ data.hospitales_consultados }} de {{ data.hospitales_totales }} hospitales.
        Los totales de pacientes/usuarios no incluyen los hospitales marcados como "No se pudo consultar" en la tabla de abajo.
      </div>

      <!-- Aviso de módulos pendientes -->
      <div class="report-note">
        <strong>Nota:</strong> Citas, emergencias y altas ya están implementadas en el sistema, pero este reporte todavía no las agrega como métricas. Se incorporarán en una próxima iteración de este reporte.
      </div>

      <!-- Cobertura de módulos -->
      <div class="report-section">
        <h2 class="report-section-title">Cobertura de Módulos (Top 10)</h2>
        <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
          <div class="table-responsive">
            <table class="auditoria-table">
              <thead>
                <tr>
                  <th><span class="th-content">Módulo</span></th>
                  <th><span class="th-content">Hospitales</span></th>
                  <th><span class="th-content">Cobertura</span></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="mod in data.modules_coverage" :key="mod.code">
                  <td class="model-text" style="color: var(--ink)">{{ mod.name }}</td>
                  <td class="ip-text">{{ mod.hospitals_with_module }}/{{ mod.total_hospitals }}</td>
                  <td>
                    <span class="badge badge--ok">{{ mod.percentage }}%</span>
                  </td>
                </tr>
                <tr v-if="!data.modules_coverage.length">
                  <td colspan="3" class="report-empty-row">Sin datos.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Resumen por hospital -->
      <div class="report-section">
        <h2 class="report-section-title">Hospitales — Resumen del Período</h2>
        <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
          <div class="table-responsive">
            <table class="auditoria-table">
              <thead>
                <tr>
                  <th><span class="th-content">Hospital</span></th>
                  <th><span class="th-content">Estado <span class="scope-tag scope-tag--actual">hoy</span></span></th>
                  <th><span class="th-content">Pacientes Nuevos <span class="scope-tag scope-tag--periodo">mes</span></span></th>
                  <th><span class="th-content">Usuarios <span class="scope-tag scope-tag--actual">hoy</span></span></th>
                  <th><span class="th-content">Módulos <span class="scope-tag scope-tag--actual">hoy</span></span></th>
                  <th><span class="th-content">Registrado</span></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in data.hospitales" :key="h.id">
                  <td class="user-name">
                    {{ h.hospital_name }}
                    <span class="ip-text" style="display: block;">{{ h.domain }}</span>
                  </td>
                  <td>
                    <span class="badge" :class="h.is_active ? 'badge--ok' : 'badge--neutral'">
                      {{ h.is_active ? 'Activo' : 'Inactivo' }}
                    </span>
                  </td>
                  <td class="model-text" style="color: var(--ink)">
                    <span v-if="!h.disponible" style="color: var(--alert)" title="No se pudo conectar a la base de este hospital">No se pudo consultar</span>
                    <template v-else>{{ h.pacientes_nuevos }}</template>
                  </td>
                  <td class="model-text" style="color: var(--ink)">{{ h.disponible ? h.usuarios_count : '—' }}</td>
                  <td class="model-text" style="color: var(--ink)">{{ h.modules_count }}</td>
                  <td class="ip-text">{{ formatDate(h.created_at) }}</td>
                </tr>
                <tr v-if="!data.hospitales.length">
                  <td colspan="6" class="report-empty-row">Sin hospitales.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <!-- Hospitales registrados en el período -->
      <div class="report-section">
        <h2 class="report-section-title">Hospitales Registrados en el Período</h2>
        <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
          <div class="table-responsive">
            <table class="auditoria-table">
              <tbody>
                <tr v-for="h in data.hospitales_registrados_periodo" :key="h.domain">
                  <td class="user-name">
                    {{ h.name }}
                    <span class="ip-text" style="display: block;">{{ h.domain }}</span>
                  </td>
                  <td class="ip-text" style="text-align: right">{{ formatDate(h.created_at) }}</td>
                </tr>
                <tr v-if="!data.hospitales_registrados_periodo.length">
                  <td colspan="2" class="report-empty-row">Sin hospitales registrados en este período.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </template>

    <div v-else class="table-error" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg);">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
      <p style="color: var(--alert)">No se pudo cargar el reporte.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface ModuleCoverage {
  code: string
  name: string
  hospitals_with_module: number
  total_hospitals: number
  percentage: number
}

interface HospitalSummary {
  id: string
  hospital_name: string
  domain: string
  is_active: boolean
  pacientes_nuevos: number
  usuarios_count: number
  modules_count: number
  created_at: string
  disponible: boolean
}

interface HospitalRegistrado {
  name: string
  domain: string
  created_at: string
}

interface MonthlyReport {
  month: string
  total_hospitales_activos: number
  pacientes_nuevos_total: number
  modules_coverage: ModuleCoverage[]
  hospitales: HospitalSummary[]
  hospitales_registrados_periodo: HospitalRegistrado[]
  usuarios_centrales_registrados: number | null
  hospitales_consultados: number
  hospitales_totales: number
  es_parcial: boolean
  es_estado_actual: boolean
  pacientes_solo_hospitales_activos: boolean
}

const { api } = useApi()

const meses = [
  'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre',
]

const hoy = new Date()
const anios = Array.from({ length: 5 }, (_, i) => hoy.getFullYear() - i)

const mes = ref(String(hoy.getMonth() + 1).padStart(2, '0'))
const anio = ref(hoy.getFullYear())
const tenantFilter = ref('')

const data = ref<MonthlyReport | null>(null)
const loading = ref(true)
const error = ref('')

const hospitalesOpciones = computed(() => data.value?.hospitales || [])

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    const month = `${anio.value}-${mes.value}`
    const query = tenantFilter.value ? `?month=${month}&tenant_id=${tenantFilter.value}` : `?month=${month}`
    data.value = await api<MonthlyReport>(`/admin/reportes/mensuales${query}`)
  } catch (e: any) {
    error.value = apiErr(e, 'Error de conexión')
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>