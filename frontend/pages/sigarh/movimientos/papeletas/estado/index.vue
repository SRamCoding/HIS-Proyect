<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
interface Item {
  id: string; empleado_nombre: string | null; empleado_cargo: string | null
  motivo: string | null; numero_documento: string | null; fecha_tramite: string
  documento_url: string | null; detalle: string | null; estado: string
  hora_salida: string | null; hora_retorno: string | null
  revisado_por: string | null; motivo_rechazo: string | null
}
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const fEstado = ref('')
const fFecha = ref('')
const rechazando = ref<Item | null>(null)
const motivoRechazo = ref('')
const procesando = ref('')

const MOT: Record<string, string> = {
  asuntos_particulares: 'Asuntos particulares', comision: 'Comisión', salud: 'Salud',
  tramite_personal: 'Trámite personal', otro: 'Otro',
}
const EST: Record<string, { t: string; c: string }> = {
  pendiente: { t: 'Pendiente', c: 'badge--warning' },
  aprobado: { t: 'Aprobado', c: 'badge--ok' },
  rechazado: { t: 'Rechazado', c: 'badge--danger' },
  caducado: { t: 'Caducado', c: 'badge--neutral' },
}
const pend = computed(() => items.value.filter(i => i.estado === 'pendiente').length)
const fuera = computed(() => items.value.filter(i => i.estado === 'aprobado' && !i.hora_retorno).length)

const cargar = async () => {
  loading.value = true; error.value = ''
  const q = new URLSearchParams()
  if (fEstado.value) q.set('estado', fEstado.value)
  if (fFecha.value) q.set('fecha', fFecha.value)
  try { items.value = await api<Item[]>(`/sigarh/movimientos/papeletas?${q}`) }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
const accion = async (it: Item, ruta: 'aprobar' | 'registrar-retorno') => {
  procesando.value = it.id
  try { const d = await api<any>(`/sigarh/movimientos/papeletas/${it.id}/${ruta}`, { method: 'POST', body: {} }); Object.assign(it, d) }
  catch (e: any) { error.value = apiErr(e, 'No se pudo procesar') }
  finally { procesando.value = '' }
}
const confirmarRechazo = async () => {
  if (!rechazando.value || !motivoRechazo.value.trim()) return
  procesando.value = rechazando.value.id
  try {
    const d = await api<any>(`/sigarh/movimientos/papeletas/${rechazando.value.id}/rechazar`, { method: 'POST', body: { motivo_rechazo: motivoRechazo.value } })
    Object.assign(rechazando.value, d)
    rechazando.value = null; motivoRechazo.value = ''
  } catch (e: any) { error.value = apiErr(e, 'No se pudo rechazar') }
  finally { procesando.value = '' }
}
watch([fEstado, fFecha], cargar)
onMounted(cargar)
const fmt = (s: string | null) => s ? new Date(s + 'T00:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: '2-digit' }) : '—'
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--orange-soft)"><UIcon name="i-heroicons-ticket" class="w-5 h-5" style="color: var(--orange)" /></div>
        <div><h1 class="page-title">Estado de Papeletas</h1><p class="page-subtitle">Autoriza la salida y registra el retorno del personal</p></div>
      </div>
      <NuxtLink :to="`/sigarh/movimientos/papeletas/tramitar?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Tramitar</NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--orange)">
        <div class="sigarh-stat-icon" style="background: var(--orange-soft)"><UIcon name="i-heroicons-ticket" class="w-5 h-5" style="color: var(--orange)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length }}</div><div class="sigarh-stat-label">Total</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><div class="sigarh-stat-value">{{ pend }}</div><div class="sigarh-stat-label">Por autorizar</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-arrow-right-start-on-rectangle" class="w-5 h-5" style="color: var(--teal)" /></div>
        <div><div class="sigarh-stat-value">{{ fuera }}</div><div class="sigarh-stat-label">Fuera (sin retorno)</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><div class="sigarh-stat-value">{{ items.filter(i => i.estado === 'aprobado').length }}</div><div class="sigarh-stat-label">Aprobadas</div></div>
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
          <input v-model="fFecha" type="date" class="input-clinical" style="max-width: 160px; padding-left: 0.75rem" />
        </div>
        <span class="sigarh-result-count">{{ items.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--orange)" /></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!items.length" class="sigarh-table-state"><UIcon name="i-heroicons-ticket" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" /><p style="color: var(--ink-soft)">Sin papeletas</p></div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr>
            <th style="width: 10%">Fecha</th><th style="width: 22%">Trabajador</th><th style="width: 14%">Motivo</th>
            <th style="width: 8%">Doc.</th><th style="width: 9%">Estado</th><th style="width: 8%">Salida</th>
            <th style="width: 8%">Retorno</th><th style="width: 21%; text-align: right">Acciones</th>
          </tr></thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td class="font-mono-data" style="font-size: 0.8125rem; color: var(--ink-soft)">{{ fmt(it.fecha_tramite) }}</td>
              <td><div class="sigarh-item-cell"><div class="sigarh-item-icon" style="background: var(--orange-soft)"><UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--orange)" /></div><span class="sigarh-item-name">{{ it.empleado_nombre || '—' }}</span></div></td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ MOT[it.motivo || ''] || it.motivo || '—' }}</td>
              <td><a v-if="it.documento_url" :href="it.documento_url" target="_blank" class="sigarh-action-btn"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" style="color: var(--teal)" /></a><span v-else style="color: var(--ink-soft)">—</span></td>
              <td><span class="badge" :class="(EST[it.estado] || {}).c || 'badge--neutral'">{{ (EST[it.estado] || {}).t || it.estado }}</span></td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ it.hora_salida || '—' }}</td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ it.hora_retorno || '—' }}</td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <template v-if="it.estado === 'pendiente'">
                    <button class="sigarh-action-btn" title="Aprobar" :disabled="procesando === it.id" @click="accion(it, 'aprobar')"><UIcon name="i-heroicons-check-circle" class="w-4 h-4" style="color: var(--green)" /></button>
                    <button class="sigarh-action-btn danger" title="Rechazar" @click="rechazando = it; motivoRechazo = ''"><UIcon name="i-heroicons-x-circle" class="w-4 h-4" style="color: var(--alert)" /></button>
                  </template>
                  <button v-else-if="it.estado === 'aprobado' && !it.hora_retorno" class="sigarh-action-btn" title="Registrar retorno" :disabled="procesando === it.id" @click="accion(it, 'registrar-retorno')">
                    <UIcon name="i-heroicons-arrow-uturn-left" class="w-4 h-4" style="color: var(--teal)" />
                  </button>
                  <span v-else-if="it.revisado_por" class="field-hint" style="margin: 0">por {{ it.revisado_por }}</span>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="rechazando" class="sigarh-modal-overlay" @click.self="rechazando = null">
      <div class="sigarh-modal" style="max-width: 420px">
        <h3 style="font-weight: 700; margin: 0 0 0.75rem">Rechazar papeleta</h3>
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
