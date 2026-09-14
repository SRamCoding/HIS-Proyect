<template>
  <div class="sigarh-index-container">

    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-academic-cap" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Profesiones</h1>
          <p class="page-subtitle">Catalogo comun del personal de salud y su grupo ocupacional</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/mantenimiento/profesiones/create?tenant=${tenantId}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nueva Profesion
      </NuxtLink>
    </div>
    <p style="color: var(--ink-soft); font-size: 0.8125rem; margin: -0.75rem 0 1rem">
      Base: profesiones del D. Leg. 1153, tecnicos y auxiliares asistenciales. La clasificacion administrativa es una
      configuracion operativa; no cambia la profesion del trabajador.
    </p>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-academic-cap" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.length }}</div>
          <div class="sigarh-stat-label">Total Profesiones</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ activeCount }}</div>
          <div class="sigarh-stat-label">Activas</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ inactiveCount }}</div>
          <div class="sigarh-stat-label">Inactivas</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-building-library" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ baseCount }}</div>
          <div class="sigarh-stat-label">Catalogo Base</div>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar profesion, codigo o grupo..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button @click="filtro = 'all'" class="sigarh-filter-btn" :class="{ active: filtro === 'all' }">
              Todas <span class="sigarh-filter-count">{{ items.length }}</span>
            </button>
            <button @click="filtro = 'active'" class="sigarh-filter-btn" :class="{ active: filtro === 'active' }">
              Activas <span class="sigarh-filter-count">{{ activeCount }}</span>
            </button>
            <button @click="filtro = 'inactive'" class="sigarh-filter-btn" :class="{ active: filtro === 'inactive' }">
              Inactivas <span class="sigarh-filter-count">{{ inactiveCount }}</span>
            </button>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span class="sigarh-result-count">{{ filteredItems.length }} resultados</span>
          <button v-if="search || filtro !== 'all'" @click="search = ''; filtro = 'all'" class="sigarh-clear-btn">Limpiar</button>
        </div>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
        <p style="color: var(--ink-soft)">Cargando profesiones...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button @click="cargar" class="btn-outline">Reintentar</button>
      </div>
      <div v-else-if="!filteredItems.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-academic-cap" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">Sin profesiones registradas</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Comienza creando una profesion del hospital</p>
        </div>
        <NuxtLink :to="`/sigarh/mantenimiento/profesiones/create?tenant=${tenantId}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Profesion
        </NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 28%">Profesion</th>
              <th style="width: 20%">Grupo Ocupacional</th>
              <th style="width: 20%">Colegio Profesional</th>
              <th style="width: 12%">Origen</th>
              <th style="width: 10%">Estado</th>
              <th style="width: 10%; text-align: right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--teal-soft)">
                    <UIcon name="i-heroicons-academic-cap" class="w-4 h-4" style="color: var(--teal)" />
                  </div>
                  <div>
                    <span class="sigarh-item-name">{{ item.nombre }}</span>
                    <div v-if="item.codigo" class="sigarh-code-badge" style="margin-top: 0.25rem; display: inline-block">{{ item.codigo }}</div>
                  </div>
                </div>
              </td>
              <td>{{ nombreGrupo(item.grupo_ocupacional_id) }}</td>
              <td style="color: var(--ink-soft)">{{ item.colegio_profesional || '-' }}</td>
              <td>
                <span class="badge" :class="item.es_base ? 'badge--neutral' : 'badge--ok'">
                  {{ item.es_base ? 'Catalogo base' : 'Del hospital' }}
                </span>
              </td>
              <td>
                <span class="badge" :class="item.is_active ? 'badge--ok' : 'badge--neutral'">
                  {{ item.is_active ? 'Activa' : 'Inactiva' }}
                </span>
              </td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/mantenimiento/profesiones/${item.id}?tenant=${tenantId}`" class="sigarh-action-btn" :title="item.es_base ? 'Configurar' : 'Editar'">
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" />
                  </NuxtLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">
          Mostrando <strong>{{ filteredItems.length }}</strong> de <strong>{{ items.length }}</strong> profesiones
        </div>
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
  grupo_ocupacional_id: string
  colegio_profesional: string | null
  categoria_personal: string | null
  es_base: boolean
  is_active: boolean
}

const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const grupos = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const filtro = ref('all')

const activeCount = computed(() => items.value.filter(i => i.is_active).length)
const inactiveCount = computed(() => items.value.filter(i => !i.is_active).length)
const baseCount = computed(() => items.value.filter(i => i.es_base).length)

const nombreGrupo = (id: string) => grupos.value.find(g => g.id === id)?.nombre || '-'

const filteredItems = computed(() => {
  let r = items.value
  if (filtro.value === 'active') r = r.filter(i => i.is_active)
  else if (filtro.value === 'inactive') r = r.filter(i => !i.is_active)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    r = r.filter(i =>
      i.nombre.toLowerCase().includes(q) ||
      (i.codigo || '').toLowerCase().includes(q) ||
      nombreGrupo(i.grupo_ocupacional_id).toLowerCase().includes(q)
    )
  }
  return r
})

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    const [p, g] = await Promise.all([
      api<Item[]>('/sigarh/mantenimiento/profesiones?limit=500'),
      api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales?limit=500'),
    ])
    items.value = p
    grupos.value = g
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo cargar el catalogo' }
  finally { loading.value = false }
}

onMounted(cargar)
</script>
