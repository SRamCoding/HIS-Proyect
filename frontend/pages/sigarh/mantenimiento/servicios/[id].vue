<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/servicios?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Servicios</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Servicio</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)">
            <UIcon name="i-heroicons-squares-2x2" class="w-6 h-6" style="color: var(--navy)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Servicio' }}</h1>
            <p class="page-subtitle">Actualiza los datos del servicio</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" />
      </div>

      <template v-else>
        <SFormCard title="Datos del Servicio" subtitle="Actualiza los datos del servicio"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-squares-2x2" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Emergencia, Hospitalizacion" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Codigo</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-barcode" class="input-icon" />
              <input v-model="form.codigo" class="input-clinical font-mono-data" placeholder="Ej: SRV-001" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Departamento</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-building-office-2" class="input-icon" />
              <select v-model="form.departamento_id" class="input-clinical">
                <option value="">Sin departamento</option>
                <option v-for="d in departamentos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
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
            <label class="form-label">Minutos por paciente (consulta externa)</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-clock" class="input-icon" />
              <input v-model.number="form.tiempo_atencion_min" type="number" min="5" max="120" class="input-clinical font-mono-data" placeholder="15" />
            </div>
            <p class="field-hint">Define cuántos cupos abre cada bloque de rol aprobado. Vacío = 15 min.</p>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Servicio Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Descripcion</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea v-model="form.descripcion" class="input-clinical" rows="3" placeholder="Descripcion del servicio..." />
            </div>
          </div>

          <div class="form-group full-width"><label class="form-label">UPSS donde funciona</label><div class="grid sm:grid-cols-2 gap-2 rounded-xl border p-3"><label v-for="u in upss" :key="u.id" class="flex items-center gap-2 text-sm"><input v-model="form.upss_ids" type="checkbox" :value="u.id" /> {{u.nombre}}</label></div></div>
          <div class="form-group full-width"><label class="form-label">Especialidades atendidas</label><div class="grid sm:grid-cols-2 gap-2 rounded-xl border p-3 max-h-64 overflow-auto"><label v-for="e in especialidades" :key="e.id" class="flex items-center gap-2 text-sm"><input v-model="form.especialidad_ids" type="checkbox" :value="e.id" /> {{e.nombre}}</label></div></div>

          <SFormPreview
            :nombre="form.nombre"
            :codigo="form.codigo"
            :extra="departamentoNombre"
            :active="form.is_active"
            icon="i-heroicons-squares-2x2"
            icon-color="var(--navy)"
            icon-bg="var(--navy-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/servicios?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Los servicios agrupan la atencion asistencial del hospital', 'Pueden asociarse a un departamento y a un piso', 'Se usan en la asignacion de personal y turnos', 'Los servicios inactivos no se pueden asignar']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Codigo', value: form.codigo, mono: true },
        { label: 'Departamento', value: departamentoNombre },
        { label: 'Piso', value: pisoNombre },
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
      <SWidgetTip text="Asocia el servicio a su departamento y piso para facilitar los reportes y la asignacion de guardias." />
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
const pisos = ref<any[]>([])
const upss = ref<any[]>([])
const especialidades = ref<any[]>([])
const form = reactive({ nombre: '', codigo: '', descripcion: '', departamento_id: '', piso_id: '', tiempo_atencion_min: null as number | null, is_active: true, upss_ids: [] as string[], especialidad_ids: [] as string[] })

const departamentoNombre = computed(() => departamentos.value.find(d => d.id === form.departamento_id)?.nombre || '')
const pisoNombre = computed(() => pisos.value.find(p => p.id === form.piso_id)?.nombre || '')

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/servicios/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        codigo: form.codigo || null,
        descripcion: form.descripcion || null,
        departamento_id: form.departamento_id || null,
        piso_id: form.piso_id || null,
        tiempo_atencion_min: form.tiempo_atencion_min || null,
        is_active: form.is_active,
      },
    })
    await api(`/sigarh/mantenimiento/servicios/${id.value}/estructura`, { method: 'PUT', body: { upss_ids: form.upss_ids, especialidad_ids: form.especialidad_ids } })
    router.push(`/sigarh/mantenimiento/servicios?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, deps, pisosData, structure, specialties] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/servicios/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/departamentos'),
      api<any[]>('/sigarh/infraestructura-hosp/pisos').catch(() => []),
      api<any>('/sigarh/mantenimiento/estructura-asistencial'),
      api<any[]>('/sigarh/rrhh/especialidades?active_only=true'),
    ])
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.descripcion = data.descripcion || ''
    form.departamento_id = data.departamento_id || ''
    form.piso_id = data.piso_id || ''
    form.tiempo_atencion_min = data.tiempo_atencion_min ?? null
    form.is_active = data.is_active
    departamentos.value = deps
    pisos.value = pisosData
    upss.value = structure.upss
    especialidades.value = specialties.filter((e:any) => e.tipo === 'especialidad')
    const current = [...structure.upss.flatMap((u:any) => u.servicios), ...structure.servicios_sin_upss].find((s:any) => s.id === id.value)
    form.upss_ids = current?.upss_ids || []
    form.especialidad_ids = current?.especialidades?.map((e:any) => e.id) || []
  } catch (e: any) { error.value = 'No se pudo cargar el servicio' }
  finally { loading.value = false }
})
</script>
