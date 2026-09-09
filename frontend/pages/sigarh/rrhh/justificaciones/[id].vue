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
const motivos = ref<any[]>([])
const info = reactive({ empleado_nombre: '', empleado_dni: '', empleado_regimen: '', empleado_cargo: '' })

const form = reactive({
  motivo_id: '', numero_documento: '', fecha_tramite: '',
  fecha_inicio: '', fecha_fin: '', descripcion: '', estado: 'pendiente',
})

const dias = computed(() => {
  if (!form.fecha_inicio || !form.fecha_fin) return 0
  const d = Math.ceil((new Date(form.fecha_fin).getTime() - new Date(form.fecha_inicio).getTime()) / 86400000) + 1
  return d > 0 ? d : 0
})

const revisadoPor = ref('')
const motivoRechazo = ref('')

const handleSave = async () => {
  if (!form.fecha_inicio || !form.fecha_fin) { error.value = 'Las fechas son requeridas'; return }
  if (new Date(form.fecha_fin) < new Date(form.fecha_inicio)) { error.value = 'La fecha de fin no puede ser anterior a la de inicio'; return }
  saving.value = true; error.value = ''
  try {
    await api(`/sigarh/rrhh/justificaciones/${id.value}`, { method: 'PATCH', body: {
      motivo_id: form.motivo_id || null,
      numero_documento: form.numero_documento || null,
      fecha_tramite: form.fecha_tramite || null,
      fecha_inicio: form.fecha_inicio,
      fecha_fin: form.fecha_fin,
      descripcion: form.descripcion || null,
    } })
    router.push(`/sigarh/rrhh/justificaciones?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}

const decidir = async (aprobar: boolean) => {
  if (!aprobar && !motivoRechazo.value.trim()) { error.value = 'Indica el motivo del rechazo'; return }
  saving.value = true; error.value = ''
  try {
    const ruta = aprobar ? 'aprobar' : 'rechazar'
    const d = await api<any>(`/sigarh/rrhh/justificaciones/${id.value}/${ruta}`, {
      method: 'POST', body: aprobar ? {} : { motivo_rechazo: motivoRechazo.value },
    })
    form.estado = d.estado
    revisadoPor.value = d.revisado_por || ''
    if (aprobar) router.push(`/sigarh/rrhh/justificaciones?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo procesar la decisión') }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const [m, d] = await Promise.all([api<any[]>('/sigarh/rrhh/motivos-justificacion'), api<any>(`/sigarh/rrhh/justificaciones/${id.value}`)])
    motivos.value = m
    form.motivo_id = d.motivo_id || ''
    form.numero_documento = d.numero_documento || ''
    form.fecha_tramite = d.fecha_tramite || ''
    form.fecha_inicio = d.fecha_inicio
    form.fecha_fin = d.fecha_fin
    form.descripcion = d.descripcion || ''
    form.estado = d.estado || 'pendiente'
    revisadoPor.value = d.revisado_por || ''
    motivoRechazo.value = d.motivo_rechazo || ''
    info.empleado_nombre = d.empleado_nombre || ''
    info.empleado_dni = d.empleado_dni || ''
    info.empleado_regimen = d.empleado_regimen || ''
    info.empleado_cargo = d.empleado_cargo || ''
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/justificaciones?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Justificaciones</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Editar</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-document-check" class="w-6 h-6" style="color: var(--teal)" /></div>
          <div><h1 class="page-title">{{ info.empleado_nombre || 'Editar Justificación' }}</h1><p class="page-subtitle">Revisa el sustento y define el estado de la solicitud</p></div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" /></div>
      <template v-else>
        <SFormCard title="Resolución" subtitle="Aprobar o rechazar la solicitud"
          icon="i-heroicons-check-badge" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">
          <div class="form-group full-width">
            <label class="form-label">Estado actual</label>
            <div class="flex items-center gap-2">
              <span class="badge" :class="form.estado === 'aprobado' ? 'badge--ok' : form.estado === 'rechazado' ? 'badge--danger' : 'badge--warning'" style="text-transform: capitalize">{{ form.estado }}</span>
              <span v-if="revisadoPor" class="field-hint" style="margin: 0">· revisado por {{ revisadoPor }}</span>
            </div>
          </div>
          <template v-if="form.estado === 'pendiente'">
            <div class="form-group full-width">
              <label class="form-label">Motivo del rechazo <span class="field-hint" style="margin:0">(requerido para rechazar)</span></label>
              <div class="input-wrapper"><UIcon name="i-heroicons-chat-bubble-bottom-center-text" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="motivoRechazo" class="input-clinical" rows="2" maxlength="500" placeholder="Explica por qué se rechaza..." /></div>
            </div>
            <div class="form-group full-width flex gap-2">
              <button type="button" class="btn-primary" :disabled="saving" @click="decidir(true)">
                <UIcon name="i-heroicons-check" class="w-4 h-4" /> Aprobar
              </button>
              <button type="button" class="btn-outline" :disabled="saving" style="border-color: var(--alert); color: var(--alert)" @click="decidir(false)">
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4" /> Rechazar
              </button>
            </div>
            <p class="field-hint full-width">Al aprobar, la asistencia del período se marca automáticamente como <strong>Justificado</strong>.</p>
          </template>
          <p v-else-if="form.estado === 'rechazado' && motivoRechazo" class="field-hint full-width">Motivo del rechazo: {{ motivoRechazo }}</p>
        </SFormCard>

        <SFormCard title="Datos de la Justificación" subtitle="Motivo, documento y período"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)">
          <div class="form-group">
            <label class="form-label">Motivo</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-flag" class="input-icon" />
              <select v-model="form.motivo_id" class="input-clinical">
                <option value="">Sin motivo específico</option>
                <option v-for="m in motivos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">N° de documento</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-hashtag" class="input-icon" /><input v-model="form.numero_documento" class="input-clinical font-mono-data" maxlength="50" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Fecha de trámite</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_tramite" type="date" class="input-clinical" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Días</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-calculator" class="input-icon" /><input :value="dias" disabled class="input-clinical font-mono-data" style="background: var(--surface-2, #f4f5f7)" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Fecha inicio <span class="required">*</span></label>
            <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.fecha_inicio" type="date" class="input-clinical" @change="error = ''" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Fecha fin <span class="required">*</span></label>
            <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.fecha_fin" type="date" class="input-clinical" @change="error = ''" /></div>
          </div>
          <div class="form-group full-width">
            <label class="form-label">Descripción / Sustento</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.descripcion" class="input-clinical" rows="3" /></div>
          </div>
          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/rrhh/justificaciones?tenant=${tenantId}`" @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>
    <template #sidebar>
      <SWidgetSummary :items="[
        { label: 'Trabajador', value: info.empleado_nombre },
        { label: 'DNI', value: info.empleado_dni, mono: true },
        { label: 'Régimen', value: info.empleado_regimen },
        { label: 'Cargo', value: info.empleado_cargo },
        { divider: true },
        { label: 'Días', value: String(dias) },
        { label: 'Estado', value: form.estado },
      ]" />
      <SWidgetInfo :items="['Solo las justificaciones aprobadas afectan el control de asistencia', 'Rechazar mantiene el registro para historial', 'Los días se recalculan si cambias las fechas']" />
      <SWidgetTip text="Antes de aprobar, verifica que el N° de documento y el sustento estén completos." />
    </template>
  </SFormLayout>
</template>
