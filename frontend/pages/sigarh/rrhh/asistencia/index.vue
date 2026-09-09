<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
interface Item {
  id: string; empleado_id: string; empleado_nombre: string | null
  grupo_ocupacional_nombre: string | null; horario_guardia_nombre: string | null
  fecha: string; actividad_texto: string | null; servicio_texto: string | null
  hora_entrada_programada: string | null; hora_salida_programada: string | null
  hora_entrada_real: string | null; hora_salida_real: string | null
  minutos_tardanza: number; horas_trabajadas: string | null; estado: string
}
const items = ref<Item[]>([])
const empleados = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const hoy = new Date().toISOString().split('T')[0]
const fFecha = ref('')
const fDesde = ref('')
const fHasta = ref('')
const fEmpleado = ref('')
const fSoloTardanza = ref(false)

const EST: Record<string, { t: string; c: string }> = {
  presente: { t: 'Presente', c: 'badge--ok' },
  ausente: { t: 'Ausente', c: 'badge--danger' },
  tardanza: { t: 'Tardanza', c: 'badge--warning' },
  justificado: { t: 'Justificado', c: 'badge--neutral' },
}
const tardanzas = computed(() => items.value.filter(i => i.minutos_tardanza > 0).length)
const ausentes = computed(() => items.value.filter(i => i.estado === 'ausente').length)

const cargar = async () => {
  loading.value = true; error.value = ''
  const q = new URLSearchParams()
  if (fFecha.value) q.set('fecha', fFecha.value)
  if (fDesde.value) q.set('desde', fDesde.value)
  if (fHasta.value) q.set('hasta', fHasta.value)
  if (fEmpleado.value) q.set('empleado_id', fEmpleado.value)
  if (fSoloTardanza.value) q.set('solo_tardanza', 'true')
  try { items.value = await api<Item[]>(`/sigarh/rrhh/asistencia?${q}`) }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
const eliminar = async (it: Item) => {
  if (!confirm('Eliminar este registro de asistencia?')) return
  try { await api(`/sigarh/rrhh/asistencia/${it.id}`, { method: 'DELETE' }); items.value = items.value.filter(i => i.id !== it.id) }
  catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}
watch([fFecha, fDesde, fHasta, fEmpleado, fSoloTardanza], cargar)
onMounted(async () => {
  try { empleados.value = await api<any[]>('/sigarh/rrhh/empleados') } catch {}
  await cargar()
})
const fmtFecha = (s: string) => new Date(s + 'T00:00:00').toLocaleDateString('es-PE', { day: '2-digit', month: 'short', year: 'numeric' })
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-clipboard-document-check" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><h1 class="page-title">Registro de Asistencia</h1><p class="page-subtitle">Control diario de entrada, salida y tardanzas del personal</p></div>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/asistencia/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Registrar</NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-clipboard-document-check" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length }}</div><div class="sigarh-stat-label">Registros</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><div class="sigarh-stat-value">{{ tardanzas }}</div><div class="sigarh-stat-label">Con tardanza</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--alert)">
        <div class="sigarh-stat-icon" style="background: var(--alert-soft, #fde8e8)"><UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--alert)" /></div>
        <div><div class="sigarh-stat-value">{{ ausentes }}</div><div class="sigarh-stat-label">Ausentes</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-sum" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><div class="sigarh-stat-value">{{ items.reduce((s, i) => s + i.minutos_tardanza, 0) }}'</div><div class="sigarh-stat-label">Min. tardanza acum.</div></div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left" style="flex-wrap: wrap">
          <label class="text-xs" style="color: var(--ink-soft)">Día
            <input v-model="fFecha" type="date" class="input-clinical" style="max-width: 160px; padding-left: 0.75rem" />
          </label>
          <label class="text-xs" style="color: var(--ink-soft)">Desde
            <input v-model="fDesde" type="date" class="input-clinical" style="max-width: 150px; padding-left: 0.75rem" />
          </label>
          <label class="text-xs" style="color: var(--ink-soft)">Hasta
            <input v-model="fHasta" type="date" class="input-clinical" style="max-width: 150px; padding-left: 0.75rem" />
          </label>
          <select v-model="fEmpleado" class="input-clinical" style="max-width: 200px; padding-left: 0.75rem">
            <option value="">Todos los empleados</option>
            <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre_completo }}</option>
          </select>
          <label class="sigarh-filter-btn" :class="{ active: fSoloTardanza }" style="cursor: pointer">
            <input v-model="fSoloTardanza" type="checkbox" style="margin-right: 0.35rem" /> Solo tardanzas
          </label>
        </div>
        <span class="sigarh-result-count">{{ items.length }} registros</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--green)" /></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!items.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-clipboard-document-check" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" />
        <p style="color: var(--ink-soft)">Sin registros para el filtro seleccionado</p>
        <NuxtLink :to="`/sigarh/rrhh/asistencia/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Registrar</NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr>
            <th style="width: 10%">Fecha</th><th style="width: 20%">Empleado</th><th style="width: 14%">Servicio / Actividad</th>
            <th style="width: 13%">Programado</th><th style="width: 13%">Real</th><th style="width: 9%">Tardanza</th>
            <th style="width: 8%">H. trab.</th><th style="width: 8%">Estado</th><th style="width: 5%; text-align: right">Acc.</th>
          </tr></thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ fmtFecha(it.fecha) }}</td>
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--green)" /></div>
                  <div>
                    <span class="sigarh-item-name">{{ it.empleado_nombre || '—' }}</span>
                    <div v-if="it.grupo_ocupacional_nombre" style="font-size: 0.75rem; color: var(--ink-soft)">{{ it.grupo_ocupacional_nombre }}</div>
                  </div>
                </div>
              </td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">
                <div>{{ it.servicio_texto || '—' }}</div>
                <div v-if="it.actividad_texto" style="font-size: 0.75rem">{{ it.actividad_texto }}</div>
              </td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ it.hora_entrada_programada || '--:--' }} → {{ it.hora_salida_programada || '--:--' }}</td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ it.hora_entrada_real || '--:--' }} → {{ it.hora_salida_real || '--:--' }}</td>
              <td><span class="badge" :class="it.minutos_tardanza > 0 ? 'badge--warning' : 'badge--neutral'">{{ it.minutos_tardanza }} min</span></td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ it.horas_trabajadas || '—' }}</td>
              <td><span class="badge" :class="(EST[it.estado] || {}).c || 'badge--neutral'">{{ (EST[it.estado] || {}).t || it.estado }}</span></td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/rrhh/asistencia/${it.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" /></NuxtLink>
                  <button class="sigarh-action-btn danger" title="Eliminar" @click="eliminar(it)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">Mostrando <strong>{{ items.length }}</strong> registros</div>
      </div>
    </div>
  </div>
</template>
