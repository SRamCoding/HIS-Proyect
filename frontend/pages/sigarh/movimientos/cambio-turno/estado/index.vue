<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
interface Item {
  id: string; numero_documento: string | null
  solicitante_nombre: string | null; aceptante_nombre: string | null
  fecha_original: string; fecha_reemplazo: string
  servicio_nombre: string | null; estado: string
  revisado_por: string | null; motivo_rechazo: string | null; created_at: string
}
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const fEstado = ref('')
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
  const q = fEstado.value ? `?estado=${fEstado.value}` : ''
  try { items.value = await api<Item[]>(`/sigarh/movimientos/cambio-turno${q}`) }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
const aprobar = async (it: Item) => {
  procesando.value = it.id
  try { const d = await api<any>(`/sigarh/movimientos/cambio-turno/${it.id}/aprobar`, { method: 'POST', body: {} }); Object.assign(it, d) }
  catch (e: any) { error.value = apiErr(e, 'No se pudo aprobar') }
  finally { procesando.value = '' }
}
const confirmarRechazo = async () => {
  if (!rechazando.value || !motivoRechazo.value.trim()) return
  procesando.value = rechazando.value.id
  try {
    const d = await api<any>(`/sigarh/movimientos/cambio-turno/${rechazando.value.id}/rechazar`, { method: 'POST', body: { motivo_rechazo: motivoRechazo.value } })
    Object.assign(rechazando.value, d)
    rechazando.value = null; motivoRechazo.value = ''
  } catch (e: any) { error.value = apiErr(e, 'No se pudo rechazar') }
  finally { procesando.value = '' }
}
watch(fEstado, cargar)
onMounted(cargar)
const fmt = (s: string | null) => s ? new Date(s + 'T00:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: '2-digit' }) : '—'
const fmtDT = (s: string) => s ? new Date(s).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: '2-digit' }) : '—'
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--purple-soft)"><UIcon name="i-heroicons-arrows-right-left" class="w-5 h-5" style="color: var(--purple)" /></div>
        <div><h1 class="page-title">Estado de Cambios de Turno</h1><p class="page-subtitle">Revisa y decide las solicitudes de intercambio</p></div>
      </div>
      <NuxtLink :to="`/sigarh/movimientos/cambio-turno/tramitar?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Tramitar</NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)"><UIcon name="i-heroicons-arrows-right-left" class="w-5 h-5" style="color: var(--purple)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length }}</div><div class="sigarh-stat-label">Total</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><div class="sigarh-stat-value">{{ pend }}</div><div class="sigarh-stat-label">Pendientes</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><div class="sigarh-stat-value">{{ items.filter(i => i.estado === 'aprobado').length }}</div><div class="sigarh-stat-label">Aprobados</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--alert)">
        <div class="sigarh-stat-icon" style="background: var(--alert-soft, #fde8e8)"><UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--alert)" /></div>
        <div><div class="sigarh-stat-value">{{ items.filter(i => i.estado === 'rechazado').length }}</div><div class="sigarh-stat-label">Rechazados</div></div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-filter-group">
            <button @click="fEstado = ''" class="sigarh-filter-btn" :class="{ active: fEstado === '' }">Todos</button>
            <button @click="fEstado = 'pendiente'" class="sigarh-filter-btn" :class="{ active: fEstado === 'pendiente' }">Pendientes</button>
            <button @click="fEstado = 'aprobado'" class="sigarh-filter-btn" :class="{ active: fEstado === 'aprobado' }">Aprobados</button>
            <button @click="fEstado = 'rechazado'" class="sigarh-filter-btn" :class="{ active: fEstado === 'rechazado' }">Rechazados</button>
          </div>
        </div>
        <span class="sigarh-result-count">{{ items.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--purple)" /></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!items.length" class="sigarh-table-state"><UIcon name="i-heroicons-arrows-right-left" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" /><p style="color: var(--ink-soft)">Sin solicitudes</p></div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr>
            <th style="width: 10%">Documento</th><th style="width: 10%">Solicitud</th><th style="width: 18%">Solicitante</th>
            <th style="width: 18%">Aceptante</th><th style="width: 11%">F. original</th><th style="width: 11%">F. reemplazo</th>
            <th style="width: 9%">Estado</th><th style="width: 13%; text-align: right">Acciones</th>
          </tr></thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.numero_documento || '—' }}</td>
              <td class="font-mono-data" style="font-size: 0.8125rem; color: var(--ink-soft)">{{ fmtDT(it.created_at) }}</td>
              <td><span class="sigarh-item-name">{{ it.solicitante_nombre || '—' }}</span></td>
              <td><span class="sigarh-item-name">{{ it.aceptante_nombre || '—' }}</span></td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ fmt(it.fecha_original) }}</td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ fmt(it.fecha_reemplazo) }}</td>
              <td><span class="badge" :class="(EST[it.estado] || {}).c || 'badge--neutral'">{{ (EST[it.estado] || {}).t || it.estado }}</span></td>
              <td style="text-align: right">
                <div class="sigarh-actions" v-if="it.estado === 'pendiente'">
                  <button class="sigarh-action-btn" title="Aprobar" :disabled="procesando === it.id" @click="aprobar(it)"><UIcon name="i-heroicons-check-circle" class="w-4 h-4" style="color: var(--green)" /></button>
                  <button class="sigarh-action-btn danger" title="Rechazar" @click="rechazando = it; motivoRechazo = ''"><UIcon name="i-heroicons-x-circle" class="w-4 h-4" style="color: var(--alert)" /></button>
                </div>
                <span v-else-if="it.revisado_por" class="field-hint" style="margin: 0">por {{ it.revisado_por }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="rechazando" class="sigarh-modal-overlay" @click.self="rechazando = null">
      <div class="sigarh-modal" style="max-width: 420px">
        <h3 style="font-weight: 700; margin: 0 0 0.75rem">Rechazar cambio de turno</h3>
        <p style="font-size: 0.875rem; color: var(--ink-soft); margin: 0 0 0.5rem">{{ rechazando.solicitante_nombre }} ⇄ {{ rechazando.aceptante_nombre }}</p>
        <textarea v-model="motivoRechazo" class="input-clinical" rows="3" maxlength="500" placeholder="Motivo del rechazo (requerido)" style="padding-left: 0.75rem" />
        <div style="text-align: right; margin-top: 1rem; display: flex; gap: 0.5rem; justify-content: flex-end">
          <button class="btn-outline" @click="rechazando = null">Cancelar</button>
          <button class="btn-primary" :disabled="!motivoRechazo.trim() || !!procesando" style="background: var(--alert)" @click="confirmarRechazo">Rechazar</button>
        </div>
      </div>
    </div>
  </div>
</template>
