<template>
  <div class="sigarh-index-container">
    <SAccesosPanelInfo />

    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h1 class="page-title">Roles del Sistema</h1>
          <p class="page-subtitle">Roles y permisos por panel</p>
        </div>
      </div>
      <NuxtLink
        :to="puedeAdministrarSeguridad ? `/sigarh/mantenimiento/roles-sistema/create?tenant=${tenantId}` : ''"
        class="btn-primary"
        :class="{ 'is-disabled': !puedeAdministrarSeguridad }"
        :title="puedeAdministrarSeguridad ? '' : 'Necesitas el permiso Administrar Seguridad para crear roles'"
        @click="!puedeAdministrarSeguridad && $event.preventDefault()"
      >
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Rol
      </NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.length }}</div>
          <div class="sigarh-stat-label">Total Roles</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ activeCount }}</div>
          <div class="sigarh-stat-label">Activos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ inactiveCount }}</div>
          <div class="sigarh-stat-label">Inactivos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-computer-desktop" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.filter(i => i.panel === 'sigarh').length }}</div>
          <div class="sigarh-stat-label">Panel SIGARH</div>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar rol por nombre o codigo..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button @click="filtro = 'all'" class="sigarh-filter-btn" :class="{ active: filtro === 'all' }">
              Todos <span class="sigarh-filter-count">{{ items.length }}</span>
            </button>
            <button @click="filtro = 'active'" class="sigarh-filter-btn" :class="{ active: filtro === 'active' }">
              Activos <span class="sigarh-filter-count">{{ activeCount }}</span>
            </button>
            <button @click="filtro = 'inactive'" class="sigarh-filter-btn" :class="{ active: filtro === 'inactive' }">
              Inactivos <span class="sigarh-filter-count">{{ inactiveCount }}</span>
            </button>
          </div>
        </div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span class="sigarh-result-count">{{ filteredItems.length }} resultados</span>
          <button v-if="search || filtro !== 'all'" @click="search = ''; filtro = 'all'" class="sigarh-clear-btn">Limpiar</button>
        </div>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" />
        <p style="color: var(--ink-soft)">Cargando roles...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button @click="cargar" class="btn-outline">Reintentar</button>
      </div>
      <div v-else-if="!filteredItems.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-shield-check" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">Sin roles registrados</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Comienza creando un rol del sistema</p>
        </div>
        <NuxtLink :to="`/sigarh/mantenimiento/roles-sistema/create?tenant=${tenantId}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Rol
        </NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 15%">Codigo</th>
              <th style="width: 28%">Nombre</th>
              <th style="width: 12%">Panel</th>
              <th style="width: 25%">Descripcion</th>
              <th style="width: 10%">Estado</th>
              <th style="width: 10%; text-align: right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td>
                <span v-if="item.codigo" class="sigarh-code-badge">{{ item.codigo }}</span>
                <span v-else style="color: var(--ink-soft)">-</span>
              </td>
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--navy-soft)">
                    <UIcon name="i-heroicons-shield-check" class="w-4 h-4" style="color: var(--navy)" />
                  </div>
                  <span class="sigarh-item-name">{{ item.nombre }}</span>
                </div>
              </td>
              <td><span class="badge badge--neutral">{{ item.panel === 'app' ? 'Hospitalario' : 'SIGARH' }}</span></td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ item.descripcion || '-' }}</td>
              <td>
                <span class="badge" :class="item.is_active ? 'badge--ok' : 'badge--neutral'">
                  {{ item.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink
                    :to="puedeAdministrarSeguridad ? `/sigarh/mantenimiento/roles-sistema/${item.id}?tenant=${tenantId}` : ''"
                    class="sigarh-action-btn"
                    :class="{ 'is-disabled': !puedeAdministrarSeguridad }"
                    :title="puedeAdministrarSeguridad ? 'Editar' : 'Necesitas el permiso Administrar Seguridad'"
                    @click="!puedeAdministrarSeguridad && $event.preventDefault()"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" />
                  </NuxtLink>
                  <button
                    class="sigarh-action-btn danger"
                    :disabled="!puedeAdministrarSeguridad"
                    :title="puedeAdministrarSeguridad ? 'Eliminar' : 'Necesitas el permiso Administrar Seguridad'"
                    @click="puedeAdministrarSeguridad && confirmarEliminar(item)"
                  >
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">
          Mostrando <strong>{{ filteredItems.length }}</strong> de <strong>{{ items.length }}</strong> roles
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

interface Item {
  id: string
  codigo: string | null
  nombre: string
  panel: string
  descripcion: string | null
  is_active: boolean
}

const { api } = useApi()
const route = useRoute()
const { puedeAdministrarSeguridad } = useSigarhPermisos()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const filtro = ref('all')

const activeCount = computed(() => items.value.filter(i => i.is_active).length)
const inactiveCount = computed(() => items.value.filter(i => !i.is_active).length)

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
    await api(`/sigarh/mantenimiento/roles-sistema/${item.id}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id !== item.id)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try { items.value = await api<Item[]>('/sigarh/mantenimiento/roles-sistema') }
  catch (e: any) { error.value = apiErr(e, 'Error de conexion') }
  finally { loading.value = false }
}

onMounted(cargar)
</script>
