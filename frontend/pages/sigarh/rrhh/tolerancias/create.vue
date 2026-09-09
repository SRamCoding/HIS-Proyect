<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const dependencias = ref<any[]>([])
const grupos = ref<any[]>([])
const form = reactive({ nombre: '', dependencia_id: '', grupo_ocupacional_id: '', minutos_tolerancia: 0, minutos_tolerancia_dia: 0, is_active: true })

const depNombre = computed(() => dependencias.value.find(d => d.id === form.dependencia_id)?.nombre || '—')
const grpNombre = computed(() => grupos.value.find(g => g.id === form.grupo_ocupacional_id)?.nombre || '—')

const handleCreate = async (otro: boolean) => {
  if (!form.dependencia_id) { error.value = 'La dependencia es requerida'; return }
  if (!form.grupo_ocupacional_id) { error.value = 'El grupo ocupacional es requerido'; return }
  saving.value = true; error.value = ''
  try {
    await api('/sigarh/rrhh/tolerancias', { method: 'POST', body: {
      nombre: form.nombre || null,
      dependencia_id: form.dependencia_id,
      grupo_ocupacional_id: form.grupo_ocupacional_id,
      minutos_tolerancia: form.minutos_tolerancia || 0,
      minutos_tolerancia_dia: form.minutos_tolerancia_dia || 0,
      is_active: form.is_active,
    } })
    if (otro) Object.assign(form, { nombre: '', dependencia_id: '', grupo_ocupacional_id: '', minutos_tolerancia: 0, minutos_tolerancia_dia: 0, is_active: true })
    else router.push(`/sigarh/rrhh/tolerancias?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo crear la tolerancia') }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const [d, g] = await Promise.all([
      api<any[]>('/sigarh/mantenimiento/dependencias'),
      api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
    ])
    dependencias.value = d.filter((x: any) => x.is_active !== false)
    grupos.value = g.filter((x: any) => x.is_active !== false)
  } catch (e: any) { error.value = apiErr(e, 'Error al cargar catálogos') }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/tolerancias?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Tolerancias</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Nueva</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-clock" class="w-6 h-6" style="color: var(--navy)" /></div>
          <div><h1 class="page-title">Crear Tolerancia</h1><p class="page-subtitle">Define el margen de tardanza para una dependencia y grupo</p></div>
        </div>
      </div>

      <SFormCard title="Ámbito de la Regla" subtitle="A qué dependencia y grupo ocupacional aplica"
        icon="i-heroicons-building-office-2" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">
        <div class="form-group">
          <label class="form-label">Dependencia <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-building-office" class="input-icon" />
            <select v-model="form.dependencia_id" class="input-clinical" @change="error = ''">
              <option value="">Seleccione una dependencia</option>
              <option v-for="d in dependencias" :key="d.id" :value="d.id">{{ d.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Grupo ocupacional <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user-group" class="input-icon" />
            <select v-model="form.grupo_ocupacional_id" class="input-clinical" @change="error = ''">
              <option value="">Seleccione un grupo</option>
              <option v-for="g in grupos" :key="g.id" :value="g.id">{{ g.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Nombre de la regla</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-tag" class="input-icon" /><input v-model="form.nombre" class="input-clinical" maxlength="255" placeholder="Opcional. Ej: Tolerancia médicos consulta externa" /></div>
        </div>
      </SFormCard>

      <SFormCard title="Márgenes de Tolerancia" subtitle="Minutos que no cuentan como tardanza"
        icon="i-heroicons-clock" icon-bg="var(--teal-soft)" icon-color="var(--teal)">
        <div class="form-group">
          <label class="form-label">Tolerancia de entrada (min)</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-arrow-right-on-rectangle" class="input-icon" /><input v-model.number="form.minutos_tolerancia" type="number" min="0" class="input-clinical font-mono-data" /></div>
          <p class="field-hint">Margen tras la hora de entrada programada antes de marcar tardanza</p>
        </div>
        <div class="form-group">
          <label class="form-label">Tolerancia diaria acumulada (min)</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model.number="form.minutos_tolerancia_dia" type="number" min="0" class="input-clinical font-mono-data" /></div>
          <p class="field-hint">Tope de minutos tolerados en el día para el grupo</p>
        </div>
        <div class="form-group">
          <label class="form-label">Estado</label>
          <div class="status-toggle"><span class="toggle-label">Regla Activa</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }"><span class="toggle-slider" /></button>
          </div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Crear" saving-text="Creando..."
            :cancel-to="`/sigarh/rrhh/tolerancias?tenant=${tenantId}`" :show-create-another="true"
            @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetInfo :items="['El Registro de Asistencia usa esta regla para calcular la tardanza', 'Tardanza = (entrada real − programada) − tolerancia de entrada', 'Si no hay regla para el grupo, la tolerancia es 0', 'Debe existir una sola regla activa por dependencia + grupo']" />
      <SWidgetSummary :items="[{ label: 'Dependencia', value: depNombre }, { label: 'Grupo', value: grpNombre }, { divider: true }, { label: 'Tol. entrada', value: form.minutos_tolerancia + ' min' }, { label: 'Tol. diaria', value: form.minutos_tolerancia_dia + ' min' }]" />
      <SWidgetTip text="Mantén valores realistas (5–15 min). Una tolerancia muy alta desvirtúa el control de puntualidad." />
    </template>
  </SFormLayout>
</template>
