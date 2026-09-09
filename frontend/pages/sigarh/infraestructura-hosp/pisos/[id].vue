<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/infraestructura-hosp/pisos?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Pisos</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Piso</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)">
            <UIcon name="i-heroicons-building-office-2" class="w-6 h-6" style="color: var(--navy)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Piso' }}</h1>
            <p class="page-subtitle">Actualiza los datos del piso</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" />
      </div>

      <template v-else>
        <SFormCard title="Datos del Piso" subtitle="Actualiza los datos del piso"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre del piso <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-building-office-2" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" maxlength="100" placeholder="Ej: Segundo piso, Sótano" />
            </div>
            <p class="field-hint">Máximo 100 caracteres</p>
          </div>

          <div class="form-group">
            <label class="form-label">Orden de visualización</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-bars-arrow-down" class="input-icon" />
              <input v-model.number="form.orden" type="number" min="0" class="input-clinical font-mono-data" placeholder="0" @input="form.orden = Math.max(0, Math.floor(form.orden || 0))" />
            </div>
            <p class="field-hint">Posición en los listados (no es el número físico del piso)</p>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Piso Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Descripcion</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea v-model="form.descripcion" class="input-clinical" rows="3" placeholder="Ubicación o características del piso..." />
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre"
            :extra="`Orden ${form.orden ?? 0}`"
            :active="form.is_active"
            icon="i-heroicons-building-office-2"
            icon-color="var(--navy)"
            icon-bg="var(--navy-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/infraestructura-hosp/pisos?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Los pisos representan los niveles físicos del hospital', 'El orden define la posición en los selectores, no el número real', 'Luego se le asignan servicios desde Mantenimiento', 'Las salas quedan vinculadas al piso a través de esos servicios']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Orden', value: String(form.orden ?? 0), mono: true },
        { label: 'Servicios', value: String(stats.total_servicios) },
        { label: 'Salas', value: String(stats.total_salas) },
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
      <SWidgetTip text="Un piso con servicios o salas asociados no se puede eliminar: primero reasigna o elimina esos registros." />
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
const form = reactive({ nombre: '', orden: 0, descripcion: '', is_active: true })
const stats = reactive({ total_servicios: 0, total_salas: 0 })

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre del piso es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/infraestructura-hosp/pisos/${id.value}`, {
      method: 'PATCH',
      body: { nombre: form.nombre, orden: form.orden || 0, descripcion: form.descripcion || null, is_active: form.is_active },
    })
    router.push(`/sigarh/infraestructura-hosp/pisos?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const data = await api<any>(`/sigarh/infraestructura-hosp/pisos/${id.value}`)
    form.nombre = data.nombre
    form.orden = data.orden ?? 0
    form.descripcion = data.descripcion || ''
    form.is_active = data.is_active
    stats.total_servicios = data.total_servicios ?? 0
    stats.total_salas = data.total_salas ?? 0
  } catch { error.value = 'No se pudo cargar el piso' }
  finally { loading.value = false }
})
</script>
