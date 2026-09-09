<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/tipos-guardia?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Tipos de Guardia</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Nuevo Tipo</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-clock" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">Crear Tipo de Guardia</h1>
            <p class="page-subtitle">Define un nuevo tipo de guardia para el hospital</p>
          </div>
        </div>
      </div>

      <SFormCard title="Datos del Tipo" subtitle="Ingresa los datos del nuevo tipo de guardia"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">

        <div class="form-group full-width">
          <label class="form-label">Nombre <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-clock" class="input-icon" />
            <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Guardia Ordinaria, Guardia Especializada" @focus="error = ''" />
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
          <SFormActions :saving="saving" save-text="Crear Tipo" saving-text="Creando..."
            :cancel-to="`/sigarh/mantenimiento/tipos-guardia?tenant=${tenantId}`"
            :show-create-another="true" @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
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

const buildBody = () => ({
  nombre: form.nombre,
  codigo: form.codigo || null,
  horas: form.horas || null,
  descripcion: form.descripcion || null,
  es_laborable: form.es_laborable,
  requiere_epp: form.requiere_epp,
  is_active: form.is_active,
})

const handleCreate = async (createAnother: boolean) => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/tipos-guardia', { method: 'POST', body: buildBody() })
    if (createAnother) {
      Object.assign(form, { nombre: '', codigo: '', horas: null, descripcion: '', es_laborable: true, requiere_epp: false, is_active: true })
    } else {
      router.push(`/sigarh/mantenimiento/tipos-guardia?tenant=${tenantId.value}`)
    }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear' }
  finally { saving.value = false }
}
</script>
