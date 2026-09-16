<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-video-camera" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">TELESALUD · LEY N.° 30421 / LEY N.° 31166</span>
          <h1 class="page-title">{{ titulo }}</h1>
        </div>
      </div>
      <div style="display:flex; gap:0.5rem">
        <button v-if="mode === 'formulario-solicitud'" class="btn-primary" @click="mostrarForm = true"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Nueva solicitud</button>
        <button v-if="mode === 'monitor' || mode === 'medicos'" class="btn-secondary" :disabled="loading" @click="cargar">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': loading }" />Actualizar
        </button>
      </div>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <!-- ═══════════ RESUMEN TELECONSULTAS ═══════════ -->
    <template v-if="mode === 'resumen-teleconsultas'">
      <section class="panel search-panel">
        <form class="search-form" @submit.prevent="cargar">
          <div class="search-grid">
            <div class="search-field"><label class="form-label">Desde</label><input v-model="filtro.fecha_desde" type="date" class="input-clinical" required /></div>
            <div class="search-field"><label class="form-label">Hasta</label><input v-model="filtro.fecha_hasta" type="date" class="input-clinical" required /></div>
          </div>
          <div class="search-actions"><button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button></div>
        </form>
      </section>

      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <template v-else-if="resumen">
        <section class="stats-row">
          <div class="stat-card"><div class="stat-icon" style="background:var(--teal-soft)"><UIcon name="i-heroicons-calendar" class="w-5 h-5" style="color:var(--teal)" /></div><div class="stat-body"><span class="stat-num">{{ resumen.citas_virtuales_programadas }}</span><span class="stat-label">Citas virtuales programadas</span></div></div>
          <div class="stat-card"><div class="stat-icon" style="background:var(--green-soft)"><UIcon name="i-heroicons-check-badge" class="w-5 h-5" style="color:var(--green)" /></div><div class="stat-body"><span class="stat-num">{{ resumen.teleconsultas_firmadas }}</span><span class="stat-label">Teleconsultas firmadas</span></div></div>
          <div class="stat-card" :class="{ 'stat-card--alert': resumen.tasa_no_asistio > 20 }"><div class="stat-icon" style="background:var(--amber-soft)"><UIcon name="i-heroicons-signal-slash" class="w-5 h-5" style="color:var(--amber)" /></div><div class="stat-body"><span class="stat-num">{{ resumen.tasa_no_asistio }}%</span><span class="stat-label">Tasa de no asistencia</span><span class="stat-hint">{{ resumen.no_asistio }} no asistió</span></div></div>
        </section>
        <section class="panel results-panel">
          <div class="results-header"><h2 class="results-title">Por médico</h2></div>
          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th>Médico</th><th>Teleconsultas firmadas</th></tr></thead>
              <tbody>
                <tr v-for="m in resumen.por_medico" :key="m.medico_nombre"><td>{{ m.medico_nombre }}</td><td>{{ m.teleconsultas_firmadas }}</td></tr>
                <tr v-if="!resumen.por_medico.length"><td colspan="2" style="text-align:center;color:var(--ink-soft)">Sin teleconsultas firmadas en este rango.</td></tr>
              </tbody>
            </table>
          </div>
        </section>
        <section class="panel results-panel">
          <div class="results-header"><h2 class="results-title">Por especialidad</h2></div>
          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th>Especialidad</th><th>Citas</th></tr></thead>
              <tbody>
                <tr v-for="e in resumen.por_especialidad" :key="e.especialidad"><td>{{ e.especialidad }}</td><td>{{ e.citas }}</td></tr>
                <tr v-if="!resumen.por_especialidad.length"><td colspan="2" style="text-align:center;color:var(--ink-soft)">Sin datos en este rango.</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </template>

    <!-- ═══════════ GUÍA RÁPIDA MINSA ═══════════ -->
    <template v-else-if="mode === 'guia-rapida-minsa'">
      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <template v-else-if="guia">
        <section class="panel">
          <h2 class="results-title" style="margin-bottom:0.75rem">Marco legal</h2>
          <div class="guia-list">
            <div v-for="n in guia.marco_legal" :key="n.norma" class="guia-item">
              <strong>{{ n.norma }}</strong><span>{{ n.descripcion }}</span>
            </div>
          </div>
        </section>
        <section class="panel">
          <h2 class="results-title" style="margin-bottom:0.75rem">Modalidades reconocidas</h2>
          <div class="guia-list">
            <div v-for="m in guia.modalidades" :key="m.nombre" class="guia-item">
              <strong>{{ m.nombre }}</strong><span>{{ m.descripcion }}</span>
            </div>
          </div>
        </section>
        <section class="panel">
          <h2 class="results-title" style="margin-bottom:0.75rem">Checklist operativa</h2>
          <ul class="checklist">
            <li v-for="(c, i) in guia.checklist_operativa" :key="i"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" style="color:var(--teal)" />{{ c }}</li>
          </ul>
        </section>
      </template>
    </template>

    <!-- ═══════════ FORMULARIO SOLICITUD ═══════════ -->
    <template v-else-if="mode === 'formulario-solicitud'">
      <section v-if="mostrarForm" class="panel">
        <div class="card-header-row"><h2 class="results-title">Nueva solicitud de teleconsulta</h2><button class="btn-secondary" @click="mostrarForm=false"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
        <form class="editor-form" @submit.prevent="crearSolicitud">
          <div class="form-grid">
            <div class="form-group"><label class="form-label">DNI o ID del paciente</label><input v-model="nuevo.patient_id" class="input-clinical" placeholder="UUID del paciente" required /></div>
            <div class="form-group"><label class="form-label">Medio preferido</label>
              <select v-model="nuevo.medio_preferido" class="input-clinical">
                <option value="LLAMADA">Llamada</option><option value="WHATSAPP">WhatsApp</option><option value="VIDEOLLAMADA">Videollamada</option>
              </select>
            </div>
            <div class="form-group full-width"><label class="form-label">Motivo</label><textarea v-model="nuevo.motivo" class="input-clinical" rows="2" required></textarea></div>
            <div class="form-group full-width"><label class="form-label">Contacto (opcional, si es distinto al registrado)</label><input v-model="nuevo.contacto" class="input-clinical" placeholder="Teléfono o correo" /></div>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Registrar solicitud</button></div>
        </form>
      </section>

      <section class="panel search-panel">
        <div class="search-actions" style="justify-content:flex-start">
          <button v-for="e in ['', 'pendiente', 'programada', 'rechazada']" :key="e" class="btn-secondary btn-sm" :class="{ 'btn-active': filtroEstado === e }" @click="filtroEstado = e; cargar()">{{ e || 'Todas' }}</button>
        </div>
      </section>

      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <section v-else class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ solicitudes.length }} solicitudes</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Paciente</th><th>Motivo</th><th>Medio</th><th>Estado</th><th>Fecha</th><th></th></tr></thead>
            <tbody>
              <tr v-for="s in solicitudes" :key="s.id">
                <td>{{ s.paciente_nombre }} <span class="field-hint">({{ s.paciente_dni }})</span></td>
                <td>{{ s.motivo }}</td><td>{{ s.medio_preferido }}</td>
                <td>
                  <span class="badge" :class="s.estado === 'programada' ? 'badge-ok' : s.estado === 'rechazada' ? 'badge-off' : 'badge-pendiente'">{{ s.estado }}</span>
                  <div v-if="s.motivo_rechazo" class="field-hint">{{ s.motivo_rechazo }}</div>
                </td>
                <td>{{ formatFechaHora(s.created_at) }}</td>
                <td>
                  <div v-if="s.estado === 'pendiente'" class="row-actions">
                    <input v-model="citaPorSolicitud[s.id]" class="input-clinical input-sm" placeholder="ID de cita virtual" />
                    <button class="btn-secondary btn-sm" :disabled="busy || !citaPorSolicitud[s.id]" @click="programar(s)"><UIcon name="i-heroicons-calendar-days" class="w-4 h-4" />Programar</button>
                    <button class="btn-secondary btn-sm" :disabled="busy" @click="rechazar(s)"><UIcon name="i-heroicons-x-circle" class="w-4 h-4" />Rechazar</button>
                  </div>
                </td>
              </tr>
              <tr v-if="!solicitudes.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">No hay solicitudes registradas todavía.</td></tr>
            </tbody>
          </table>
        </div>
        <p class="field-hint" style="margin-top:0.75rem">Para programar, cree primero la cita en Consulta Externa sobre una programación con modalidad VIRTUAL y pegue aquí su ID.</p>
      </section>
    </template>

    <!-- ═══════════ MONITOR ═══════════ -->
    <template v-else-if="mode === 'monitor'">
      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <section v-else class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ citasHoy.length }} teleconsultas hoy</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Hora</th><th>Paciente</th><th>DNI</th><th>Médico</th><th>Estado</th></tr></thead>
            <tbody>
              <tr v-for="c in citasHoy" :key="c.cita_id">
                <td>{{ c.hora_inicio }} – {{ c.hora_fin }}</td><td>{{ c.paciente_nombre }}</td><td>{{ c.paciente_dni }}</td>
                <td>{{ c.medico_nombre }}</td>
                <td><span class="badge" :class="c.estado === 'atendida' ? 'badge-ok' : c.estado === 'cancelada' || c.estado === 'no_asistio' ? 'badge-off' : 'badge-pendiente'">{{ c.estado }}</span></td>
              </tr>
              <tr v-if="!citasHoy.length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Sin teleconsultas programadas para hoy.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <!-- ═══════════ MÉDICOS ═══════════ -->
    <template v-else-if="mode === 'medicos'">
      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <section v-else class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ medicos.length }} médicos con actividad de telesalud</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Médico</th><th>DNI</th><th>CMP</th><th>Especialidades (RNE)</th><th>Contacto</th></tr></thead>
            <tbody>
              <tr v-for="m in medicos" :key="m.id">
                <td>{{ m.nombre }}</td><td>{{ m.dni }}</td><td>{{ m.numero_cmp || '—' }}</td>
                <td>{{ m.especialidades.map((e:any) => `${e.especialidad}${e.numero_rne ? ' (' + e.numero_rne + ')' : ''}`).join(', ') || '—' }}</td>
                <td>{{ m.celular || m.correo || '—' }}</td>
              </tr>
              <tr v-if="!medicos.length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Ningún médico tiene programaciones virtuales todavía.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'resumen-teleconsultas' | 'guia-rapida-minsa' | 'formulario-solicitud' | 'monitor' | 'medicos'
const props = defineProps<{ mode: Mode }>()
const { api } = useApi()
const endpoint = '/app/telesalud'

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)

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
  'resumen-teleconsultas': 'Resumen Teleconsultas',
  'guia-rapida-minsa': 'Guía Rápida MINSA',
  'formulario-solicitud': 'Formulario de Solicitud',
  monitor: 'Monitor',
  medicos: 'Médicos',
}[props.mode]))

const filtro = reactive({ fecha_desde: primerDiaMes(), fecha_hasta: hoy() })
const resumen = ref<any>(null)
const guia = ref<any>(null)
const solicitudes = ref<any[]>([])
const filtroEstado = ref('')
const citasHoy = ref<any[]>([])
const medicos = ref<any[]>([])

const mostrarForm = ref(false)
const nuevo = reactive({ patient_id: '', motivo: '', medio_preferido: 'LLAMADA', contacto: '' })
const citaPorSolicitud = reactive<Record<string, string>>({})

async function cargar() {
  loading.value = true; error.value = ''
  try {
    if (props.mode === 'resumen-teleconsultas') {
      resumen.value = await api(endpoint + '/resumen-teleconsultas', { query: { fecha_desde: filtro.fecha_desde, fecha_hasta: filtro.fecha_hasta } })
    } else if (props.mode === 'guia-rapida-minsa') {
      guia.value = await api(endpoint + '/guia-rapida-minsa')
    } else if (props.mode === 'formulario-solicitud') {
      solicitudes.value = await api(endpoint + '/formulario-solicitud', { query: filtroEstado.value ? { estado: filtroEstado.value } : {} })
    } else if (props.mode === 'monitor') {
      citasHoy.value = await api(endpoint + '/monitor')
    } else if (props.mode === 'medicos') {
      medicos.value = await api(endpoint + '/medicos')
    }
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function crearSolicitud() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/formulario-solicitud', { method: 'POST', body: { ...nuevo, contacto: nuevo.contacto || undefined } })
    notice.value = 'Solicitud registrada.'
    mostrarForm.value = false
    Object.assign(nuevo, { patient_id: '', motivo: '', medio_preferido: 'LLAMADA', contacto: '' })
    await cargar()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function programar(s: any) {
  const citaId = citaPorSolicitud[s.id]
  if (!citaId) return
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/formulario-solicitud/' + s.id + '/programar', { method: 'POST', body: { cita_id: citaId } })
    notice.value = 'Solicitud programada.'
    await cargar()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function rechazar(s: any) {
  const motivo = prompt('Motivo del rechazo:')
  if (!motivo) return
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/formulario-solicitud/' + s.id + '/rechazar', { method: 'POST', body: { motivo_rechazo: motivo } })
    notice.value = 'Solicitud rechazada.'
    await cargar()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

onMounted(cargar)
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
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.btn-active { background: var(--teal-soft); border-color: var(--teal); color: var(--teal); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.search-form { display: flex; flex-direction: column; gap: 1rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
.search-field { display: flex; flex-direction: column; gap: 0.25rem; }
.search-actions { display: flex; gap: 0.75rem; justify-content: flex-end; flex-wrap: wrap; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.input-sm { width: 160px; padding: 0.375rem 0.5rem; font-size: 0.75rem; }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); white-space: nowrap; }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.row-actions { display: flex; align-items: center; gap: 0.375rem; flex-wrap: wrap; }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; white-space: nowrap; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-off { color: var(--ink-soft); background: var(--mist); }
.badge-pendiente { color: var(--amber); background: var(--amber-soft); }
.editor-form { display: flex; flex-direction: column; gap: 1rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }

.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { display: flex; align-items: center; gap: 1rem; padding: 1.125rem 1.25rem; border-radius: var(--radius-lg); border: 1px solid var(--line); background: var(--paper); box-shadow: var(--shadow-sm); }
.stat-card--alert { border-color: var(--alert-soft); }
.stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-body { display: flex; flex-direction: column; min-width: 0; }
.stat-num { font-size: 1.375rem; font-weight: 700; color: var(--ink); line-height: 1.2; }
.stat-label { font-size: 0.8125rem; color: var(--ink-soft); }
.stat-hint { font-size: 0.6875rem; color: var(--ink-soft); opacity: 0.85; margin-top: 0.125rem; }

.guia-list { display: flex; flex-direction: column; gap: 0.75rem; }
.guia-item { display: flex; flex-direction: column; gap: 0.125rem; padding: 0.75rem; border-radius: 8px; background: var(--mist); }
.guia-item strong { font-size: 0.875rem; color: var(--ink); }
.guia-item span { font-size: 0.8125rem; color: var(--ink-soft); }
.checklist { display: flex; flex-direction: column; gap: 0.5rem; list-style: none; padding: 0; margin: 0; }
.checklist li { display: flex; align-items: flex-start; gap: 0.5rem; font-size: 0.8125rem; color: var(--ink); }

@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid, .form-grid { grid-template-columns: 1fr; }
}
</style>
