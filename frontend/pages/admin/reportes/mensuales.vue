<!-- frontend/pages/admin/reportes/mensuales.vue -->
<template>
  <div>
    <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
      <span>Reportes</span><span>/</span><span>Mensuales</span>
    </div>
    <h1 class="text-lg font-semibold mb-1" style="color: var(--ink)">Reporte Mensual del Sistema</h1>
    <p class="text-sm mb-4" style="color: var(--ink-soft)">
      Resumen de actividad del sistema por período.
    </p>

    <!-- Filtros -->
    <div class="mb-4 flex flex-wrap items-end gap-3">
      <div>
        <label class="text-xs block mb-1" style="color: var(--ink-soft)">Hospital</label>
        <select v-model="tenantFilter" class="input-clinical" @change="cargar">
          <option value="">Todos los hospitales</option>
          <option v-for="h in hospitalesOpciones" :key="h.id" :value="h.id">{{ h.hospital_name }}</option>
        </select>
      </div>
      <div>
        <label class="text-xs block mb-1" style="color: var(--ink-soft)">Mes</label>
        <select v-model="mes" class="input-clinical" @change="cargar">
          <option v-for="(nombre, i) in meses" :key="i" :value="String(i + 1).padStart(2, '0')">{{ nombre }}</option>
        </select>
      </div>
      <div>
        <label class="text-xs block mb-1" style="color: var(--ink-soft)">Año</label>
        <select v-model="anio" class="input-clinical" @change="cargar">
          <option v-for="y in anios" :key="y" :value="y">{{ y }}</option>
        </select>
      </div>
    </div>

    <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
    <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>

    <template v-else-if="data">
      <!-- KPIs principales -->
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 mb-6">
        <div class="p-4" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-xs" style="color: var(--ink-soft)">Hospitales Activos</p>
          <p class="text-2xl font-bold" style="color: var(--ink)">{{ data.total_hospitales_activos }}</p>
        </div>
        <div class="p-4" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-xs" style="color: var(--ink-soft)">Pacientes Nuevos</p>
          <p class="text-2xl font-bold" style="color: var(--ink)">{{ data.pacientes_nuevos_total }}</p>
        </div>
        <div class="p-4" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-xs" style="color: var(--ink-soft)">Hospitales Registrados</p>
          <p class="text-2xl font-bold" style="color: var(--ink)">{{ data.hospitales_registrados_periodo.length }}</p>
        </div>
        <div class="p-4" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-xs" style="color: var(--ink-soft)">Usuarios Centrales Nuevos</p>
          <p class="text-2xl font-bold" style="color: var(--ink)">{{ data.usuarios_centrales_registrados }}</p>
        </div>
      </div>

      <!-- Aviso de módulos pendientes -->
      <div class="mb-6 p-4 text-sm" style="background: var(--mist); border: 1px solid var(--line); border-radius: var(--radius); color: var(--ink-soft)">
        <strong>Nota:</strong> Citas, emergencias y altas todavía no están implementadas en el sistema (no existen esos módulos en el backend). Estas métricas se agregarán cuando se desarrolle el módulo clínico correspondiente.
      </div>

      <!-- Cobertura de módulos -->
      <div class="mb-6">
        <h2 class="text-sm font-semibold mb-2" style="color: var(--ink)">Cobertura de Módulos (Top 10)</h2>
        <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <table class="w-full text-sm">
            <thead>
              <tr style="border-bottom: 1px solid var(--line)">
                <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Módulo</th>
                <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Hospitales</th>
                <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Cobertura</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="mod in data.modules_coverage" :key="mod.code" style="border-bottom: 1px solid var(--line)">
                <td class="px-5 py-3" style="color: var(--ink)">{{ mod.name }}</td>
                <td class="px-5 py-3" style="color: var(--ink-soft)">{{ mod.hospitals_with_module }}/{{ mod.total_hospitals }}</td>
                <td class="px-5 py-3">
                  <span class="badge badge--ok">{{ mod.percentage }}%</span>
                </td>
              </tr>
              <tr v-if="!data.modules_coverage.length">
                <td colspan="3" class="px-5 py-6 text-center text-sm" style="color: var(--ink-soft)">Sin datos.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Resumen por hospital -->
      <div class="mb-6">
        <h2 class="text-sm font-semibold mb-2" style="color: var(--ink)">Hospitales — Resumen del Período</h2>
        <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <table class="w-full text-sm">
            <thead>
              <tr style="border-bottom: 1px solid var(--line)">
                <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Hospital</th>
                <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Estado</th>
                <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Pacientes Nuevos</th>
                <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Usuarios</th>
                <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Módulos</th>
                <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Registrado</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="h in data.hospitales" :key="h.id" style="border-bottom: 1px solid var(--line)">
                <td class="px-5 py-3 font-medium" style="color: var(--ink)">
                  {{ h.hospital_name }}
                  <span class="text-xs block" style="color: var(--ink-soft)">{{ h.domain }}</span>
                </td>
                <td class="px-5 py-3">
                  <span class="badge" :class="h.is_active ? 'badge--ok' : 'badge--neutral'">
                    {{ h.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </td>
                <td class="px-5 py-3" style="color: var(--ink)">{{ h.pacientes_nuevos }}</td>
                <td class="px-5 py-3" style="color: var(--ink)">{{ h.usuarios_count }}</td>
                <td class="px-5 py-3" style="color: var(--ink)">{{ h.modules_count }}</td>
                <td class="px-5 py-3 text-xs" style="color: var(--ink-soft)">{{ formatDate(h.created_at) }}</td>
              </tr>
              <tr v-if="!data.hospitales.length">
                <td colspan="6" class="px-5 py-6 text-center text-sm" style="color: var(--ink-soft)">Sin hospitales.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Hospitales registrados en el período -->
      <div>
        <h2 class="text-sm font-semibold mb-2" style="color: var(--ink)">Hospitales Registrados en el Período</h2>
        <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <table class="w-full text-sm">
            <tbody>
              <tr v-for="h in data.hospitales_registrados_periodo" :key="h.domain" style="border-bottom: 1px solid var(--line)">
                <td class="px-5 py-3 font-medium" style="color: var(--ink)">
                  {{ h.name }}
                  <span class="text-xs block" style="color: var(--ink-soft)">{{ h.domain }}</span>
                </td>
                <td class="px-5 py-3 text-xs text-right" style="color: var(--ink-soft)">{{ formatDate(h.created_at) }}</td>
              </tr>
              <tr v-if="!data.hospitales_registrados_periodo.length">
                <td colspan="2" class="px-5 py-6 text-center text-sm" style="color: var(--ink-soft)">
                  Sin hospitales registrados en este período.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
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
  usuarios_centrales_registrados: number
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
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>