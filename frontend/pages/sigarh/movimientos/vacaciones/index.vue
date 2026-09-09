<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
interface Item {
  id: string; tipo: string; empleado_nombre: string | null; empleado_dni: string | null
  motivo_nombre: string | null; fecha_tramite: string | null
  fecha_inicio: string; fecha_fin: string; dias: number; estado: string
  descripcion: string | null; documento_url: string | null; motivo_rechazo: string | null
}
const items = ref<Item[]>([])
const motivos = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const fEstado = ref('')
const fMotivo = ref('')
const detalle = ref<Item | null>(null)
const rechazando = ref<Item | null>(null)
const motivoRechazo = ref('')
const procesando = ref('')

const EST: Record<string, { t: string; c: string }> = {
  pendiente: { t: 'Pendiente', c: 'badge--warning' },
  aprobado: { t: 'Aprobado', c: 'badge--ok' },
  rechazado: { t: 'Rechazado', c: 'badge--danger' },
}
const pend = computed(() => items.value.filter(i => i.estado === 'pendiente').length)

const cargar = async () => {
  loading.value = true; error.value = ''
  const q = new URLSearchParams()
  if (fEstado.value) q.set('estado', fEstado.value)
  if (fMotivo.value) q.set('motivo_id', fMotivo.value)
  try { items.value = await api<Item[]>(`/sigarh/movimientos/vacaciones?${q}`) }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
const aprobar = async (it: Item) => {
  procesando.value = it.id
  try { const d = await api<any>(`/sigarh/movimientos/vacaciones/${it.id}/aprobar`, { method: 'POST', body: {} }); Object.assign(it, d) }
  catch (e: any) { error.value = apiErr(e, 'No se pudo aprobar') }
  finally { procesando.value = '' }
}
const confirmarRechazo = async () => {
  if (!rechazando.value || !motivoRechazo.value.trim()) return
  procesando.value = rechazando.value.id
  try {
    const d = await api<any>(`/sigarh/movimientos/vacaciones/${rechazando.value.id}/rechazar`, { method: 'POST', body: { motivo_rechazo: motivoRechazo.value } })
    Object.assign(rechazando.value, d)
    rechazando.value = null; motivoRechazo.value = ''
  } catch (e: any) { error.value = apiErr(e, 'No se pudo rechazar') }
  finally { procesando.value = '' }
}
watch([fEstado, fMotivo], cargar)
onMounted(async () => {
  try { motivos.value = await api<any[]>('/sigarh/movimientos/motivos') } catch {}
  await cargar()
})
const fmt = (s: string | null) => s ? new Date(s + 'T00:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: '2-digit' }) : '—'
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-sun" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><h1 class="page-title">Justificación y Vacaciones</h1><p class="page-subtitle">Bandeja de revisión: aprueba o rechaza licencias y justificaciones</p></div>
      </div>
      <NuxtLink :to="`/sigarh/movimientos/vacaciones/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva solicitud</NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-sun" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length }}</div><div class="sigarh-stat-label">Total</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--alert)">
        <div class="sigarh-stat-icon" style="background: var(--alert-soft, #fde8e8)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--alert)" /></div>
        <div><div class="sigarh-stat-value">{{ pend }}</div><div class="sigarh-stat-label">Por revisar</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><div class="sigarh-stat-value">{{ items.filter(i => i.estado === 'aprobado').length }}</div><div class="sigarh-stat-label">Aprobadas</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><div class="sigarh-stat-value">{{ items.filter(i => i.estado === 'aprobado').reduce((s, i) => s + i.dias, 0) }}</div><div class="sigarh-stat-label">Días aprobados</div></div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left" style="flex-wrap: wrap">
          <div class="sigarh-filter-group">
            <button @click="fEstado = ''" class="sigarh-filter-btn" :class="{ active: fEstado === '' }">Todas</button>
            <button @click="fEstado = 'pendiente'" class="sigarh-filter-btn" :class="{ active: fEstado === 'pendiente' }">Pendientes</button>
            <button @click="fEstado = 'aprobado'" class="sigarh-filter-btn" :class="{ active: fEstado === 'aprobado' }">Aprobadas</button>
            <button @click="fEstado = 'rechazado'" class="sigarh-filter-btn" :class="{ active: fEstado === 'rechazado' }">Rechazadas</button>
          </div>
          <select v-model="fMotivo" class="input-clinical" style="max-width: 190px; padding-left: 0.75rem">
            <option value="">Todos los motivos</option>
            <option v-for="m in motivos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
          </select>
        </div>
        <span class="sigarh-result-count">{{ items.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--amber)" /></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!items.length" class="sigarh-table-state"><UIcon name="i-heroicons-sun" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" /><p style="color: var(--ink-soft)">Sin solicitudes</p></div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr>
            <th style="width: 9%">DNI</th><th style="width: 20%">Empleado</th><th style="width: 10%">Tipo</th>
            <th style="width: 15%">Motivo</th><th style="width: 15%">Inicio – Fin</th><th style="width: 6%">Días</th>
            <th style="width: 9%">Estado</th><th style="width: 16%; text-align: right">Acciones</th>
          </tr></thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ it.empleado_dni || '—' }}</td>
              <td><div class="sigarh-item-cell"><div class="sigarh-item-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--amber)" /></div><span class="sigarh-item-name">{{ it.empleado_nombre || '—' }}</span></div></td>
              <td><span class="badge badge--neutral" style="text-transform: capitalize">{{ it.tipo }}</span></td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.motivo_nombre || '—' }}</td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ fmt(it.fecha_inicio) }} – {{ fmt(it.fecha_fin) }}</td>
              <td><span class="badge badge--neutral">{{ it.dias }}</span></td>
              <td><span class="badge" :class="(EST[it.estado] || {}).c || 'badge--neutral'">{{ (EST[it.estado] || {}).t || it.estado }}</span></td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <button class="sigarh-action-btn" title="Ver detalle" @click="detalle = it"><UIcon name="i-heroicons-eye" class="w-4 h-4" style="color: var(--teal)" /></button>
                  <template v-if="it.estado === 'pendiente'">
                    <button class="sigarh-action-btn" title="Aprobar" :disabled="procesando === it.id" @click="aprobar(it)"><UIcon name="i-heroicons-check-circle" class="w-4 h-4" style="color: var(--green)" /></button>
                    <button class="sigarh-action-btn danger" title="Rechazar" @click="rechazando = it; motivoRechazo = ''"><UIcon name="i-heroicons-x-circle" class="w-4 h-4" style="color: var(--alert)" /></button>
                  </template>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="detalle" class="sigarh-modal-overlay" @click.self="detalle = null">
      <div class="sigarh-modal" style="max-width: 460px">
        <h3 style="font-weight: 700; margin: 0 0 0.75rem">{{ detalle.empleado_nombre }}</h3>
        <div style="font-size: 0.875rem; display: grid; gap: 0.4rem">
          <div><strong>DNI:</strong> {{ detalle.empleado_dni || '—' }}</div>
          <div><strong>Tipo:</strong> <span style="text-transform: capitalize">{{ detalle.tipo }}</span></div>
          <div><strong>Motivo:</strong> {{ detalle.motivo_nombre || '—' }}</div>
          <div><strong>Trámite:</strong> {{ fmt(detalle.fecha_tramite) }}</div>
          <div><strong>Período:</strong> {{ fmt(detalle.fecha_inicio) }} – {{ fmt(detalle.fecha_fin) }} ({{ detalle.dias }} días)</div>
          <div><strong>Detalle:</strong> {{ detalle.descripcion || '—' }}</div>
          <div v-if="detalle.motivo_rechazo"><strong>Motivo de rechazo:</strong> {{ detalle.motivo_rechazo }}</div>
          <div v-if="detalle.documento_url"><a :href="detalle.documento_url" target="_blank" style="color: var(--teal)">Ver documento</a></div>
        </div>
        <div style="text-align: right; margin-top: 1rem"><button class="btn-outline" @click="detalle = null">Cerrar</button></div>
      </div>
    </div>

    <div v-if="rechazando" class="sigarh-modal-overlay" @click.self="rechazando = null">
      <div class="sigarh-modal" style="max-width: 420px">
        <h3 style="font-weight: 700; margin: 0 0 0.75rem">Rechazar solicitud</h3>
        <p style="font-size: 0.875rem; color: var(--ink-soft); margin: 0 0 0.5rem">{{ rechazando.empleado_nombre }}</p>
        <textarea v-model="motivoRechazo" class="input-clinical" rows="3" maxlength="500" placeholder="Motivo del rechazo (requerido)" style="padding-left: 0.75rem" />
        <div style="text-align: right; margin-top: 1rem; display: flex; gap: 0.5rem; justify-content: flex-end">
          <button class="btn-outline" @click="rechazando = null">Cancelar</button>
          <button class="btn-primary" :disabled="!motivoRechazo.trim() || !!procesando" style="background: var(--alert)" @click="confirmarRechazo">Rechazar</button>
        </div>
      </div>
    </div>
  </div>
</template>
