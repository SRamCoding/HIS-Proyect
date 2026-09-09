<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/tipos-trabajador?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Tipos de Trabajador</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Tipo</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--green-soft)">
            <UIcon name="i-heroicons-user-group" class="w-6 h-6" style="color: var(--green)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Tipo de Trabajador' }}</h1>
            <p class="page-subtitle">Actualiza los datos del tipo de trabajador</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--green)" />
      </div>

      <template v-else>
        <SFormCard title="Datos del Tipo" subtitle="Actualiza los datos del tipo de trabajador"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--green-soft)" icon-color="var(--green)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-user-group" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Nombrado, Contratado, CAS" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Codigo</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-barcode" class="input-icon" />
              <input v-model="form.codigo" class="input-clinical font-mono-data" placeholder="Ej: NOM" />
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
              <textarea v-model="form.descripcion" class="input-clinical" rows="3" placeholder="Descripcion del tipo..." />
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre"
            :codigo="form.codigo"
            :active="form.is_active"
            icon="i-heroicons-user-group"
            icon-color="var(--green)"
            icon-bg="var(--green-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/tipos-trabajador?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Clasifican al personal segun su modalidad de contratacion', 'Ej: Nombrado, Contratado, CAS, Locacion', 'Se usan en la ficha del empleado', 'Los tipos inactivos no se pueden asignar']" />
      <SWidgetSummary :items="[{ label: 'Nombre', value: form.nombre }, { label: 'Codigo', value: form.codigo, mono: true }, { divider: true }, { label: 'Estado', slot: 'estado' }]">
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Usa nombres cortos y claros que identifiquen la modalidad de contratacion." />
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
    await api(`/sigarh/mantenimiento/tipos-trabajador/${id.value}`, { method: 'PATCH', body: { ...form } })
    router.push(`/sigarh/mantenimiento/tipos-trabajador?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const data = await api<any>(`/sigarh/mantenimiento/tipos-trabajador/${id.value}`)
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.descripcion = data.descripcion || ''
    form.is_active = data.is_active
  } catch (e: any) { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>
