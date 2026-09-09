<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const empleados = ref<any[]>([])
const motivos = ref<any[]>([])

const form = reactive({
  empleado_id: '', motivo_id: '', numero_documento: '',
  fecha_tramite: new Date().toISOString().split('T')[0],
  fecha_inicio: '', fecha_fin: '', descripcion: '', estado: 'pendiente',
})

const empSel = computed(() => empleados.value.find(e => e.id === form.empleado_id))
const dias = computed(() => {
  if (!form.fecha_inicio || !form.fecha_fin) return 0
  const d = Math.ceil((new Date(form.fecha_fin).getTime() - new Date(form.fecha_inicio).getTime()) / 86400000) + 1
  return d > 0 ? d : 0
})

const handleCreate = async () => {
  if (!form.empleado_id) { error.value = 'El empleado es requerido'; return }
  if (!form.fecha_inicio || !form.fecha_fin) { error.value = 'Las fechas de inicio y fin son requeridas'; return }
  if (new Date(form.fecha_fin) < new Date(form.fecha_inicio)) { error.value = 'La fecha de fin no puede ser anterior a la de inicio'; return }
  saving.value = true; error.value = ''
  try {
    await api('/sigarh/rrhh/justificaciones', { method: 'POST', body: {
      empleado_id: form.empleado_id,
      motivo_id: form.motivo_id || null,
      numero_documento: form.numero_documento || null,
      fecha_tramite: form.fecha_tramite || null,
      fecha_inicio: form.fecha_inicio,
      fecha_fin: form.fecha_fin,
      descripcion: form.descripcion || null,
      estado: form.estado,
    } })
    router.push(`/sigarh/rrhh/justificaciones?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo crear la justificación') }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const [e, m] = await Promise.all([api<any[]>('/sigarh/rrhh/empleados'), api<any[]>('/sigarh/rrhh/motivos-justificacion')])
    empleados.value = e
    motivos.value = m.filter((x: any) => x.is_active !== false)
  } catch (err: any) { error.value = apiErr(err, 'Error al cargar datos') }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/justificaciones?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Justificaciones</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Nueva</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-document-check" class="w-6 h-6" style="color: var(--teal)" /></div>
          <div><h1 class="page-title">Crear Justificación</h1><p class="page-subtitle">Registra una justificación de ausencia o permiso</p></div>
        </div>
      </div>

      <SFormCard title="Trabajador y Motivo" subtitle="Quién solicita y por qué"
        icon="i-heroicons-user" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">
        <div class="form-group">
          <label class="form-label">Empleado <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" />
            <select v-model="form.empleado_id" class="input-clinical" @change="error = ''">
              <option value="">Seleccione un empleado</option>
              <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre_completo }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Motivo</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-flag" class="input-icon" />
            <select v-model="form.motivo_id" class="input-clinical">
              <option value="">Sin motivo específico</option>
              <option v-for="m in motivos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">N° de documento</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-hashtag" class="input-icon" /><input v-model="form.numero_documento" class="input-clinical font-mono-data" maxlength="50" placeholder="Ej: MEMO-0123-2026" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha de trámite</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_tramite" type="date" class="input-clinical" /></div>
        </div>
      </SFormCard>

      <SFormCard title="Período y Estado" subtitle="Rango de días que cubre la justificación"
        icon="i-heroicons-calendar-days" icon-bg="var(--navy-soft)" icon-color="var(--navy)">
        <div class="form-group">
          <label class="form-label">Fecha inicio <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.fecha_inicio" type="date" class="input-clinical" @change="error = ''" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha fin <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.fecha_fin" type="date" class="input-clinical" @change="error = ''" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Días</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calculator" class="input-icon" /><input :value="dias" disabled class="input-clinical font-mono-data" style="background: var(--surface-2, #f4f5f7)" /></div>
          <p class="field-hint">Calculado automáticamente (ambos extremos incluidos)</p>
        </div>
        <div class="form-group">
          <label class="form-label">Estado</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-flag" class="input-icon" />
            <select v-model="form.estado" class="input-clinical">
              <option value="pendiente">Pendiente</option><option value="aprobado">Aprobado</option><option value="rechazado">Rechazado</option>
            </select>
          </div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Descripción / Sustento</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.descripcion" class="input-clinical" rows="3" placeholder="Detalle del permiso o ausencia..." /></div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Crear" saving-text="Creando..."
            :cancel-to="`/sigarh/rrhh/justificaciones?tenant=${tenantId}`" @save="handleCreate" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetSummary :items="[
        { label: 'Empleado', value: empSel?.nombre_completo || '—' },
        { label: 'DNI', value: empSel?.dni || '—', mono: true },
        { divider: true },
        { label: 'Días', value: String(dias) },
        { label: 'Estado', value: form.estado },
      ]" />
      <SWidgetInfo :items="['Una justificación aprobada permite marcar la asistencia como Justificado', 'Los días se calculan incluyendo la fecha de inicio y la de fin', 'El motivo es opcional pero recomendado para reportes de ausentismo']" />
      <SWidgetTip text="Registra el N° de documento del memo o solicitud física: es la trazabilidad ante auditoría." />
    </template>
  </SFormLayout>
</template>
