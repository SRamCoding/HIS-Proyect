<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const empleados = ref<any[]>([])
const grupos = ref<any[]>([])
const horarios = ref<any[]>([])
const feriados = ref<string[]>([])

const form = reactive({
  empleado_id: '', grupo_ocupacional_id: '', horario_guardia_id: '',
  fecha: new Date().toISOString().split('T')[0],
  servicio_texto: '', actividad_texto: '',
  hora_entrada_programada: '', hora_salida_programada: '',
  hora_entrada_real: '', hora_salida_real: '',
  estado: 'presente', observacion: '',
})

const empSel = computed(() => empleados.value.find(e => e.id === form.empleado_id))
const grpNombre = computed(() => grupos.value.find(g => g.id === form.grupo_ocupacional_id)?.nombre || '—')
const esFeriado = computed(() => feriados.value.includes(form.fecha))

const _min = (h: string) => { const [a, b] = h.split(':').map(Number); return a * 60 + b }
const tardanzaEstimada = computed(() => {
  if (!form.hora_entrada_programada || !form.hora_entrada_real) return 0
  const d = _min(form.hora_entrada_real) - _min(form.hora_entrada_programada)
  return d > 0 ? d : 0
})
const horasTrab = computed(() => {
  if (!form.hora_entrada_real || !form.hora_salida_real) return '—'
  let d = _min(form.hora_salida_real) - _min(form.hora_entrada_real)
  if (d < 0) d += 1440
  return `${String(Math.floor(d / 60)).padStart(2, '0')}:${String(d % 60).padStart(2, '0')}`
})

watch(() => form.empleado_id, async (id) => {
  if (!id) return
  try {
    const emp = await api<any>(`/sigarh/rrhh/empleados/${id}`)
    if (emp.grupo_ocupacional_id) form.grupo_ocupacional_id = emp.grupo_ocupacional_id
  } catch {}
})
watch(() => form.horario_guardia_id, (id) => {
  const h = horarios.value.find(x => x.id === id)
  if (h) {
    form.hora_entrada_programada = (h.hora_inicio || '').slice(0, 5)
    form.hora_salida_programada = (h.hora_fin || '').slice(0, 5)
  }
})

const handleCreate = async (otro: boolean) => {
  if (!form.empleado_id) { error.value = 'El empleado es requerido'; return }
  if (!form.fecha) { error.value = 'La fecha es requerida'; return }
  saving.value = true; error.value = ''
  try {
    await api('/sigarh/rrhh/asistencia', { method: 'POST', body: {
      empleado_id: form.empleado_id,
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
    if (otro) Object.assign(form, { empleado_id: '', grupo_ocupacional_id: '', horario_guardia_id: '', servicio_texto: '', actividad_texto: '', hora_entrada_programada: '', hora_salida_programada: '', hora_entrada_real: '', hora_salida_real: '', estado: 'presente', observacion: '' })
    else router.push(`/sigarh/rrhh/asistencia?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo registrar la asistencia') }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const [e, g, h, f] = await Promise.all([
      api<any[]>('/sigarh/rrhh/empleados'),
      api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
      api<any[]>('/sigarh/mantenimiento/horarios-guardia'),
      api<any[]>('/sigarh/rrhh/feriados'),
    ])
    empleados.value = e
    grupos.value = g
    horarios.value = h.filter((x: any) => x.is_active !== false)
    feriados.value = f.filter((x: any) => x.is_active).map((x: any) => x.fecha)
  } catch (err: any) { error.value = apiErr(err, 'Error al cargar datos') }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/asistencia?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Registro de Asistencia</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Registrar</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-clipboard-document-check" class="w-6 h-6" style="color: var(--green)" /></div>
          <div><h1 class="page-title">Registrar Asistencia</h1><p class="page-subtitle">Marca la jornada de un empleado y calcula la tardanza</p></div>
        </div>
      </div>

      <SFormCard title="Empleado y Jornada" subtitle="A quién y qué día corresponde el registro"
        icon="i-heroicons-user" icon-bg="var(--green-soft)" icon-color="var(--green)" :error="error">
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
          <label class="form-label">Fecha <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.fecha" type="date" class="input-clinical" @change="error = ''" /></div>
          <p v-if="esFeriado" class="field-hint" style="color: var(--amber)"><UIcon name="i-heroicons-exclamation-triangle" class="w-3.5 h-3.5 inline" /> Esta fecha es feriado — el registro se permite igual.</p>
        </div>
        <div class="form-group">
          <label class="form-label">Grupo ocupacional</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user-group" class="input-icon" />
            <select v-model="form.grupo_ocupacional_id" class="input-clinical">
              <option value="">Sin grupo</option>
              <option v-for="g in grupos" :key="g.id" :value="g.id">{{ g.nombre }}</option>
            </select>
          </div>
          <p class="field-hint">Determina la regla de tolerancia aplicada. Se autocompleta del empleado.</p>
        </div>
        <div class="form-group">
          <label class="form-label">Horario / Guardia programada</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-clock" class="input-icon" />
            <select v-model="form.horario_guardia_id" class="input-clinical">
              <option value="">Sin horario</option>
              <option v-for="h in horarios" :key="h.id" :value="h.id">{{ h.nombre }} ({{ (h.hora_inicio || '').slice(0,5) }}–{{ (h.hora_fin || '').slice(0,5) }})</option>
            </select>
          </div>
          <p class="field-hint">Al elegirlo se autocompletan las horas programadas.</p>
        </div>
        <div class="form-group">
          <label class="form-label">Servicio</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-building-office" class="input-icon" /><input v-model="form.servicio_texto" class="input-clinical" maxlength="100" placeholder="Ej: Emergencia" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Actividad</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-briefcase" class="input-icon" /><input v-model="form.actividad_texto" class="input-clinical" maxlength="100" placeholder="Ej: Guardia diurna" /></div>
        </div>
      </SFormCard>

      <SFormCard title="Horas y Estado" subtitle="Programado vs. real — la tardanza se calcula automáticamente"
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
          <p class="field-hint">Si hay tardanza calculada y el estado es "Presente", el sistema lo cambia a "Tardanza".</p>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Observación</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.observacion" class="input-clinical" rows="2" /></div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Registrar" saving-text="Registrando..."
            :cancel-to="`/sigarh/rrhh/asistencia?tenant=${tenantId}`" :show-create-another="true"
            @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetSummary :items="[
        { label: 'Empleado', value: empSel?.nombre_completo || '—' },
        { label: 'Grupo', value: grpNombre },
        { divider: true },
        { label: 'Tardanza estimada', value: tardanzaEstimada + ' min' },
        { label: 'Horas trabajadas', value: horasTrab },
      ]" />
      <SWidgetInfo :items="['La tardanza real descuenta la tolerancia configurada para el grupo', 'Programadas se autocompletan desde el horario de guardia', 'Un registro en feriado se permite pero queda marcado', 'registrado_por guarda el usuario que hace el registro']" />
      <SWidgetTip text="Vincula el grupo ocupacional correcto: es lo que conecta la asistencia con la regla de tolerancia y el rol aprobado." />
    </template>
  </SFormLayout>
</template>
