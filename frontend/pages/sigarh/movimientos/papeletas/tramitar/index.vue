<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')

const dniBusqueda = ref('')
const buscando = ref(false)
const empleado = ref<any>(null)
const empError = ref('')

const MOTIVOS = [
  { v: 'asuntos_particulares', t: 'Asuntos particulares' },
  { v: 'comision', t: 'Comisión' },
  { v: 'salud', t: 'Salud' },
  { v: 'tramite_personal', t: 'Trámite personal' },
  { v: 'otro', t: 'Otro' },
]

const form = reactive({
  empleado_id: '', motivo: '', numero_documento: '', documento_url: '', detalle: '',
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
  if (!form.motivo) { error.value = 'El motivo es requerido'; return }
  if (form.motivo === 'salud' && !form.documento_url) { error.value = 'Para el motivo Salud es obligatorio adjuntar el documento'; return }
  saving.value = true; error.value = ''
  try {
    await api('/sigarh/movimientos/papeletas', { method: 'POST', body: {
      empleado_id: form.empleado_id, motivo: form.motivo,
      numero_documento: form.numero_documento || null,
      documento_url: form.documento_url || null, detalle: form.detalle || null,
    } })
    router.push(`/sigarh/movimientos/papeletas/estado?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo tramitar la papeleta') }
  finally { saving.value = false }
}
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/movimientos/papeletas/estado?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Papeletas</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Tramitar</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--orange-soft)"><UIcon name="i-heroicons-ticket" class="w-6 h-6" style="color: var(--orange)" /></div>
          <div><h1 class="page-title">Tramitar Papeleta</h1><p class="page-subtitle">Solicitud de salida del trabajador durante la jornada</p></div>
        </div>
      </div>

      <SFormCard title="Solicitud de Salida" subtitle="Empleado, motivo y sustento"
        icon="i-heroicons-ticket" icon-bg="var(--orange-soft)" icon-color="var(--orange)" :error="error">
        <div class="form-group">
          <label class="form-label">DNI del trabajador <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-identification" class="input-icon" />
            <input v-model="dniBusqueda" class="input-clinical font-mono-data" maxlength="8" inputmode="numeric"
              @input="dniBusqueda = dniBusqueda.replace(/\D/g, '').slice(0, 8)" @blur="buscarEmpleado" />
            <UIcon v-if="buscando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" style="position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--ink-soft)" />
          </div>
          <span v-if="empError" class="error-message">{{ empError }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Trabajador</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" /><input :value="empleado?.nombre_completo || ''" disabled class="input-clinical" style="background: var(--mist)" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Motivo <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-flag" class="input-icon" />
            <select v-model="form.motivo" class="input-clinical" @change="error = ''">
              <option value="">Seleccione</option>
              <option v-for="m in MOTIVOS" :key="m.v" :value="m.v">{{ m.t }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">N° de documento</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-hashtag" class="input-icon" /><input v-model="form.numero_documento" class="input-clinical font-mono-data" maxlength="50" /></div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Documento sustentatorio (URL) <span v-if="form.motivo === 'salud'" class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-link" class="input-icon" /><input v-model="form.documento_url" class="input-clinical" placeholder="Obligatorio si el motivo es Salud" /></div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Detalle</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.detalle" class="input-clinical" rows="3" maxlength="500" /></div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Tramitar" saving-text="Enviando..."
            :cancel-to="`/sigarh/movimientos/papeletas/estado?tenant=${tenantId}`" @save="handleCreate" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetSummary :items="[
        { label: 'Trabajador', value: empleado?.nombre_completo || '—' },
        { label: 'DNI', value: dniBusqueda, mono: true },
        { label: 'Motivo', value: MOTIVOS.find(m => m.v === form.motivo)?.t || '—' },
      ]" />
      <SWidgetInfo :items="['El empleado no puede tener otra papeleta pendiente o aprobada el mismo día', 'Si el motivo es Salud, el documento es obligatorio', 'La hora de salida se registra al aprobar; la de retorno al ejecutar Registrar Retorno', 'La fecha de trámite es hoy y no se edita']" />
    </template>
  </SFormLayout>
</template>
