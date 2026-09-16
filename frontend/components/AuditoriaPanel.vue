<template>
  <div class="lab-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-document-magnifying-glass" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ATENCIÓN HOSPITALARIA</span>
            <h1 class="page-title">Auditoría · {{ titles[mode] }}</h1>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary btn-sm" @click="init"><UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />Actualizar</button>
        <button v-if="mode==='auditoria'" class="btn-secondary btn-sm" @click="download"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />Exportar CSV</button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="lab-tabs">
      <NuxtLink v-for="(title, key) in titles" :key="key" :to="'/app/auditoria/'+key" class="tab-link" :class="{ 'tab-link--active': key === mode }">{{ title }}</NuxtLink>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>

    <!-- ═══════════ AUDITORIA (detalle, fila por fila) ═══════════ -->
    <template v-if="mode==='auditoria'">
      <section class="panel search-panel">
        <form class="search-form" @submit.prevent="buscar">
          <div class="search-grid">
            <div class="search-field">
              <label class="form-label">Módulo</label>
              <select v-model="filtro.modelo" class="input-clinical">
                <option value="">Todos</option>
                <option v-for="m in modelos" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
            <div class="search-field"><label class="form-label">Acción</label><input v-model="filtro.accion" class="input-clinical" placeholder="crear, anular, validar..." /></div>
            <div class="search-field"><label class="form-label">Usuario</label><input v-model="filtro.usuario" class="input-clinical" /></div>
            <div class="search-field"><label class="form-label">Buscar (id, descripción)</label><input v-model="filtro.q" class="input-clinical" /></div>
            <div class="search-field"><label class="form-label">Desde</label><input v-model="filtro.desde" type="date" class="input-clinical" /></div>
            <div class="search-field"><label class="form-label">Hasta</label><input v-model="filtro.hasta" type="date" class="input-clinical" /></div>
          </div>
          <div class="search-actions">
            <button type="button" class="btn-secondary" @click="limpiar"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Limpiar</button>
            <button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button>
          </div>
        </form>
      </section>

      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ total }} registros</h2></div>
        <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
        <div v-else class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Fecha (UTC)</th><th>Usuario</th><th>Módulo</th><th>Acción</th><th>Registro</th><th></th></tr></thead>
            <tbody>
              <tr v-for="a in lista" :key="a.id">
                <td>{{ a.created_at }}</td><td>{{ a.user_name || '—' }}</td><td>{{ a.model || '—' }}</td>
                <td>{{ a.action }}</td><td class="mono">{{ (a.model_id || '').slice(0, 8) }}</td>
                <td><button class="action-btn action-view" @click="verDetalle(a.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button></td>
              </tr>
              <tr v-if="!lista.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">Sin registros.</td></tr>
            </tbody>
          </table>
        </div>
        <nav class="pagination">
          <button class="btn-secondary btn-sm" :disabled="page<=1" @click="cambiarPagina(page-1)"><UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />Anterior</button>
          <span class="page-info">{{ page }} / {{ pages }}</span>
          <button class="btn-secondary btn-sm" :disabled="page>=pages" @click="cambiarPagina(page+1)">Siguiente<UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></button>
        </nav>
      </section>

      <section v-if="detalle" class="panel detail-panel">
        <div class="detail-header">
          <div><h2 class="detail-title">{{ detalle.model }} · {{ detalle.action }}</h2><p class="detail-subtitle">{{ detalle.user_name }} · {{ detalle.created_at }} UTC</p></div>
          <button class="btn-secondary" @click="detalle=null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button>
        </div>
        <p class="field-hint">Registro: {{ detalle.model_id }}</p>
        <p v-if="detalle.description" class="field-hint">{{ detalle.description }}</p>
        <div class="diff-grid">
          <div>
            <h4 class="section-title">Antes</h4>
            <pre v-if="detalle.old_values">{{ JSON.stringify(detalle.old_values, null, 2) }}</pre>
            <p v-else class="field-hint">Sin estado previo (creación).</p>
          </div>
          <div>
            <h4 class="section-title">Después</h4>
            <pre v-if="detalle.new_values">{{ JSON.stringify(detalle.new_values, null, 2) }}</pre>
            <p v-else class="field-hint">—</p>
          </div>
        </div>
      </section>
    </template>

    <!-- ═══════════ AUDITORIA GENERAL (resumen agregado) ═══════════ -->
    <template v-else-if="mode==='auditoria-general'">
      <section class="panel">
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Desde</label><input v-model="rango.desde" type="date" class="input-clinical" @change="cargarResumen" /></div>
          <div class="form-group"><label class="form-label">Hasta</label><input v-model="rango.hasta" type="date" class="input-clinical" @change="cargarResumen" /></div>
        </div>
      </section>

      <section v-if="resumen" class="panel">
        <h2 class="results-title">{{ resumen.total }} registros en el período</h2>
      </section>

      <div v-if="resumen" class="stats-grid">
        <section class="panel">
          <h3 class="section-title">Por módulo</h3>
          <div v-for="m in resumen.por_modelo" :key="m.modelo" class="stat-row">
            <span>{{ m.modelo }}</span>
            <div class="stat-bar-wrap"><div class="stat-bar" :style="{ width: pct(m.total, resumen.por_modelo) + '%' }"></div></div>
            <span class="stat-num">{{ m.total }}</span>
          </div>
          <p v-if="!resumen.por_modelo.length" class="field-hint">Sin datos en este período.</p>
        </section>
        <section class="panel">
          <h3 class="section-title">Por acción</h3>
          <div v-for="a in resumen.por_accion" :key="a.accion" class="stat-row">
            <span>{{ a.accion }}</span>
            <div class="stat-bar-wrap"><div class="stat-bar" :style="{ width: pct(a.total, resumen.por_accion) + '%' }"></div></div>
            <span class="stat-num">{{ a.total }}</span>
          </div>
        </section>
        <section class="panel">
          <h3 class="section-title">Por usuario (top 15)</h3>
          <div v-for="u in resumen.por_usuario" :key="u.usuario" class="stat-row">
            <span>{{ u.usuario }}</span>
            <div class="stat-bar-wrap"><div class="stat-bar" :style="{ width: pct(u.total, resumen.por_usuario) + '%' }"></div></div>
            <span class="stat-num">{{ u.total }}</span>
          </div>
        </section>
        <section class="panel">
          <h3 class="section-title">Últimos 30 días</h3>
          <div v-for="d in resumen.por_dia" :key="d.fecha" class="stat-row">
            <span>{{ d.fecha }}</span>
            <div class="stat-bar-wrap"><div class="stat-bar" :style="{ width: pct(d.total, resumen.por_dia) + '%' }"></div></div>
            <span class="stat-num">{{ d.total }}</span>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'auditoria' | 'auditoria-general'
const props = defineProps<{ mode: Mode }>()
const { api } = useApi()
const endpoint = '/app/auditoria'

const titles = { 'auditoria': 'Auditoría', 'auditoria-general': 'Auditoría General' }

const error = ref('')
const loading = ref(false)

const filtro = reactive({ modelo: '', accion: '', usuario: '', q: '', desde: '', hasta: '' })
const modelos = ref<string[]>([])
const lista = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const detalle = ref<any>(null)

const rango = reactive({ desde: '', hasta: '' })
const resumen = ref<any>(null)

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}

function pct(valor: number, lista: any[]) {
  const max = Math.max(...lista.map((x: any) => x.total), 1)
  return Math.max(4, Math.round((valor / max) * 100))
}

async function cargarModelos() {
  try { modelos.value = await api<string[]>(endpoint + '/catalogos/modelos') } catch (e) { /* filtro por texto sigue funcionando */ }
}

async function buscar() { page.value = 1; await cargarLista() }

function limpiar() {
  Object.assign(filtro, { modelo: '', accion: '', usuario: '', q: '', desde: '', hasta: '' })
  void buscar()
}

async function cargarLista() {
  loading.value = true; error.value = ''
  try {
    const q = Object.fromEntries(Object.entries(filtro).filter(([, v]) => v))
    const data = await api<any>(endpoint + '/auditoria', { query: { ...q, page: page.value, page_size: pageSize.value } })
    lista.value = data.items; total.value = data.total
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function cambiarPagina(p: number) { page.value = p; await cargarLista() }

async function verDetalle(id: string) {
  try { detalle.value = await api(endpoint + '/auditoria/' + id) } catch (e) { error.value = err(e) }
}

async function cargarResumen() {
  loading.value = true; error.value = ''
  try {
    const q = Object.fromEntries(Object.entries(rango).filter(([, v]) => v))
    resumen.value = await api(endpoint + '/auditoria-general/resumen', { query: q })
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function download() {
  try {
    const q = Object.fromEntries(Object.entries(filtro).filter(([, v]) => v))
    const blob = await api<Blob>(endpoint + '/reportes/auditoria.csv', { query: q, responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'auditoria.csv'; a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) { error.value = err(e) }
}

async function init() {
  if (props.mode === 'auditoria') { await cargarModelos(); await cargarLista() }
  else { await cargarResumen() }
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
.header-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.lab-tabs { display: flex; gap: 0.25rem; border-bottom: 2px solid var(--line); margin-bottom: 1.5rem; flex-wrap: wrap; }
.tab-link { padding: 0.625rem 1.25rem; font-size: 0.875rem; font-weight: 500; color: var(--ink-soft); text-decoration: none; border-bottom: 2px solid transparent; margin-bottom: -2px; }
.tab-link--active { color: var(--teal); border-bottom-color: var(--teal); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.search-form { display: flex; flex-direction: column; gap: 1rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
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
.mono { font-family: monospace; font-size: 0.75rem; }
.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; color: var(--ink-soft); cursor: pointer; }
.action-btn:hover { background: var(--mist); }
.action-view:hover { color: var(--teal); border-color: var(--teal-soft); background: var(--teal-soft); }
.pagination { display: flex; align-items: center; gap: 0.75rem; justify-content: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--line); }
.page-info { font-size: 0.8125rem; color: var(--ink-soft); }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.detail-title { font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0; }
.detail-subtitle { font-size: 0.875rem; color: var(--ink-soft); margin: 0.125rem 0 0 0; }
.section-title { font-size: 0.875rem; font-weight: 600; color: var(--ink); margin: 0 0 0.75rem 0; }
.diff-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; }
.diff-grid pre { background: var(--mist); border-radius: 6px; padding: 0.75rem; font-size: 0.75rem; overflow-x: auto; white-space: pre-wrap; word-break: break-word; }
.stats-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1.5rem; }
.stat-row { display: grid; grid-template-columns: 140px 1fr 40px; align-items: center; gap: 0.5rem; font-size: 0.8125rem; padding: 0.375rem 0; }
.stat-bar-wrap { background: var(--mist); border-radius: 4px; height: 8px; overflow: hidden; }
.stat-bar { background: var(--teal); height: 100%; border-radius: 4px; }
.stat-num { text-align: right; color: var(--ink-soft); }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid, .form-grid, .diff-grid, .stats-grid { grid-template-columns: 1fr; }
}
</style>
