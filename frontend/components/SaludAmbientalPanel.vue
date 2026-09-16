<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-globe-alt" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">SALUD AMBIENTAL · SINADEF / RENIEC</span>
          <h1 class="page-title">Defunciones</h1>
        </div>
      </div>
      <button class="btn-primary" @click="mostrarForm = true"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Nuevo certificado</button>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <section v-if="mostrarForm" class="panel">
      <div class="card-header-row"><h2 class="results-title">Emitir certificado de defunción</h2><button class="btn-secondary" @click="mostrarForm=false"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
      <form class="editor-form" @submit.prevent="crear">
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Origen</label>
            <select v-model="nuevo.origenTipo" class="input-clinical">
              <option value="atencion_emergencia_id">Emergencia</option>
              <option value="hospitalizacion_id">Hospitalización</option>
              <option value="">Directo (sin origen clínico registrado)</option>
            </select>
          </div>
          <div class="form-group" v-if="nuevo.origenTipo">
            <label class="form-label">ID del origen</label><input v-model="nuevo.origenId" class="input-clinical" placeholder="UUID de la atención/hospitalización" />
          </div>
          <div class="form-group" v-else>
            <label class="form-label">ID del paciente</label><input v-model="nuevo.patient_id" class="input-clinical" placeholder="UUID del paciente" />
          </div>
          <div class="form-group"><label class="form-label">ID del médico certificador</label><input v-model="nuevo.medico_certificador_id" class="input-clinical" placeholder="UUID del empleado (médico)" required /></div>
          <div class="form-group"><label class="form-label">Fecha y hora de defunción</label><input v-model="nuevo.fecha_defuncion" type="datetime-local" class="input-clinical" required /></div>
          <div class="form-group"><label class="form-label">Lugar de defunción</label><input v-model="nuevo.lugar_defuncion" class="input-clinical" required /></div>
          <div class="form-group"><label class="form-label">Tipo de muerte</label>
            <select v-model="nuevo.tipo_muerte" class="input-clinical"><option value="NATURAL">Natural</option><option value="VIOLENTA">Violenta</option></select>
          </div>
          <div class="form-group"><label class="form-label">Causa A — directa (CIE-10)</label><input v-model="nuevo.causa_a_id" class="input-clinical" placeholder="UUID del diagnóstico" required /></div>
          <div class="form-group"><label class="form-label">Causa B — intermedia (opcional)</label><input v-model="nuevo.causa_b_id" class="input-clinical" placeholder="UUID del diagnóstico" /></div>
          <div class="form-group"><label class="form-label">Causa C — básica (opcional)</label><input v-model="nuevo.causa_c_id" class="input-clinical" placeholder="UUID del diagnóstico" /></div>
          <div class="form-group"><label class="form-label">Causa D — contribuyente (opcional)</label><input v-model="nuevo.causa_d_id" class="input-clinical" placeholder="UUID del diagnóstico" /></div>
          <div class="form-group full-width"><label class="form-label">Observaciones</label><textarea v-model="nuevo.observaciones" class="input-clinical" rows="2"></textarea></div>
        </div>
        <p v-if="nuevo.tipo_muerte === 'VIOLENTA'" class="field-hint alert-hint"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" />Las muertes violentas requieren necropsia de ley y derivación a Medicina Legal.</p>
        <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Emitir certificado</button></div>
      </form>
    </section>

    <section class="panel search-panel">
      <div class="search-actions" style="justify-content:flex-start">
        <button v-for="t in ['', 'NATURAL', 'VIOLENTA']" :key="t" class="btn-secondary btn-sm" :class="{ 'btn-active': filtroTipo === t }" @click="filtroTipo = t; cargar()">{{ t || 'Todos' }}</button>
        <span class="field-sep" />
        <button v-for="e in ['', 'registrado', 'enviado_reniec']" :key="e" class="btn-secondary btn-sm" :class="{ 'btn-active': filtroEstado === e }" @click="filtroEstado = e; cargar()">{{ e || 'Cualquier estado' }}</button>
      </div>
    </section>

    <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
    <section v-else class="panel results-panel">
      <div class="results-header"><h2 class="results-title">{{ certificados.length }} certificados</h2></div>
      <div class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>N.° certificado</th><th>Fallecido</th><th>Fecha</th><th>Tipo</th><th>Causa A</th><th>Médico</th><th>Envío</th><th></th></tr></thead>
          <tbody>
            <tr v-for="c in certificados" :key="c.id">
              <td>{{ c.numero_certificado }}</td>
              <td>{{ c.paciente_nombre }} <span class="field-hint">({{ c.paciente_dni }})</span></td>
              <td>{{ formatFechaHora(c.fecha_defuncion) }}</td>
              <td><span class="badge" :class="c.tipo_muerte === 'VIOLENTA' ? 'badge-off' : 'badge-ok'">{{ c.tipo_muerte }}</span></td>
              <td>{{ c.causa_a }}</td>
              <td>{{ c.medico_certificador_nombre }}</td>
              <td><span class="badge" :class="c.estado_envio === 'enviado_reniec' ? 'badge-ok' : 'badge-pendiente'">{{ c.estado_envio }}</span></td>
              <td class="row-actions">
                <button class="btn-secondary btn-sm" :disabled="busy" @click="descargarPdf(c)"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />PDF</button>
                <button v-if="c.estado_envio !== 'enviado_reniec'" class="btn-secondary btn-sm" :disabled="busy" @click="marcarEnviado(c)">Marcar enviado</button>
              </td>
            </tr>
            <tr v-if="!certificados.length"><td colspan="8" style="text-align:center;color:var(--ink-soft)">Sin certificados registrados.</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const endpoint = '/app/salud-ambiental'

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)
const mostrarForm = ref(false)

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
async function descargarPdf(c: any) {
  try {
    const blob = await api<Blob>(endpoint + '/defunciones/' + c.id + '/reporte.pdf', { responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'certificado-defuncion-' + c.numero_certificado + '.pdf'; a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) { error.value = err(e) }
}

const certificados = ref<any[]>([])
const filtroTipo = ref('')
const filtroEstado = ref('')
const nuevo = reactive({
  origenTipo: 'atencion_emergencia_id', origenId: '', patient_id: '', medico_certificador_id: '',
  fecha_defuncion: '', lugar_defuncion: '', tipo_muerte: 'NATURAL',
  causa_a_id: '', causa_b_id: '', causa_c_id: '', causa_d_id: '', observaciones: '',
})

async function cargar() {
  loading.value = true; error.value = ''
  try {
    const query: any = {}
    if (filtroTipo.value) query.tipo_muerte = filtroTipo.value
    if (filtroEstado.value) query.estado_envio = filtroEstado.value
    certificados.value = await api(endpoint + '/defunciones', { query })
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function crear() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    const body: any = {
      medico_certificador_id: nuevo.medico_certificador_id,
      fecha_defuncion: nuevo.fecha_defuncion, lugar_defuncion: nuevo.lugar_defuncion, tipo_muerte: nuevo.tipo_muerte,
      causa_a_id: nuevo.causa_a_id, causa_b_id: nuevo.causa_b_id || undefined, causa_c_id: nuevo.causa_c_id || undefined,
      causa_d_id: nuevo.causa_d_id || undefined, observaciones: nuevo.observaciones || undefined,
    }
    if (nuevo.origenTipo) body[nuevo.origenTipo] = nuevo.origenId
    else body.patient_id = nuevo.patient_id
    await api(endpoint + '/defunciones', { method: 'POST', body })
    notice.value = 'Certificado de defunción emitido.'
    mostrarForm.value = false
    Object.assign(nuevo, { origenTipo: 'atencion_emergencia_id', origenId: '', patient_id: '', medico_certificador_id: '',
      fecha_defuncion: '', lugar_defuncion: '', tipo_muerte: 'NATURAL',
      causa_a_id: '', causa_b_id: '', causa_c_id: '', causa_d_id: '', observaciones: '' })
    await cargar()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function marcarEnviado(c: any) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/defunciones/' + c.id + '/marcar-enviado', { method: 'POST' })
    notice.value = 'Certificado marcado como enviado a RENIEC.'
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
.btn-secondary { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; text-decoration: none; }
.btn-secondary:hover { background: var(--mist); }
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { padding: 0.375rem 0.625rem; font-size: 0.75rem; }
.btn-active { background: var(--teal-soft); border-color: var(--teal); color: var(--teal); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); }
.alert-hint { display: flex; align-items: center; gap: 0.375rem; color: var(--alert); margin-top: -0.5rem; }
.field-sep { width: 1px; background: var(--line); margin: 0 0.25rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.search-actions { display: flex; gap: 0.375rem; flex-wrap: wrap; align-items: center; }
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
.row-actions { display: flex; align-items: center; gap: 0.375rem; flex-wrap: wrap; }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; white-space: nowrap; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-off { color: var(--ink-soft); background: var(--mist); }
.badge-pendiente { color: var(--amber); background: var(--amber-soft); }
.editor-form { display: flex; flex-direction: column; gap: 1rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }

@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
