<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
interface Item { id: string; nombre: string | null; dependencia_nombre: string | null; grupo_ocupacional_nombre: string | null; minutos_tolerancia: number; minutos_tolerancia_dia: number; is_active: boolean }
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const filtro = ref('all')
const activeCount = computed(() => items.value.filter(i => i.is_active).length)
const filteredItems = computed(() => {
  let r = items.value
  if (filtro.value === 'active') r = r.filter(i => i.is_active)
  else if (filtro.value === 'inactive') r = r.filter(i => !i.is_active)
  if (search.value.trim()) { const q = search.value.toLowerCase(); r = r.filter(i => (i.nombre || '').toLowerCase().includes(q) || (i.dependencia_nombre || '').toLowerCase().includes(q) || (i.grupo_ocupacional_nombre || '').toLowerCase().includes(q)) }
  return r
})
const eliminar = async (it: Item) => {
  if (!confirm('Eliminar esta regla de tolerancia?')) return
  try { await api(`/sigarh/rrhh/tolerancias/${it.id}`, { method: 'DELETE' }); items.value = items.value.filter(i => i.id !== it.id) }
  catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}
const cargar = async () => {
  loading.value = true; error.value = ''
  try { items.value = await api<Item[]>('/sigarh/rrhh/tolerancias') }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
onMounted(cargar)
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><h1 class="page-title">Tolerancias</h1><p class="page-subtitle">Márgenes de tardanza permitidos por dependencia y grupo ocupacional</p></div>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/tolerancias/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Tolerancia</NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length }}</div><div class="sigarh-stat-label">Reglas</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><div class="sigarh-stat-value">{{ activeCount }}</div><div class="sigarh-stat-label">Activas</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length - activeCount }}</div><div class="sigarh-stat-label">Inactivas</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-calculator" class="w-5 h-5" style="color: var(--teal)" /></div>
        <div><div class="sigarh-stat-value">{{ activeCount ? Math.round(items.filter(i => i.is_active).reduce((s, i) => s + i.minutos_tolerancia, 0) / activeCount) : 0 }}'</div><div class="sigarh-stat-label">Tolerancia media</div></div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar por dependencia o grupo..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button @click="filtro = 'all'" class="sigarh-filter-btn" :class="{ active: filtro === 'all' }">Todas <span class="sigarh-filter-count">{{ items.length }}</span></button>
            <button @click="filtro = 'active'" class="sigarh-filter-btn" :class="{ active: filtro === 'active' }">Activas <span class="sigarh-filter-count">{{ activeCount }}</span></button>
            <button @click="filtro = 'inactive'" class="sigarh-filter-btn" :class="{ active: filtro === 'inactive' }">Inactivas <span class="sigarh-filter-count">{{ items.length - activeCount }}</span></button>
          </div>
        </div>
        <span class="sigarh-result-count">{{ filteredItems.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" /></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!filteredItems.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-clock" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" />
        <p style="color: var(--ink-soft)">Sin reglas de tolerancia</p>
        <NuxtLink :to="`/sigarh/rrhh/tolerancias/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva</NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr><th style="width: 24%">Regla</th><th style="width: 24%">Dependencia</th><th style="width: 22%">Grupo ocupacional</th><th style="width: 12%">Tol. entrada</th><th style="width: 11%">Tol. diaria</th><th style="width: 7%">Estado</th><th style="width: 5%; text-align: right">Acciones</th></tr></thead>
          <tbody>
            <tr v-for="it in filteredItems" :key="it.id">
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-clock" class="w-4 h-4" style="color: var(--navy)" /></div>
                  <span class="sigarh-item-name">{{ it.nombre || 'Regla de tolerancia' }}</span>
                </div>
              </td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ it.dependencia_nombre || '-' }}</td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ it.grupo_ocupacional_nombre || '-' }}</td>
              <td><span class="badge badge--neutral">{{ it.minutos_tolerancia }} min</span></td>
              <td><span class="badge badge--neutral">{{ it.minutos_tolerancia_dia }} min</span></td>
              <td><span class="badge" :class="it.is_active ? 'badge--ok' : 'badge--neutral'">{{ it.is_active ? 'Activa' : 'Inactiva' }}</span></td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/rrhh/tolerancias/${it.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" /></NuxtLink>
                  <button class="sigarh-action-btn danger" title="Eliminar" @click="eliminar(it)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">Mostrando <strong>{{ filteredItems.length }}</strong> de <strong>{{ items.length }}</strong> reglas</div>
      </div>
    </div>
  </div>
</template>
