<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/grupos-ocupacionales?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Grupos Ocupacionales</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Grupo</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--green-soft)">
            <UIcon name="i-heroicons-users" class="w-6 h-6" style="color: var(--green)" />
          </div>
          <div>
            <h1 class="page-title">{{ form.nombre || 'Editar Grupo Ocupacional' }}</h1>
            <p class="page-subtitle">Actualiza los datos del grupo ocupacional</p>
          </div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--green)" />
      </div>

      <template v-else>
        <SFormCard title="Datos del Grupo" subtitle="Actualiza los datos del grupo ocupacional"
          icon="i-heroicons-cog-6-tooth" icon-bg="var(--green-soft)" icon-color="var(--green)" :error="error">

          <div class="form-group full-width">
            <label class="form-label">Nombre <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-users" class="input-icon" />
              <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Profesional de la Salud, Tecnico Asistencial" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Codigo</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-barcode" class="input-icon" />
              <input v-model="form.codigo" class="input-clinical font-mono-data" placeholder="Ej: GO-001" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Tipo de Grupo</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-rectangle-group" class="input-icon" />
              <select v-model="form.tipo_grupo_id" class="input-clinical">
                <option value="">Sin tipo</option>
                <option v-for="t in tiposGrupo" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Grupo Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Categoría de rol de turno</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-identification" class="input-icon" />
              <select v-model="form.categoria_personal" class="input-clinical">
                <option value="">Personal no clínico (no asignable a roles de turno)</option>
                <option v-for="c in CATEGORIAS" :key="c.value" :value="c.value">{{ c.label }}</option>
              </select>
            </div>
            <p class="field-hint">Define la profesión a efectos de Creación de Roles: solo el personal de este grupo podrá agregarse a un rol de esta categoría.</p>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Descripcion</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea v-model="form.descripcion" class="input-clinical" rows="3" placeholder="Descripcion del grupo ocupacional..." />
            </div>
          </div>

          <SFormPreview
            :nombre="form.nombre"
            :codigo="form.codigo"
            :extra="tipoGrupoNombre"
            :active="form.is_active"
            icon="i-heroicons-users"
            icon-color="var(--green)"
            icon-bg="var(--green-soft)"
          />

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/grupos-ocupacionales?tenant=${tenantId}`"
              @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Agrupan al personal segun su naturaleza ocupacional', 'Ej: Profesional, Tecnico, Auxiliar, Administrativo', 'El tipo de grupo permite clasificarlos por categoria', 'Los grupos inactivos no se pueden asignar']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'Codigo', value: form.codigo, mono: true },
        { label: 'Tipo de Grupo', value: tipoGrupoNombre },
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
      <SWidgetTip text="Usa nombres alineados a la normativa de grupos ocupacionales del sector salud." />
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
const tiposGrupo = ref<any[]>([])
const CATEGORIAS = [
  { value: 'medicos', label: 'Médicos' },
  { value: 'otros_profesionales', label: 'Otros profesionales de la salud' },
  { value: 'residentes', label: 'Residentes' },
  { value: 'tecnicos', label: 'Técnicos y auxiliares' },
  { value: 'internos', label: 'Internos' },
]
const form = reactive({ nombre: '', codigo: '', descripcion: '', tipo_grupo_id: '', categoria_personal: '', is_active: true })

const tipoGrupoNombre = computed(() => tiposGrupo.value.find(t => t.id === form.tipo_grupo_id)?.nombre || '')

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/mantenimiento/grupos-ocupacionales/${id.value}`, {
      method: 'PATCH',
      body: {
        nombre: form.nombre,
        codigo: form.codigo || null,
        descripcion: form.descripcion || null,
        tipo_grupo_id: form.tipo_grupo_id || null,
        categoria_personal: form.categoria_personal || null,
        is_active: form.is_active,
      },
    })
    router.push(`/sigarh/mantenimiento/grupos-ocupacionales?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, tipos] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/grupos-ocupacionales/${id.value}`),
      api<any[]>('/sigarh/infraestructura/catalogos?categoria=tipos_grupo_ocupacional').catch(() => []),
    ])
    form.nombre = data.nombre
    form.codigo = data.codigo || ''
    form.descripcion = data.descripcion || ''
    form.tipo_grupo_id = data.tipo_grupo_id || ''
    form.categoria_personal = data.categoria_personal || ''
    form.is_active = data.is_active
    tiposGrupo.value = tipos
  } catch (e: any) { error.value = apiErr(e, 'No se pudo cargar') }
  finally { loading.value = false }
})
</script>
