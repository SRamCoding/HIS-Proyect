<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const motivos = ref<any[]>([])

const dniBusqueda = ref('')
const buscando = ref(false)
const empleado = ref<any>(null)
const empError = ref('')

const form = reactive({
  empleado_id: '', tipo: 'justificacion', motivo_id: '', numero_documento: '',
  fecha_tramite: new Date().toISOString().split('T')[0],
  fecha_inicio: '', fecha_fin: '', documento_url: '', descripcion: '',
})

const dias = computed(() => {
  if (!form.fecha_inicio || !form.fecha_fin) return 0
  const d = Math.ceil((new Date(form.fecha_fin).getTime() - new Date(form.fecha_inicio).getTime()) / 86400000) + 1
  return d > 0 ? d : 0
})

const buscarEmpleado = async () => {
  empError.value = ''; empleado.value = null; form.empleado_id = ''
  if (dniBusqueda.value.length !== 8) return
  buscando.value = true
  try {
    const e = await api<any>(`/sigarh/movimientos/empleados/buscar-dni/${dniBusqueda.value}`)
    if (!e.is_active) { empError.value = 'El empleado está inactivo'; return }
    empleado.value = e; form.empleado_id = e.id
  } catch (e: any) { empError.value = apiErr(e, 'No se encontró el empleado') }
  finally { buscando.value = false }
}

const handleCreate = async () => {
  if (!form.empleado_id) { error.value = 'Busca y selecciona un empleado por DNI'; return }
  if (!form.fecha_inicio || !form.fecha_fin) { error.value = 'Las fechas son requeridas'; return }
  if (new Date(form.fecha_fin) < new Date(form.fecha_inicio)) { error.value = 'La fecha de fin no puede ser anterior a la de inicio'; return }
  saving.value = true; error.value = ''
  try {
    await api('/sigarh/movimientos/vacaciones', { method: 'POST', body: {
      empleado_id: form.empleado_id, tipo: form.tipo, motivo_id: form.motivo_id || null,
      numero_documento: form.numero_documento || null, fecha_tramite: form.fecha_tramite || null,
      fecha_inicio: form.fecha_inicio, fecha_fin: form.fecha_fin,
      documento_url: form.documento_url || null, descripcion: form.descripcion || null,
    } })
    router.push(`/sigarh/movimientos/vacaciones?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo registrar la solicitud') }
  finally { saving.value = false }
}
onMounted(async () => {
  try { motivos.value = await api<any[]>('/sigarh/movimientos/motivos') } catch {}
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/movimientos/vacaciones?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Justificación y Vacaciones</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Nueva</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-sun" class="w-6 h-6" style="color: var(--amber)" /></div>
          <div><h1 class="page-title">Nueva solicitud</h1><p class="page-subtitle">Justificación / inasistencia o solicitud de vacaciones</p></div>
        </div>
      </div>

      <SFormCard title="Trabajador y Tipo" subtitle="Búscalo por DNI"
        icon="i-heroicons-user" icon-bg="var(--amber-soft)" icon-color="var(--amber)" :error="error">
        <div class="form-group">
          <label class="form-label">Tipo de movimiento <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-adjustments-horizontal" class="input-icon" />
            <select v-model="form.tipo" class="input-clinical">
              <option value="justificacion">Justificación / Inasistencia</option>
              <option value="vacacion">Solicitud de Vacaciones</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">DNI del empleado <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-identification" class="input-icon" />
            <input v-model="dniBusqueda" class="input-clinical font-mono-data" maxlength="8" inputmode="numeric"
              @input="dniBusqueda = dniBusqueda.replace(/\D/g, '').slice(0, 8)" @blur="buscarEmpleado" />
            <UIcon v-if="buscando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" style="position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--ink-soft)" />
          </div>
          <span v-if="empError" class="error-message">{{ empError }}</span>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Empleado</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" /><input :value="empleado?.nombre_completo || ''" disabled class="input-clinical" style="background: var(--mist)" /></div>
        </div>
      </SFormCard>

      <SFormCard title="Datos de la Solicitud" subtitle="Motivo, período y sustento"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--teal-soft)" icon-color="var(--teal)">
        <div class="form-group">
          <label class="form-label">Motivo</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-flag" class="input-icon" />
            <select v-model="form.motivo_id" class="input-clinical"><option value="">Sin motivo específico</option><option v-for="m in motivos" :key="m.id" :value="m.id">{{ m.nombre }}</option></select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">N° de documento</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-hashtag" class="input-icon" /><input v-model="form.numero_documento" class="input-clinical font-mono-data" maxlength="50" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha de trámite</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_tramite" type="date" class="input-clinical" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Días</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calculator" class="input-icon" /><input :value="dias" disabled class="input-clinical font-mono-data" style="background: var(--mist)" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha inicio <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.fecha_inicio" type="date" class="input-clinical" @change="error = ''" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha fin <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.fecha_fin" type="date" class="input-clinical" @change="error = ''" /></div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Documento sustentatorio (URL)</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-link" class="input-icon" /><input v-model="form.documento_url" class="input-clinical" /></div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Detalle</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.descripcion" class="input-clinical" rows="3" maxlength="500" /></div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Registrar" saving-text="Enviando..."
            :cancel-to="`/sigarh/movimientos/vacaciones?tenant=${tenantId}`" @save="handleCreate" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetSummary :items="[
        { label: 'Empleado', value: empleado?.nombre_completo || '—' },
        { label: 'Tipo', value: form.tipo },
        { divider: true },
        { label: 'Días', value: String(dias) },
      ]" />
      <SWidgetInfo :items="['Queda en estado Pendiente hasta que se revise en esta misma bandeja', 'Una solicitud aprobada marca la asistencia del período como Justificado', 'El módulo de saldo vacacional aún no está implementado']" />
    </template>
  </SFormLayout>
</template>
