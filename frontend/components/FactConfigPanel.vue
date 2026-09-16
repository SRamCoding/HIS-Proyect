<template>
  <div class="lab-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ATENCIÓN HOSPITALARIA</span>
            <h1 class="page-title">Fact - Config · {{ titles[mode] }}</h1>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary btn-sm" @click="init"><UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />Actualizar</button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="lab-tabs">
      <NuxtLink v-for="(title, key) in titles" :key="key" :to="'/app/fact-config/'+key" class="tab-link" :class="{ 'tab-link--active': key === mode }">{{ title }}</NuxtLink>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <p class="field-hint" style="margin-bottom:1rem">Catálogo administrado en SIGARH · {{ mode==='catalogo-bienes-insumos' ? 'Config. Farmacia' : 'Config. Financiera' }}. Solo consulta desde aquí.</p>

    <!-- Búsqueda -->
    <section class="panel search-panel">
      <form class="search-form" @submit.prevent="buscar">
        <div class="search-grid">
          <div class="search-field"><label class="form-label">Buscar</label><input v-model="filtro.q" class="input-clinical" :placeholder="placeholders[mode]" /></div>
          <div class="search-field" v-if="mode==='catalogo-bienes-insumos'">
            <label class="form-label">Tipo de producto</label>
            <select v-model="filtro.tipo_id" class="input-clinical">
              <option value="">Todos</option>
              <option v-for="t in tipos" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div class="search-field" v-else>
            <label class="form-label">Tipo de servicio</label>
            <select v-model="filtro.tipo_servicio" class="input-clinical">
              <option value="">Todos</option>
              <option value="CONSULTA_EXTERNA">Consulta externa</option>
              <option value="APOYO_DIAGNOSTICO">Apoyo al diagnóstico</option>
              <option value="HOSPITALIZACION">Hospitalización</option>
              <option value="EMERGENCIA">Emergencia</option>
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

      <div v-else-if="mode==='catalogo-bienes-insumos'" class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>Código</th><th>Nombre comercial</th><th>DCI</th><th>Tipo</th><th>Precio ref. S/</th><th></th></tr></thead>
          <tbody>
            <tr v-for="b in lista" :key="b.id">
              <td>{{ b.codigo_interno }}</td><td>{{ b.nombre_comercial }}</td><td>{{ b.dci || '—' }}</td>
              <td>{{ b.tipo_producto_nombre || '—' }}</td><td>{{ b.precio_referencia?.toFixed(2) ?? '—' }}</td>
              <td><button class="action-btn action-view" @click="verBien(b.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button></td>
            </tr>
            <tr v-if="!lista.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">Sin resultados.</td></tr>
          </tbody>
        </table>
      </div>

      <div v-else class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>Código</th><th>Servicio</th><th>Tipo</th><th>Especialidad</th><th>Seguro</th><th>Precio S/</th><th></th></tr></thead>
          <tbody>
            <tr v-for="s in lista" :key="s.id">
              <td>{{ s.codigo || '—' }}</td><td>{{ s.descripcion_servicio }}</td><td>{{ s.tipo_servicio || '—' }}</td>
              <td>{{ s.especialidad_nombre || '—' }}</td><td>{{ s.seguro_nombre || 'General' }}</td><td>{{ s.precio?.toFixed(2) ?? '0.00' }}</td>
              <td><button class="action-btn action-view" @click="verServicio(s.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button></td>
            </tr>
            <tr v-if="!lista.length"><td colspan="7" style="text-align:center;color:var(--ink-soft)">Sin resultados.</td></tr>
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
        <div><h2 class="detail-title">{{ detalle.nombre_comercial || detalle.descripcion_servicio }}</h2></div>
        <button class="btn-secondary" @click="detalle=null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button>
      </div>

      <div v-if="mode==='catalogo-bienes-insumos'" class="detail-info">
        <p>Código {{ detalle.codigo_interno }} · Tipo {{ detalle.tipo_producto_nombre || '—' }} · Unidad {{ detalle.unidad }}</p>
        <p>DCI {{ detalle.dci || '—' }} · Genérico {{ detalle.nombre_generico }} · Presentación {{ detalle.presentacion || '—' }} <span v-if="detalle.concentracion">· {{ detalle.concentracion }}</span></p>
        <p>Precio referencial S/ {{ detalle.precio_referencia?.toFixed(2) ?? '—' }} <span v-if="detalle.precio_referencia_sismed">· SISMED S/ {{ detalle.precio_referencia_sismed.toFixed(2) }}</span></p>
        <p>Registro sanitario {{ detalle.numero_registro_sanitario || '—' }} · Condición de venta: {{ detalle.condicion_venta }}</p>
        <p>
          <span v-if="detalle.requiere_receta" class="tag">Requiere receta</span>
          <span v-if="detalle.controlado" class="tag">Controlado</span>
          <span v-if="detalle.fiscalizado_digemid" class="tag">Fiscalizado DIGEMID</span>
          <span v-if="detalle.reporte_sismed" class="tag">Reporta a SISMED</span>
        </p>
      </div>

      <div v-else class="detail-info">
        <p>Código {{ detalle.codigo || '—' }} · Tipo de servicio {{ detalle.tipo_servicio || '—' }}</p>
        <p>Especialidad {{ detalle.especialidad_nombre || 'Sin especialidad' }} · Seguro {{ detalle.seguro_nombre || 'Tarifa general (todo seguro)' }}</p>
        <p class="total">Precio S/ {{ detalle.precio?.toFixed(2) ?? '0.00' }}</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
type Mode = 'catalogo-bienes-insumos' | 'catalogo-servicios'
const props = defineProps<{ mode: Mode }>()
const { api } = useApi()
const endpoint = '/app/fact-config'

const titles = { 'catalogo-bienes-insumos': 'Catálogo de Bienes e Insumos', 'catalogo-servicios': 'Catálogo de Servicios' }
const placeholders = { 'catalogo-bienes-insumos': 'Nombre, código o DCI...', 'catalogo-servicios': 'Nombre o código del servicio...' }

const error = ref('')
const loading = ref(false)
const filtro = reactive({ q: '', tipo_id: '', tipo_servicio: '' })
const tipos = ref<any[]>([])
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
    if (props.mode === 'catalogo-bienes-insumos' && filtro.tipo_id) q.tipo_id = filtro.tipo_id
    if (props.mode === 'catalogo-servicios' && filtro.tipo_servicio) q.tipo_servicio = filtro.tipo_servicio
    const path = props.mode === 'catalogo-bienes-insumos' ? '/bienes-insumos' : '/servicios'
    const data = await api<any>(endpoint + path, { query: q })
    lista.value = data.items; total.value = data.total
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function cambiarPagina(p: number) { page.value = p; await cargarLista() }

async function verBien(id: string) { try { detalle.value = await api(endpoint + '/bienes-insumos/' + id) } catch (e) { error.value = err(e) } }
async function verServicio(id: string) { try { detalle.value = await api(endpoint + '/servicios/' + id) } catch (e) { error.value = err(e) } }

async function init() {
  detalle.value = null
  if (props.mode === 'catalogo-bienes-insumos' && !tipos.value.length) {
    try { tipos.value = await api<any[]>(endpoint + '/catalogos/tipos-producto') } catch (e) { /* filtro por texto sigue funcionando */ }
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
.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; color: var(--ink-soft); cursor: pointer; }
.action-btn:hover { background: var(--mist); }
.action-view:hover { color: var(--teal); border-color: var(--teal-soft); background: var(--teal-soft); }
.pagination { display: flex; align-items: center; gap: 0.75rem; justify-content: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--line); }
.page-info { font-size: 0.8125rem; color: var(--ink-soft); }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.detail-title { font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0; }
.detail-info { font-size: 0.875rem; color: var(--ink); padding: 0.5rem 0; }
.total { font-weight: 600; font-size: 1rem; }
.tag { display: inline-block; font-size: 0.6875rem; font-weight: 600; color: var(--teal); background: var(--teal-soft); padding: 0.125rem 0.5rem; border-radius: 999px; margin-right: 0.375rem; }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid { grid-template-columns: 1fr; }
}
</style>
