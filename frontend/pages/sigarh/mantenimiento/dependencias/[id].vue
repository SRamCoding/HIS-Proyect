<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/dependencias?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Dependencias</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Dependencia</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-rectangle-group" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Dependencia' }}</h1>
            <p class="page-subtitle">Actualiza los datos de la dependencia</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>

      <template v-else>
        <SFormCard title="Datos de la Dependencia" subtitle="Actualiza los datos de la dependencia"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-rectangle-group" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Unidad de Recursos Humanos" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Codigo</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-barcode" class="input-icon" />
              <input v-model="form.codigo" class="input-clinical font-mono-data" placeholder="Ej: DEP-001" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Clasificacion</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-tag" class="input-icon" />
              <select v-model="form.clasificacion" class="input-clinical">
                <option value="administrativa">Administrativa</option>
                <option value="asistencial">Asistencial</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Departamento</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-building-office-2" class="input-icon" />
              <select v-model="form.departamento_id" class="input-clinical" @change="form.servicio_id = ''">
                <option value="">Sin departamento</option>
                <option v-for="d in departamentos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Servicio</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-squares-2x2" class="input-icon" />
              <select v-model="form.servicio_id" class="input-clinical" :disabled="!form.departamento_id">
                <option value="">Sin servicio</option>
                <option v-for="s in serviciosFiltrados" :key="s.id" :value="s.id">{{ s.nombre }}</option>
              </select>
            </div>
            <p class="field-hint">Selecciona primero un departamento</p>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Dependencia Activa</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre"
            :codigo="form.codigo"
            :extra="departamentoNombre"
            :active="form.is_active"
            icon="i-heroicons-rectangle-group"
            icon-color="var(--teal)"
            icon-bg="var(--teal-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/dependencias?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Las dependencias organizan las unidades del hospital', 'Se clasifican en administrativas y asistenciales', 'Pueden asociarse a un departamento y a un servicio', 'Las dependencias inactivas no se pueden asignar']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Codigo', value: form.codigo, mono: true },
        { label: 'Clasificacion', value: form.clasificacion },
        { label: 'Departamento', value: departamentoNombre },
        { label: 'Servicio', value: servicioNombre },
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
      <SWidgetTip text="Asocia la dependencia a su departamento y servicio para reflejar la estructura organizativa real." />
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
const departamentos = ref<any[]>([])
const servicios = ref<any[]>([])
const form = reactive({ nombre: '', codigo: '', clasificacion: 'administrativa', departamento_id: '', servicio_id: '', is_active: true })

const serviciosFiltrados = computed(() => servicios.value.filter(s => s.departamento_id === form.departamento_id))
const departamentoNombre = computed(() => departamentos.value.find(d => d.id === form.departamento_id)?.nombre || '')
const servicioNombre = computed(() => servicios.value.find(s => s.id === form.servicio_id)?.nombre || '')

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/dependencias/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        codigo: form.codigo || null,
        clasificacion: form.clasificacion,
        departamento_id: form.departamento_id || null,
        servicio_id: form.servicio_id || null,
        is_active: form.is_active,
      },
    })
    router.push(`/sigarh/mantenimiento/dependencias?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, deps, servs] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/dependencias/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/departamentos'),
      api<any[]>('/sigarh/mantenimiento/servicios'),
    ])
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.clasificacion = data.clasificacion || 'administrativa'
    form.departamento_id = data.departamento_id || ''
    form.servicio_id = data.servicio_id || ''
    form.is_active = data.is_active
    departamentos.value = deps
    servicios.value = servs
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>
