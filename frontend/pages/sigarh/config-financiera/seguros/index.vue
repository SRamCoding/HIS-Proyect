<template>
  <div class="sigarh-index-container">

    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Seguros</h1>
          <p class="page-subtitle">Seguros y convenios del hospital</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/config-financiera/seguros/create?tenant=${tenantId}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Seguro
      </NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ lista.length }}</div>
          <div class="sigarh-stat-label">Total Seguros</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ activeItems }}</div>
          <div class="sigarh-stat-label">Activos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ inactiveItems }}</div>
          <div class="sigarh-stat-label">Inactivos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-list-bullet" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ new Set(lista.map(s => s.tipo)).size }}</div>
          <div class="sigarh-stat-label">Tipos Diferentes</div>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar por nombre, RUC o tipo..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button @click="activeFilter = 'all'" class="sigarh-filter-btn" :class="{ active: activeFilter === 'all' }">
              Todos <span class="sigarh-filter-count">{{ lista.length }}</span>
            </button>
            <button @click="activeFilter = 'active'" class="sigarh-filter-btn" :class="{ active: activeFilter === 'active' }">
              Activos <span class="sigarh-filter-count">{{ activeItems }}</span>
            </button>
            <button @click="activeFilter = 'inactive'" class="sigarh-filter-btn" :class="{ active: activeFilter === 'inactive' }">
              Inactivos <span class="sigarh-filter-count">{{ inactiveItems }}</span>
            </button>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span class="sigarh-result-count">{{ filteredLista.length }} resultados</span>
          <button v-if="search || activeFilter !== 'all'" @click="clearFilters" class="sigarh-clear-btn">Limpiar</button>
        </div>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
        <p style="color: var(--ink-soft)">Cargando seguros...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button @click="cargar" class="btn-outline">Reintentar</button>
      </div>
      <div v-else-if="!filteredLista.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-shield-check" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">No hay seguros registrados</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Comienza creando un seguro o convenio</p>
        </div>
        <NuxtLink :to="`/sigarh/config-financiera/seguros/create?tenant=${tenantId}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Seguro
        </NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 25%">Nombre</th>
              <th style="width: 15%">RUC</th>
              <th style="width: 15%">Tipo</th>
              <th style="width: 15%">Cobertura</th>
              <th style="width: 15%">Estado</th>
              <th style="width: 15%; text-align: right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="s in filteredLista" :key="s.id">
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" :style="{ background: s.is_active ? getTipoBgColor(s.tipo) : 'var(--mist)' }">
                    <UIcon name="i-heroicons-shield-check" class="w-4 h-4" :style="{ color: s.is_active ? getTipoColor(s.tipo) : 'var(--ink-soft)' }" />
                  </div>
                  <span class="sigarh-item-name">{{ s.nombre }}</span>
                </div>
              </td>
              <td style="font-family: monospace; color: var(--ink-soft)">{{ s.ruc || '-' }}</td>
              <td>
                <span class="sigarh-code-badge" :style="{ background: getTipoBgColor(s.tipo), color: getTipoColor(s.tipo) }">
                  {{ formatTipo(s.tipo) }}
                </span>
              </td>
              <td>{{ formatPorcentaje(s.porcentaje_cobertura) }}</td>
              <td>
                <span class="badge" :class="s.is_active ? 'badge--ok' : 'badge--neutral'">
                  {{ s.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/config-financiera/seguros/${s.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar">
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" />
                  </NuxtLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">
          Mostrando <strong>{{ filteredLista.length }}</strong> de <strong>{{ lista.length }}</strong> seguros
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')

const lista = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const activeFilter = ref('all')

const activeItems = computed(() => lista.value.filter(s => s.is_active).length)
const inactiveItems = computed(() => lista.value.filter(s => !s.is_active).length)

const filteredLista = computed(() => {
  let result = lista.value
  if (activeFilter.value === 'active') result = result.filter(s => s.is_active)
  else if (activeFilter.value === 'inactive') result = result.filter(s => !s.is_active)
  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(s =>
      s.nombre?.toLowerCase().includes(q) || s.ruc?.includes(q) || s.tipo?.toLowerCase().includes(q)
    )
  }
  return result
})

const getTipoColor = (tipo: string) => {
  const map: Record<string, string> = { sis: 'var(--purple)', essalud: 'var(--green)', soat: 'var(--amber)', privado: 'var(--teal)', convenio: 'var(--navy)', particular: 'var(--ink-soft)' }
  return map[tipo?.toLowerCase()] || 'var(--ink-soft)'
}
const getTipoBgColor = (tipo: string) => {
  const map: Record<string, string> = { sis: 'var(--purple-soft)', essalud: 'var(--green-soft)', soat: 'var(--amber-soft)', privado: 'var(--teal-soft)', convenio: 'var(--navy-soft)', particular: 'var(--mist)' }
  return map[tipo?.toLowerCase()] || 'var(--mist)'
}
const formatTipo = (tipo: string) => {
  const map: Record<string, string> = { sis: 'SIS', essalud: 'EsSalud', soat: 'SOAT', privado: 'Privado', convenio: 'Convenio', particular: 'Particular' }
  return tipo ? (map[tipo.toLowerCase()] || tipo) : '-'
}
const formatPorcentaje = (valor: number | null) => valor === null || valor === undefined ? '-' : `${valor}%`

const clearFilters = () => { search.value = ''; activeFilter.value = 'all' }

const cargar = async () => {
  loading.value = true
  error.value = ''
  try { lista.value = await api('/sigarh/config-financiera/seguros', { tenant: tenantId.value }) }
  catch (e: any) { error.value = e?.data?.detail || 'Error al cargar datos' }
  finally { loading.value = false }
}

onMounted(cargar)
</script>
