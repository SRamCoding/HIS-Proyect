<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-currency-dollar" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <h1 class="page-title">Guardias Valorizadas</h1>
          <p class="page-subtitle">Valores economicos por tipo de guardia</p>
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
        <div><div class="sigarh-stat-value font-mono-data" style="font-size:1rem">S/ {{ totalValor.toFixed(2) }}</div><div class="sigarh-stat-label">Valor Total</div></div>
      </div>
    </div>
    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar guardia..." class="sigarh-search-input" />
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
            <th style="width:10%">Estado</th>
            <th style="width:10%;text-align:right">Acciones</th>
          </tr></thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-currency-dollar" class="w-4 h-4" style="color: var(--amber)" /></div>
                  <span class="sigarh-item-name">{{ item.tipo_guardia_nombre || '-' }}</span>
                </div>
              </td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ item.grupo_ocupacional_nombre || '-' }}</td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ item.nivel_remunerativo_nombre || '-' }}</td>
              <td><span class="sigarh-code-badge">S/ {{ item.valor?.toFixed(2) }}</span></td>
              <td><span class="badge" :class="item.is_active ? 'badge--ok' : 'badge--neutral'">{{ item.is_active ? 'Activo' : 'Inactivo' }}</span></td>
              <td style="text-align:right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/mantenimiento/guardias-valorizadas/${item.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color:var(--teal)" /></NuxtLink>
                  <button class="sigarh-action-btn danger" @click="confirmarEliminar(item)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color:var(--alert)" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">Mostrando <strong>{{ filteredItems.length }}</strong> de <strong>{{ items.length }}</strong> guardias</div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
interface Item { id: string; tipo_guardia_nombre: string | null; grupo_ocupacional_nombre: string | null; nivel_remunerativo_nombre: string | null; valor: number; is_active: boolean }
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
const totalValor = computed(() => items.value.reduce((acc, i) => acc + (i.valor || 0), 0))
const filteredItems = computed(() => {
  let r = items.value
  if (filtro.value === 'active') r = r.filter(i => i.is_active)
  else if (filtro.value === 'inactive') r = r.filter(i => !i.is_active)
  if (search.value.trim()) { const q = search.value.toLowerCase(); r = r.filter(i => (i.tipo_guardia_nombre || '').toLowerCase().includes(q)) }
  return r
})
const confirmarEliminar = async (item: Item) => {
  if (!confirm('Eliminar esta guardia valorizada?')) return
  try { await api(`/sigarh/mantenimiento/guardias-valorizadas/${item.id}`, { method: 'DELETE' }); items.value = items.value.filter(i => i.id !== item.id) }
  catch (e: any) { error.value = e?.data?.detail || 'No se pudo eliminar' }
}
onMounted(async () => {
  try { items.value = await api<Item[]>('/sigarh/mantenimiento/guardias-valorizadas') }
  catch (e: any) { error.value = e?.data?.detail || 'Error' }
  finally { loading.value = false }
})
</script>