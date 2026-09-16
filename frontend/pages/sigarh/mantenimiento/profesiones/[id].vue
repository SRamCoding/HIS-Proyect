<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/profesiones?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Profesiones</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">{{ esBase ? 'Configurar Profesion' : 'Editar Profesion' }}</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-academic-cap" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Profesion' }}</h1>
            <p class="page-subtitle">{{ esBase ? 'Catalogo base: solo puedes activar o desactivar' : 'Actualiza los datos de la profesion' }}</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>

      <template v-else>
        <SFormCard title="Datos de la Profesion" subtitle="Actualiza los datos de la profesion"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">

          <div v-if="esBase" class="form-group full-width" style="background: var(--mist); border-radius: var(--radius); padding: 0.75rem 1rem; display: flex; gap: 0.5rem; align-items: flex-start">
            <UIcon name="i-heroicons-information-circle" class="w-4 h-4 shrink-0" style="color: var(--ink-soft); margin-top: 0.125rem" />
            <p style="font-size: 0.8125rem; color: var(--ink-soft); margin: 0">
              Esta profesion viene del catalogo base (D. Leg. 1153). Sus datos no se pueden editar; solo puedes activarla o desactivarla para este hospital.
            </p>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-academic-cap" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Ingeniero Biomedico" :disabled="esBase" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Codigo interno <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-barcode" class="input-icon" />
              <input v-model="form.codigo" class="input-clinical font-mono-data" placeholder="Ej: ING-BIO" maxlength="20" :disabled="esBase" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Grupo Ocupacional <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-user-group" class="input-icon" />
              <select v-model="form.grupo_ocupacional_id" class="input-clinical" :disabled="esBase">
                <option value="">Selecciona</option>
                <option v-for="g in grupos.filter(g => g.is_active || g.id === form.grupo_ocupacional_id)" :key="g.id" :value="g.id">{{ g.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Colegio Profesional</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-building-library" class="input-icon" />
              <input v-model="form.colegio_profesional" class="input-clinical" placeholder="Ej: Colegio Medico del Peru" maxlength="255" :disabled="esBase" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Categoria para Roles de Turno</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-tag" class="input-icon" />
              <select v-model="form.categoria_personal" class="input-clinical" :disabled="esBase">
                <option value="">Personal administrativo</option>
                <option value="medicos">Medicos</option>
                <option value="otros_profesionales">Otros profesionales de salud</option>
                <option value="tecnicos">Tecnicos y auxiliares</option>
              </select>
            </div>
          </div>

          <div class="form-group full-width">
            <div class="status-toggle">
              <span class="toggle-label">Profesion Activa</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre"
            :codigo="form.codigo"
            :extra="nombreGrupo(form.grupo_ocupacional_id)"
            :active="form.is_active"
            icon="i-heroicons-academic-cap"
            icon-color="var(--teal)"
            icon-bg="var(--teal-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/profesiones?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Base: profesiones del D. Leg. 1153, tecnicos y auxiliares asistenciales', 'La categoria para roles de turno es una configuracion operativa', 'No cambia la profesion real del trabajador', 'Las profesiones inactivas no se pueden asignar']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Codigo', value: form.codigo, mono: true },
        { label: 'Grupo', value: nombreGrupo(form.grupo_ocupacional_id) },
        { label: 'Colegio', value: form.colegio_profesional },
        { label: 'Origen', value: esBase ? 'Catalogo base' : 'Del hospital' },
        { divider: true },
        { label: 'Estado', slot: 'estado' },
      ]">
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activa' : 'Inactiva' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Desactivar una profesion no elimina el historial de empleados que ya la tienen asignada." />
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
const esBase = ref(false)
const grupos = ref<any[]>([])
const form = reactive({
  nombre: '', codigo: '', grupo_ocupacional_id: '', colegio_profesional: '', categoria_personal: '', is_active: true,
})

const nombreGrupo = (id: string) => grupos.value.find(g => g.id === id)?.nombre || ''

const handleSave = async () => {
  if (!esBase.value && !form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    const body = esBase.value
      ? { is_active: form.is_active }
      : {
          nombre: form.nombre, codigo: form.codigo, grupo_ocupacional_id: form.grupo_ocupacional_id,
          colegio_profesional: form.colegio_profesional || null, categoria_personal: form.categoria_personal || null,
          is_active: form.is_active,
        }
    await api(`/sigarh/mantenimiento/profesiones/${id.value}`, { method: 'PATCH', body })
    router.push(`/sigarh/mantenimiento/profesiones?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, gruposData] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/profesiones/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales?limit=500'),
    ])
    esBase.value = !!data.es_base
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.grupo_ocupacional_id = data.grupo_ocupacional_id
    form.colegio_profesional = data.colegio_profesional || ''
    form.categoria_personal = data.categoria_personal || ''
    form.is_active = data.is_active
    grupos.value = gruposData
  } catch (e: any) { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>
