<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/infraestructura-hosp/camas?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Camas</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Cama</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)">
            <UIcon name="i-heroicons-rectangle-stack" class="w-6 h-6" style="color: var(--navy)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.codigo || 'Editar Cama' }}</h1>
            <p class="page-subtitle">{{ form.nombre || 'Actualiza los datos de la cama' }}</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" />
      </div>

      <template v-else>
        <SFormCard title="Datos de la Cama" subtitle="Actualiza los datos de la cama"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">

          <div class="form-group">
            <label class="form-label">Piso</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-building-office-2" class="input-icon" />
              <select v-model="filtroPiso" class="input-clinical">
                <option value="">Todos</option>
                <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Sala</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-squares-plus" class="input-icon" />
              <select v-model="form.sala_id" class="input-clinical" @change="onSala">
                <option value="">Sin sala (solo texto)</option>
                <option v-for="s in salasFiltradas" :key="s.id" :value="s.id">{{ s.nombre }}<span v-if="s.piso_nombre"> — {{ s.piso_nombre }}</span></option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Codigo <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-barcode" class="input-icon" />
              <input v-model="form.codigo" class="input-clinical font-mono-data" maxlength="20" placeholder="Ej: UCI-01" @input="form.codigo = form.codigo.toUpperCase().slice(0, 20)" />
            </div>
            <p class="field-hint">Único, máximo 20 caracteres</p>
          </div>

          <div class="form-group">
            <label class="form-label">Nombre / Descripción <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-rectangle-stack" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" maxlength="100" placeholder="Ej: Cama 1 — Sala A" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Tipo de cama <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-tag" class="input-icon" />
              <select v-model="form.tipo_cama" class="input-clinical">
                <option value="">Seleccione un tipo</option>
                <option v-for="t in tiposCama" :key="t.id" :value="t.nombre">{{ t.nombre }}</option>
                <option v-if="form.tipo_cama && !tiposCama.some(t => t.nombre === form.tipo_cama)" :value="form.tipo_cama">{{ form.tipo_cama }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Estado <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-signal" class="input-icon" />
              <select v-model="form.estado" class="input-clinical">
                <option v-for="e in ESTADOS" :key="e" :value="e">{{ label(e) }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Estado de habilitación</label>
            <div class="status-toggle">
              <span class="toggle-label">Cama Activa</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <div class="form-group full-width" style="border-top: 1px solid var(--line); padding-top: 1rem;">
            <label class="form-label">Ubicación (texto, editable)</label>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.5rem;">
              <input v-model="form.sala_texto" class="input-clinical" style="padding-left: 0.75rem" placeholder="Sala" />
              <input v-model="form.piso_texto" class="input-clinical" style="padding-left: 0.75rem" placeholder="Piso" />
              <input v-model="form.servicio_texto" class="input-clinical" style="padding-left: 0.75rem" placeholder="Servicio" />
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre || form.codigo"
            :codigo="form.codigo"
            :extra="form.tipo_cama"
            :active="form.estado === 'DISPONIBLE' && form.is_active"
            icon="i-heroicons-rectangle-stack"
            icon-color="var(--navy)"
            icon-bg="var(--navy-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/infraestructura-hosp/camas?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['El código es único y en mayúsculas (máx. 20)', 'La sala aporta servicio y piso; los textos quedan editables', 'Estado y Activa son independientes', 'Una cama ocupada no se puede eliminar']" />
      <SWidgetSummary :items="[
        { label: 'Codigo', value: form.codigo, mono: true },
        { label: 'Nombre', value: form.nombre },
        { label: 'Sala', value: form.sala_texto },
        { label: 'Tipo', value: form.tipo_cama },
        { divider: true },
        { label: 'Estado', slot: 'estado' },
        { label: 'Activa', slot: 'activa' },
      ]">
        <template #estado><span class="badge" :class="badgeEstado(form.estado)">{{ label(form.estado) }}</span></template>
        <template #activa>{{ form.is_active ? 'Si' : 'No' }}</template>
      </SWidgetSummary>
      <SWidgetTip text="Para pasar una cama a Disponible u otro estado rápido usa 'Cambiar estado' desde el listado de Camas." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const ESTADOS = ['DISPONIBLE', 'OCUPADA', 'MANTENIMIENTO', 'RESERVADA'] as const
const label = (e: string) => ({ DISPONIBLE: 'Disponible', OCUPADA: 'Ocupada', MANTENIMIENTO: 'Mantenimiento', RESERVADA: 'Reservada' }[e] || e)
const badgeEstado = (e: string) => ({ DISPONIBLE: 'badge--ok', OCUPADA: 'badge--danger', MANTENIMIENTO: 'badge--warning', RESERVADA: 'badge--warning' }[e] || 'badge--neutral')

const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const pisos = ref<any[]>([])
const salas = ref<any[]>([])
const tiposCama = ref<any[]>([])
const filtroPiso = ref('')

const form = reactive({
  sala_id: '', piso_id: '', servicio_id: '',
  codigo: '', nombre: '',
  sala_texto: '', piso_texto: '', servicio_texto: '',
  tipo_cama: '', estado: 'DISPONIBLE', is_active: true,
})

const salasFiltradas = computed(() => filtroPiso.value ? salas.value.filter(s => s.piso_id === filtroPiso.value) : salas.value)

const onSala = () => {
  const s = salas.value.find(x => x.id === form.sala_id)
  if (!s) return
  form.piso_id = s.piso_id || ''
  form.servicio_id = s.servicio_id || ''
  form.sala_texto = s.nombre || ''
  form.piso_texto = s.piso_nombre || ''
  form.servicio_texto = s.servicio_nombre || ''
}

const handleSave = async () => {
  if (!form.codigo.trim()) { error.value = 'El código es requerido'; return }
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  if (!form.tipo_cama) { error.value = 'El tipo de cama es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/infraestructura-hosp/camas/${id.value}`, {
      method: 'PATCH',
      body: {
        sala_id: form.sala_id || null,
        piso_id: form.piso_id || null,
        servicio_id: form.servicio_id || null,
        codigo: form.codigo,
        nombre: form.nombre,
        sala_texto: form.sala_texto || null,
        piso_texto: form.piso_texto || null,
        servicio_texto: form.servicio_texto || null,
        tipo_cama: form.tipo_cama,
        estado: form.estado,
        is_active: form.is_active,
      },
    })
    router.push(`/sigarh/infraestructura-hosp/camas?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, ps, ss, tc] = await Promise.all([
      api<any>(`/sigarh/infraestructura-hosp/camas/${id.value}`),
      api<any[]>('/sigarh/infraestructura-hosp/pisos').catch(() => []),
      api<any[]>('/sigarh/infraestructura-hosp/salas').catch(() => []),
      api<any[]>('/sigarh/infraestructura/catalogos?categoria=tipos_cama').catch(() => []),
    ])
    form.sala_id = data.sala_id || ''
    form.piso_id = data.piso_id || ''
    form.servicio_id = data.servicio_id || ''
    form.codigo = data.codigo || ''
    form.nombre = data.nombre || ''
    form.sala_texto = data.sala_texto || ''
    form.piso_texto = data.piso_texto || ''
    form.servicio_texto = data.servicio_texto || ''
    form.tipo_cama = data.tipo_cama || ''
    form.estado = data.estado || 'DISPONIBLE'
    form.is_active = data.is_active
    if (form.piso_id) filtroPiso.value = form.piso_id
    pisos.value = ps
    salas.value = ss
    tiposCama.value = tc
  } catch { error.value = 'No se pudo cargar la cama' }
  finally { loading.value = false }
})
</script>
