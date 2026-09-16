<template>
  <div class="sigarh-index-container">

    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-rectangle-stack" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <h1 class="page-title">Camas</h1>
          <p class="page-subtitle">Camas individuales, ubicación, tipo y estado</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/infraestructura-hosp/camas/create?tenant=${tenantId}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nueva Cama
      </NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ contar('DISPONIBLE') }}</div>
          <div class="sigarh-stat-label">Disponibles</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-user" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ contar('OCUPADA') }}</div>
          <div class="sigarh-stat-label">Ocupadas</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-wrench-screwdriver" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ contar('MANTENIMIENTO') }}</div>
          <div class="sigarh-stat-label">Mantenimiento</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-bookmark" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ contar('RESERVADA') }}</div>
          <div class="sigarh-stat-label">Reservadas</div>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar cama por codigo o nombre..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button @click="filtro = 'all'" class="sigarh-filter-btn" :class="{ active: filtro === 'all' }">Todas <span class="sigarh-filter-count">{{ items.length }}</span></button>
            <button v-for="e in ESTADOS" :key="e" @click="filtro = e" class="sigarh-filter-btn" :class="{ active: filtro === e }">
              {{ label(e) }} <span class="sigarh-filter-count">{{ contar(e) }}</span>
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
        <p style="color: var(--ink-soft)">Cargando camas...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button @click="cargar" class="btn-outline">Reintentar</button>
      </div>
      <div v-else-if="!filteredItems.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-rectangle-stack" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">Sin camas registradas</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Crea camas o genéralas desde una sala</p>
        </div>
        <NuxtLink :to="`/sigarh/infraestructura-hosp/camas/create?tenant=${tenantId}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Cama
        </NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 12%">Codigo</th>
              <th style="width: 26%">Nombre</th>
              <th style="width: 20%">Sala</th>
              <th style="width: 14%">Tipo</th>
              <th style="width: 12%">Estado</th>
              <th style="width: 16%; text-align: right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td><span class="sigarh-code-badge">{{ item.codigo }}</span></td>
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--navy-soft)">
                    <UIcon name="i-heroicons-rectangle-stack" class="w-4 h-4" style="color: var(--navy)" />
                  </div>
                  <span class="sigarh-item-name">{{ item.nombre }}</span>
                </div>
              </td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ item.sala_texto || '-' }}</td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ item.tipo_cama || '-' }}</td>
              <td>
                <span class="badge" :class="badgeEstado(item.estado)">{{ label(item.estado) }}</span>
                <span v-if="!item.is_active" class="badge badge--neutral" style="margin-left: 0.25rem">Inactiva</span>
              </td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <button class="sigarh-action-btn" title="Cambiar estado" @click="abrirEstado(item)">
                    <UIcon name="i-heroicons-arrow-path-rounded-square" class="w-4 h-4" style="color: var(--purple)" />
                  </button>
                  <NuxtLink :to="`/sigarh/infraestructura-hosp/camas/${item.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar">
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" />
                  </NuxtLink>
                  <button class="sigarh-action-btn danger" title="Eliminar" @click="eliminar(item)">
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">
          Mostrando <strong>{{ filteredItems.length }}</strong> de <strong>{{ items.length }}</strong> camas
        </div>
      </div>
    </div>

    <!-- Modal Cambiar Estado -->
    <div v-if="estadoModal.cama" class="sigarh-modal-overlay" @click.self="estadoModal.cama = null">
      <div class="sigarh-modal">
        <h3 style="font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0 0 0.25rem">Cambiar estado</h3>
        <p style="font-size: 0.8125rem; color: var(--ink-soft); margin: 0 0 1rem">
          {{ estadoModal.cama.codigo }} · {{ estadoModal.cama.nombre }}
        </p>
        <div v-if="estadoModal.error" class="error-banner" style="margin-bottom: 1rem">{{ estadoModal.error }}</div>
        <div class="form-group" style="margin-bottom: 1rem">
          <label class="form-label">Nuevo estado</label>
          <select v-model="estadoModal.estado" class="input-clinical" style="padding-left: 0.75rem">
            <option v-for="e in ESTADOS" :key="e" :value="e">{{ label(e) }}</option>
          </select>
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 0.5rem">
          <button class="btn-cancel" @click="estadoModal.cama = null">Cancelar</button>
          <button class="btn-primary" :disabled="estadoModal.saving" @click="confirmarEstado">
            {{ estadoModal.saving ? 'Guardando...' : 'Cambiar' }}
          </button>
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

type Estado = 'DISPONIBLE' | 'OCUPADA' | 'MANTENIMIENTO' | 'RESERVADA'
const ESTADOS: Estado[] = ['DISPONIBLE', 'OCUPADA', 'MANTENIMIENTO', 'RESERVADA']

interface Item {
  id: string
  codigo: string
  nombre: string
  sala_texto: string | null
  tipo_cama: string | null
  estado: Estado
  is_active: boolean
}

const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const filtro = ref<'all' | Estado>('all')

const label = (e: string) => ({ DISPONIBLE: 'Disponible', OCUPADA: 'Ocupada', MANTENIMIENTO: 'Mantenimiento', RESERVADA: 'Reservada' }[e] || e)
const badgeEstado = (e: string) => ({ DISPONIBLE: 'badge--ok', OCUPADA: 'badge--danger', MANTENIMIENTO: 'badge--warning', RESERVADA: 'badge--warning' }[e] || 'badge--neutral')
const contar = (e: Estado) => items.value.filter(i => i.estado === e).length

const filteredItems = computed(() => {
  let r = items.value
  if (filtro.value !== 'all') r = r.filter(i => i.estado === filtro.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    r = r.filter(i => i.codigo.toLowerCase().includes(q) || i.nombre.toLowerCase().includes(q))
  }
  return r
})

const estadoModal = reactive<{ cama: Item | null; estado: Estado; saving: boolean; error: string }>({
  cama: null, estado: 'DISPONIBLE', saving: false, error: '',
})
const abrirEstado = (item: Item) => Object.assign(estadoModal, { cama: item, estado: item.estado, saving: false, error: '' })
const confirmarEstado = async () => {
  if (!estadoModal.cama) return
  estadoModal.saving = true
  estadoModal.error = ''
  try {
    const upd = await api<Item>(`/sigarh/infraestructura-hosp/camas/${estadoModal.cama.id}/estado`, {
      method: 'POST', body: { estado: estadoModal.estado },
    })
    const i = items.value.findIndex(x => x.id === upd.id)
    if (i >= 0) items.value[i] = { ...items.value[i], estado: upd.estado }
    estadoModal.cama = null
  } catch (e: any) { estadoModal.error = apiErr(e, 'No se pudo cambiar el estado') }
  finally { estadoModal.saving = false }
}

const eliminar = async (item: Item) => {
  if (!confirm(`Eliminar la cama "${item.codigo}"?`)) return
  try {
    await api(`/sigarh/infraestructura-hosp/camas/${item.id}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id !== item.id)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try { items.value = await api<Item[]>('/sigarh/infraestructura-hosp/camas') }
  catch (e: any) { error.value = apiErr(e, 'Error de conexion') }
  finally { loading.value = false }
}

onMounted(cargar)
</script>
