<template>
  <div class="sigarh-index-container">

    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Salas</h1>
          <p class="page-subtitle">Ambientes por servicio y su capacidad de camas</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/infraestructura-hosp/salas/create?tenant=${tenantId}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nueva Sala
      </NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.length }}</div>
          <div class="sigarh-stat-label">Total Salas</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)">
          <UIcon name="i-heroicons-rectangle-stack" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ capacidadTotal }}</div>
          <div class="sigarh-stat-label">Capacidad Total</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ camasDisponibles }}</div>
          <div class="sigarh-stat-label">Camas Disponibles</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-user" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ camasOcupadas }}</div>
          <div class="sigarh-stat-label">Camas Ocupadas</div>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar sala por nombre o codigo..." class="sigarh-search-input" />
          </div>
          <select v-model="filtroPiso" class="input-clinical" style="max-width: 220px; padding-left: 0.75rem;">
            <option value="">Todos los pisos</option>
            <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
          </select>
        </div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span class="sigarh-result-count">{{ filteredItems.length }} resultados</span>
          <button v-if="search || filtroPiso" @click="search = ''; filtroPiso = ''" class="sigarh-clear-btn">Limpiar</button>
        </div>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
        <p style="color: var(--ink-soft)">Cargando salas...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button @click="cargar" class="btn-outline">Reintentar</button>
      </div>
      <div v-else-if="!filteredItems.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-squares-plus" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">Sin salas registradas</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Comienza creando una sala</p>
        </div>
        <NuxtLink :to="`/sigarh/infraestructura-hosp/salas/create?tenant=${tenantId}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Sala
        </NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 22%">Nombre</th>
              <th style="width: 10%">Codigo</th>
              <th style="width: 16%">Piso</th>
              <th style="width: 16%">Servicio</th>
              <th style="width: 9%">Capacidad</th>
              <th style="width: 12%">Camas</th>
              <th style="width: 15%; text-align: right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--teal-soft)">
                    <UIcon name="i-heroicons-squares-plus" class="w-4 h-4" style="color: var(--teal)" />
                  </div>
                  <span class="sigarh-item-name">{{ item.nombre }}</span>
                </div>
              </td>
              <td>
                <span v-if="item.codigo" class="sigarh-code-badge">{{ item.codigo }}</span>
                <span v-else style="color: var(--ink-soft)">-</span>
              </td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ item.piso_nombre || '-' }}</td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ item.servicio_nombre || '-' }}</td>
              <td style="font-family: monospace; color: var(--ink-soft)">{{ item.capacidad }}</td>
              <td style="font-size: 0.8125rem">
                <span class="badge" :class="item.total_camas >= item.capacidad ? 'badge--ok' : 'badge--warning'">{{ item.total_camas }}/{{ item.capacidad }}</span>
                <span style="color: var(--ink-soft); margin-left: 0.35rem">{{ item.camas_disponibles }} disp · {{ item.camas_ocupadas }} ocup</span>
              </td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <button v-if="item.total_camas < item.capacidad" class="sigarh-action-btn" title="Generar camas" @click="abrirGenerar(item)">
                    <UIcon name="i-heroicons-sparkles" class="w-4 h-4" style="color: var(--purple)" />
                  </button>
                  <NuxtLink :to="`/sigarh/infraestructura-hosp/salas/${item.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar">
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
          Mostrando <strong>{{ filteredItems.length }}</strong> de <strong>{{ items.length }}</strong> salas
        </div>
      </div>
    </div>

    <!-- Modal Generar Camas -->
    <div v-if="genModal.sala" class="sigarh-modal-overlay" @click.self="genModal.sala = null">
      <div class="sigarh-modal">
        <h3 style="font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0 0 0.25rem">Generar camas</h3>
        <p style="font-size: 0.8125rem; color: var(--ink-soft); margin: 0 0 1rem">
          {{ genModal.sala.nombre }} · faltan <strong>{{ genModal.sala.capacidad - genModal.sala.total_camas }}</strong> de {{ genModal.sala.capacidad }}
        </p>
        <div v-if="genModal.error" class="error-banner" style="margin-bottom: 1rem">{{ genModal.error }}</div>
        <div class="form-group" style="margin-bottom: 0.75rem">
          <label class="form-label">Prefijo del código</label>
          <input v-model="genModal.prefijo" class="input-clinical font-mono-data" style="padding-left: 0.75rem" placeholder="Ej: H (genera H01, H02...)" />
        </div>
        <div class="form-group" style="margin-bottom: 1rem">
          <label class="form-label">Tipo de cama <span class="required">*</span></label>
          <select v-model="genModal.tipo_cama" class="input-clinical" style="padding-left: 0.75rem">
            <option value="">Seleccione un tipo</option>
            <option v-for="t in tiposCama" :key="t.id" :value="t.nombre">{{ t.nombre }}</option>
          </select>
          <p v-if="!tiposCama.length" class="field-hint">Configura los tipos de cama en Infraestructura → Catálogos (categoría "tipos_cama")</p>
        </div>
        <div style="display: flex; justify-content: flex-end; gap: 0.5rem">
          <button class="btn-cancel" @click="genModal.sala = null">Cancelar</button>
          <button class="btn-primary" :disabled="genModal.saving || !genModal.tipo_cama" @click="confirmarGenerar">
            {{ genModal.saving ? 'Generando...' : 'Generar' }}
          </button>
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
  piso_id: string | null
  piso_nombre: string | null
  servicio_nombre: string | null
  capacidad: number
  total_camas: number
  camas_disponibles: number
  camas_ocupadas: number
  is_active: boolean
}

const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const pisos = ref<any[]>([])
const tiposCama = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const filtroPiso = ref('')

const capacidadTotal = computed(() => items.value.reduce((s, i) => s + (i.capacidad || 0), 0))
const camasDisponibles = computed(() => items.value.reduce((s, i) => s + (i.camas_disponibles || 0), 0))
const camasOcupadas = computed(() => items.value.reduce((s, i) => s + (i.camas_ocupadas || 0), 0))

const filteredItems = computed(() => {
  let r = items.value
  if (filtroPiso.value) r = r.filter(i => i.piso_id === filtroPiso.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    r = r.filter(i => i.nombre.toLowerCase().includes(q) || (i.codigo || '').toLowerCase().includes(q))
  }
  return r
})

const genModal = reactive<{ sala: Item | null; prefijo: string; tipo_cama: string; saving: boolean; error: string }>({
  sala: null, prefijo: '', tipo_cama: '', saving: false, error: '',
})
const abrirGenerar = (item: Item) => {
  Object.assign(genModal, { sala: item, prefijo: item.codigo || '', tipo_cama: '', saving: false, error: '' })
}
const confirmarGenerar = async () => {
  if (!genModal.sala || !genModal.tipo_cama) return
  genModal.saving = true
  genModal.error = ''
  try {
    await api(`/sigarh/infraestructura-hosp/salas/${genModal.sala.id}/generar-camas`, {
      method: 'POST',
      body: { prefijo: genModal.prefijo || null, tipo_cama: genModal.tipo_cama },
    })
    genModal.sala = null
    await cargar()
  } catch (e: any) { genModal.error = apiErr(e, 'No se pudieron generar las camas') }
  finally { genModal.saving = false }
}

const eliminar = async (item: Item) => {
  if (!confirm(`Eliminar la sala "${item.nombre}"?`)) return
  try {
    await api(`/sigarh/infraestructura-hosp/salas/${item.id}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id !== item.id)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    const [salas, ps, tc] = await Promise.all([
      api<Item[]>('/sigarh/infraestructura-hosp/salas'),
      api<any[]>('/sigarh/infraestructura-hosp/pisos').catch(() => []),
      api<any[]>('/sigarh/infraestructura/catalogos?categoria=tipos_cama').catch(() => []),
    ])
    items.value = salas
    pisos.value = ps
    tiposCama.value = tc
  } catch (e: any) { error.value = apiErr(e, 'Error de conexion') }
  finally { loading.value = false }
}

onMounted(cargar)
</script>
