<template>
  <div class="lab-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ATENCIÓN HOSPITALARIA</span>
            <h1 class="page-title">Seguridad · Empleados</h1>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary btn-sm" @click="init"><UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />Actualizar</button>
      </div>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <p class="field-hint" style="margin-bottom:1rem">Cuentas administradas en SIGARH → Mantenimiento → Usuarios. Solo consulta desde aquí.</p>

    <!-- Resumen -->
    <div v-if="resumen" class="stats-row">
      <div class="stat-card"><span class="stat-num">{{ resumen.total }}</span><span class="stat-label">Cuentas</span></div>
      <div class="stat-card"><span class="stat-num" style="color:var(--green)">{{ resumen.activos }}</span><span class="stat-label">Activas</span></div>
      <div class="stat-card"><span class="stat-num" style="color:var(--alert)">{{ resumen.inactivos }}</span><span class="stat-label">Inactivas</span></div>
      <div class="stat-card"><span class="stat-num" style="color:var(--alert)">{{ resumen.sin_perfil_hospitalario }}</span><span class="stat-label">Sin perfil</span></div>
      <div class="stat-card"><span class="stat-num" style="color:var(--alert)">{{ resumen.sin_empleado_vinculado }}</span><span class="stat-label">Sin empleado</span></div>
    </div>

    <!-- Búsqueda -->
    <section class="panel search-panel">
      <form class="search-form" @submit.prevent="buscar">
        <div class="search-grid">
          <div class="search-field"><label class="form-label">Buscar (nombre, email, DNI)</label><input v-model="filtro.q" class="input-clinical" /></div>
          <div class="search-field">
            <label class="form-label">Rol</label>
            <select v-model="filtro.role" class="input-clinical">
              <option value="">Todos</option>
              <option v-for="r in roles" :key="r" :value="r">{{ r }}</option>
            </select>
          </div>
          <div class="search-field">
            <label class="form-label">Estado</label>
            <select v-model="filtro.estado" class="input-clinical">
              <option value="">Todos</option><option value="activo">Activo</option><option value="inactivo">Inactivo</option>
            </select>
          </div>
        </div>
        <div class="search-actions"><button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button></div>
      </form>
    </section>

    <!-- Resultados -->
    <section class="panel results-panel">
      <div class="results-header"><h2 class="results-title">{{ total }} cuentas</h2></div>
      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <div v-else class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>Empleado</th><th>Cuenta</th><th>Rol</th><th>Perfil hospitalario</th><th>Estado</th><th></th></tr></thead>
          <tbody>
            <tr v-for="u in lista" :key="u.id">
              <td>{{ u.empleado_nombre || '— sin vincular' }}</td><td>{{ u.email }}</td><td>{{ u.role }}</td>
              <td>{{ u.perfil_nombre || '— sin perfil' }}</td>
              <td><span class="badge" :class="u.is_active ? 'badge-ok' : 'badge-off'">{{ u.is_active ? 'Activo' : 'Inactivo' }}</span></td>
              <td><button class="action-btn action-view" @click="verDetalle(u.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button></td>
            </tr>
            <tr v-if="!lista.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">Sin resultados.</td></tr>
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
        <div><h2 class="detail-title">{{ detalle.name }}</h2><p class="detail-subtitle">{{ detalle.email }} · {{ detalle.role }}</p></div>
        <button class="btn-secondary" @click="detalle=null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button>
      </div>
      <div class="detail-info">
        <p>Empleado: {{ detalle.empleado_nombre || 'No vinculado a ningún empleado' }} <span v-if="detalle.empleado_dni">· DNI {{ detalle.empleado_dni }}</span>
          <span v-if="detalle.empleado_id" class="tag" :class="detalle.empleado_activo ? '' : 'tag-off'">{{ detalle.empleado_activo ? 'Empleado activo' : 'Empleado inactivo' }}</span>
        </p>
        <p>Perfil hospitalario: {{ detalle.perfil_nombre || 'No tiene perfil asignado — no puede operar módulos hasta que SIGARH le asigne uno' }}</p>
        <p v-if="detalle.modulos.length">Módulos habilitados por el perfil:</p>
        <p v-if="detalle.modulos.length"><span v-for="m in detalle.modulos" :key="m" class="tag">{{ m }}</span></p>
        <p class="field-hint">Cuenta creada {{ detalle.created_at }} UTC</p>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const endpoint = '/app/seguridad'

const error = ref('')
const loading = ref(false)
const filtro = reactive({ q: '', role: '', estado: '' })
const roles = ref<string[]>([])
const lista = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const detalle = ref<any>(null)
const resumen = ref<any>(null)

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
    const q = Object.fromEntries(Object.entries(filtro).filter(([, v]) => v))
    const data = await api<any>(endpoint + '/empleados', { query: { ...q, page: page.value, page_size: pageSize.value } })
    lista.value = data.items; total.value = data.total
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function cambiarPagina(p: number) { page.value = p; await cargarLista() }

async function verDetalle(id: string) { try { detalle.value = await api(endpoint + '/empleados/' + id) } catch (e) { error.value = err(e) } }

async function init() {
  detalle.value = null
  try {
    const [r, roleList] = await Promise.all([api(endpoint + '/resumen'), api<string[]>(endpoint + '/catalogos/roles')])
    resumen.value = r; roles.value = roleList
  } catch (e) { /* la lista sigue funcionando sin el resumen */ }
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
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; }
.stats-row { display: grid; grid-template-columns: repeat(5, 1fr); gap: 0.75rem; margin-bottom: 1.5rem; }
.stat-card { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); padding: 0.875rem; display: flex; flex-direction: column; align-items: center; box-shadow: var(--shadow-sm); }
.stat-num { font-size: 1.5rem; font-weight: 700; color: var(--ink); }
.stat-label { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.125rem; }
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
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-off { color: var(--alert); background: var(--alert-soft); }
.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; color: var(--ink-soft); cursor: pointer; }
.action-btn:hover { background: var(--mist); }
.action-view:hover { color: var(--teal); border-color: var(--teal-soft); background: var(--teal-soft); }
.pagination { display: flex; align-items: center; gap: 0.75rem; justify-content: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--line); }
.page-info { font-size: 0.8125rem; color: var(--ink-soft); }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.detail-title { font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0; }
.detail-subtitle { font-size: 0.875rem; color: var(--ink-soft); margin: 0.125rem 0 0 0; }
.detail-info { font-size: 0.875rem; color: var(--ink); padding: 0.5rem 0; }
.tag { display: inline-block; font-size: 0.6875rem; font-weight: 600; color: var(--teal); background: var(--teal-soft); padding: 0.125rem 0.5rem; border-radius: 999px; margin: 0.125rem 0.375rem 0.125rem 0; }
.tag-off { color: var(--alert); background: var(--alert-soft); }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid { grid-template-columns: 1fr; }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
</style>
