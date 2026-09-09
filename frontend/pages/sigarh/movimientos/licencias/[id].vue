<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/movimientos/licencias?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Licencias</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Licencia</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-document-text" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">{{ empleadoNombre || 'Editar Licencia' }}</h1>
            <p class="page-subtitle">Actualiza los datos del tramite de licencia</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>

      <template v-else>
        <SFormCard title="Datos de la Licencia" subtitle="Actualiza la informacion del tramite"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Empleado <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-user" class="input-icon" />
              <select v-model="form.empleado_id" class="input-clinical">
                <option value="">Seleccione un empleado</option>
                <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre_completo || e.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Motivo</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-flag" class="input-icon" />
              <select v-model="form.motivo_id" class="input-clinical">
                <option value="">Sin motivo especifico</option>
                <option v-for="m in motivos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-flag" class="input-icon" />
              <select v-model="form.estado" class="input-clinical">
                <option value="pendiente">Pendiente</option>
                <option value="aprobado">Aprobado</option>
                <option value="rechazado">Rechazado</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Fecha de Tramite</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-calendar" class="input-icon" />
              <input v-model="form.fecha_tramite" type="date" class="input-clinical" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Dias</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-calendar-days" class="input-icon" />
              <input v-model.number="form.dias" type="number" min="0" class="input-clinical font-mono-data" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Fecha de Inicio <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-calendar" class="input-icon" />
              <input v-model="form.fecha_inicio" type="date" class="input-clinical" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Fecha de Fin <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-calendar" class="input-icon" />
              <input v-model="form.fecha_fin" type="date" class="input-clinical" />
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Documento (URL)</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-paper-clip" class="input-icon" />
              <input v-model="form.documento_url" class="input-clinical" placeholder="https://..." />
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Detalle</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea v-model="form.detalle" class="input-clinical" rows="3" placeholder="Detalle del motivo de la licencia..." />
            </div>
          </div>

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/movimientos/licencias?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Las licencias registran ausencias tramitadas del personal', 'Los dias se calculan segun fecha de inicio y fin', 'El estado controla la aprobacion del tramite', 'Adjunta el documento de respaldo si esta disponible']" />
      <SWidgetSummary :items="[
        { label: 'Empleado', value: empleadoNombre },
        { label: 'Motivo', value: motivoNombre || 'Sin motivo' },
        { label: 'Tramite', value: form.fecha_tramite, mono: true },
        { divider: true },
        { label: 'Inicio', value: form.fecha_inicio, mono: true },
        { label: 'Fin', value: form.fecha_fin, mono: true },
        { label: 'Dias', value: form.dias != null ? String(form.dias) : '' },
        { label: 'Estado', slot: 'estado' },
      ]">
        <template #estado>
          <span class="status-badge-mini" :class="estadoClase">
            <span class="status-dot-mini" :class="estadoDot" />
            {{ estadoLabel }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Verifica las fechas y el estado antes de guardar: una licencia aprobada afecta la asistencia del empleado." />
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
const empleados = ref<any[]>([])
const motivos = ref<any[]>([])

const form = reactive({
  empleado_id: '',
  motivo_id: '',
  fecha_tramite: '',
  fecha_inicio: '',
  fecha_fin: '',
  dias: null as number | null,
  documento_url: '',
  detalle: '',
  estado: 'pendiente',
})

const empleadoNombre = computed(() => empleados.value.find(e => e.id === form.empleado_id)?.nombre_completo || '')
const motivoNombre = computed(() => motivos.value.find(m => m.id === form.motivo_id)?.nombre || '')
const estadoLabel = computed(() => ({ pendiente: 'Pendiente', aprobado: 'Aprobado', rechazado: 'Rechazado' }[form.estado] || form.estado))
const estadoClase = computed(() => form.estado === 'aprobado' ? 'status-active-mini' : 'status-inactive-mini')
const estadoDot = computed(() => form.estado === 'aprobado' ? 'dot-active-mini' : 'dot-inactive-mini')

watch([() => form.fecha_inicio, () => form.fecha_fin], ([ini, fin]) => {
  if (ini && fin) {
    const diff = new Date(fin).getTime() - new Date(ini).getTime()
    form.dias = Math.max(0, Math.round(diff / 86400000) + 1)
  }
})

const handleSave = async () => {
  if (!form.empleado_id) { error.value = 'El empleado es requerido'; return }
  if (!form.fecha_inicio || !form.fecha_fin) { error.value = 'Las fechas de inicio y fin son requeridas'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/movimientos/licencias/${id.value}`, {
      method: 'PATCH',
      body: {
        empleado_id: form.empleado_id,
        motivo_id: form.motivo_id || null,
        fecha_tramite: form.fecha_tramite || null,
        fecha_inicio: form.fecha_inicio,
        fecha_fin: form.fecha_fin,
        dias: form.dias ?? null,
        documento_url: form.documento_url || null,
        detalle: form.detalle || null,
        estado: form.estado,
      },
    })
    router.push(`/sigarh/movimientos/licencias?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar la licencia' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, emp, mot] = await Promise.all([
      api<any>(`/sigarh/movimientos/licencias/${id.value}`),
      api<any[]>('/sigarh/rrhh/empleados').catch(() => []),
      api<any[]>('/sigarh/mantenimiento/motivos-justificacion').catch(() => []),
    ])
    form.empleado_id = data.empleado_id || ''
    form.motivo_id = data.motivo_id || ''
    form.fecha_tramite = data.fecha_tramite || ''
    form.fecha_inicio = data.fecha_inicio || ''
    form.fecha_fin = data.fecha_fin || ''
    form.dias = data.dias ?? null
    form.documento_url = data.documento_url || ''
    form.detalle = data.detalle || ''
    form.estado = data.estado || 'pendiente'
    empleados.value = emp
    motivos.value = mot
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar la licencia'
  } finally {
    loading.value = false
  }
})
</script>
