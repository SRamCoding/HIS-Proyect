<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">CONSULTA EXTERNA</span>
          <h1 class="page-title">Calendario Médico</h1>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary btn-sm" @click="irMes(-1)"><UIcon name="i-heroicons-chevron-left" class="w-4 h-4" /></button>
        <span class="mes-label">{{ nombreMes }} {{ anio }}</span>
        <button class="btn-secondary btn-sm" @click="irMes(1)"><UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></button>
        <button class="btn-secondary btn-sm" @click="irHoy">Hoy</button>
      </div>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>

    <section class="panel search-panel">
      <div class="search-grid">
        <div class="search-field">
          <label class="form-label">Servicio</label>
          <select v-model="filtro.servicio_id" class="input-clinical" @change="cargarMes">
            <option value="">Todos</option>
            <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
          </select>
        </div>
        <div class="search-field">
          <label class="form-label">Especialidad</label>
          <select v-model="filtro.especialidad_id" class="input-clinical" @change="cargarMes">
            <option value="">Todas</option>
            <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
          </select>
        </div>
      </div>
    </section>

    <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>

    <section v-else class="panel calendario-panel">
      <div class="calendario-dow">
        <span v-for="d in diasSemana" :key="d">{{ d }}</span>
      </div>
      <div class="calendario-grid">
        <button
          v-for="(dia, idx) in celdas"
          :key="idx"
          class="calendario-celda"
          :class="{ 'celda-vacia': !dia, 'celda-hoy': dia && dia.esHoy, 'celda-seleccionada': dia && diaSeleccionado === dia.fecha }"
          :disabled="!dia"
          @click="dia && seleccionarDia(dia.fecha)"
        >
          <template v-if="dia">
            <span class="celda-numero">{{ dia.numero }}</span>
            <span v-if="dia.total" class="celda-badge">{{ dia.total }}</span>
          </template>
        </button>
      </div>
    </section>

    <section v-if="diaSeleccionado" class="panel results-panel">
      <div class="results-header">
        <h2 class="results-title">Programaciones del {{ formatFechaLarga(diaSeleccionado) }}</h2>
        <span class="card-badge">{{ programacionesDia.length }}</span>
      </div>
      <div v-if="!programacionesDia.length" class="empty-state-small">
        <UIcon name="i-heroicons-calendar-days" class="w-8 h-8" style="color: var(--ink-soft)" />
        <span>No hay programaciones para este día con estos filtros.</span>
      </div>
      <div v-else class="programaciones-dia-list">
        <button v-for="p in programacionesDia" :key="p.id" class="prog-item" @click="verDetalle(p)">
          <div class="prog-item-main">
            <span class="prog-medico">{{ p.medico_nombre }}</span>
            <span class="badge" :class="p.estado === 'activo' ? 'badge-ok' : 'badge-off'">{{ p.estado }}</span>
          </div>
          <div class="prog-item-sub">
            <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />{{ p.hora_inicio }} - {{ p.hora_fin }} · {{ p.turno }}
            <span v-if="p.especialidad_nombre">· {{ p.especialidad_nombre }}</span>
            <span v-else-if="p.servicio_nombre">· {{ p.servicio_nombre }}</span>
          </div>
        </button>
      </div>
    </section>

    <!-- Detalle -->
    <div v-if="detalle" class="modal-overlay" @click.self="detalle = null">
      <div class="modal-content">
        <div class="modal-header"><h3 class="modal-title">Programación</h3><button class="action-btn" @click="detalle = null"><UIcon name="i-heroicons-x-mark" class="w-5 h-5" /></button></div>
        <div class="detail-info">
          <p><strong>Médico:</strong> {{ detalle.medico_nombre }}</p>
          <p v-if="detalle.especialidad_nombre"><strong>Especialidad:</strong> {{ detalle.especialidad_nombre }}</p>
          <p v-if="detalle.servicio_nombre"><strong>Servicio:</strong> {{ detalle.servicio_nombre }}</p>
          <p v-if="detalle.consultorio_nombre"><strong>Consultorio:</strong> {{ detalle.consultorio_nombre }}</p>
          <p><strong>Horario:</strong> {{ detalle.hora_inicio }} - {{ detalle.hora_fin }} · {{ detalle.turno }} · {{ detalle.tiempo_promedio_atencion }} min/paciente</p>
          <p><strong>Modalidad:</strong> {{ detalle.modalidad }} · <strong>Tipo:</strong> {{ detalle.tipo_servicio }}</p>
          <p v-if="detalle.descripcion" class="field-hint">{{ detalle.descripcion }}</p>
        </div>
        <div class="modal-footer">
          <button class="btn-secondary" @click="detalle = null">Cerrar</button>
          <NuxtLink class="btn-primary" :to="link('/app/admision/agendamiento')">
            <UIcon name="i-heroicons-calendar" class="w-4 h-4" />Ir a Agendamiento
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const { link } = useHospitalNav()
const endpoint = '/app/consulta-externa'

const error = ref('')
const loading = ref(false)
const servicios = ref<any[]>([])
const especialidades = ref<any[]>([])
const filtro = reactive({ servicio_id: '', especialidad_id: '' })

const hoy = new Date()
const anio = ref(hoy.getFullYear())
const mes = ref(hoy.getMonth() + 1) // 1-12
const programaciones = ref<any[]>([])
const diaSeleccionado = ref('')
const detalle = ref<any>(null)

const diasSemana = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom']
const meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
const nombreMes = computed(() => meses[mes.value - 1])

function fechaISO(y: number, m: number, d: number) {
  return `${y}-${String(m).padStart(2, '0')}-${String(d).padStart(2, '0')}`
}

const porDia = computed(() => {
  const map: Record<string, any[]> = {}
  for (const p of programaciones.value) {
    const f = String(p.fecha).slice(0, 10)
    if (!map[f]) map[f] = []
    map[f].push(p)
  }
  return map
})

const celdas = computed(() => {
  const primerDia = new Date(anio.value, mes.value - 1, 1)
  const ultimoDia = new Date(anio.value, mes.value, 0).getDate()
  // getDay(): 0=domingo..6=sabado -> convertimos a lunes=0..domingo=6
  const offset = (primerDia.getDay() + 6) % 7
  const hoyISO = fechaISO(hoy.getFullYear(), hoy.getMonth() + 1, hoy.getDate())
  const result: any[] = new Array(offset).fill(null)
  for (let d = 1; d <= ultimoDia; d++) {
    const f = fechaISO(anio.value, mes.value, d)
    result.push({ numero: d, fecha: f, esHoy: f === hoyISO, total: (porDia.value[f] || []).length })
  }
  return result
})

const programacionesDia = computed(() => {
  if (!diaSeleccionado.value) return []
  return (porDia.value[diaSeleccionado.value] || []).slice()
    .sort((a: any, b: any) => a.hora_inicio.localeCompare(b.hora_inicio))
})

function formatFechaLarga(f: string) {
  const d = new Date(`${f}T00:00:00`)
  return d.toLocaleDateString('es-PE', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' })
}

function irMes(delta: number) {
  let m = mes.value + delta
  let y = anio.value
  if (m < 1) { m = 12; y-- }
  if (m > 12) { m = 1; y++ }
  mes.value = m; anio.value = y
  diaSeleccionado.value = ''
  cargarMes()
}

function irHoy() {
  anio.value = hoy.getFullYear(); mes.value = hoy.getMonth() + 1
  diaSeleccionado.value = fechaISO(hoy.getFullYear(), hoy.getMonth() + 1, hoy.getDate())
  cargarMes()
}

function seleccionarDia(f: string) {
  diaSeleccionado.value = diaSeleccionado.value === f ? '' : f
}

function verDetalle(p: any) {
  detalle.value = p
}

async function cargarMes() {
  loading.value = true; error.value = ''
  try {
    const params: Record<string, any> = { anio: anio.value, mes: mes.value }
    if (filtro.servicio_id) params.servicio_id = filtro.servicio_id
    if (filtro.especialidad_id) params.especialidad_id = filtro.especialidad_id
    programaciones.value = await api(endpoint + '/programacion-medica', { query: params })
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar el calendario'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  try {
    servicios.value = await api(endpoint + '/programacion-medica/servicios')
    especialidades.value = await api(endpoint + '/programacion-medica/especialidades')
  } catch (e) { /* catálogos opcionales para filtrar */ }
  diaSeleccionado.value = fechaISO(hoy.getFullYear(), hoy.getMonth() + 1, hoy.getDate())
  await cargarMes()
})
</script>

<style scoped>
.lab-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.header-actions { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; }
.mes-label { font-size: 0.9375rem; font-weight: 600; color: var(--ink); min-width: 140px; text-align: center; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.25rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; text-decoration: none; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 0.75rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-sm { padding: 0.375rem 0.625rem; font-size: 0.75rem; }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.calendario-dow { display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.375rem; margin-bottom: 0.5rem; }
.calendario-dow span { text-align: center; font-size: 0.6875rem; font-weight: 600; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.05em; }
.calendario-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.375rem; }
.calendario-celda { aspect-ratio: 1; border-radius: 8px; border: 1px solid var(--line); background: var(--paper); cursor: pointer; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.25rem; position: relative; padding: 0.25rem; }
.calendario-celda:hover:not(:disabled) { background: var(--mist); }
.calendario-celda:disabled { border: none; cursor: default; }
.celda-vacia { visibility: hidden; }
.celda-numero { font-size: 0.8125rem; font-weight: 500; color: var(--ink); }
.celda-hoy .celda-numero { color: var(--teal); font-weight: 700; }
.celda-hoy { border-color: var(--teal); }
.celda-seleccionada { background: var(--teal-soft); border-color: var(--teal); }
.celda-badge { font-size: 0.625rem; font-weight: 700; padding: 0.0625rem 0.375rem; border-radius: 999px; background: var(--teal); color: white; }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; text-transform: capitalize; }
.card-badge { font-size: 0.625rem; font-weight: 500; padding: 0.125rem 0.5rem; border-radius: 10px; background: var(--green-soft); color: var(--green); }
.empty-state-small { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem 1rem; gap: 0.5rem; color: var(--ink-soft); font-size: 0.875rem; }
.programaciones-dia-list { display: flex; flex-direction: column; gap: 0.5rem; }
.prog-item { text-align: left; padding: 0.75rem 1rem; border-radius: var(--radius); border: 1px solid var(--line); background: var(--paper); cursor: pointer; }
.prog-item:hover { background: var(--mist); }
.prog-item-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.prog-medico { font-weight: 500; color: var(--ink); }
.prog-item-sub { display: flex; align-items: center; gap: 0.375rem; font-size: 0.75rem; color: var(--ink-soft); flex-wrap: wrap; }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-off { color: var(--ink-soft); background: var(--mist); }
.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; color: var(--ink-soft); cursor: pointer; }
.action-btn:hover { background: var(--mist); }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
.modal-content { max-width: 520px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 1.5rem; background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.modal-title { font-size: 1.0625rem; font-weight: 600; color: var(--ink); margin: 0; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid var(--line); margin-top: 1rem; }
.detail-info p { font-size: 0.875rem; color: var(--ink); margin: 0.375rem 0; }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid { grid-template-columns: 1fr; }
  .calendario-celda { font-size: 0.75rem; }
}
</style>
