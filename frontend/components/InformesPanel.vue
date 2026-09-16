<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-chart-bar" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">INFORMES</span>
          <h1 class="page-title">{{ titulo }}</h1>
        </div>
      </div>
      <button v-if="mode === 'visor-colas'" class="btn-secondary" :disabled="loading" @click="cargar">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': loading }" />Actualizar
      </button>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>

    <!-- Filtro de rango de fechas (todos los modos excepto visor-colas) -->
    <section v-if="mode !== 'visor-colas'" class="panel search-panel">
      <form class="search-form" @submit.prevent="cargar">
        <div class="search-grid">
          <div class="search-field"><label class="form-label">Desde</label><input v-model="filtro.fecha_desde" type="date" class="input-clinical" required /></div>
          <div class="search-field"><label class="form-label">Hasta</label><input v-model="filtro.fecha_hasta" type="date" class="input-clinical" required /></div>
          <div v-if="mode === 'gestion-cupos'" class="search-field">
            <label class="form-label">Médico</label>
            <select v-model="filtro.medico_id" class="input-clinical">
              <option value="">Todos</option>
              <option v-for="m in medicos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="search-actions">
          <button v-if="tieneCsv" class="btn-secondary" type="button" :disabled="loading" @click="descargarCsv"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />CSV</button>
          <button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button>
        </div>
      </form>
    </section>

    <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>

    <template v-else>
      <!-- ═══════════ REPORTE POR MÉDICO ═══════════ -->
      <section v-if="mode === 'reporte-medico'" class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ filas.length }} médicos con actividad en el rango</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Médico</th><th>DNI</th><th>Citas prog.</th><th>Atendidas</th><th>No asistió</th><th>Canceladas</th><th>Atenciones firmadas</th><th>Interconsultas</th></tr></thead>
            <tbody>
              <tr v-for="f in filas" :key="f.medico_id">
                <td>{{ f.medico_nombre }}</td><td>{{ f.medico_dni }}</td>
                <td>{{ f.citas_programadas }}</td><td>{{ f.citas_atendidas }}</td>
                <td>{{ f.citas_no_asistio }}</td><td>{{ f.citas_canceladas }}</td>
                <td>{{ f.total_atenciones_firmadas }} <span class="field-hint">({{ f.atenciones_firmadas_consulta_externa }} CE · {{ f.atenciones_firmadas_emergencia }} EMG)</span></td>
                <td>{{ f.interconsultas_generadas }}</td>
              </tr>
              <tr v-if="!filas.length"><td colspan="8" style="text-align:center;color:var(--ink-soft)">Sin actividad médica registrada en este rango.</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ═══════════ REPORTES DE HOSPITALIZACIÓN ═══════════ -->
      <template v-else-if="mode === 'reportes-hospitalizacion' && hosp">
        <section class="stats-row">
          <div class="stat-card"><div class="stat-icon" style="background:var(--teal-soft)"><UIcon name="i-heroicons-arrow-down-on-square" class="w-5 h-5" style="color:var(--teal)" /></div><div class="stat-body"><span class="stat-num">{{ hosp.ingresos }}</span><span class="stat-label">Ingresos</span></div></div>
          <div class="stat-card"><div class="stat-icon" style="background:var(--green-soft)"><UIcon name="i-heroicons-arrow-up-on-square" class="w-5 h-5" style="color:var(--green)" /></div><div class="stat-body"><span class="stat-num">{{ hosp.altas }}</span><span class="stat-label">Altas</span></div></div>
          <div class="stat-card"><div class="stat-icon" style="background:var(--amber-soft)"><UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color:var(--amber)" /></div><div class="stat-body"><span class="stat-num">{{ hosp.promedio_estancia_dias ?? '—' }}</span><span class="stat-label">Promedio de estancia (días)</span></div></div>
          <div class="stat-card"><div class="stat-icon" style="background:rgba(30,58,95,0.08)"><UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color:var(--navy)" /></div><div class="stat-body"><span class="stat-num">{{ hosp.camas_dia_ocupadas }}</span><span class="stat-label">Días-cama ocupados</span><span class="stat-hint">{{ hosp.porcentaje_ocupacion }}% de ocupación ({{ hosp.total_camas }} camas)</span></div></div>
        </section>
        <section class="panel results-panel">
          <div class="results-header"><h2 class="results-title">Ingresos por especialidad</h2></div>
          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th>Especialidad</th><th>Ingresos</th></tr></thead>
              <tbody>
                <tr v-for="e in hosp.por_especialidad" :key="e.especialidad"><td>{{ e.especialidad }}</td><td>{{ e.ingresos }}</td></tr>
                <tr v-if="!hosp.por_especialidad.length"><td colspan="2" style="text-align:center;color:var(--ink-soft)">Sin ingresos en este rango.</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

      <!-- ═══════════ GESTIÓN DE CUPOS ═══════════ -->
      <section v-else-if="mode === 'gestion-cupos'" class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ filas.length }} programaciones</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Código</th><th>Fecha</th><th>Turno</th><th>Médico</th><th>Servicio</th><th>Estado</th><th>Cupos totales</th><th>Usados</th><th>Disponibles</th><th>% Ocupación</th></tr></thead>
            <tbody>
              <tr v-for="f in filas" :key="f.programacion_id">
                <td>{{ f.codigo }}</td><td>{{ f.fecha }}</td><td>{{ f.turno }}</td>
                <td>{{ f.medico || '—' }}</td><td>{{ f.servicio || '—' }}</td>
                <td><span class="badge" :class="f.estado_programacion === 'activo' ? 'badge-ok' : 'badge-off'">{{ f.estado_programacion }}</span></td>
                <td>{{ f.cupos_totales }}</td><td>{{ f.cupos_usados }}</td><td>{{ f.cupos_disponibles }}</td>
                <td>{{ f.porcentaje_ocupacion }}%</td>
              </tr>
              <tr v-if="!filas.length"><td colspan="10" style="text-align:center;color:var(--ink-soft)">Sin programaciones en este rango.</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- ═══════════ GESTIÓN DE TICKETS ═══════════ -->
      <section v-else-if="mode === 'gestion-tickets' && tickets" class="stats-row">
        <div v-for="(g, key) in gruposTickets" :key="key" class="panel ticket-card">
          <h2 class="results-title">{{ g.label }}</h2>
          <span class="stat-num">{{ g.data.total }}</span>
          <div class="ticket-estados">
            <span v-for="(cnt, est) in g.data.por_estado" :key="est" class="badge badge-pendiente">{{ est }}: {{ cnt }}</span>
            <span v-if="!Object.keys(g.data.por_estado).length" class="field-hint">Sin movimientos en este rango.</span>
          </div>
        </div>
      </section>

      <!-- ═══════════ VISOR DE COLAS ═══════════ -->
      <section v-else-if="mode === 'visor-colas' && colas" class="stats-row">
        <div class="stat-card"><div class="stat-icon" style="background:var(--teal-soft)"><UIcon name="i-heroicons-queue-list" class="w-5 h-5" style="color:var(--teal)" /></div><div class="stat-body"><span class="stat-num">{{ colas.admision_lista_espera_pendientes }}</span><span class="stat-label">Lista de espera (Admisión)</span></div></div>
        <div class="stat-card"><div class="stat-icon" style="background:rgba(30,58,95,0.08)"><UIcon name="i-heroicons-clipboard-document-check" class="w-5 h-5" style="color:var(--navy)" /></div><div class="stat-body"><span class="stat-num">{{ colas.consulta_externa_citas_pendientes_hoy }}</span><span class="stat-label">Citas de hoy pendientes</span></div></div>
        <div class="stat-card" :class="{ 'stat-card--alert': colas.emergencia_admitidos_sin_triaje > 0 }"><div class="stat-icon" style="background:var(--alert-soft)"><UIcon name="i-heroicons-exclamation-triangle" class="w-5 h-5" style="color:var(--alert)" /></div><div class="stat-body"><span class="stat-num">{{ colas.emergencia_admitidos_sin_triaje }}</span><span class="stat-label">Emergencia: sin triaje</span></div></div>
        <div class="stat-card"><div class="stat-icon" style="background:var(--alert-soft)"><UIcon name="i-heroicons-heart" class="w-5 h-5" style="color:var(--alert)" /></div><div class="stat-body"><span class="stat-num">{{ colas.emergencia_en_atencion }}</span><span class="stat-label">Emergencia: en atención</span></div></div>
        <div class="stat-card"><div class="stat-icon" style="background:var(--amber-soft)"><UIcon name="i-heroicons-beaker" class="w-5 h-5" style="color:var(--amber)" /></div><div class="stat-body"><span class="stat-num">{{ colas.laboratorio_ordenes_pendientes }}</span><span class="stat-label">Laboratorio pendiente</span></div></div>
        <div class="stat-card"><div class="stat-icon" style="background:var(--amber-soft)"><UIcon name="i-heroicons-photo" class="w-5 h-5" style="color:var(--amber)" /></div><div class="stat-body"><span class="stat-num">{{ colas.imagenologia_ordenes_pendientes }}</span><span class="stat-label">Imagenología pendiente</span></div></div>
        <div class="stat-card"><div class="stat-icon" style="background:var(--green-soft)"><UIcon name="i-heroicons-document-text" class="w-5 h-5" style="color:var(--green)" /></div><div class="stat-body"><span class="stat-num">{{ colas.farmacia_recetas_pendientes }}</span><span class="stat-label">Farmacia: recetas pendientes</span></div></div>
        <p class="field-hint full-width">Actualizado: {{ formatFechaHora(colas.generado_at) }}</p>
      </section>

      <!-- ═══════════ EXTERNOS (REFERENCIAS) ═══════════ -->
      <template v-else-if="mode === 'externos' && externosData">
        <section class="stats-row">
          <div class="stat-card"><div class="stat-icon" style="background:var(--teal-soft)"><UIcon name="i-heroicons-arrow-top-right-on-square" class="w-5 h-5" style="color:var(--teal)" /></div><div class="stat-body"><span class="stat-num">{{ externosData.total }}</span><span class="stat-label">Referencias emitidas</span></div></div>
          <div class="stat-card"><div class="stat-icon" style="background:var(--amber-soft)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color:var(--amber)" /></div><div class="stat-body"><span class="stat-num">{{ externosData.promedio_dias_contrarreferencia ?? '—' }}</span><span class="stat-label">Promedio días a contrarreferencia</span></div></div>
          <div v-for="(cnt, est) in externosData.por_estado" :key="est" class="stat-card"><div class="stat-icon" style="background:var(--mist)"><UIcon name="i-heroicons-tag" class="w-5 h-5" style="color:var(--ink-soft)" /></div><div class="stat-body"><span class="stat-num">{{ cnt }}</span><span class="stat-label">{{ est }}</span></div></div>
        </section>
        <section class="panel results-panel">
          <div class="results-header"><h2 class="results-title">{{ externosData.items.length }} referencias</h2></div>
          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th>N.° referencia</th><th>Fecha</th><th>Destino</th><th>Especialidad</th><th>Estado</th><th>Contrarreferencia</th><th>Días</th></tr></thead>
              <tbody>
                <tr v-for="it in externosData.items" :key="it.id">
                  <td>{{ it.numero_referencia }}</td><td>{{ formatFechaHora(it.fecha) }}</td>
                  <td>{{ it.destino }}</td><td>{{ it.especialidad_destino || '—' }}</td>
                  <td><span class="badge" :class="it.estado === 'contrarreferida' ? 'badge-ok' : 'badge-pendiente'">{{ it.estado }}</span></td>
                  <td>{{ it.fecha_contrarreferencia || '—' }}</td><td>{{ it.dias_hasta_contrarreferencia ?? '—' }}</td>
                </tr>
                <tr v-if="!externosData.items.length"><td colspan="7" style="text-align:center;color:var(--ink-soft)">Sin referencias en este rango.</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'reporte-medico' | 'reportes-hospitalizacion' | 'gestion-cupos' | 'gestion-tickets' | 'visor-colas' | 'externos'
const props = defineProps<{ mode: Mode }>()
const { api } = useApi()
const endpoint = '/app/informes'

const error = ref('')
const loading = ref(false)

function hoy() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date())
}
function primerDiaMes() {
  const d = new Date()
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit' }).format(d) + '-01'
}
function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}
function formatFechaHora(f: string) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const titulo = computed(() => ({
  'reporte-medico': 'Reporte por Médico',
  'reportes-hospitalizacion': 'Reportes de Hospitalización',
  'gestion-cupos': 'Gestión de Cupos',
  'gestion-tickets': 'Gestión de Tickets',
  'visor-colas': 'Visor de Colas',
  externos: 'Externos',
}[props.mode]))

const tieneCsv = computed(() => ['reporte-medico', 'gestion-cupos', 'externos'].includes(props.mode))

const filtro = reactive({ fecha_desde: primerDiaMes(), fecha_hasta: hoy(), medico_id: '' })
const medicos = ref<{ id: string; nombre: string }[]>([])

const filas = ref<any[]>([])
const hosp = ref<any>(null)
const tickets = ref<any>(null)
const colas = ref<any>(null)
const externosData = ref<any>(null)

const gruposTickets = computed(() => tickets.value ? {
  laboratorio: { label: 'Laboratorio', data: tickets.value.laboratorio },
  imagenologia: { label: 'Imagenología', data: tickets.value.imagenologia },
  farmacia_recetas: { label: 'Farmacia (recetas)', data: tickets.value.farmacia_recetas },
} : {})

async function cargar() {
  loading.value = true; error.value = ''
  try {
    const rango = { fecha_desde: filtro.fecha_desde, fecha_hasta: filtro.fecha_hasta }
    if (props.mode === 'reporte-medico') {
      filas.value = await api(endpoint + '/reporte-medico', { query: rango })
    } else if (props.mode === 'reportes-hospitalizacion') {
      hosp.value = await api(endpoint + '/reportes-hospitalizacion', { query: rango })
    } else if (props.mode === 'gestion-cupos') {
      filas.value = await api(endpoint + '/gestion-cupos', { query: { ...rango, medico_id: filtro.medico_id || undefined } })
    } else if (props.mode === 'gestion-tickets') {
      tickets.value = await api(endpoint + '/gestion-tickets', { query: rango })
    } else if (props.mode === 'visor-colas') {
      colas.value = await api(endpoint + '/visor-colas')
    } else if (props.mode === 'externos') {
      externosData.value = await api(endpoint + '/externos', { query: rango })
    }
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function descargarCsv() {
  try {
    const rango = { fecha_desde: filtro.fecha_desde, fecha_hasta: filtro.fecha_hasta }
    const query = props.mode === 'gestion-cupos' ? { ...rango, medico_id: filtro.medico_id || undefined } : rango
    const blob = await api<Blob>(endpoint + '/' + props.mode + '.csv', { query, responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = props.mode + '.csv'; a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) { error.value = err(e) }
}

onMounted(async () => {
  if (props.mode === 'gestion-cupos') {
    try { medicos.value = await api(endpoint.replace('informes', 'hospitalizacion') + '/catalogos/empleados') } catch { /* catálogo opcional */ }
  }
  await cargar()
})
</script>

<style scoped>
.lab-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); }
.field-hint.full-width { grid-column: 1 / -1; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.search-form { display: flex; flex-direction: column; gap: 1rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
.search-field { display: flex; flex-direction: column; gap: 0.25rem; }
.search-actions { display: flex; gap: 0.75rem; justify-content: flex-end; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); white-space: nowrap; }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; white-space: nowrap; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-off { color: var(--ink-soft); background: var(--mist); }
.badge-pendiente { color: var(--amber); background: var(--amber-soft); }

.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { display: flex; align-items: center; gap: 1rem; padding: 1.125rem 1.25rem; border-radius: var(--radius-lg); border: 1px solid var(--line); background: var(--paper); box-shadow: var(--shadow-sm); }
.stat-card--alert { border-color: var(--alert-soft); }
.stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-body { display: flex; flex-direction: column; min-width: 0; }
.stat-num { font-size: 1.375rem; font-weight: 700; color: var(--ink); line-height: 1.2; }
.stat-label { font-size: 0.8125rem; color: var(--ink-soft); }
.stat-hint { font-size: 0.6875rem; color: var(--ink-soft); opacity: 0.85; margin-top: 0.125rem; }

.ticket-card { display: flex; flex-direction: column; gap: 0.5rem; margin-bottom: 0; }
.ticket-card .stat-num { font-size: 1.75rem; }
.ticket-estados { display: flex; flex-wrap: wrap; gap: 0.375rem; }

@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid { grid-template-columns: 1fr; }
}
</style>
