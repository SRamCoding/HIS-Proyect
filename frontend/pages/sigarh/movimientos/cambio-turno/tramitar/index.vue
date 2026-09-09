<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const servicios = ref<any[]>([])

const dniA = ref(''), dniB = ref('')
const buscandoA = ref(false), buscandoB = ref(false)
const empA = ref<any>(null), empB = ref<any>(null)
const errA = ref(''), errB = ref('')

const form = reactive({
  servicio_id: '', numero_documento: '',
  solicitante_id: '', fecha_original: '',
  aceptante_id: '', fecha_reemplazo: '',
})

const buscar = async (lado: 'A' | 'B') => {
  const dni = lado === 'A' ? dniA.value : dniB.value
  const setEmp = lado === 'A' ? empA : empB
  const setErr = lado === 'A' ? errA : errB
  const setBusc = lado === 'A' ? buscandoA : buscandoB
  setErr.value = ''; setEmp.value = null
  if (lado === 'A') form.solicitante_id = ''; else form.aceptante_id = ''
  if (dni.length !== 8) return
  setBusc.value = true
  try {
    const e = await api<any>(`/sigarh/movimientos/empleados/buscar-dni/${dni}`)
    if (!e.is_active) { setErr.value = 'El empleado está inactivo'; return }
    setEmp.value = e
    if (lado === 'A') form.solicitante_id = e.id; else form.aceptante_id = e.id
  } catch (e: any) { setErr.value = apiErr(e, 'No se encontró el empleado') }
  finally { setBusc.value = false }
}

const handleCreate = async () => {
  if (!form.servicio_id) { error.value = 'El servicio es requerido'; return }
  if (!form.solicitante_id || !form.aceptante_id) { error.value = 'Busca al solicitante y al aceptante por DNI'; return }
  if (form.solicitante_id === form.aceptante_id) { error.value = 'Deben ser personas distintas'; return }
  if (!form.fecha_original || !form.fecha_reemplazo) { error.value = 'Ambas fechas son requeridas'; return }
  if (form.fecha_original === form.fecha_reemplazo) { error.value = 'Las fechas deben ser diferentes'; return }
  saving.value = true; error.value = ''
  try {
    await api('/sigarh/movimientos/cambio-turno', { method: 'POST', body: {
      servicio_id: form.servicio_id, numero_documento: form.numero_documento || null,
      solicitante_id: form.solicitante_id, fecha_original: form.fecha_original,
      modalidad_solicitante: empA.value?.modalidad || null,
      aceptante_id: form.aceptante_id, fecha_reemplazo: form.fecha_reemplazo,
      modalidad_aceptante: empB.value?.modalidad || null,
    } })
    router.push(`/sigarh/movimientos/cambio-turno/estado?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo tramitar el cambio de turno') }
  finally { saving.value = false }
}
onMounted(async () => {
  try { servicios.value = await api<any[]>('/sigarh/movimientos/servicios') } catch {}
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/movimientos/cambio-turno/estado?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Cambio de Turno</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Tramitar</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--purple-soft)"><UIcon name="i-heroicons-arrows-right-left" class="w-6 h-6" style="color: var(--purple)" /></div>
          <div><h1 class="page-title">Tramitar Cambio de Turno</h1><p class="page-subtitle">Solicitud entre dos trabajadores y dos fechas</p></div>
        </div>
      </div>

      <SFormCard title="Identificación" subtitle="Servicio y documento de la solicitud"
        icon="i-heroicons-building-office" icon-bg="var(--purple-soft)" icon-color="var(--purple)" :error="error">
        <div class="form-group">
          <label class="form-label">Servicio <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-building-office" class="input-icon" />
            <select v-model="form.servicio_id" class="input-clinical"><option value="">Seleccione</option><option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option></select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">N° de documento</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-hashtag" class="input-icon" /><input v-model="form.numero_documento" class="input-clinical font-mono-data" maxlength="50" /></div>
        </div>
      </SFormCard>

      <SFormCard title="Solicitante" subtitle="Quien pide el cambio y su fecha original"
        icon="i-heroicons-user" icon-bg="var(--navy-soft)" icon-color="var(--navy)">
        <div class="form-group">
          <label class="form-label">DNI del solicitante <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-identification" class="input-icon" />
            <input v-model="dniA" class="input-clinical font-mono-data" maxlength="8" inputmode="numeric"
              @input="dniA = dniA.replace(/\D/g, '').slice(0, 8)" @blur="buscar('A')" />
            <UIcon v-if="buscandoA" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" style="position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--ink-soft)" />
          </div>
          <span v-if="errA" class="error-message">{{ errA }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha original <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.fecha_original" type="date" class="input-clinical" @change="error = ''" /></div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Empleado</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" /><input :value="empA ? `${empA.nombre_completo} · ${empA.modalidad || ''}` : ''" disabled class="input-clinical" style="background: var(--mist)" /></div>
        </div>
      </SFormCard>

      <SFormCard title="Aceptante" subtitle="Quien cubre el turno y su fecha de reemplazo"
        icon="i-heroicons-user-plus" icon-bg="var(--teal-soft)" icon-color="var(--teal)">
        <div class="form-group">
          <label class="form-label">DNI del aceptante <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-identification" class="input-icon" />
            <input v-model="dniB" class="input-clinical font-mono-data" maxlength="8" inputmode="numeric"
              @input="dniB = dniB.replace(/\D/g, '').slice(0, 8)" @blur="buscar('B')" />
            <UIcon v-if="buscandoB" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" style="position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--ink-soft)" />
          </div>
          <span v-if="errB" class="error-message">{{ errB }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha de reemplazo <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.fecha_reemplazo" type="date" class="input-clinical" @change="error = ''" /></div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Empleado</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" /><input :value="empB ? `${empB.nombre_completo} · ${empB.modalidad || ''}` : ''" disabled class="input-clinical" style="background: var(--mist)" /></div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Tramitar" saving-text="Enviando..."
            :cancel-to="`/sigarh/movimientos/cambio-turno/estado?tenant=${tenantId}`" @save="handleCreate" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetSummary :items="[
        { label: 'Solicitante', value: empA?.nombre_completo || '—' },
        { label: 'Fecha original', value: form.fecha_original, mono: true },
        { divider: true },
        { label: 'Aceptante', value: empB?.nombre_completo || '—' },
        { label: 'Fecha reemplazo', value: form.fecha_reemplazo, mono: true },
      ]" />
      <SWidgetInfo :items="['Solicitante y aceptante deben ser personas distintas y activas', 'La fecha original no puede ser una fecha pasada', 'No puede existir otro cambio pendiente/aprobado del mismo solicitante en esa fecha', 'Al aprobarse, la asistencia de ambos en sus fechas queda marcada como Justificado']" />
    </template>
  </SFormLayout>
</template>
