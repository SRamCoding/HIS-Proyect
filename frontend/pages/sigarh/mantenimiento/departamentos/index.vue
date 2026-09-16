<template>
  <div class="sigarh-index-container">

    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h1 class="page-title">Departamentos</h1>
          <p class="page-subtitle">Departamentos del hospital</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/mantenimiento/departamentos/create?tenant=${tenantId}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Departamento
      </NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.length }}</div>
          <div class="sigarh-stat-label">Total</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.filter(i => i.is_active).length }}</div>
          <div class="sigarh-stat-label">Activos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.filter(i => !i.is_active).length }}</div>
          <div class="sigarh-stat-label">Inactivos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-tag" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.filter(i => i.codigo).length }}</div>
          <div class="sigarh-stat-label">Con Codigo</div>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar departamento..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button @click="filtro = 'all'" class="sigarh-filter-btn" :class="{ active: filtro === 'all' }">Todos {{ items.length }}</button>
            <button @click="filtro = 'active'" class="sigarh-filter-btn" :class="{ active: filtro === 'active' }">Activos {{ items.filter(i => i.is_active).length }}</button>
            <button @click="filtro = 'inactive'" class="sigarh-filter-btn" :class="{ active: filtro === 'inactive' }">Inactivos {{ items.filter(i => !i.is_active).length }}</button>
          </div>
        </div>
        <span class="sigarh-result-count">{{ filteredItems.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" />
        <p style="color: var(--ink-soft)">Cargando...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
      </div>
      <div v-else-if="!filteredItems.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-building-office-2" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">Sin departamentos registrados</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Comienza creando un departamento</p>
        </div>
      </div>
      <table v-else class="sigarh-table">
        <thead>
          <tr>
            <th>Nombre</th>
            <th>Codigo</th>
            <th>Estado</th>
            <th class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td style="font-weight: 500">{{ item.nombre }}</td>
            <td style="color: var(--ink-soft); font-family: monospace">{{ item.codigo || '-' }}</td>
            <td>
              <span class="badge" :class="item.is_active ? 'badge--ok' : 'badge--neutral'">
                {{ item.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="text-right">
              <div class="sigarh-actions">
                <NuxtLink :to="`/sigarh/mantenimiento/departamentos/${item.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar">
                  <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" />
                </NuxtLink>
                <button class="sigarh-action-btn danger" title="Eliminar" @click="confirmarEliminar(item)">
                  <UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="filteredItems.length" class="sigarh-table-footer">
        Mostrando {{ filteredItems.length }} de {{ items.length }} departamentos
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

interface Item {
  id: string
  nombre: string
  codigo: string | null
  is_active: boolean
}

const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const filtro = ref('all')

const filteredItems = computed(() => {
  let r = items.value
  if (filtro.value === 'active') r = r.filter(i => i.is_active)
  else if (filtro.value === 'inactive') r = r.filter(i => !i.is_active)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    r = r.filter(i => i.nombre.toLowerCase().includes(q) || (i.codigo || '').toLowerCase().includes(q))
  }
  return r
})

const confirmarEliminar = async (item: Item) => {
  if (!confirm(`Eliminar "${item.nombre}"?`)) return
  try {
    await api(`/sigarh/mantenimiento/departamentos/${item.id}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id !== item.id)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}

onMounted(async () => {
  try {
    items.value = await api<Item[]>('/sigarh/mantenimiento/departamentos')
  } catch (e: any) { error.value = apiErr(e, 'Error de conexion') }
  finally { loading.value = false }
})
</script>
