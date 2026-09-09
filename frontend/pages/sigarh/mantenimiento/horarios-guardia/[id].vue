<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/horarios-guardia?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Horarios de Guardia</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Horario</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--purple-soft)">
            <UIcon name="i-heroicons-clock" class="w-6 h-6" style="color: var(--purple)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Horario de Guardia' }}</h1>
            <p class="page-subtitle">Actualiza los datos del horario de guardia</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--purple)" />
      </div>

      <template v-else>
        <SFormCard title="Datos del Horario" subtitle="Actualiza los datos del horario de guardia"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--purple-soft)" icon-color="var(--purple)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-clock" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Guardia Diurna 12h, Guardia Nocturna" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Tipo de Guardia</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-shield-check" class="input-icon" />
              <select v-model="form.tipo_guardia_id" class="input-clinical">
                <option value="">Sin tipo</option>
                <option v-for="t in tiposGuardia" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Horas Totales</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-chart-bar" class="input-icon" />
              <input v-model.number="form.horas_totales" type="number" min="0" step="0.5" class="input-clinical font-mono-data" placeholder="12" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Hora Inicio <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-arrow-right-circle" class="input-icon" />
              <input v-model="form.hora_inicio" type="time" class="input-clinical font-mono-data" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Hora Fin</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-arrow-left-circle" class="input-icon" />
              <input v-model="form.hora_fin" type="time" class="input-clinical font-mono-data" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Horario Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre"
            :extra="`${form.hora_inicio || '--:--'} - ${form.hora_fin || '--:--'}`"
            :codigo="form.horas_totales ? `${form.horas_totales} h` : ''"
            :active="form.is_active"
            icon="i-heroicons-clock"
            icon-color="var(--purple)"
            icon-bg="var(--purple-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/horarios-guardia?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Definen las franjas horarias de las guardias', 'Al elegir un tipo de guardia se calcula la hora fin', 'Las horas totales se recalculan segun inicio y fin', 'Los horarios inactivos no se pueden asignar']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Tipo de Guardia', value: tipoGuardiaNombre },
        { label: 'Inicio', value: form.hora_inicio, mono: true },
        { label: 'Fin', value: form.hora_fin, mono: true },
        { label: 'Horas Totales', value: form.horas_totales ? String(form.horas_totales) : '', mono: true },
        { divider: true },
        { label: 'Estado', slot: 'estado' },
      ]">
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Elige primero el tipo de guardia: la hora fin y las horas totales se completan automaticamente." />
    </template>
  </SFormLayout>
</template>

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
const tiposGuardia = ref<any[]>([])
const form = reactive({
  nombre: '',
  hora_inicio: '',
  hora_fin: '',
  horas_totales: null as number | null,
  tipo_guardia_id: '',
  is_active: true,
})

const tipoGuardiaNombre = computed(() => tiposGuardia.value.find(t => t.id === form.tipo_guardia_id)?.nombre || '')

const calcFin = () => {
  const tg = tiposGuardia.value.find(t => t.id === form.tipo_guardia_id)
  if (tg && tg.horas && form.hora_inicio) {
    const [h, m] = form.hora_inicio.split(':').map(Number)
    const total = h * 60 + m + tg.horas * 60
    form.hora_fin = `${String(Math.floor(total / 60) % 24).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`
  }
}

watch(() => form.tipo_guardia_id, () => {
  const tg = tiposGuardia.value.find(t => t.id === form.tipo_guardia_id)
  if (tg && tg.horas) { form.horas_totales = tg.horas; calcFin() }
})
watch(() => form.hora_inicio, calcFin)
watch([() => form.hora_inicio, () => form.hora_fin], ([inicio, fin]) => {
  if (inicio && fin) {
    const [h1, m1] = inicio.split(':').map(Number)
    const [h2, m2] = fin.split(':').map(Number)
    let diff = (h2 * 60 + m2) - (h1 * 60 + m1)
    if (diff < 0) diff += 24 * 60
    form.horas_totales = Math.round(diff / 60 * 10) / 10
  }
})

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  if (!form.hora_inicio) { error.value = 'La hora de inicio es requerida'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/horarios-guardia/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        hora_inicio: form.hora_inicio,
        hora_fin: form.hora_fin,
        horas_totales: form.horas_totales || null,
        tipo_guardia_id: form.tipo_guardia_id || null,
        is_active: form.is_active,
      },
    })
    router.push(`/sigarh/mantenimiento/horarios-guardia?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, tipos] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/horarios-guardia/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/tipos-guardia').catch(() => []),
    ])
    form.nombre = data.nombre
    form.hora_inicio = data.hora_inicio
    form.hora_fin = data.hora_fin
    form.horas_totales = data.horas_totales ?? null
    form.tipo_guardia_id = data.tipo_guardia_id || ''
    form.is_active = data.is_active
    tiposGuardia.value = tipos
  } catch (e: any) { error.value = 'No se pudo cargar el horario' }
  finally { loading.value = false }
})
</script>
