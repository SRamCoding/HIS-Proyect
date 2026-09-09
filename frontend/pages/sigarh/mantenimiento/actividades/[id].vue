<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/actividades?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Actividades</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Actividad</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--orange-soft)">
            <UIcon name="i-heroicons-bolt" class="w-6 h-6" style="color: var(--orange)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Actividad' }}</h1>
            <p class="page-subtitle">Actualiza los datos de la actividad</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--orange)" />
      </div>

      <template v-else>
        <SFormCard title="Datos de la Actividad" subtitle="Actualiza los datos de la actividad"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--orange-soft)" icon-color="var(--orange)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-bolt" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Docencia, Consulta Externa" />
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
            <label class="form-label">Tipo de Actividad</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-list-bullet" class="input-icon" />
              <select v-model="form.tipo_actividad_id" class="input-clinical">
                <option value="">Sin tipo</option>
                <option v-for="t in tiposActividad" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Requiere Consultorio</label>
            <div class="status-toggle">
              <span class="toggle-label" style="color: var(--ink-soft); font-size: 0.8125rem;">Actívalo si la actividad se atiende en un consultorio (los días se configuran en Consultorios). Déjalo apagado para Guardia, Retén o Sin Actividad.</span>
              <button type="button" @click="form.requiere_consultorio = !form.requiere_consultorio" class="toggle-switch" :class="{ 'toggle-active': form.requiere_consultorio }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Actividad Activa</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre"
            :codigo="form.codigo"
            :extra="tipoNombre"
            :active="form.is_active"
            icon="i-heroicons-bolt"
            icon-color="var(--orange)"
            icon-bg="var(--orange-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/actividades?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Las actividades definen qué hace el personal en su rol de turno', 'El tipo de actividad las agrupa por categoria', 'Requiere Consultorio: los días se toman del módulo Consultorios', 'Las actividades inactivas no se pueden asignar']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Codigo', value: form.codigo, mono: true },
        { label: 'Tipo', value: tipoNombre },
        { divider: true },
        { label: 'Requiere Consultorio', slot: 'consultorio' },
        { label: 'Estado', slot: 'estado' },
      ]">
        <template #consultorio>{{ form.requiere_consultorio ? 'Si' : 'No' }}</template>
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Usa nombres claros que identifiquen la actividad tal como aparecerá en la programación de roles." />
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
const tiposActividad = ref<any[]>([])
const form = reactive({ nombre: '', codigo: '', tipo_actividad_id: '', requiere_consultorio: false, is_active: true })

const tipoNombre = computed(() => tiposActividad.value.find(t => t.id === form.tipo_actividad_id)?.nombre || '')

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/actividades/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        codigo: form.codigo || null,
        tipo_actividad_id: form.tipo_actividad_id || null,
        requiere_consultorio: form.requiere_consultorio,
        is_active: form.is_active,
      },
    })
    router.push(`/sigarh/mantenimiento/actividades?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, tipos] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/actividades/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/tipos-actividad').catch(() => []),
    ])
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.tipo_actividad_id = data.tipo_actividad_id || ''
    form.requiere_consultorio = data.requiere_consultorio ?? false
    form.is_active = data.is_active
    tiposActividad.value = tipos
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>
