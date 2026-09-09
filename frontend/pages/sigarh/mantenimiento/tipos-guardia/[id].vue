<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/tipos-guardia?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Tipos de Guardia</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Tipo</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-clock" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Tipo de Guardia' }}</h1>
            <p class="page-subtitle">Actualiza los datos del tipo de guardia</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>

      <template v-else>
        <SFormCard title="Datos del Tipo" subtitle="Actualiza los datos del tipo de guardia"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-clock" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Guardia Ordinaria, Guardia Especializada" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Codigo</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-barcode" class="input-icon" />
              <input v-model="form.codigo" class="input-clinical font-mono-data" placeholder="Ej: TG-001" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Horas</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-chart-bar" class="input-icon" />
              <input v-model.number="form.horas" type="number" min="0" step="1" class="input-clinical font-mono-data" placeholder="12" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Guardia Laborable</label>
            <div class="status-toggle">
              <span class="toggle-label" style="color: var(--ink-soft); font-size: 0.8125rem;">No laborable: vacaciones, descanso, etc.</span>
              <div class="flex items-center gap-2">
                <label class="flex items-center gap-1 text-sm cursor-pointer"><input type="radio" :value="true" v-model="form.es_laborable" /> SI</label>
                <label class="flex items-center gap-1 text-sm cursor-pointer"><input type="radio" :value="false" v-model="form.es_laborable" /> NO</label>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Requiere EPP</label>
            <div class="status-toggle">
              <span class="toggle-label" style="color: var(--ink-soft); font-size: 0.8125rem;">No requiere EPP: guardia remota, descanso, etc.</span>
              <div class="flex items-center gap-2">
                <label class="flex items-center gap-1 text-sm cursor-pointer"><input type="radio" :value="true" v-model="form.requiere_epp" /> SI</label>
                <label class="flex items-center gap-1 text-sm cursor-pointer"><input type="radio" :value="false" v-model="form.requiere_epp" /> NO</label>
              </div>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Tipo Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Descripcion</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea v-model="form.descripcion" class="input-clinical" rows="3" placeholder="Descripcion del tipo de guardia..." />
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre"
            :codigo="form.codigo"
            :extra="form.horas ? `${form.horas} h` : ''"
            :active="form.is_active"
            icon="i-heroicons-clock"
            icon-color="var(--teal)"
            icon-bg="var(--teal-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/tipos-guardia?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Clasifican las guardias segun su modalidad y duracion', 'Las horas definen la duracion estandar de la guardia', 'Marca si la guardia cuenta como tiempo laborable', 'Indica si el personal requiere EPP durante la guardia']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Codigo', value: form.codigo, mono: true },
        { label: 'Horas', value: form.horas ? String(form.horas) : '', mono: true },
        { divider: true },
        { label: 'Laborable', slot: 'laborable' },
        { label: 'Requiere EPP', slot: 'epp' },
        { label: 'Estado', slot: 'estado' },
      ]">
        <template #laborable>{{ form.es_laborable ? 'Si' : 'No' }}</template>
        <template #epp>{{ form.requiere_epp ? 'Si' : 'No' }}</template>
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Define nombres claros y una duracion en horas coherente con la jornada real de la guardia." />
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
const form = reactive({
  nombre: '',
  codigo: '',
  horas: null as number | null,
  descripcion: '',
  es_laborable: true,
  requiere_epp: false,
  is_active: true,
})

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/tipos-guardia/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        codigo: form.codigo || null,
        horas: form.horas || null,
        descripcion: form.descripcion || null,
        es_laborable: form.es_laborable,
        requiere_epp: form.requiere_epp,
        is_active: form.is_active,
      },
    })
    router.push(`/sigarh/mantenimiento/tipos-guardia?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const data = await api<any>(`/sigarh/mantenimiento/tipos-guardia/${id.value}`)
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.horas = data.horas ?? null
    form.descripcion = data.descripcion || ''
    form.es_laborable = data.es_laborable ?? true
    form.requiere_epp = data.requiere_epp ?? false
    form.is_active = data.is_active
  } catch (e: any) { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>
