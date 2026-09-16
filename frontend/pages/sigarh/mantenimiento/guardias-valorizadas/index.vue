<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-currency-dollar" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <h1 class="page-title">Guardias Valorizadas</h1>
          <p class="page-subtitle">Tarifas por modalidad y nivel del trabajador · D.S. 232-2017-EF</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/mantenimiento/guardias-valorizadas/create?tenant=${tenantId}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Guardia
      </NuxtLink>
    </div>
    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-currency-dollar" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length }}</div><div class="sigarh-stat-label">Total</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><div class="sigarh-stat-value">{{ activeCount }}</div><div class="sigarh-stat-label">Activas</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--alert)">
        <div class="sigarh-stat-icon" style="background: var(--alert-soft)"><UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--alert)" /></div>
        <div><div class="sigarh-stat-value">{{ inactiveCount }}</div><div class="sigarh-stat-label">Inactivas</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-calculator" class="w-5 h-5" style="color: var(--teal)" /></div>
        <div><div class="sigarh-stat-value">{{ vigentesCount }}</div><div class="sigarh-stat-label">Vigentes hoy</div></div>
      </div>
    </div>
    <p class="text-sm text-slate-500 mb-4">Consulta los importes publicados en los artículos 3–5 del decreto.
      <a href="https://cdn.www.gob.pe/uploads/document/file/6792759/5883027-r-j-n-000280-2022-mp-fn-jn-imlcf.pdf" target="_blank" rel="noopener noreferrer" class="underline">Ver tablas en publicación estatal</a>.
      El detalle del rol muestra la estimación por empleado, fecha y horario. RR. HH. debe validar el derecho y la ejecución antes de pagar.
    </p>
    <p v-if="error" class="text-red-600 mb-4" role="alert">{{ error }}</p>
    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar modalidad, grupo o nivel..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button @click="filtro = 'all'" class="sigarh-filter-btn" :class="{ active: filtro === 'all' }">Todos <span class="sigarh-filter-count">{{ items.length }}</span></button>
            <button @click="filtro = 'active'" class="sigarh-filter-btn" :class="{ active: filtro === 'active' }">Activas <span class="sigarh-filter-count">{{ activeCount }}</span></button>
            <button @click="filtro = 'inactive'" class="sigarh-filter-btn" :class="{ active: filtro === 'inactive' }">Inactivas <span class="sigarh-filter-count">{{ inactiveCount }}</span></button>
          </div>
        </div>
        <span class="sigarh-result-count">{{ filteredItems.length }} resultados</span>
      </div>
      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--amber)" />
        <p style="color: var(--ink-soft)">Cargando...</p>
      </div>
      <div v-else-if="!filteredItems.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-currency-dollar" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <p style="font-weight: 600; color: var(--ink); margin: 0">Sin guardias registradas</p>
      </div>
      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr>
            <th style="width:25%">Tipo de Guardia</th>
            <th style="width:20%">Grupo Ocupacional</th>
            <th style="width:20%">Nivel Remunerativo</th>
            <th style="width:15%">Valor</th>
            <th>Vigencia</th>
            <th style="width:10%">Estado</th>
            <th style="width:10%;text-align:right">Acciones</th>
          </tr></thead>
          <tbody>
            <tr v-for="item in paginatedItems" :key="item.id">
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-currency-dollar" class="w-4 h-4" style="color: var(--amber)" /></div>
                  <span class="sigarh-item-name">{{ item.tipo_guardia_nombre || '-' }}</span>
                </div>
              </td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ item.grupo_ocupacional_nombre || '-' }}</td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ item.nivel_remunerativo_nombre || '-' }}</td>
              <td><span class="sigarh-code-badge">S/ {{ item.valor?.toFixed(2) }}</span></td>
              <td class="text-xs">{{ item.vigencia_desde || 'Sin fecha' }}<br>{{ item.vigencia_hasta || 'Sin fecha de cierre' }}</td>
              <td><span class="badge" :class="item.is_active ? 'badge--ok' : 'badge--neutral'">{{ item.is_active ? 'Activo' : 'Inactivo' }}</span></td>
              <td style="text-align:right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/mantenimiento/guardias-valorizadas/${item.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Consultar tarifa"><UIcon name="i-heroicons-eye" class="w-4 h-4" style="color:var(--teal)" /></NuxtLink>
                  <button v-if="!item.vigencia_desde || item.vigencia_desde > hoy" class="sigarh-action-btn danger" @click="confirmarEliminar(item)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color:var(--alert)" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer flex items-center justify-between gap-3">
          <span>{{ filteredItems.length }} tarifas · Página {{ page }} de {{ totalPages }}</span>
          <div class="flex items-center gap-3">
            <select v-model.number="pageSize" aria-label="Tarifas por página"><option :value="25">25 por página</option><option :value="50">50 por página</option><option :value="100">100 por página</option></select>
            <button :disabled="page <= 1" class="disabled:opacity-40" @click="page--">Anterior</button>
            <button :disabled="page >= totalPages" class="disabled:opacity-40" @click="page++">Siguiente</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
interface Item { id: string; tipo_guardia_nombre: string | null; grupo_ocupacional_nombre: string | null; nivel_remunerativo_nombre: string | null; valor: number; is_active: boolean; vigencia_desde: string | null; vigencia_hasta: string | null }
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const filtro = ref('all')
const activeCount = computed(() => items.value.filter(i => i.is_active).length)
const inactiveCount = computed(() => items.value.filter(i => !i.is_active).length)
const hoy = new Date().toLocaleDateString('en-CA', { timeZone: 'America/Lima' })
const vigentesCount = computed(() => items.value.filter(i => i.is_active && i.vigencia_desde && i.vigencia_desde <= hoy && (!i.vigencia_hasta || i.vigencia_hasta >= hoy)).length)
const page = ref(1)
const pageSize = ref(25)
const filteredItems = computed(() => {
  let r = items.value
  if (filtro.value === 'active') r = r.filter(i => i.is_active)
  else if (filtro.value === 'inactive') r = r.filter(i => !i.is_active)
  if (search.value.trim()) { const q = search.value.toLocaleLowerCase('es'); r = r.filter(i => [i.tipo_guardia_nombre, i.grupo_ocupacional_nombre, i.nivel_remunerativo_nombre].some(s => (s || '').toLocaleLowerCase('es').includes(q))) }
  return r
})
const totalPages = computed(() => Math.max(1, Math.ceil(filteredItems.value.length / pageSize.value)))
const paginatedItems = computed(() => filteredItems.value.slice((page.value - 1) * pageSize.value, page.value * pageSize.value))
watch([search, filtro, pageSize], () => { page.value = 1 })
watch(totalPages, n => { page.value = Math.min(page.value, n) })
const confirmarEliminar = async (item: Item) => {
  if (!confirm('Eliminar esta guardia valorizada?')) return
  try { await api(`/sigarh/mantenimiento/guardias-valorizadas/${item.id}`, { method: 'DELETE', tenant: tenantId.value }); items.value = items.value.filter(i => i.id !== item.id) }
  catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}
onMounted(async () => {
  try {
    const todas: Item[] = []
    for (let offset = 0; ; offset += 200) {
      const lote = await api<Item[]>(`/sigarh/mantenimiento/guardias-valorizadas?offset=${offset}&limit=200`, { tenant: tenantId.value })
      todas.push(...lote)
      if (lote.length < 200) break
    }
    items.value = todas.sort((a, b) => `${a.tipo_guardia_nombre} ${a.nivel_remunerativo_nombre}`.localeCompare(`${b.tipo_guardia_nombre} ${b.nivel_remunerativo_nombre}`, 'es', { numeric: true }))
  }
  catch (e: any) { error.value = apiErr(e, 'Error') }
  finally { loading.value = false }
})
</script>
