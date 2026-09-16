<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/infraestructura/consultorios?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Consultorios</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Consultorio</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)">
            <UIcon name="i-heroicons-building-office-2" class="w-6 h-6" style="color: var(--navy)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Consultorio' }}</h1>
            <p class="page-subtitle">Actualiza los datos del consultorio</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" />
      </div>

      <template v-else>
        <SFormCard title="Datos del Consultorio" subtitle="Actualiza los datos del consultorio"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre del consultorio <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-building-office-2" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" maxlength="100" placeholder="Ej: Consultorio 5" />
            </div>
            <p class="field-hint">Máximo 100 caracteres</p>
          </div>

          <div class="form-group">
            <label class="form-label">Especialidad fija</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-academic-cap" class="input-icon" />
              <select v-model="form.especialidad_id" class="input-clinical">
                <option value="">Uso general (sin especialidad)</option>
                <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Piso</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-building-office" class="input-icon" />
              <select v-model="form.piso_id" class="input-clinical">
                <option value="">Sin piso</option>
                <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Capacidad de sala <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-users" class="input-icon" />
              <input v-model.number="form.capacidad" type="number" min="1" class="input-clinical font-mono-data" @input="form.capacidad = Math.max(1, Math.floor(form.capacidad || 1))" />
            </div>
            <p class="field-hint">Pacientes que caben físicamente; no define los cupos de citas</p>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Consultorio Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Equipamiento</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-wrench" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea v-model="form.equipamiento" class="input-clinical" rows="2" maxlength="255" placeholder="Describe los equipos disponibles (máx. 255)" />
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre"
            :extra="especialidadNombre || 'Uso general'"
            :codigo="pisoNombre"
            :active="form.is_active"
            icon="i-heroicons-building-office-2"
            icon-color="var(--navy)"
            icon-bg="var(--navy-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/infraestructura/consultorios?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['El consultorio se ubica en un piso y puede fijar una especialidad', 'La especialidad filtra los médicos asignables', 'La capacidad es física, no equivale a los cupos de citas', 'La asignación de médicos y turnos se hace en Programación Médica']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Especialidad', value: especialidadNombre || 'Uso general' },
        { label: 'Piso', value: pisoNombre },
        { label: 'Capacidad', value: String(form.capacidad || 1), mono: true },
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
      <SWidgetTip text="Fija una especialidad si el consultorio es de una sola disciplina: así el selector de médicos en Programación Médica mostrará solo a los pertinentes." />
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
const especialidades = ref<any[]>([])
const pisos = ref<any[]>([])
const form = reactive({ nombre: '', especialidad_id: '', piso_id: '', capacidad: 1, equipamiento: '', is_active: true })

const especialidadNombre = computed(() => especialidades.value.find(e => e.id === form.especialidad_id)?.nombre || '')
const pisoNombre = computed(() => pisos.value.find(p => p.id === form.piso_id)?.nombre || '')

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre del consultorio es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/infraestructura/consultorios/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        especialidad_id: form.especialidad_id || null,
        piso_id: form.piso_id || null,
        capacidad: form.capacidad || 1,
        equipamiento: form.equipamiento || null,
        is_active: form.is_active,
      },
    })
    router.push(`/sigarh/infraestructura/consultorios?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, esp, ps] = await Promise.all([
      api<any>(`/sigarh/infraestructura/consultorios/${id.value}`),
      api<any[]>('/sigarh/rrhh/especialidades?active_only=true').catch(() => []),
      api<any[]>('/sigarh/infraestructura-hosp/pisos').catch(() => []),
    ])
    form.nombre = data.nombre
    form.especialidad_id = data.especialidad_id || ''
    form.piso_id = data.piso_id || ''
    form.capacidad = data.capacidad ?? 1
    form.equipamiento = data.equipamiento || ''
    form.is_active = data.is_active
    especialidades.value = esp
    pisos.value = ps
  } catch { error.value = 'No se pudo cargar el consultorio' }
  finally { loading.value = false }
})
</script>
