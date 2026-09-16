<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-document-text" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">EPIDEMIOLOGÍA · NOTIFICACIÓN OBLIGATORIA (RENACE / CDC-MINSA)</span>
          <h1 class="page-title">{{ config.titulo }}</h1>
        </div>
      </div>
      <button class="btn-primary" @click="mostrarForm = true"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Nueva ficha</button>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <section v-if="mostrarForm" class="panel">
      <div class="card-header-row"><h2 class="results-title">Notificar {{ config.titulo }}</h2><button class="btn-secondary" @click="mostrarForm=false"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
      <form class="editor-form" @submit.prevent="crear">
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Origen</label>
            <select v-model="nuevo.origenTipo" class="input-clinical">
              <option value="atencion_medica_id">Consulta Externa</option>
              <option value="atencion_emergencia_id">Emergencia</option>
              <option value="">Directo (sin origen clínico registrado)</option>
            </select>
          </div>
          <div class="form-group" v-if="nuevo.origenTipo">
            <label class="form-label">ID del origen</label><input v-model="nuevo.origenId" class="input-clinical" placeholder="UUID de la atención" />
          </div>
          <div class="form-group" v-else>
            <label class="form-label">ID del paciente</label><input v-model="nuevo.patient_id" class="input-clinical" placeholder="UUID del paciente" />
          </div>
          <div class="form-group"><label class="form-label">ID del médico notificante</label><input v-model="nuevo.medico_notificante_id" class="input-clinical" placeholder="UUID del empleado (médico)" required /></div>
          <div class="form-group"><label class="form-label">ID de diagnóstico CIE-10 (opcional)</label><input v-model="nuevo.diagnostico_cie10_id" class="input-clinical" placeholder="UUID del diagnóstico" /></div>
        </div>

        <h3 class="section-title">Datos clínicos — {{ config.titulo }}</h3>
        <div class="form-grid">
          <div v-for="campo in config.campos" :key="campo.key" class="form-group" :class="{ 'full-width': campo.tipo === 'checklist' }">
            <label class="form-label">{{ campo.label }}</label>
            <input v-if="campo.tipo === 'date'" v-model="datos[campo.key]" type="date" class="input-clinical" :required="campo.requerido" />
            <input v-else-if="campo.tipo === 'number'" v-model.number="datos[campo.key]" type="number" step="any" class="input-clinical" />
            <input v-else-if="campo.tipo === 'text'" v-model="datos[campo.key]" class="input-clinical" :required="campo.requerido" />
            <label v-else-if="campo.tipo === 'boolean'" class="check-field"><input type="checkbox" v-model="datos[campo.key]" /> Sí</label>
            <select v-else-if="campo.tipo === 'select'" v-model="datos[campo.key]" class="input-clinical" :required="campo.requerido">
              <option v-for="op in campo.opciones" :key="op" :value="op">{{ op.replaceAll('_',' ') }}</option>
            </select>
            <div v-else-if="campo.tipo === 'checklist'" class="check-list">
              <label v-for="op in campo.opciones" :key="op" class="check-field"><input type="checkbox" :value="op" v-model="datos[campo.key]" /> {{ op.replaceAll('_',' ') }}</label>
            </div>
          </div>
        </div>
        <div class="form-group full-width"><label class="form-label">Observaciones</label><textarea v-model="nuevo.observaciones" class="input-clinical" rows="2"></textarea></div>
        <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Registrar ficha</button></div>
      </form>
    </section>

    <section class="panel search-panel">
      <div class="search-actions" style="justify-content:flex-start">
        <button v-for="e in ['', 'registrada', 'enviada_red_salud']" :key="e" class="btn-secondary btn-sm" :class="{ 'btn-active': filtroEstado === e }" @click="filtroEstado = e; cargar()">{{ e || 'Todas' }}</button>
      </div>
    </section>

    <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
    <section v-else class="panel results-panel">
      <div class="results-header"><h2 class="results-title">{{ fichas.length }} fichas</h2></div>
      <div class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>N.° ficha</th><th>Paciente</th><th>Origen</th><th>Fecha notificación</th><th>Médico notificante</th><th>Envío</th><th></th></tr></thead>
          <tbody>
            <tr v-for="f in fichas" :key="f.id">
              <td>{{ f.numero_ficha }}</td>
              <td>{{ f.paciente_nombre }} <span class="field-hint">({{ f.paciente_dni }})</span></td>
              <td>{{ f.origen }}</td>
              <td>{{ f.fecha_notificacion }}</td>
              <td>{{ f.medico_notificante_nombre }}</td>
              <td><span class="badge" :class="f.estado_envio === 'enviada_red_salud' ? 'badge-ok' : 'badge-pendiente'">{{ f.estado_envio }}</span></td>
              <td>
                <button v-if="f.estado_envio !== 'enviada_red_salud'" class="btn-secondary btn-sm" :disabled="busy" @click="marcarEnviado(f)">Marcar enviado</button>
                <button class="btn-secondary btn-sm" @click="verDetalle(f)"><UIcon name="i-heroicons-eye" class="w-4 h-4" />Ver</button>
              </td>
            </tr>
            <tr v-if="!fichas.length"><td colspan="7" style="text-align:center;color:var(--ink-soft)">Sin fichas registradas.</td></tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="detalle" class="panel">
      <div class="card-header-row"><h2 class="results-title">Ficha {{ detalle.numero_ficha }}</h2><button class="btn-secondary" @click="detalle=null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
      <pre class="detalle-json">{{ JSON.stringify(detalle.datos_clinicos, null, 2) }}</pre>
    </section>
  </div>
</template>

<script setup lang="ts">
type Tipo = 'COVID' | 'CANCER' | 'DIABETES' | 'DENGUE' | 'LEPTOSPIROSIS'
const props = defineProps<{ tipo: Tipo }>()
const { api } = useApi()

const CONFIGS: Record<Tipo, { titulo: string; ruta: string; campos: any[] }> = {
  COVID: {
    titulo: 'Ficha Covid', ruta: 'ficha-covid',
    campos: [
      { key: 'fecha_inicio_sintomas', label: 'Fecha de inicio de síntomas', tipo: 'date', requerido: true },
      { key: 'sintomas', label: 'Síntomas', tipo: 'checklist', opciones: ['fiebre', 'tos', 'dificultad_respiratoria', 'anosmia', 'dolor_garganta', 'cefalea'] },
      { key: 'contacto_caso_confirmado', label: 'Contacto con caso confirmado', tipo: 'boolean' },
      { key: 'tipo_prueba', label: 'Tipo de prueba', tipo: 'select', opciones: ['PCR', 'ANTIGENA', 'SEROLOGICA'] },
      { key: 'resultado_prueba', label: 'Resultado de la prueba', tipo: 'select', opciones: ['PENDIENTE', 'POSITIVO', 'NEGATIVO'] },
      { key: 'fecha_prueba', label: 'Fecha de la prueba', tipo: 'date' },
      { key: 'condicion', label: 'Condición', tipo: 'select', opciones: ['AMBULATORIO', 'HOSPITALIZADO', 'UCI', 'FALLECIDO'] },
      { key: 'requiere_aislamiento', label: 'Requiere aislamiento', tipo: 'boolean' },
    ],
  },
  DENGUE: {
    titulo: 'Ficha Dengue', ruta: 'ficha-dengue',
    campos: [
      { key: 'fecha_inicio_sintomas', label: 'Fecha de inicio de síntomas', tipo: 'date', requerido: true },
      { key: 'signos_alarma', label: 'Signos de alarma', tipo: 'checklist', opciones: ['dolor_abdominal', 'vomitos_persistentes', 'sangrado_mucosas', 'letargia', 'hepatomegalia'] },
      { key: 'clasificacion', label: 'Clasificación', tipo: 'select', requerido: true, opciones: ['SIN_SENALES_ALARMA', 'CON_SENALES_ALARMA', 'GRAVE'] },
      { key: 'prueba_serologica', label: 'Prueba serológica', tipo: 'select', opciones: ['NS1', 'IGM', 'IGG'] },
      { key: 'resultado_prueba', label: 'Resultado de la prueba', tipo: 'select', opciones: ['PENDIENTE', 'POSITIVO', 'NEGATIVO'] },
      { key: 'zona_probable_infeccion', label: 'Zona probable de infección', tipo: 'text' },
      { key: 'plaquetas', label: 'Plaquetas (por mm³)', tipo: 'number' },
      { key: 'hematocrito', label: 'Hematocrito (%)', tipo: 'number' },
    ],
  },
  LEPTOSPIROSIS: {
    titulo: 'Ficha Leptospirosis', ruta: 'ficha-leptospirosis',
    campos: [
      { key: 'fecha_inicio_sintomas', label: 'Fecha de inicio de síntomas', tipo: 'date', requerido: true },
      { key: 'exposicion_agua_contaminada', label: 'Exposición a agua contaminada', tipo: 'boolean' },
      { key: 'exposicion_roedores', label: 'Exposición a roedores', tipo: 'boolean' },
      { key: 'ocupacion_riesgo', label: 'Ocupación de riesgo', tipo: 'text' },
      { key: 'sintomas', label: 'Síntomas', tipo: 'checklist', opciones: ['fiebre', 'mialgias', 'ictericia', 'cefalea', 'conjuntivitis'] },
      { key: 'prueba_diagnostica', label: 'Prueba diagnóstica', tipo: 'text' },
      { key: 'resultado_prueba', label: 'Resultado de la prueba', tipo: 'select', opciones: ['PENDIENTE', 'POSITIVO', 'NEGATIVO'] },
    ],
  },
  DIABETES: {
    titulo: 'Ficha Diabetes', ruta: 'ficha-diabetes',
    campos: [
      { key: 'tipo_diabetes', label: 'Tipo de diabetes', tipo: 'select', requerido: true, opciones: ['TIPO_1', 'TIPO_2', 'GESTACIONAL'] },
      { key: 'fecha_diagnostico', label: 'Fecha de diagnóstico', tipo: 'date', requerido: true },
      { key: 'glucosa_ayunas', label: 'Glucosa en ayunas (mg/dL)', tipo: 'number' },
      { key: 'hba1c', label: 'HbA1c (%)', tipo: 'number' },
      { key: 'imc', label: 'IMC', tipo: 'number' },
      { key: 'complicaciones', label: 'Complicaciones', tipo: 'checklist', opciones: ['retinopatia', 'nefropatia', 'neuropatia', 'pie_diabetico'] },
      { key: 'tratamiento', label: 'Tratamiento', tipo: 'select', opciones: ['DIETA_Y_EJERCICIO', 'METFORMINA', 'INSULINA', 'OTROS'] },
    ],
  },
  CANCER: {
    titulo: 'Ficha Cáncer', ruta: 'ficha-cancer',
    campos: [
      { key: 'sitio_primario', label: 'Sitio primario', tipo: 'text', requerido: true },
      { key: 'estadio', label: 'Estadio', tipo: 'select', opciones: ['I', 'II', 'III', 'IV'] },
      { key: 'fecha_diagnostico', label: 'Fecha de diagnóstico', tipo: 'date', requerido: true },
      { key: 'metodo_diagnostico', label: 'Método diagnóstico', tipo: 'select', requerido: true, opciones: ['HISTOPATOLOGICO', 'CITOLOGICO', 'CLINICO', 'IMAGEN'] },
      { key: 'tratamiento_indicado', label: 'Tratamiento indicado', tipo: 'checklist', opciones: ['CIRUGIA', 'QUIMIOTERAPIA', 'RADIOTERAPIA', 'PALIATIVO'] },
      { key: 'habito_tabaco', label: 'Hábito de tabaco', tipo: 'boolean' },
      { key: 'antecedente_familiar', label: 'Antecedente familiar', tipo: 'boolean' },
    ],
  },
}

const config = computed(() => CONFIGS[props.tipo])
const endpoint = computed(() => '/app/epidemiologia/' + config.value.ruta)

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)
const mostrarForm = ref(false)
const fichas = ref<any[]>([])
const filtroEstado = ref('')
const detalle = ref<any>(null)

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  const errors = e?.data?.errors
  if (errors) return Object.values(errors).flat().join('; ')
  return 'No se pudo completar la operación.'
}

function valoresPorDefecto() {
  const d: Record<string, any> = {}
  for (const campo of config.value.campos) {
    d[campo.key] = campo.tipo === 'checklist' ? [] : campo.tipo === 'boolean' ? false : campo.tipo === 'select' ? (campo.opciones[0] ?? '') : ''
  }
  return d
}

const datos = reactive<Record<string, any>>(valoresPorDefecto())
const nuevo = reactive({ origenTipo: 'atencion_medica_id', origenId: '', patient_id: '', medico_notificante_id: '', diagnostico_cie10_id: '', observaciones: '' })

watch(() => props.tipo, () => Object.assign(datos, valoresPorDefecto()))

async function cargar() {
  loading.value = true; error.value = ''
  try {
    fichas.value = await api(endpoint.value, { query: filtroEstado.value ? { estado_envio: filtroEstado.value } : {} })
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function crear() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    const datosLimpios: Record<string, any> = {}
    for (const [k, v] of Object.entries(datos)) datosLimpios[k] = v === '' ? undefined : v
    const body: any = {
      medico_notificante_id: nuevo.medico_notificante_id,
      diagnostico_cie10_id: nuevo.diagnostico_cie10_id || undefined,
      tipo_ficha: props.tipo, datos_clinicos: datosLimpios, observaciones: nuevo.observaciones || undefined,
    }
    if (nuevo.origenTipo) body[nuevo.origenTipo] = nuevo.origenId
    else body.patient_id = nuevo.patient_id
    await api(endpoint.value, { method: 'POST', body })
    notice.value = 'Ficha registrada.'
    mostrarForm.value = false
    Object.assign(datos, valoresPorDefecto())
    Object.assign(nuevo, { origenTipo: 'atencion_medica_id', origenId: '', patient_id: '', medico_notificante_id: '', diagnostico_cie10_id: '', observaciones: '' })
    await cargar()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function marcarEnviado(f: any) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api('/app/epidemiologia/fichas/' + f.id + '/marcar-enviado', { method: 'POST' })
    notice.value = 'Ficha marcada como enviada a la Red de Salud.'
    await cargar()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

function verDetalle(f: any) {
  detalle.value = f
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
.btn-secondary { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { padding: 0.375rem 0.625rem; font-size: 0.75rem; margin-left: 0.375rem; }
.btn-active { background: var(--teal-soft); border-color: var(--teal); color: var(--teal); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.section-title { font-size: 0.875rem; font-weight: 600; color: var(--ink); margin: 1rem 0 0.75rem; }
.search-actions { display: flex; gap: 0.375rem; flex-wrap: wrap; }
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
.badge-pendiente { color: var(--amber); background: var(--amber-soft); }
.editor-form { display: flex; flex-direction: column; gap: 0.5rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.75rem; }
.check-field { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8125rem; color: var(--ink); }
.check-list { display: flex; flex-wrap: wrap; gap: 1rem; }
.detalle-json { background: var(--mist); border-radius: 8px; padding: 1rem; font-size: 0.75rem; overflow-x: auto; }

@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
