<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
interface Item {
  id: string; codigo: string; nombre: string; tipo: string
  fuente_financiamiento: string | null; ubicacion_fisica: string | null
  despacha_recetas: boolean; is_active: boolean
}
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const fTipo = ref('')
const fDespacha = ref('')
const fEstado = ref('all')

const TIPOS: Record<string, string> = { farmacia: 'Farmacia', almacen_central: 'Almacén Central', laboratorio: 'Laboratorio', dispensacion: 'Dispensación' }
const FUENTES: Record<string, string> = { sismed: 'SISMED', donaciones: 'Donaciones', mixto: 'Mixto' }

const activos = computed(() => items.value.filter(i => i.is_active).length)
const despachan = computed(() => items.value.filter(i => i.despacha_recetas).length)
const filtrados = computed(() => {
  let r = items.value
  if (fEstado.value === 'active') r = r.filter(i => i.is_active)
  else if (fEstado.value === 'inactive') r = r.filter(i => !i.is_active)
  if (search.value.trim()) { const q = search.value.toLowerCase(); r = r.filter(i => i.nombre.toLowerCase().includes(q) || i.codigo.toLowerCase().includes(q)) }
  return r
})

const cargar = async () => {
  loading.value = true; error.value = ''
  const q = new URLSearchParams()
  if (fTipo.value) q.set('tipo', fTipo.value)
  if (fDespacha.value) q.set('despacha_recetas', fDespacha.value)
  try { items.value = await api<Item[]>(`/sigarh/config-farmacia/almacenes?${q}`) }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
const eliminar = async (it: Item) => {
  if (!confirm(`Eliminar el almacén "${it.nombre}"?`)) return
  try { await api(`/sigarh/config-farmacia/almacenes/${it.id}`, { method: 'DELETE' }); items.value = items.value.filter(i => i.id !== it.id) }
  catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}
watch([fTipo, fDespacha], cargar)
onMounted(cargar)
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-building-storefront" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><h1 class="page-title">Almacenes / Farmacias</h1><p class="page-subtitle">Establecimientos y depósitos que manejan existencias</p></div>
      </div>
      <NuxtLink :to="`/sigarh/config-farmacia/almacenes/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Almacén</NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-building-storefront" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length }}</div><div class="sigarh-stat-label">Total</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><div class="sigarh-stat-value">{{ activos }}</div><div class="sigarh-stat-label">Activos</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-document-check" class="w-5 h-5" style="color: var(--teal)" /></div>
        <div><div class="sigarh-stat-value">{{ despachan }}</div><div class="sigarh-stat-label">Despachan recetas</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length - activos }}</div><div class="sigarh-stat-label">Inactivos</div></div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left" style="flex-wrap: wrap">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar por nombre o código..." class="sigarh-search-input" />
          </div>
          <select v-model="fTipo" class="input-clinical" style="max-width: 170px; padding-left: 0.75rem">
            <option value="">Todos los tipos</option>
            <option v-for="(t, k) in TIPOS" :key="k" :value="k">{{ t }}</option>
          </select>
          <select v-model="fDespacha" class="input-clinical" style="max-width: 170px; padding-left: 0.75rem">
            <option value="">Despacho: todos</option>
            <option value="true">Solo despachan recetas</option>
            <option value="false">No despachan</option>
          </select>
          <div class="sigarh-filter-group">
            <button @click="fEstado = 'all'" class="sigarh-filter-btn" :class="{ active: fEstado === 'all' }">Todos</button>
            <button @click="fEstado = 'active'" class="sigarh-filter-btn" :class="{ active: fEstado === 'active' }">Activos</button>
            <button @click="fEstado = 'inactive'" class="sigarh-filter-btn" :class="{ active: fEstado === 'inactive' }">Inactivos</button>
          </div>
        </div>
        <span class="sigarh-result-count">{{ filtrados.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" /></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!filtrados.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-building-storefront" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" />
        <p style="color: var(--ink-soft)">Sin almacenes</p>
        <NuxtLink :to="`/sigarh/config-farmacia/almacenes/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo</NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr>
            <th style="width: 12%">Código</th><th style="width: 26%">Nombre</th><th style="width: 15%">Tipo</th>
            <th style="width: 13%">Financiamiento</th><th style="width: 12%">Despacha recetas</th>
            <th style="width: 12%">Estado</th><th style="width: 10%; text-align: right">Acciones</th>
          </tr></thead>
          <tbody>
            <tr v-for="it in filtrados" :key="it.id">
              <td><span class="sigarh-code-badge">{{ it.codigo }}</span></td>
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-building-storefront" class="w-4 h-4" style="color: var(--navy)" /></div>
                  <div>
                    <span class="sigarh-item-name">{{ it.nombre }}</span>
                    <div v-if="it.ubicacion_fisica" style="font-size: 0.72rem; color: var(--ink-soft)">{{ it.ubicacion_fisica }}</div>
                  </div>
                </div>
              </td>
              <td><span class="badge badge--neutral">{{ TIPOS[it.tipo] || it.tipo }}</span></td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.fuente_financiamiento ? (FUENTES[it.fuente_financiamiento] || it.fuente_financiamiento) : '—' }}</td>
              <td><span class="badge" :class="it.despacha_recetas ? 'badge--ok' : 'badge--neutral'">{{ it.despacha_recetas ? 'Sí' : 'No' }}</span></td>
              <td><span class="badge" :class="it.is_active ? 'badge--ok' : 'badge--neutral'">{{ it.is_active ? 'Activo' : 'Inactivo' }}</span></td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/config-farmacia/almacenes/${it.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" /></NuxtLink>
                  <button class="sigarh-action-btn danger" title="Eliminar" @click="eliminar(it)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">Mostrando <strong>{{ filtrados.length }}</strong> de <strong>{{ items.length }}</strong> almacenes</div>
      </div>
    </div>
  </div>
</template>
