<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
interface Item {
  id: string; empleado_nombre: string | null; empleado_dni: string | null
  motivo_nombre: string | null; numero_documento: string | null
  fecha_tramite: string | null; fecha_inicio: string; fecha_fin: string
  dias: number; estado: string; documento_url: string | null
}
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const fEstado = ref('')

const EST: Record<string, { t: string; c: string }> = {
  pendiente: { t: 'Pendiente', c: 'badge--warning' },
  aprobado: { t: 'Aprobado', c: 'badge--ok' },
  rechazado: { t: 'Rechazado', c: 'badge--danger' },
}
const pend = computed(() => items.value.filter(i => i.estado === 'pendiente').length)
const aprob = computed(() => items.value.filter(i => i.estado === 'aprobado').length)

const cargar = async () => {
  loading.value = true; error.value = ''
  const q = fEstado.value ? `?estado=${fEstado.value}` : ''
  try { items.value = await api<Item[]>(`/sigarh/movimientos/licencias${q}`) }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
watch(fEstado, cargar)
onMounted(cargar)
const fmt = (s: string | null) => s ? new Date(s + 'T00:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: '2-digit' }) : '—'
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-clipboard-document-list" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><h1 class="page-title">Estado de Licencias</h1><p class="page-subtitle">Consulta el resultado y los documentos de las licencias tramitadas</p></div>
      </div>
      <NuxtLink :to="`/sigarh/movimientos/licencias/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Tramitar Licencia</NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-clipboard-document-list" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length }}</div><div class="sigarh-stat-label">Total</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><div class="sigarh-stat-value">{{ pend }}</div><div class="sigarh-stat-label">Pendientes</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><div class="sigarh-stat-value">{{ aprob }}</div><div class="sigarh-stat-label">Aprobadas</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" /></div>
        <div><div class="sigarh-stat-value">{{ items.filter(i => i.estado === 'aprobado').reduce((s, i) => s + i.dias, 0) }}</div><div class="sigarh-stat-label">Días aprobados</div></div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-filter-group">
            <button @click="fEstado = ''" class="sigarh-filter-btn" :class="{ active: fEstado === '' }">Todos</button>
            <button @click="fEstado = 'pendiente'" class="sigarh-filter-btn" :class="{ active: fEstado === 'pendiente' }">Pendientes</button>
            <button @click="fEstado = 'aprobado'" class="sigarh-filter-btn" :class="{ active: fEstado === 'aprobado' }">Aprobadas</button>
            <button @click="fEstado = 'rechazado'" class="sigarh-filter-btn" :class="{ active: fEstado === 'rechazado' }">Rechazadas</button>
          </div>
        </div>
        <span class="sigarh-result-count">{{ items.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" /></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!items.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-clipboard-document-list" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" />
        <p style="color: var(--ink-soft)">Sin licencias para el filtro seleccionado</p>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr>
            <th style="width: 10%">Trámite</th><th style="width: 20%">Empleado</th><th style="width: 10%">DNI</th>
            <th style="width: 16%">Motivo</th><th style="width: 15%">Inicio – Fin</th><th style="width: 6%">Días</th>
            <th style="width: 9%">Estado</th><th style="width: 9%">Doc.</th><th style="width: 5%; text-align: right">Acc.</th>
          </tr></thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td class="font-mono-data" style="font-size: 0.8125rem; color: var(--ink-soft)">{{ fmt(it.fecha_tramite) }}</td>
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--navy)" /></div>
                  <span class="sigarh-item-name">{{ it.empleado_nombre || '—' }}</span>
                </div>
              </td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ it.empleado_dni || '—' }}</td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.motivo_nombre || '—' }}</td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ fmt(it.fecha_inicio) }} – {{ fmt(it.fecha_fin) }}</td>
              <td><span class="badge badge--neutral">{{ it.dias }}</span></td>
              <td><span class="badge" :class="(EST[it.estado] || {}).c || 'badge--neutral'">{{ (EST[it.estado] || {}).t || it.estado }}</span></td>
              <td>
                <a v-if="it.documento_url" :href="it.documento_url" target="_blank" class="sigarh-action-btn" title="Ver documento"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" style="color: var(--teal)" /></a>
                <span v-else style="color: var(--ink-soft)">—</span>
              </td>
              <td style="text-align: right">
                <NuxtLink :to="`/sigarh/movimientos/licencias/${it.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Ver / Editar"><UIcon name="i-heroicons-eye" class="w-4 h-4" style="color: var(--teal)" /></NuxtLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
