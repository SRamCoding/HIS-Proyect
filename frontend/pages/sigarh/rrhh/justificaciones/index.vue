<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
interface Item {
  id: string; empleado_id: string; empleado_nombre: string | null; empleado_dni: string | null
  empleado_regimen: string | null; empleado_cargo: string | null
  motivo_id: string | null; motivo_nombre: string | null
  numero_documento: string | null; fecha_tramite: string | null
  fecha_inicio: string; fecha_fin: string; dias: number; estado: string
}
const items = ref<Item[]>([])
const empleados = ref<any[]>([])
const motivos = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const fEmpleado = ref('')
const fMotivo = ref('')
const fEstado = ref('')
const fDesde = ref('')
const fHasta = ref('')

const EST: Record<string, { t: string; c: string }> = {
  pendiente: { t: 'Pendiente', c: 'badge--warning' },
  aprobado: { t: 'Aprobado', c: 'badge--ok' },
  rechazado: { t: 'Rechazado', c: 'badge--danger' },
}
const pendientes = computed(() => items.value.filter(i => i.estado === 'pendiente').length)
const aprobados = computed(() => items.value.filter(i => i.estado === 'aprobado').length)
const diasAprob = computed(() => items.value.filter(i => i.estado === 'aprobado').reduce((s, i) => s + i.dias, 0))

const cargar = async () => {
  loading.value = true; error.value = ''
  const q = new URLSearchParams()
  if (fEmpleado.value) q.set('empleado_id', fEmpleado.value)
  if (fMotivo.value) q.set('motivo_id', fMotivo.value)
  if (fEstado.value) q.set('estado', fEstado.value)
  if (fDesde.value) q.set('desde', fDesde.value)
  if (fHasta.value) q.set('hasta', fHasta.value)
  try { items.value = await api<Item[]>(`/sigarh/rrhh/justificaciones?${q}`) }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
const eliminar = async (it: Item) => {
  if (!confirm('Eliminar esta justificación?')) return
  try { await api(`/sigarh/rrhh/justificaciones/${it.id}`, { method: 'DELETE' }); items.value = items.value.filter(i => i.id !== it.id) }
  catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}
watch([fEmpleado, fMotivo, fEstado, fDesde, fHasta], cargar)
onMounted(async () => {
  try {
    const [e, m] = await Promise.all([api<any[]>('/sigarh/rrhh/empleados'), api<any[]>('/sigarh/rrhh/motivos-justificacion')])
    empleados.value = e; motivos.value = m
  } catch {}
  await cargar()
})
const fmt = (s: string) => s ? new Date(s + 'T00:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: '2-digit' }) : '—'
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-document-check" class="w-5 h-5" style="color: var(--teal)" /></div>
        <div><h1 class="page-title">Justificaciones e Inasistencias</h1><p class="page-subtitle">Consulta y gestión de justificaciones de ausencias y permisos</p></div>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/justificaciones/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Justificación</NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-document-check" class="w-5 h-5" style="color: var(--teal)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length }}</div><div class="sigarh-stat-label">Total</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><div class="sigarh-stat-value">{{ pendientes }}</div><div class="sigarh-stat-label">Pendientes</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><div class="sigarh-stat-value">{{ aprobados }}</div><div class="sigarh-stat-label">Aprobadas</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><div class="sigarh-stat-value">{{ diasAprob }}</div><div class="sigarh-stat-label">Días justificados</div></div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left" style="flex-wrap: wrap">
          <select v-model="fEmpleado" class="input-clinical" style="max-width: 190px; padding-left: 0.75rem">
            <option value="">Todos los empleados</option>
            <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre_completo }}</option>
          </select>
          <select v-model="fMotivo" class="input-clinical" style="max-width: 170px; padding-left: 0.75rem">
            <option value="">Todos los motivos</option>
            <option v-for="m in motivos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
          </select>
          <select v-model="fEstado" class="input-clinical" style="max-width: 150px; padding-left: 0.75rem">
            <option value="">Todos los estados</option>
            <option value="pendiente">Pendiente</option><option value="aprobado">Aprobado</option><option value="rechazado">Rechazado</option>
          </select>
          <label class="text-xs" style="color: var(--ink-soft)">Desde <input v-model="fDesde" type="date" class="input-clinical" style="max-width: 145px; padding-left: 0.75rem" /></label>
          <label class="text-xs" style="color: var(--ink-soft)">Hasta <input v-model="fHasta" type="date" class="input-clinical" style="max-width: 145px; padding-left: 0.75rem" /></label>
        </div>
        <span class="sigarh-result-count">{{ items.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" /></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!items.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-document-check" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" />
        <p style="color: var(--ink-soft)">Sin justificaciones para el filtro seleccionado</p>
        <NuxtLink :to="`/sigarh/rrhh/justificaciones/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva</NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr>
            <th style="width: 9%">DNI</th><th style="width: 18%">Trabajador</th><th style="width: 12%">Régimen</th>
            <th style="width: 13%">Cargo</th><th style="width: 12%">Motivo</th><th style="width: 12%">Inicio – Fin</th>
            <th style="width: 6%">Días</th><th style="width: 9%">Documento</th><th style="width: 7%">Estado</th><th style="width: 5%; text-align: right">Acc.</th>
          </tr></thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ it.empleado_dni || '—' }}</td>
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--teal)" /></div>
                  <span class="sigarh-item-name">{{ it.empleado_nombre || '—' }}</span>
                </div>
              </td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.empleado_regimen || '—' }}</td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.empleado_cargo || '—' }}</td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.motivo_nombre || '—' }}</td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ fmt(it.fecha_inicio) }} – {{ fmt(it.fecha_fin) }}</td>
              <td><span class="badge badge--neutral">{{ it.dias }}</span></td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.numero_documento || '—' }}</td>
              <td><span class="badge" :class="(EST[it.estado] || {}).c || 'badge--neutral'">{{ (EST[it.estado] || {}).t || it.estado }}</span></td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/rrhh/justificaciones/${it.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" /></NuxtLink>
                  <button class="sigarh-action-btn danger" title="Eliminar" @click="eliminar(it)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">Mostrando <strong>{{ items.length }}</strong> justificaciones</div>
      </div>
    </div>
  </div>
</template>
