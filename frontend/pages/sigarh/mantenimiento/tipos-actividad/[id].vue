<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/tipos-actividad?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Tipos de Actividad</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Tipo</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--orange-soft)">
            <UIcon name="i-heroicons-list-bullet" class="w-6 h-6" style="color: var(--orange)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Tipo de Actividad' }}</h1>
            <p class="page-subtitle">Actualiza los datos del tipo de actividad</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--orange)" />
      </div>

      <template v-else>
        <SFormCard title="Datos del Tipo" subtitle="Actualiza los datos del tipo de actividad"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--orange-soft)" icon-color="var(--orange)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-list-bullet" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Actividad Complementaria, Formacion Continua" />
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
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/tipos-actividad?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
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
const id = computed(() => route.params.id as string)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const form = reactive({ nombre: '', codigo: '', is_active: true })

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/tipos-actividad/${id.value}`, {
      method: 'PATCH',
      body: { nombre: form.nombre, codigo: form.codigo || null, is_active: form.is_active },
    })
    router.push(`/sigarh/mantenimiento/tipos-actividad?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const data = await api<any>(`/sigarh/mantenimiento/tipos-actividad/${id.value}`)
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.is_active = data.is_active
  } catch (e: any) { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>
