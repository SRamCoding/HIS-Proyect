<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/tipos-actividad?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Tipos de Actividad</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Nuevo Tipo</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--orange-soft)">
            <UIcon name="i-heroicons-list-bullet" class="w-6 h-6" style="color: var(--orange)" />
          </div>
          <div>
            <h1 class="page-title">Crear Tipo de Actividad</h1>
            <p class="page-subtitle">Define un nuevo tipo de actividad complementaria</p>
          </div>
        </div>
      </div>

      <SFormCard title="Datos del Tipo" subtitle="Ingresa los datos del nuevo tipo de actividad"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--orange-soft)" icon-color="var(--orange)" :error="error">

        <div class="form-group full-width">
          <label class="form-label">Nombre <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-list-bullet" class="input-icon" />
            <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Actividad Complementaria, Formacion Continua" @focus="error = ''" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Codigo</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-barcode" class="input-icon" />
            <input v-model="form.codigo" class="input-clinical font-mono-data" placeholder="Ej: ACT-001" />
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

        <SFormPreview
          :nombre="form.nombre"
          :codigo="form.codigo"
          :active="form.is_active"
          icon="i-heroicons-list-bullet"
          icon-color="var(--orange)"
          icon-bg="var(--orange-soft)"
        />

        <template #actions>
          <SFormActions :saving="saving" save-text="Crear Tipo" saving-text="Creando..."
            :cancel-to="`/sigarh/mantenimiento/tipos-actividad?tenant=${tenantId}`"
            :show-create-another="true" @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Los tipos de actividad clasifican actividades complementarias', 'Se utilizan para categorizar registros de actividades', 'El codigo interno ayuda a identificar rapidamente', 'Los tipos inactivos no se pueden asignar']" />
      <SWidgetSummary :items="[{ label: 'Nombre', value: form.nombre }, { label: 'Codigo', value: form.codigo, mono: true }, { divider: true }, { label: 'Estado', slot: 'estado' }]">
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Define nombres claros que describan el proposito de la actividad para facilitar su identificacion en el sistema." />
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
const form = reactive({ nombre: '', codigo: '', is_active: true })

const handleCreate = async (createAnother: boolean) => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/tipos-actividad', {
      method: 'POST',
      body: { nombre: form.nombre, codigo: form.codigo || null, is_active: form.is_active },
    })
    if (createAnother) { Object.assign(form, { nombre: '', codigo: '', is_active: true }) }
    else { router.push(`/sigarh/mantenimiento/tipos-actividad?tenant=${tenantId.value}`) }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear' }
  finally { saving.value = false }
}
</script>
