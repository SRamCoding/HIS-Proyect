<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/departamentos?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Departamentos</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Departamento</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)">
            <UIcon name="i-heroicons-building-office-2" class="w-6 h-6" style="color: var(--navy)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Departamento' }}</h1>
            <p class="page-subtitle">Actualiza los datos del departamento</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" />
      </div>

      <template v-else>
        <SFormCard
          title="Datos del Departamento"
          subtitle="Actualiza los datos del departamento"
          icon="i-heroicons-cog-6-tooth"
          icon-bg="var(--navy-soft)"
          icon-color="var(--navy)"
          :error="error"
        >
          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-building-office-2" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Medicina Interna" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Codigo</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-barcode" class="input-icon" />
              <input v-model="form.codigo" class="input-clinical font-mono-data" placeholder="Ej: MED-INT" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Departamento Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Descripcion</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea v-model="form.descripcion" class="input-clinical" rows="3" placeholder="Descripcion del departamento..." />
            </div>
          </div>

          <template #actions>
            <SFormActions
              :saving="saving"
              save-text="Guardar Cambios"
              saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/departamentos?tenant=${tenantId}`"
              @save="handleSave"
            />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="[
        'Los departamentos organizan las areas del hospital',
        'Se utilizan para agrupar servicios y personal',
        'El codigo es de referencia interna',
        'Los departamentos inactivos no se pueden asignar',
      ]" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Codigo', value: form.codigo, mono: true },
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
      <SWidgetTip text="Define nombres claros que identifiquen el area del hospital que representa el departamento." />
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
const form = reactive({ nombre: '', codigo: '', descripcion: '', is_active: true })

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/departamentos/${id.value}`, { method: 'PATCH', body: { ...form } })
    router.push(`/sigarh/mantenimiento/departamentos?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const data = await api<any>(`/sigarh/mantenimiento/departamentos/${id.value}`)
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.descripcion = data.descripcion || ''
    form.is_active = data.is_active
  } catch (e: any) { error.value = 'No se pudo cargar el departamento' }
  finally { loading.value = false }
})
</script>
