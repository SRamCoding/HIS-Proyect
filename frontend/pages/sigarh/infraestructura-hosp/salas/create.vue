<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/infraestructura-hosp/salas?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Salas</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Nueva Sala</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-squares-plus" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">Crear Sala</h1>
            <p class="page-subtitle">Registra un ambiente y su capacidad de camas</p>
          </div>
        </div>
      </div>

      <SFormCard title="Datos de la Sala" subtitle="Ingresa los datos de la nueva sala"
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
          <p class="field-hint">Filtra los servicios por piso (auxiliar)</p>
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
          <p class="field-hint">Vincula la sala con el servicio responsable</p>
        </div>

        <div class="form-group full-width">
          <label class="form-label">Nombre de la sala <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-squares-plus" class="input-icon" />
            <input v-model="form.nombre" class="input-clinical" maxlength="100" placeholder="Ej: Habitación 301" @focus="error = ''" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Codigo</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-barcode" class="input-icon" />
            <input v-model="form.codigo" class="input-clinical font-mono-data" maxlength="30" placeholder="Ej: H301" />
          </div>
          <p class="field-hint">También sirve de prefijo al generar camas</p>
        </div>

        <div class="form-group">
          <label class="form-label">Capacidad <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-rectangle-stack" class="input-icon" />
            <input v-model.number="form.capacidad" type="number" min="1" class="input-clinical font-mono-data" @input="form.capacidad = Math.max(1, Math.floor(form.capacidad || 1))" />
          </div>
          <p class="field-hint">Número previsto de camas</p>
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
          <SFormActions :saving="saving" save-text="Crear Sala" saving-text="Creando..."
            :cancel-to="`/sigarh/infraestructura-hosp/salas?tenant=${tenantId}`"
            :show-create-another="true" @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['La sala pertenece a un servicio; el piso se obtiene del servicio', 'La capacidad determina cuántas camas puede generar la acción automática', 'Desde el listado puedes generar las camas faltantes', 'Una sala con camas ocupadas no se puede eliminar']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Codigo', value: form.codigo, mono: true },
        { label: 'Servicio', value: servicioNombre },
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
      <SWidgetTip text="Define un código corto y una capacidad realista: la generación automática crea las camas que falten para llegar a ese número." />
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
const pisos = ref<any[]>([])
const servicios = ref<any[]>([])
const form = reactive({ piso_id: '', servicio_id: '', nombre: '', codigo: '', capacidad: 1, is_active: true })

const serviciosFiltrados = computed(() => form.piso_id ? servicios.value.filter(s => s.piso_id === form.piso_id || !s.piso_id) : servicios.value)
const servicioNombre = computed(() => servicios.value.find(s => s.id === form.servicio_id)?.nombre || '')
const pisoNombre = computed(() => pisos.value.find(p => p.id === form.piso_id)?.nombre || '')

const onServicio = () => {
  const s = servicios.value.find(x => x.id === form.servicio_id)
  if (s?.piso_id) form.piso_id = s.piso_id
}

const handleCreate = async (createAnother: boolean) => {
  if (!form.servicio_id) { error.value = 'El servicio es requerido'; return }
  if (!form.nombre.trim()) { error.value = 'El nombre de la sala es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/infraestructura-hosp/salas', {
      method: 'POST',
      body: {
        piso_id: form.piso_id || null,
        servicio_id: form.servicio_id || null,
        nombre: form.nombre,
        codigo: form.codigo || null,
        capacidad: form.capacidad || 1,
        is_active: form.is_active,
      },
    })
    if (createAnother) { Object.assign(form, { piso_id: '', servicio_id: '', nombre: '', codigo: '', capacidad: 1, is_active: true }) }
    else { router.push(`/sigarh/infraestructura-hosp/salas?tenant=${tenantId.value}`) }
  } catch (e: any) { error.value = apiErr(e, 'No se pudo crear') }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [ps, ss] = await Promise.all([
      api<any[]>('/sigarh/infraestructura-hosp/pisos').catch(() => []),
      api<any[]>('/sigarh/mantenimiento/servicios').catch(() => []),
    ])
    pisos.value = ps
    servicios.value = ss
  } catch (e: any) { error.value = 'Error al cargar datos' }
})
</script>
