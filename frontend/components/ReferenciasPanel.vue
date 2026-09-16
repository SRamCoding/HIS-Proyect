<template>
  <div class="lab-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-arrow-top-right-on-square" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ATENCIÓN HOSPITALARIA</span>
            <h1 class="page-title">Referencias</h1>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary btn-sm" @click="cargarLista"><UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />Actualizar</button>
        <button class="btn-secondary btn-sm" @click="download('/reportes/referencias.csv', 'referencias.csv')"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />Exportar CSV</button>
        <button class="btn-primary" @click="abrirAdmision"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Admitir desde Emergencia</button>
      </div>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <!-- Admitir desde Emergencia -->
    <section v-if="formAdmision" class="panel">
      <div class="card-header-row"><h2 class="results-title">Admitir referencia derivada de Emergencia</h2>
        <button class="btn-secondary" @click="formAdmision=false"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
      <div class="choices">
        <button v-for="d in pendientesEmergencia" :key="d.destino_id" class="choice-btn" :class="{'choice-btn--active': admisionForm.destino_id===d.destino_id}" @click="admisionForm.destino_id=d.destino_id">
          {{ d.numero_cuenta }} · {{ d.paciente_nombre }} · {{ d.paciente_dni }}
        </button>
        <p v-if="!pendientesEmergencia.length" class="field-hint">No hay pacientes de Emergencia esperando referencia.</p>
      </div>
      <form v-if="admisionForm.destino_id" class="editor-form" @submit.prevent="admitirEmergencia">
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Tipo de destino</label>
            <select v-model="admisionForm.tipo" class="input-clinical"><option value="EXTERNO">IPRESS externo</option><option value="INTERNO">Hospital del sistema</option></select>
          </div>
          <div class="form-group" v-if="admisionForm.tipo==='EXTERNO'">
            <label class="form-label">Establecimiento destino</label>
            <input v-model="admisionForm.nombre_ipress_destino" class="input-clinical" required maxlength="255" />
          </div>
          <div class="form-group" v-if="admisionForm.tipo==='EXTERNO'">
            <label class="form-label">Código RENIPRESS (opcional)</label>
            <input v-model="admisionForm.codigo_renipress_destino" class="input-clinical" maxlength="20" />
          </div>
          <div class="form-group" v-if="admisionForm.tipo==='INTERNO'">
            <label class="form-label">Hospital destino</label>
            <select v-model="admisionForm.tenant_destino_id" class="input-clinical" required>
              <option value="">Seleccionar</option><option v-for="t in catalogs.tenants" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Especialidad destino</label>
            <input v-model="admisionForm.especialidad_destino" class="input-clinical" maxlength="150" />
          </div>
          <div class="form-group">
            <label class="form-label">Diagnóstico</label>
            <select v-model="admisionForm.diagnostico_id" class="input-clinical">
              <option value="">Sin especificar</option><option v-for="d in catalogs.diagnosticos" :key="d.id" :value="d.id">{{ d.codigo }} · {{ d.descripcion }}</option>
            </select>
          </div>
          <div class="form-group full-width"><label class="form-label">Motivo</label><textarea v-model="admisionForm.motivo" class="input-clinical" rows="2" required maxlength="4000"></textarea></div>
        </div>
        <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Generar referencia</button></div>
      </form>
    </section>

    <!-- Búsqueda -->
    <section class="panel search-panel">
      <form class="search-form" @submit.prevent="buscar">
        <div class="search-grid">
          <div class="search-field"><label class="form-label">Buscar paciente / N.° referencia</label><input v-model="filtro.q" class="input-clinical" /></div>
          <div class="search-field">
            <label class="form-label">Estado</label>
            <select v-model="filtro.estado" class="input-clinical">
              <option value="">Todos</option><option value="enviada">Enviada</option><option value="aceptada">Aceptada</option>
              <option value="rechazada">Rechazada</option><option value="contrarreferida">Contrarreferida</option>
            </select>
          </div>
        </div>
        <div class="search-actions"><button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button></div>
      </form>
    </section>

    <!-- Resultados -->
    <section class="panel results-panel">
      <div class="results-header"><h2 class="results-title">{{ total }} registros</h2></div>
      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <div v-else class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>N.°</th><th>Paciente</th><th>Origen</th><th>Destino</th><th>Estado</th><th>Fecha</th><th></th></tr></thead>
          <tbody>
            <tr v-for="r in lista" :key="r.id">
              <td>{{ r.numero_referencia }}</td><td>{{ r.paciente }}</td><td>{{ r.origen }}</td>
              <td>{{ r.nombre_ipress_destino || r.tenant_destino_nombre || '—' }}</td>
              <td>{{ r.estado }}</td><td>{{ r.created_at }}</td>
              <td>
                <div class="action-buttons">
                  <button class="action-btn action-view" @click="verReferencia(r.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button>
                  <button class="action-btn action-pdf" @click="download('/referencias/'+r.id+'/comprobante.pdf', 'referencia.pdf')"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" /></button>
                </div>
              </td>
            </tr>
            <tr v-if="!lista.length"><td colspan="7" style="text-align:center;color:var(--ink-soft)">Sin referencias.</td></tr>
          </tbody>
        </table>
      </div>
      <nav class="pagination">
        <button class="btn-secondary btn-sm" :disabled="page<=1" @click="cambiarPagina(page-1)"><UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />Anterior</button>
        <span class="page-info">{{ page }} / {{ pages }}</span>
        <button class="btn-secondary btn-sm" :disabled="page>=pages" @click="cambiarPagina(page+1)">Siguiente<UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></button>
      </nav>
    </section>

    <!-- Detalle -->
    <section v-if="detalle" class="panel detail-panel">
      <div class="detail-header">
        <div><h2 class="detail-title">{{ detalle.numero_referencia }}</h2><p class="detail-subtitle">{{ detalle.paciente }} · HC {{ detalle.historia }} · {{ detalle.estado }}</p></div>
        <button class="btn-secondary" @click="detalle=null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button>
      </div>
      <div class="detail-info">
        <p>Origen {{ detalle.origen }} · Destino {{ detalle.nombre_ipress_destino || detalle.tenant_destino_nombre || '—' }} ({{ detalle.destino_tipo }}) · Especialidad {{ detalle.especialidad_destino || '—' }}</p>
        <p>Diagnóstico {{ detalle.diagnostico_codigo || '—' }} {{ detalle.diagnostico_descripcion || '' }}</p>
        <p>Motivo: {{ detalle.motivo }}</p>
        <p v-if="detalle.observacion_resolucion" class="field-hint">Resolución: {{ detalle.observacion_resolucion }}</p>
      </div>

      <template v-if="detalle.estado==='contrarreferida'">
        <h3 class="section-title">Contrarreferencia</h3>
        <p>Fecha {{ detalle.fecha_contrarreferencia }} · Profesional {{ detalle.profesional_receptor }}</p>
        <p>{{ detalle.resumen_contrarreferencia }}</p>
      </template>

      <form v-if="detalle.estado==='enviada'" class="editor-form" @submit.prevent="resolver">
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Resolución</label>
            <select v-model="resolucionForm.estado" class="input-clinical"><option value="aceptada">Aceptada por el destino</option><option value="rechazada">Rechazada</option></select>
          </div>
          <div class="form-group full-width"><label class="form-label">Observación</label><textarea v-model="resolucionForm.observacion_resolucion" class="input-clinical" rows="2" maxlength="2000"></textarea></div>
        </div>
        <div class="form-actions"><button class="btn-secondary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Registrar resolución</button></div>
      </form>

      <form v-if="['enviada','aceptada'].includes(detalle.estado)" class="editor-form" @submit.prevent="contrarreferir">
        <h3 class="section-title">Registrar contrarreferencia</h3>
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Fecha</label><input v-model="contraForm.fecha_contrarreferencia" type="date" class="input-clinical" required /></div>
          <div class="form-group"><label class="form-label">Profesional receptor</label><input v-model="contraForm.profesional_receptor" class="input-clinical" required maxlength="255" /></div>
          <div class="form-group"><label class="form-label">Diagnóstico</label>
            <select v-model="contraForm.diagnostico_contrarreferencia_id" class="input-clinical">
              <option value="">Sin especificar</option><option v-for="d in catalogs.diagnosticos" :key="d.id" :value="d.id">{{ d.codigo }} · {{ d.descripcion }}</option>
            </select>
          </div>
          <div class="form-group full-width"><label class="form-label">Resumen</label><textarea v-model="contraForm.resumen_contrarreferencia" class="input-clinical" rows="3" required maxlength="4000"></textarea></div>
        </div>
        <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Registrar contrarreferencia</button></div>
      </form>
    </section>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const endpoint = '/app/referencias'

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)

const filtro = reactive({ q: '', estado: '' })
const lista = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const detalle = ref<any>(null)

const catalogs = reactive<Record<string, any[]>>({ diagnosticos: [], tenants: [] })
const pendientesEmergencia = ref<any[]>([])
const formAdmision = ref(false)
const admisionForm = reactive({ destino_id: '', tipo: 'EXTERNO', nombre_ipress_destino: '', codigo_renipress_destino: '',
  tenant_destino_id: '', especialidad_destino: '', diagnostico_id: '', motivo: '' })
const resolucionForm = reactive({ estado: 'aceptada', observacion_resolucion: '' })
const contraForm = reactive({ fecha_contrarreferencia: today(), profesional_receptor: '', diagnostico_contrarreferencia_id: '', resumen_contrarreferencia: '' })

function today() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date())
}

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}

async function run(fn: () => Promise<void>) {
  if (busy.value) return
  busy.value = true; error.value = ''; notice.value = ''
  try { await fn() } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function getCatalogs() {
  catalogs.diagnosticos = await api<any[]>(endpoint + '/catalogos/diagnosticos')
  catalogs.tenants = await api<any[]>(endpoint + '/catalogos/tenants')
}

async function abrirAdmision() {
  await run(async () => {
    formAdmision.value = true
    await getCatalogs()
    pendientesEmergencia.value = await api<any[]>(endpoint + '/emergencia-pendientes')
    Object.assign(admisionForm, { destino_id: '', tipo: 'EXTERNO', nombre_ipress_destino: '', codigo_renipress_destino: '',
      tenant_destino_id: '', especialidad_destino: '', diagnostico_id: '', motivo: '' })
  })
}

async function admitirEmergencia() {
  await run(async () => {
    const body: Record<string, any> = { destino_id: admisionForm.destino_id, especialidad_destino: admisionForm.especialidad_destino || null,
      diagnostico_id: admisionForm.diagnostico_id || null, motivo: admisionForm.motivo }
    if (admisionForm.tipo === 'EXTERNO') { body.nombre_ipress_destino = admisionForm.nombre_ipress_destino; body.codigo_renipress_destino = admisionForm.codigo_renipress_destino || null }
    else { body.tenant_destino_id = admisionForm.tenant_destino_id }
    await api(endpoint + '/referencias/admitir-emergencia', { method: 'POST', body })
    notice.value = 'Referencia generada.'
    formAdmision.value = false
    await cargarLista()
  })
}

async function buscar() { page.value = 1; await cargarLista() }

async function cargarLista() {
  loading.value = true; error.value = ''
  try {
    const q: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (filtro.q) q.q = filtro.q
    if (filtro.estado) q.estado = filtro.estado
    const data = await api<any>(endpoint + '/referencias', { query: q })
    lista.value = data.items; total.value = data.total
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function cambiarPagina(p: number) { page.value = p; await cargarLista() }

async function verReferencia(id: string) {
  await run(async () => {
    detalle.value = await api(endpoint + '/referencias/' + id)
    Object.assign(resolucionForm, { estado: 'aceptada', observacion_resolucion: '' })
    Object.assign(contraForm, { fecha_contrarreferencia: today(), profesional_receptor: '', diagnostico_contrarreferencia_id: '', resumen_contrarreferencia: '' })
    if (!catalogs.diagnosticos.length) await getCatalogs()
  })
}

async function resolver() {
  await run(async () => {
    detalle.value = await api(endpoint + '/referencias/' + detalle.value.id + '/resolver', { method: 'POST', body: resolucionForm })
    notice.value = 'Resolución registrada.'
    await cargarLista()
  })
}

async function contrarreferir() {
  await run(async () => {
    const body = { ...contraForm, diagnostico_contrarreferencia_id: contraForm.diagnostico_contrarreferencia_id || null }
    detalle.value = await api(endpoint + '/referencias/' + detalle.value.id + '/contrarreferencia', { method: 'POST', body })
    notice.value = 'Contrarreferencia registrada.'
    await cargarLista()
  })
}

async function download(path: string, name: string) {
  await run(async () => {
    const blob = await api<Blob>(endpoint + path, { responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = name; a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  })
}

onMounted(cargarLista)
</script>

<style scoped>
.lab-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.header-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.search-form { display: flex; flex-direction: column; gap: 1rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.search-field { display: flex; flex-direction: column; gap: 0.25rem; }
.search-actions { display: flex; gap: 0.75rem; justify-content: flex-end; }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.action-buttons { display: flex; gap: 0.25rem; }
.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; color: var(--ink-soft); cursor: pointer; }
.action-btn:hover { background: var(--mist); }
.action-view:hover { color: var(--teal); border-color: var(--teal-soft); background: var(--teal-soft); }
.action-pdf:hover { color: var(--alert); border-color: var(--alert-soft); background: var(--alert-soft); }
.pagination { display: flex; align-items: center; gap: 0.75rem; justify-content: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--line); }
.page-info { font-size: 0.8125rem; color: var(--ink-soft); }
.editor-form { display: flex; flex-direction: column; gap: 1rem; margin-top: 0.75rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.5rem; }
.choices { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.75rem 0; }
.choice-btn { padding: 0.375rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.8125rem; cursor: pointer; }
.choice-btn:hover, .choice-btn--active { background: var(--teal-soft); border-color: var(--teal); }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.detail-title { font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0; }
.detail-subtitle { font-size: 0.875rem; color: var(--ink-soft); margin: 0.125rem 0 0 0; }
.detail-info { font-size: 0.875rem; color: var(--ink); padding: 0.5rem 0; }
.section-title { font-size: 0.875rem; font-weight: 600; color: var(--ink); margin: 0 0 0.5rem 0; }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid, .form-grid { grid-template-columns: 1fr; }
}
</style>
