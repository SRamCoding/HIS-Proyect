<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const grupos = ref<any[]>([])
const horarios = ref<any[]>([])
const empleadoNombre = ref('')
const minutosTardanza = ref(0)
const horasTrabajadas = ref('')
const registradoPor = ref('')

const form = reactive({
  grupo_ocupacional_id: '', horario_guardia_id: '', fecha: '',
  servicio_texto: '', actividad_texto: '',
  hora_entrada_programada: '', hora_salida_programada: '',
  hora_entrada_real: '', hora_salida_real: '',
  estado: 'presente', observacion: '',
})

watch(() => form.horario_guardia_id, (hid, old) => {
  if (!old) return
  const h = horarios.value.find(x => x.id === hid)
  if (h) {
    form.hora_entrada_programada = (h.hora_inicio || '').slice(0, 5)
    form.hora_salida_programada = (h.hora_fin || '').slice(0, 5)
  }
})

const handleSave = async () => {
  if (!form.fecha) { error.value = 'La fecha es requerida'; return }
  saving.value = true; error.value = ''
  try {
    await api(`/sigarh/rrhh/asistencia/${id.value}`, { method: 'PATCH', body: {
      grupo_ocupacional_id: form.grupo_ocupacional_id || null,
      horario_guardia_id: form.horario_guardia_id || null,
      fecha: form.fecha,
      servicio_texto: form.servicio_texto || null,
      actividad_texto: form.actividad_texto || null,
      hora_entrada_programada: form.hora_entrada_programada || null,
      hora_salida_programada: form.hora_salida_programada || null,
      hora_entrada_real: form.hora_entrada_real || null,
      hora_salida_real: form.hora_salida_real || null,
      estado: form.estado,
      observacion: form.observacion || null,
    } })
    router.push(`/sigarh/rrhh/asistencia?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const [g, h, d] = await Promise.all([
      api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
      api<any[]>('/sigarh/mantenimiento/horarios-guardia'),
      api<any>(`/sigarh/rrhh/asistencia/${id.value}`),
    ])
    grupos.value = g
    horarios.value = h
    form.grupo_ocupacional_id = d.grupo_ocupacional_id || ''
    form.horario_guardia_id = d.horario_guardia_id || ''
    form.fecha = d.fecha
    form.servicio_texto = d.servicio_texto || ''
    form.actividad_texto = d.actividad_texto || ''
    form.hora_entrada_programada = d.hora_entrada_programada || ''
    form.hora_salida_programada = d.hora_salida_programada || ''
    form.hora_entrada_real = d.hora_entrada_real || ''
    form.hora_salida_real = d.hora_salida_real || ''
    form.estado = d.estado || 'presente'
    form.observacion = d.observacion || ''
    empleadoNombre.value = d.empleado_nombre || ''
    minutosTardanza.value = d.minutos_tardanza || 0
    horasTrabajadas.value = d.horas_trabajadas || '—'
    registradoPor.value = d.registrado_por || '—'
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/asistencia?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Registro de Asistencia</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Editar</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-clipboard-document-check" class="w-6 h-6" style="color: var(--green)" /></div>
          <div><h1 class="page-title">{{ empleadoNombre || 'Editar Registro' }}</h1><p class="page-subtitle">Ajusta horas y estado — la tardanza se recalcula al guardar</p></div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--green)" /></div>
      <template v-else>
        <SFormCard title="Jornada" subtitle="Grupo, horario, servicio y actividad"
          icon="i-heroicons-user" icon-bg="var(--green-soft)" icon-color="var(--green)" :error="error">
          <div class="form-group">
            <label class="form-label">Fecha <span class="required">*</span></label>
            <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.fecha" type="date" class="input-clinical" @change="error = ''" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Grupo ocupacional</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-user-group" class="input-icon" />
              <select v-model="form.grupo_ocupacional_id" class="input-clinical">
                <option value="">Sin grupo</option>
                <option v-for="g in grupos" :key="g.id" :value="g.id">{{ g.nombre }}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Horario / Guardia</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-clock" class="input-icon" />
              <select v-model="form.horario_guardia_id" class="input-clinical">
                <option value="">Sin horario</option>
                <option v-for="h in horarios" :key="h.id" :value="h.id">{{ h.nombre }} ({{ (h.hora_inicio || '').slice(0,5) }}–{{ (h.hora_fin || '').slice(0,5) }})</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Servicio</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-building-office" class="input-icon" /><input v-model="form.servicio_texto" class="input-clinical" maxlength="100" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Actividad</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-briefcase" class="input-icon" /><input v-model="form.actividad_texto" class="input-clinical" maxlength="100" /></div>
          </div>
        </SFormCard>

        <SFormCard title="Horas y Estado" subtitle="Programado vs. real"
          icon="i-heroicons-clock" icon-bg="var(--navy-soft)" icon-color="var(--navy)">
          <div class="form-group">
            <label class="form-label">Entrada programada</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-arrow-right-on-rectangle" class="input-icon" /><input v-model="form.hora_entrada_programada" type="time" class="input-clinical font-mono-data" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Salida programada</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-arrow-left-on-rectangle" class="input-icon" /><input v-model="form.hora_salida_programada" type="time" class="input-clinical font-mono-data" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Entrada real</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-arrow-right-on-rectangle" class="input-icon" /><input v-model="form.hora_entrada_real" type="time" class="input-clinical font-mono-data" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Salida real</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-arrow-left-on-rectangle" class="input-icon" /><input v-model="form.hora_salida_real" type="time" class="input-clinical font-mono-data" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-flag" class="input-icon" />
              <select v-model="form.estado" class="input-clinical">
                <option value="presente">Presente</option><option value="tardanza">Tardanza</option>
                <option value="ausente">Ausente</option><option value="justificado">Justificado</option>
              </select>
            </div>
          </div>
          <div class="form-group full-width">
            <label class="form-label">Observación</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.observacion" class="input-clinical" rows="2" /></div>
          </div>
          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/rrhh/asistencia?tenant=${tenantId}`" @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>
    <template #sidebar>
      <SWidgetSummary :items="[
        { label: 'Empleado', value: empleadoNombre },
        { divider: true },
        { label: 'Tardanza registrada', value: minutosTardanza + ' min' },
        { label: 'Horas trabajadas', value: horasTrabajadas },
        { label: 'Registrado por', value: registradoPor },
      ]" />
      <SWidgetInfo :items="['Al guardar, la tardanza se recalcula con la tolerancia vigente del grupo', 'Cambiar el horario reescribe las horas programadas', 'El estado puede pasar a Justificado si hay una justificación aprobada']" />
      <SWidgetTip text="Si el empleado tiene una justificación aprobada para esta fecha, marca el estado como Justificado." />
    </template>
  </SFormLayout>
</template>
