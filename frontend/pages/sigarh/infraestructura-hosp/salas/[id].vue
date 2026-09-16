<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/infraestructura-hosp/salas?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Salas</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Sala</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-squares-plus" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Sala' }}</h1>
            <p class="page-subtitle">Actualiza los datos de la sala</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>

      <template v-else>
        <SFormCard title="Datos de la Sala" subtitle="Actualiza los datos de la sala"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">

          <div class="form-group">
            <label class="form-label">Piso</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-building-office-2" class="input-icon" />
              <select v-model="form.piso_id" class="input-clinical" @change="form.servicio_id = ''">
                <option value="">Todos los pisos</option>
                <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Servicio <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-squares-2x2" class="input-icon" />
              <select v-model="form.servicio_id" class="input-clinical" @change="onServicio">
                <option value="">Seleccione un servicio</option>
                <option v-for="s in serviciosFiltrados" :key="s.id" :value="s.id">{{ s.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Nombre de la sala <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-squares-plus" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" maxlength="100" placeholder="Ej: Habitación 301" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Codigo</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-barcode" class="input-icon" />
              <input v-model="form.codigo" class="input-clinical font-mono-data" maxlength="30" placeholder="Ej: H301" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Capacidad <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-rectangle-stack" class="input-icon" />
              <input v-model.number="form.capacidad" type="number" min="1" class="input-clinical font-mono-data" @input="form.capacidad = Math.max(1, Math.floor(form.capacidad || 1))" />
            </div>
            <p class="field-hint">Actualmente hay {{ stats.total_camas }} cama(s) registrada(s)</p>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Sala Activa</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre"
            :codigo="form.codigo"
            :extra="servicioNombre"
            :active="form.is_active"
            icon="i-heroicons-squares-plus"
            icon-color="var(--teal)"
            icon-bg="var(--teal-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/infraestructura-hosp/salas?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['La sala pertenece a un servicio; el piso se obtiene del servicio', 'La capacidad determina cuántas camas puede generar la acción automática', 'Desde el listado puedes generar las camas faltantes', 'Una sala con camas ocupadas no se puede eliminar']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Codigo', value: form.codigo, mono: true },
        { label: 'Servicio', value: servicioNombre },
        { divider: true },
        { label: 'Camas', value: `${stats.total_camas}/${form.capacidad || 1}` },
        { label: 'Disponibles', value: String(stats.camas_disponibles) },
        { label: 'Ocupadas', value: String(stats.camas_ocupadas) },
        { label: 'Estado', slot: 'estado' },
      ]">
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Para crear las camas de esta sala usa la acción 'Generar camas' desde el listado de Salas." />
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
const pisos = ref<any[]>([])
const servicios = ref<any[]>([])
const form = reactive({ piso_id: '', servicio_id: '', nombre: '', codigo: '', capacidad: 1, is_active: true })
const stats = reactive({ total_camas: 0, camas_disponibles: 0, camas_ocupadas: 0 })

const serviciosFiltrados = computed(() => form.piso_id ? servicios.value.filter(s => s.piso_id === form.piso_id || !s.piso_id) : servicios.value)
const servicioNombre = computed(() => servicios.value.find(s => s.id === form.servicio_id)?.nombre || '')

const onServicio = () => {
  const s = servicios.value.find(x => x.id === form.servicio_id)
  if (s?.piso_id) form.piso_id = s.piso_id
}

const handleSave = async () => {
  if (!form.servicio_id) { error.value = 'El servicio es requerido'; return }
  if (!form.nombre.trim()) { error.value = 'El nombre de la sala es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/infraestructura-hosp/salas/${id.value}`, {
      method: 'PATCH',
      body: {
        piso_id: form.piso_id || null,
        servicio_id: form.servicio_id || null,
        nombre: form.nombre,
        codigo: form.codigo || null,
        capacidad: form.capacidad || 1,
        is_active: form.is_active,
      },
    })
    router.push(`/sigarh/infraestructura-hosp/salas?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, ps, ss] = await Promise.all([
      api<any>(`/sigarh/infraestructura-hosp/salas/${id.value}`),
      api<any[]>('/sigarh/infraestructura-hosp/pisos').catch(() => []),
      api<any[]>('/sigarh/mantenimiento/servicios').catch(() => []),
    ])
    form.piso_id = data.piso_id || ''
    form.servicio_id = data.servicio_id || ''
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.capacidad = data.capacidad ?? 1
    form.is_active = data.is_active
    stats.total_camas = data.total_camas ?? 0
    stats.camas_disponibles = data.camas_disponibles ?? 0
    stats.camas_ocupadas = data.camas_ocupadas ?? 0
    pisos.value = ps
    servicios.value = ss
  } catch { error.value = 'No se pudo cargar la sala' }
  finally { loading.value = false }
})
</script>
