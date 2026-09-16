<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-document-text" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">SIS · SEGURO INTEGRAL DE SALUD</span>
          <h1 class="page-title">{{ mode === 'formato-fua' ? 'Formato FUA' : 'Afiliaciones SIS' }}</h1>
        </div>
      </div>
      <button class="btn-secondary btn-sm" @click="init"><UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />Actualizar</button>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <!-- ═══════════ FORMATO FUA ═══════════ -->
    <template v-if="mode === 'formato-fua'">
      <section v-if="pendientes.length" class="panel">
        <div class="card-header-row"><h2 class="results-title">Atenciones SIS pendientes de generar FUA <span class="card-badge">{{ pendientes.length }}</span></h2></div>
        <div class="choices-list">
          <div v-for="p in pendientes" :key="(p.atencion_medica_id || p.atencion_emergencia_id)" class="pending-item">
            <div>
              <span class="pending-name">{{ p.paciente_nombre }}</span>
              <span class="field-hint">{{ p.paciente_dni }} · {{ p.origen === 'CONSULTA_EXTERNA' ? 'Consulta Externa' : 'Emergencia' }} · {{ p.seguro_nombre }} · {{ formatFecha(p.fecha_atencion) }}</span>
            </div>
            <button class="btn-primary btn-sm" :disabled="busy" @click="generarFua(p)"><UIcon name="i-heroicons-document-plus" class="w-4 h-4" />Generar FUA</button>
          </div>
        </div>
      </section>

      <section class="panel search-panel">
        <form class="search-form" @submit.prevent="buscarFua">
          <div class="search-grid">
            <div class="search-field"><label class="form-label">Paciente, DNI o N.° FUA</label><input v-model="filtro.q" class="input-clinical" /></div>
            <div class="search-field">
              <label class="form-label">Estado</label>
              <select v-model="filtro.estado" class="input-clinical"><option value="">Todos</option>
                <option value="generado">Generado</option><option value="enviado">Enviado</option>
                <option value="observado">Observado</option><option value="pagado">Pagado</option><option value="anulado">Anulado</option>
              </select>
            </div>
          </div>
          <div class="search-actions"><button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button></div>
        </form>
      </section>

      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ total }} FUA</h2></div>
        <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
        <div v-else class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>N.° FUA</th><th>Paciente</th><th>Seguro</th><th>Fecha atención</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              <tr v-for="f in items" :key="f.id">
                <td>{{ f.numero_fua }}</td><td>{{ f.paciente_nombre }}</td><td>{{ f.seguro_nombre }}</td>
                <td>{{ formatFecha(f.fecha_atencion) }}</td>
                <td><span class="badge" :class="'badge-' + f.estado">{{ f.estado }}</span></td>
                <td><button class="action-btn action-view" @click="verDetalle(f.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button></td>
              </tr>
              <tr v-if="!items.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">Sin registros.</td></tr>
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
          <div><h2 class="detail-title">{{ detalle.numero_fua }}</h2><p class="detail-subtitle">{{ detalle.paciente_nombre }} · HC {{ detalle.historia }} · {{ detalle.seguro_nombre }} · <span class="badge" :class="'badge-' + detalle.estado">{{ detalle.estado }}</span></p></div>
          <div class="detail-actions">
            <button class="btn-secondary" @click="download(detalle.id)"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />PDF</button>
            <button class="btn-secondary" @click="detalle=null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button>
          </div>
        </div>
        <div class="detail-info">
          <p>Origen {{ detalle.origen === 'CONSULTA_EXTERNA' ? 'Consulta Externa' : 'Emergencia' }} · Cuenta {{ detalle.numero_cuenta || '—' }} · Profesional {{ detalle.profesional_nombre || '—' }}</p>
          <p>Prestaciones: <span v-if="detalle.prestaciones.length">{{ detalle.prestaciones.join(', ') }}</span><span v-else>—</span></p>
        </div>
        <h3 class="section-title">Diagnósticos CIE-10</h3>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Código</th><th>Descripción</th><th>Tipo</th></tr></thead>
            <tbody>
              <tr v-for="(dx, i) in detalle.diagnosticos" :key="i"><td>{{ dx.codigo }}</td><td>{{ dx.descripcion }}</td><td>{{ dx.tipo }}</td></tr>
              <tr v-if="!detalle.diagnosticos.length"><td colspan="3" style="text-align:center;color:var(--ink-soft)">Sin diagnósticos registrados.</td></tr>
            </tbody>
          </table>
        </div>
        <div v-if="transicionesDisponibles.length" class="form-actions" style="margin-top:1rem">
          <template v-for="t in transicionesDisponibles" :key="t">
            <button v-if="t !== 'observado' && t !== 'anulado'" class="btn-primary" :disabled="busy" @click="cambiarEstado(t)">Marcar {{ t }}</button>
          </template>
          <button v-if="transicionesDisponibles.includes('observado')" class="btn-secondary" :disabled="busy" @click="motivoPara='observado'">Observar</button>
          <button v-if="transicionesDisponibles.includes('anulado')" class="btn-secondary" style="color:var(--alert)" :disabled="busy" @click="motivoPara='anulado'">Anular</button>
        </div>
        <form v-if="motivoPara" class="cancel-form" @submit.prevent="cambiarEstado(motivoPara)">
          <div class="form-group"><label class="form-label">Motivo</label><textarea v-model="motivo" class="input-clinical" required rows="2"></textarea></div>
          <div class="form-actions"><button class="btn-danger" :disabled="busy">Confirmar {{ motivoPara }}</button><button type="button" class="btn-secondary" @click="motivoPara=''; motivo=''">Cancelar</button></div>
        </form>
      </section>
    </template>

    <!-- ═══════════ AFILIACIONES SIS ═══════════ -->
    <template v-else>
      <section class="panel search-panel">
        <form class="search-form" @submit.prevent="buscarAfiliaciones">
          <div class="search-grid">
            <div class="search-field"><label class="form-label">Paciente o DNI</label><input v-model="filtroAfil.q" class="input-clinical" /></div>
          </div>
          <div class="search-actions"><button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button></div>
        </form>
      </section>
      <p class="field-hint" style="margin-bottom:1rem">Pacientes con seguro SIS registrado en Admisión. Para editar la afiliación, ve a Admisión → Pacientes.</p>
      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ totalAfil }} afiliados</h2></div>
        <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
        <div v-else class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Paciente</th><th>DNI</th><th>H.C.</th><th>Seguro</th><th>N.° afiliación</th><th>Estado</th></tr></thead>
            <tbody>
              <tr v-for="a in afiliaciones" :key="a.id">
                <td>{{ a.nombre }}</td><td>{{ a.dni || 'NN' }}</td><td>{{ a.historia || '—' }}</td>
                <td>{{ a.insurance_type }}</td><td>{{ a.insurance_number || '—' }}</td>
                <td><span class="badge" :class="a.is_active ? 'badge-generado' : 'badge-anulado'">{{ a.is_active ? 'Activo' : 'Inactivo' }}</span></td>
              </tr>
              <tr v-if="!afiliaciones.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">Sin pacientes con seguro SIS registrado.</td></tr>
            </tbody>
          </table>
        </div>
        <nav class="pagination">
          <button class="btn-secondary btn-sm" :disabled="pageAfil<=1" @click="cambiarPaginaAfil(pageAfil-1)"><UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />Anterior</button>
          <span class="page-info">{{ pageAfil }} / {{ pagesAfil }}</span>
          <button class="btn-secondary btn-sm" :disabled="pageAfil>=pagesAfil" @click="cambiarPaginaAfil(pageAfil+1)">Siguiente<UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></button>
        </nav>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'formato-fua' | 'afiliaciones'
const props = defineProps<{ mode: Mode }>()
const { api } = useApi()
const endpoint = '/app/sis'

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)

// Formato FUA
const pendientes = ref<any[]>([])
const filtro = reactive({ q: '', estado: '' })
const items = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const detalle = ref<any>(null)
const motivoPara = ref('')
const motivo = ref('')

const transiciones: Record<string, string[]> = {
  generado: ['enviado', 'anulado'],
  enviado: ['observado', 'pagado', 'anulado'],
  observado: ['enviado', 'anulado'],
  pagado: [], anulado: [],
}
const transicionesDisponibles = computed(() => detalle.value ? (transiciones[detalle.value.estado] || []) : [])

function formatFecha(f: string) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
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

async function cargarPendientes() {
  try { pendientes.value = await api<any[]>(endpoint + '/formato-fua/pendientes') } catch (e) { /* opcional */ }
}

async function buscarFua() { page.value = 1; await cargarFua() }

async function cargarFua() {
  loading.value = true; error.value = ''
  try {
    const q: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (filtro.q) q.q = filtro.q
    if (filtro.estado) q.estado = filtro.estado
    const data = await api<any>(endpoint + '/formato-fua', { query: q })
    items.value = data.items; total.value = data.total
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function cambiarPagina(p: number) { page.value = p; await cargarFua() }

async function generarFua(p: any) {
  await run(async () => {
    await api(endpoint + '/formato-fua', { method: 'POST', body: {
      atencion_medica_id: p.atencion_medica_id, atencion_emergencia_id: p.atencion_emergencia_id,
    } })
    notice.value = 'FUA generado correctamente.'
    await cargarPendientes()
    await cargarFua()
  })
}

async function verDetalle(id: string) {
  await run(async () => {
    detalle.value = await api(endpoint + '/formato-fua/' + id)
    motivoPara.value = ''; motivo.value = ''
  })
}

async function cambiarEstado(estado: string) {
  await run(async () => {
    await api(endpoint + '/formato-fua/' + detalle.value.id + '/estado', { method: 'POST', body: { estado, observaciones: motivo.value || undefined } })
    notice.value = 'Estado actualizado.'
    motivoPara.value = ''; motivo.value = ''
    await verDetalle(detalle.value.id)
    await cargarFua()
  })
}

async function download(id: string) {
  await run(async () => {
    const blob = await api<Blob>(endpoint + '/formato-fua/' + id + '/reporte.pdf', { responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'fua.pdf'; a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  })
}

// Afiliaciones
const filtroAfil = reactive({ q: '' })
const afiliaciones = ref<any[]>([])
const totalAfil = ref(0)
const pageAfil = ref(1)
const pageSizeAfil = ref(20)
const pagesAfil = computed(() => Math.max(1, Math.ceil(totalAfil.value / pageSizeAfil.value)))

async function buscarAfiliaciones() { pageAfil.value = 1; await cargarAfiliaciones() }

async function cargarAfiliaciones() {
  loading.value = true; error.value = ''
  try {
    const q: Record<string, any> = { page: pageAfil.value, page_size: pageSizeAfil.value }
    if (filtroAfil.q) q.q = filtroAfil.q
    const data = await api<any>(endpoint + '/afiliaciones', { query: q })
    afiliaciones.value = data.items; totalAfil.value = data.total
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function cambiarPaginaAfil(p: number) { pageAfil.value = p; await cargarAfiliaciones() }

async function init() {
  detalle.value = null
  if (props.mode === 'formato-fua') { await cargarPendientes(); await cargarFua() }
  else { await cargarAfiliaciones() }
}

onMounted(init)
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
.btn-danger { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--alert); color: white; border: none; cursor: pointer; }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.card-badge { font-size: 0.625rem; font-weight: 500; padding: 0.125rem 0.5rem; border-radius: 10px; background: var(--amber-soft); color: var(--amber); margin-left: 0.375rem; }
.choices-list { display: flex; flex-direction: column; gap: 0.5rem; }
.pending-item { display: flex; justify-content: space-between; align-items: center; padding: 0.75rem 1rem; border-radius: var(--radius); border: 1px solid var(--line); background: var(--paper); gap: 1rem; flex-wrap: wrap; }
.pending-name { font-weight: 500; color: var(--ink); display: block; }
.search-form { display: flex; flex-direction: column; gap: 1rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
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
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; text-transform: capitalize; }
.badge-generado { color: var(--teal); background: var(--teal-soft); }
.badge-enviado { color: var(--navy); background: rgba(30,58,95,0.08); }
.badge-observado { color: var(--amber); background: var(--amber-soft); }
.badge-pagado { color: var(--green); background: var(--green-soft); }
.badge-anulado { color: var(--alert); background: var(--alert-soft); }
.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; color: var(--ink-soft); cursor: pointer; }
.action-btn:hover { background: var(--mist); }
.action-view:hover { color: var(--teal); border-color: var(--teal-soft); background: var(--teal-soft); }
.pagination { display: flex; align-items: center; gap: 0.75rem; justify-content: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--line); }
.page-info { font-size: 0.8125rem; color: var(--ink-soft); }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.75rem; }
.detail-actions { display: flex; gap: 0.5rem; }
.detail-title { font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0; }
.detail-subtitle { font-size: 0.875rem; color: var(--ink-soft); margin: 0.125rem 0 0 0; display: flex; align-items: center; gap: 0.375rem; flex-wrap: wrap; }
.detail-info { font-size: 0.875rem; color: var(--ink); padding: 0.5rem 0; }
.section-title { font-size: 0.875rem; font-weight: 600; color: var(--ink); margin: 1.25rem 0 0.5rem 0; padding-top: 0.75rem; border-top: 1px solid var(--line); }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.cancel-form { border-top: 1px solid var(--alert-soft); padding-top: 1rem; margin-top: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid { grid-template-columns: 1fr; }
}
</style>
