<template>
  <div class="lab-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-computer-desktop" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ATENCIÓN HOSPITALARIA</span>
            <h1 class="page-title">General · {{ titles[mode] }}</h1>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary btn-sm" @click="init"><UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />Actualizar</button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="lab-tabs">
      <NuxtLink v-for="(title, key) in titles" :key="key" :to="'/app/general/'+key" class="tab-link" :class="{ 'tab-link--active': key === mode }">{{ title }}</NuxtLink>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <p class="field-hint" style="margin-bottom:1rem">Catálogo administrado en SIGARH · {{ mode==='servicios' ? 'Mantenimiento' : 'General' }}. Solo consulta desde aquí.</p>

    <!-- Búsqueda -->
    <section class="panel search-panel">
      <form class="search-form" @submit.prevent="buscar">
        <div class="search-grid">
          <div class="search-field"><label class="form-label">Buscar</label><input v-model="filtro.q" class="input-clinical" :placeholder="placeholders[mode]" /></div>
          <div class="search-field" v-if="mode==='diagnosticos'">
            <label class="form-label">Capítulo</label>
            <select v-model="filtro.capitulo" class="input-clinical">
              <option value="">Todos</option>
              <option v-for="c in capitulos" :key="c" :value="c">{{ c }}</option>
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

      <div v-else-if="mode==='servicios'" class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>Código</th><th>Nombre</th><th>Departamento</th><th>Tiempo atención</th><th></th></tr></thead>
          <tbody>
            <tr v-for="s in lista" :key="s.id">
              <td>{{ s.codigo || '—' }}</td><td>{{ s.nombre }}</td><td>{{ s.departamento_nombre || '—' }}</td>
              <td>{{ s.tiempo_atencion_min ? s.tiempo_atencion_min + ' min' : '—' }}</td>
              <td><button class="action-btn action-view" @click="verServicio(s.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button></td>
            </tr>
            <tr v-if="!lista.length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Sin resultados.</td></tr>
          </tbody>
        </table>
      </div>

      <div v-else-if="mode==='diagnosticos'" class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>CIE-10</th><th>Descripción</th><th>Capítulo</th><th>Sexo</th><th></th></tr></thead>
          <tbody>
            <tr v-for="d in lista" :key="d.id">
              <td class="mono">{{ d.codigo_cie10 }}</td><td>{{ d.descripcion }}</td><td>{{ d.capitulo || '—' }}</td><td>{{ d.sexo }}</td>
              <td><button class="action-btn action-view" @click="verDiagnostico(d.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button></td>
            </tr>
            <tr v-if="!lista.length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Sin resultados.</td></tr>
          </tbody>
        </table>
      </div>

      <div v-else class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>Código</th><th>Nombre</th><th>Especialidad</th><th></th></tr></thead>
          <tbody>
            <tr v-for="p in lista" :key="p.id">
              <td>{{ p.codigo || '—' }}</td><td>{{ p.nombre }}</td><td>{{ p.especialidad_nombre || '—' }}</td>
              <td><button class="action-btn action-view" @click="verPaquete(p.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button></td>
            </tr>
            <tr v-if="!lista.length"><td colspan="4" style="text-align:center;color:var(--ink-soft)">Sin resultados.</td></tr>
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
        <div><h2 class="detail-title">{{ detalle.nombre || detalle.descripcion }}</h2></div>
        <button class="btn-secondary" @click="detalle=null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button>
      </div>

      <div v-if="mode==='servicios'" class="detail-info">
        <p>Código {{ detalle.codigo || '—' }} · Departamento {{ detalle.departamento_nombre || '—' }} · Piso {{ detalle.piso_nombre || '—' }}</p>
        <p>Tiempo de atención: {{ detalle.tiempo_atencion_min ? detalle.tiempo_atencion_min + ' min' : 'No configurado (usa 15 min por defecto)' }}</p>
        <p v-if="detalle.descripcion">{{ detalle.descripcion }}</p>
      </div>

      <div v-else-if="mode==='diagnosticos'" class="detail-info">
        <p class="mono">{{ detalle.codigo_cie10 }} <span v-if="detalle.codigo_cie9">(CIE-9: {{ detalle.codigo_cie9 }})</span></p>
        <p>Capítulo {{ detalle.capitulo || '—' }} · Grupo {{ detalle.grupo || '—' }} · Categoría {{ detalle.categoria || '—' }}</p>
        <p>Sexo: {{ detalle.sexo }} <span v-if="detalle.edad_minima || detalle.edad_maxima">· Edad {{ detalle.edad_minima ?? '0' }}-{{ detalle.edad_maxima ?? '∞' }}</span></p>
        <p>
          <span v-if="detalle.morbilidad" class="tag">Morbilidad</span>
          <span v-if="detalle.intrahospitalario" class="tag">Intrahospitalario</span>
          <span v-if="detalle.gestacion" class="tag">Gestación</span>
        </p>
        <p v-if="detalle.vigencia_desde" class="field-hint">Vigente desde {{ detalle.vigencia_desde }}<span v-if="detalle.vigencia_hasta"> hasta {{ detalle.vigencia_hasta }}</span></p>
      </div>

      <template v-else>
        <div class="detail-info"><p>Código {{ detalle.codigo || '—' }} · Especialidad {{ detalle.especialidad_nombre || '—' }}</p><p v-if="detalle.descripcion">{{ detalle.descripcion }}</p></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Medicamento</th><th>DCI</th><th>Presentación</th><th>Cantidad</th></tr></thead>
            <tbody>
              <tr v-for="i in detalle.items" :key="i.id"><td>{{ i.medicamento_nombre || '—' }}</td><td>{{ i.dci || '—' }}</td><td>{{ i.presentacion || '—' }}</td><td>{{ i.cantidad }}</td></tr>
              <tr v-if="!detalle.items.length"><td colspan="4" style="text-align:center;color:var(--ink-soft)">Sin items.</td></tr>
            </tbody>
          </table>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
type Mode = 'servicios' | 'diagnosticos' | 'paquetes'
const props = defineProps<{ mode: Mode }>()
const { api } = useApi()
const endpoint = '/app/general'

const titles = { servicios: 'Servicios', diagnosticos: 'Diagnósticos', paquetes: 'Paquetes' }
const placeholders = { servicios: 'Nombre o código...', diagnosticos: 'Código CIE-10 o descripción...', paquetes: 'Nombre o código...' }

const error = ref('')
const loading = ref(false)
const filtro = reactive({ q: '', capitulo: '' })
const capitulos = ref<string[]>([])
const lista = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const detalle = ref<any>(null)

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}

async function buscar() { page.value = 1; detalle.value = null; await cargarLista() }

async function cargarLista() {
  loading.value = true; error.value = ''
  try {
    const q: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (filtro.q) q.q = filtro.q
    if (props.mode === 'diagnosticos' && filtro.capitulo) q.capitulo = filtro.capitulo
    const data = await api<any>(endpoint + '/' + props.mode, { query: q })
    lista.value = data.items; total.value = data.total
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function cambiarPagina(p: number) { page.value = p; await cargarLista() }

async function verServicio(id: string) { try { detalle.value = await api(endpoint + '/servicios/' + id) } catch (e) { error.value = err(e) } }
async function verDiagnostico(id: string) { try { detalle.value = await api(endpoint + '/diagnosticos/' + id) } catch (e) { error.value = err(e) } }
async function verPaquete(id: string) { try { detalle.value = await api(endpoint + '/paquetes/' + id) } catch (e) { error.value = err(e) } }

async function init() {
  detalle.value = null
  if (props.mode === 'diagnosticos' && !capitulos.value.length) {
    try { capitulos.value = await api<string[]>(endpoint + '/diagnosticos/capitulos') } catch (e) { /* filtro por texto sigue funcionando */ }
  }
  await cargarLista()
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
.lab-tabs { display: flex; gap: 0.25rem; border-bottom: 2px solid var(--line); margin-bottom: 1rem; flex-wrap: wrap; }
.tab-link { padding: 0.625rem 1.25rem; font-size: 0.875rem; font-weight: 500; color: var(--ink-soft); text-decoration: none; border-bottom: 2px solid transparent; margin-bottom: -2px; }
.tab-link--active { color: var(--teal); border-bottom-color: var(--teal); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
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
.mono { font-family: monospace; }
.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; color: var(--ink-soft); cursor: pointer; }
.action-btn:hover { background: var(--mist); }
.action-view:hover { color: var(--teal); border-color: var(--teal-soft); background: var(--teal-soft); }
.pagination { display: flex; align-items: center; gap: 0.75rem; justify-content: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--line); }
.page-info { font-size: 0.8125rem; color: var(--ink-soft); }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.detail-title { font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0; }
.detail-info { font-size: 0.875rem; color: var(--ink); padding: 0.5rem 0; }
.tag { display: inline-block; font-size: 0.6875rem; font-weight: 600; color: var(--teal); background: var(--teal-soft); padding: 0.125rem 0.5rem; border-radius: 999px; margin-right: 0.375rem; }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid { grid-template-columns: 1fr; }
}
</style>
