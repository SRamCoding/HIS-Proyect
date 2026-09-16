<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-user-group" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">SERVICIO SOCIAL · TRABAJO SOCIAL HOSPITALARIO</span>
          <h1 class="page-title">Servicio Social</h1>
        </div>
      </div>
      <button class="btn-primary" @click="mostrarForm = true"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Nueva evaluación</button>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <section v-if="mostrarForm" class="panel">
      <div class="card-header-row"><h2 class="results-title">Nueva evaluación social</h2><button class="btn-secondary" @click="mostrarForm=false"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
      <form class="editor-form" @submit.prevent="crear">
        <div class="form-grid">
          <div class="form-group"><label class="form-label">ID del paciente</label><input v-model="nuevo.patient_id" class="input-clinical" placeholder="UUID del paciente" required /></div>
          <div class="form-group"><label class="form-label">ID del trabajador social</label><input v-model="nuevo.trabajador_social_id" class="input-clinical" placeholder="UUID del empleado (TSO)" required /></div>
          <div class="form-group"><label class="form-label">Origen (opcional)</label>
            <select v-model="nuevo.origenTipo" class="input-clinical">
              <option value="">Directo</option>
              <option value="atencion_medica_id">Consulta Externa</option>
              <option value="atencion_emergencia_id">Emergencia</option>
              <option value="hospitalizacion_id">Hospitalización</option>
            </select>
          </div>
          <div class="form-group" v-if="nuevo.origenTipo"><label class="form-label">ID del origen</label><input v-model="nuevo.origenId" class="input-clinical" placeholder="UUID de la atención/hospitalización" /></div>
          <div class="form-group"><label class="form-label">Tipo de vivienda</label>
            <select v-model="nuevo.tipo_vivienda" class="input-clinical">
              <option value="">— Sin registrar —</option>
              <option v-for="t in ['PROPIA','ALQUILADA','ALOJADA','ASENTAMIENTO_HUMANO','SIN_VIVIENDA']" :key="t" :value="t">{{ t.replaceAll('_',' ') }}</option>
            </select>
          </div>
          <div class="form-group"><label class="form-label">Clasificación socioeconómica (referencial)</label>
            <select v-model="nuevo.clasificacion_socioeconomica" class="input-clinical">
              <option value="">— Sin registrar —</option>
              <option v-for="c in ['NO_POBRE','POBRE','POBRE_EXTREMO']" :key="c" :value="c">{{ c.replaceAll('_',' ') }}</option>
            </select>
          </div>
          <div class="form-group full-width"><label class="form-label">Red de apoyo familiar</label><textarea v-model="nuevo.red_apoyo_familiar" class="input-clinical" rows="2"></textarea></div>
          <div class="form-group full-width">
            <label class="form-label">Factores de riesgo social</label>
            <div class="check-list">
              <label v-for="f in FACTORES_RIESGO" :key="f" class="check-field"><input type="checkbox" :value="f" v-model="nuevo.factores_riesgo" /> {{ f.replaceAll('_',' ') }}</label>
            </div>
          </div>
          <label class="check-field"><input type="checkbox" v-model="nuevo.requiere_derivacion_externa" /> Requiere derivación externa</label>
          <div class="form-group" v-if="nuevo.requiere_derivacion_externa"><label class="form-label">Entidad de derivación</label>
            <select v-model="nuevo.entidad_derivacion" class="input-clinical">
              <option v-for="e in ['MIMP','CEM','INABIF','DEMUNA','OTRO']" :key="e" :value="e">{{ e }}</option>
            </select>
          </div>
          <div class="form-group full-width"><label class="form-label">Recomendaciones</label><textarea v-model="nuevo.recomendaciones" class="input-clinical" rows="2"></textarea></div>
        </div>
        <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Registrar evaluación</button></div>
      </form>
    </section>

    <section class="panel search-panel">
      <div class="search-actions" style="justify-content:flex-start">
        <button v-for="e in ['', 'abierto', 'cerrado']" :key="e" class="btn-secondary btn-sm" :class="{ 'btn-active': filtroEstado === e }" @click="filtroEstado = e; cargar()">{{ e || 'Todos' }}</button>
      </div>
    </section>

    <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
    <div v-else class="case-list">
      <div v-for="e in evaluaciones" :key="e.id" class="case-card">
        <div class="case-head">
          <div>
            <strong>{{ e.numero_ficha }}</strong> — {{ e.paciente_nombre }} <span class="field-hint">({{ e.paciente_dni }})</span>
            <div class="field-hint">{{ e.origen }} · Trabajador social: {{ e.trabajador_social_nombre }} · {{ e.fecha_evaluacion }}</div>
          </div>
          <span class="badge" :class="e.estado === 'abierto' ? 'badge-pendiente' : 'badge-ok'">{{ e.estado }}</span>
        </div>
        <div class="case-body">
          <p v-if="e.tipo_vivienda"><strong>Vivienda:</strong> {{ e.tipo_vivienda.replaceAll('_',' ') }}</p>
          <p v-if="e.clasificacion_socioeconomica"><strong>Clasificación:</strong> {{ e.clasificacion_socioeconomica.replaceAll('_',' ') }}</p>
          <p v-if="e.factores_riesgo?.length"><strong>Factores de riesgo:</strong> {{ e.factores_riesgo.map((f:string)=>f.replaceAll('_',' ')).join(', ') }}</p>
          <p v-if="e.requiere_derivacion_externa"><strong>Derivado a:</strong> {{ e.entidad_derivacion }}</p>
          <p v-if="e.recomendaciones"><strong>Recomendaciones:</strong> {{ e.recomendaciones }}</p>
        </div>
        <table v-if="e.gestiones?.length" class="lab-table">
          <thead><tr><th>Fecha</th><th>Tipo</th><th>Descripción</th><th>Por</th></tr></thead>
          <tbody>
            <tr v-for="g in e.gestiones" :key="g.id"><td>{{ formatFechaHora(g.fecha) }}</td><td>{{ g.tipo_gestion.replaceAll('_',' ') }}</td><td>{{ g.descripcion }}</td><td>{{ g.registrado_por }}</td></tr>
          </tbody>
        </table>
        <div v-if="e.estado === 'abierto'" class="row-actions" style="margin-top:0.75rem">
          <select v-model="gestionTipoPorEval[e.id]" class="input-clinical input-sm">
            <option v-for="t in TIPOS_GESTION" :key="t" :value="t">{{ t.replaceAll('_',' ') }}</option>
          </select>
          <input v-model="gestionDescPorEval[e.id]" class="input-clinical input-sm input-wide" placeholder="Descripción de la gestión" />
          <button class="btn-secondary btn-sm" :disabled="busy || !gestionDescPorEval[e.id]" @click="agregarGestion(e)"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Registrar gestión</button>
          <button class="btn-secondary btn-sm" :disabled="busy" @click="cerrarCaso(e)"><UIcon name="i-heroicons-check-circle" class="w-4 h-4" />Cerrar caso</button>
        </div>
      </div>
      <p v-if="!evaluaciones.length" class="field-hint">Sin evaluaciones sociales registradas.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const endpoint = '/app/servicio-social'

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)
const mostrarForm = ref(false)

const FACTORES_RIESGO = ['violencia_familiar', 'abandono', 'situacion_calle', 'adulto_mayor_solo', 'discapacidad_sin_soporte', 'menor_en_riesgo']
const TIPOS_GESTION = ['VISITA_DOMICILIARIA', 'LLAMADA_TELEFONICA', 'COORDINACION_INTERINSTITUCIONAL', 'ENTREVISTA', 'GESTION_APOYO_SOCIAL', 'OTRO']

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  const errors = e?.data?.errors
  if (errors) return Object.values(errors).flat().join('; ')
  return 'No se pudo completar la operación.'
}
function formatFechaHora(f: string) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const evaluaciones = ref<any[]>([])
const filtroEstado = ref('')
const nuevo = reactive({
  patient_id: '', trabajador_social_id: '', origenTipo: '', origenId: '',
  tipo_vivienda: '', clasificacion_socioeconomica: '', red_apoyo_familiar: '',
  factores_riesgo: [] as string[], requiere_derivacion_externa: false, entidad_derivacion: 'MIMP', recomendaciones: '',
})
const gestionTipoPorEval = reactive<Record<string, string>>({})
const gestionDescPorEval = reactive<Record<string, string>>({})

async function cargar() {
  loading.value = true; error.value = ''
  try {
    evaluaciones.value = await api(endpoint + '/servicio-social', { query: filtroEstado.value ? { estado: filtroEstado.value } : {} })
    for (const e of evaluaciones.value) if (!gestionTipoPorEval[e.id]) gestionTipoPorEval[e.id] = TIPOS_GESTION[0]
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function crear() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    const body: any = {
      patient_id: nuevo.patient_id, trabajador_social_id: nuevo.trabajador_social_id,
      tipo_vivienda: nuevo.tipo_vivienda || undefined, clasificacion_socioeconomica: nuevo.clasificacion_socioeconomica || undefined,
      red_apoyo_familiar: nuevo.red_apoyo_familiar || undefined, factores_riesgo: nuevo.factores_riesgo,
      requiere_derivacion_externa: nuevo.requiere_derivacion_externa,
      entidad_derivacion: nuevo.requiere_derivacion_externa ? nuevo.entidad_derivacion : undefined,
      recomendaciones: nuevo.recomendaciones || undefined,
    }
    if (nuevo.origenTipo) body[nuevo.origenTipo] = nuevo.origenId
    await api(endpoint + '/servicio-social', { method: 'POST', body })
    notice.value = 'Evaluación social registrada.'
    mostrarForm.value = false
    Object.assign(nuevo, { patient_id: '', trabajador_social_id: '', origenTipo: '', origenId: '',
      tipo_vivienda: '', clasificacion_socioeconomica: '', red_apoyo_familiar: '',
      factores_riesgo: [], requiere_derivacion_externa: false, entidad_derivacion: 'MIMP', recomendaciones: '' })
    await cargar()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function agregarGestion(e: any) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/servicio-social/' + e.id + '/gestiones', {
      method: 'POST', body: { tipo_gestion: gestionTipoPorEval[e.id], descripcion: gestionDescPorEval[e.id] },
    })
    notice.value = 'Gestión registrada.'
    gestionDescPorEval[e.id] = ''
    await cargar()
  } catch (err_) { error.value = err(err_) } finally { busy.value = false }
}

async function cerrarCaso(e: any) {
  if (!confirm(`¿Cerrar el caso ${e.numero_ficha}?`)) return
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/servicio-social/' + e.id + '/cerrar', { method: 'POST', body: {} })
    notice.value = 'Caso cerrado.'
    await cargar()
  } catch (err_) { error.value = err(err_) } finally { busy.value = false }
}

onMounted(cargar)
</script>

<style scoped>
.lab-container { max-width: 1200px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { padding: 0.375rem 0.625rem; font-size: 0.75rem; }
.btn-active { background: var(--teal-soft); border-color: var(--teal); color: var(--teal); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.search-actions { display: flex; gap: 0.375rem; flex-wrap: wrap; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.input-sm { width: auto; padding: 0.375rem 0.5rem; font-size: 0.75rem; display: inline-block; }
.input-wide { min-width: 240px; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.editor-form { display: flex; flex-direction: column; gap: 1rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.check-field { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8125rem; color: var(--ink); }
.check-list { display: flex; flex-wrap: wrap; gap: 1rem; }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; white-space: nowrap; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-pendiente { color: var(--amber); background: var(--amber-soft); }
.row-actions { display: flex; align-items: center; gap: 0.375rem; flex-wrap: wrap; }

.case-list { display: flex; flex-direction: column; gap: 1rem; }
.case-card { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; box-shadow: var(--shadow-sm); }
.case-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; margin-bottom: 0.5rem; }
.case-body p { font-size: 0.8125rem; color: var(--ink); margin: 0.25rem 0; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; margin-top: 0.75rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.5rem 0.625rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); }
.lab-table td { padding: 0.5rem 0.625rem; border-bottom: 1px solid var(--line); }

@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
