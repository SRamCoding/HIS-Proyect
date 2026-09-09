<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
interface Item { id: string; nombre: string; fecha: string; tipo: string; is_active: boolean }
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const now = new Date()
const fAnio = ref<number | ''>(now.getFullYear())
const fMes = ref<number | ''>('')
const fEstado = ref('all')
const MESES = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

const filtered = computed(() => fEstado.value === 'all' ? items.value : items.value.filter(i => fEstado.value === 'active' ? i.is_active : !i.is_active))
const cargar = async () => {
  loading.value = true; error.value = ''
  const q = new URLSearchParams()
  if (fAnio.value) q.set('anio', String(fAnio.value))
  if (fMes.value) q.set('mes', String(fMes.value))
  try { items.value = await api<Item[]>(`/sigarh/rrhh/feriados?${q}`) }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
const eliminar = async (it: Item) => {
  if (!confirm(`Eliminar el feriado "${it.nombre}"?`)) return
  try { await api(`/sigarh/rrhh/feriados/${it.id}`, { method: 'DELETE' }); items.value = items.value.filter(i => i.id !== it.id) }
  catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}
watch([fAnio, fMes], cargar)
onMounted(cargar)
const fmtFecha = (s: string) => new Date(s + 'T00:00:00').toLocaleDateString('es-PE', { weekday: 'short', day: '2-digit', month: 'long', year: 'numeric' })
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-calendar" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><h1 class="page-title">Días Feriados</h1><p class="page-subtitle">Calendario de fechas especiales del hospital</p></div>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/feriados/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Feriado</NuxtLink>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left" style="flex-wrap: wrap">
          <input v-model.number="fAnio" type="number" placeholder="Año" class="input-clinical font-mono-data" style="max-width: 110px; padding-left: 0.75rem" />
          <select v-model.number="fMes" class="input-clinical" style="max-width: 160px; padding-left: 0.75rem">
            <option value="">Todos los meses</option>
            <option v-for="m in 12" :key="m" :value="m">{{ MESES[m] }}</option>
          </select>
          <div class="sigarh-filter-group">
            <button @click="fEstado = 'all'" class="sigarh-filter-btn" :class="{ active: fEstado === 'all' }">Todos</button>
            <button @click="fEstado = 'active'" class="sigarh-filter-btn" :class="{ active: fEstado === 'active' }">Activos</button>
            <button @click="fEstado = 'inactive'" class="sigarh-filter-btn" :class="{ active: fEstado === 'inactive' }">Inactivos</button>
          </div>
        </div>
        <span class="sigarh-result-count">{{ filtered.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" /></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!filtered.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-calendar" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" />
        <p style="color: var(--ink-soft)">Sin feriados en el período seleccionado</p>
        <NuxtLink :to="`/sigarh/rrhh/feriados/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo</NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr><th style="width: 44%">Descripción</th><th style="width: 30%">Fecha</th><th style="width: 14%">Tipo</th><th style="width: 7%">Estado</th><th style="width: 5%; text-align: right">Acciones</th></tr></thead>
          <tbody>
            <tr v-for="it in filtered" :key="it.id">
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-calendar" class="w-4 h-4" style="color: var(--navy)" /></div>
                  <span class="sigarh-item-name">{{ it.nombre }}</span>
                </div>
              </td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem; text-transform: capitalize">{{ fmtFecha(it.fecha) }}</td>
              <td><span class="badge badge--neutral" style="text-transform: capitalize">{{ it.tipo }}</span></td>
              <td><span class="badge" :class="it.is_active ? 'badge--ok' : 'badge--neutral'">{{ it.is_active ? 'Activo' : 'Inactivo' }}</span></td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/rrhh/feriados/${it.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" /></NuxtLink>
                  <button class="sigarh-action-btn danger" title="Eliminar" @click="eliminar(it)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
