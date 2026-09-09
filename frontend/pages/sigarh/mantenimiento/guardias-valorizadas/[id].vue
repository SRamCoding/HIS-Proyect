<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/mantenimiento/guardias-valorizadas?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Guardias Valorizadas</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Editar Guardia</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--amber-soft)">
            <UIcon name="i-heroicons-currency-dollar" class="w-6 h-6" style="color: var(--amber)" />
          </div>
          <div>
            <h1 class="page-title">Editar Guardia Valorizada</h1>
            <p class="page-subtitle">Actualiza el valor de la guardia</p>
          </div>
        </div>
      </div>
      <div v-if="loading" class="form-card flex items-center justify-center py-16">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--amber)" />
      </div>
      <template v-else>
        <SFormCard title="Datos de la Guardia" subtitle="Actualiza los datos de la guardia valorizada"
          icon="i-heroicons-currency-dollar" icon-bg="var(--amber-soft)" icon-color="var(--amber)" :error="error">

          <div class="form-group">
            <label class="form-label">Tipo de Guardia <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-shield-check" class="input-icon" />
              <select v-model="form.tipo_guardia_id" class="input-clinical">
                <option value="">Seleccione un tipo</option>
                <option v-for="t in tiposGuardia" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Valor (S/) <span class="required">*</span></label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-currency-dollar" class="input-icon" />
              <input v-model.number="form.valor" type="number" step="0.01" min="0" class="input-clinical font-mono-data" placeholder="0.00" />
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Grupo Ocupacional</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-user-group" class="input-icon" />
              <select v-model="form.grupo_ocupacional_id" class="input-clinical">
                <option value="">Sin grupo</option>
                <option v-for="g in gruposOcupacionales" :key="g.id" :value="g.id">{{ g.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group">
            <label class="form-label">Nivel Remunerativo</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-banknotes" class="input-icon" />
              <select v-model="form.nivel_remunerativo_id" class="input-clinical">
                <option value="">Sin nivel</option>
                <option v-for="n in nivelesRemunerativos" :key="n.id" :value="n.id">{{ n.nombre }}</option>
              </select>
            </div>
          </div>

          <div class="form-group full-width">
            <label class="form-label">Estado</label>
            <div class="status-toggle">
              <span class="toggle-label">Guardia Activa</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
                <span class="toggle-slider" />
              </button>
            </div>
          </div>

          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/mantenimiento/guardias-valorizadas?tenant=${tenantId}`" @save="handleSave" />
          </template>
        </SFormCard>
      </template>
    </template>
    <template #sidebar>
      <SWidgetInfo :items="['Define el valor economico de cada tipo de guardia', 'Se puede segmentar por grupo ocupacional y nivel', 'El valor se expresa en soles (S/)', 'Las guardias inactivas no se pueden asignar']" />
      <SWidgetSummary :items="[
        { label: 'Tipo Guardia', value: tiposGuardia.find(t => t.id === form.tipo_guardia_id)?.nombre },
        { label: 'Valor', value: form.valor > 0 ? `S/ ${form.valor.toFixed(2)}` : undefined, mono: true },
        { divider: true },
        { label: 'Estado', slot: 'estado' }
      ]">
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Puedes tener diferentes valores para el mismo tipo de guardia segun el grupo ocupacional o nivel remunerativo." />
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
const tiposGuardia = ref<any[]>([])
const gruposOcupacionales = ref<any[]>([])
const nivelesRemunerativos = ref<any[]>([])
const form = reactive({ tipo_guardia_id: '', grupo_ocupacional_id: '', nivel_remunerativo_id: '', valor: 0, is_active: true })
const handleSave = async () => {
  if (!form.tipo_guardia_id) { error.value = 'El tipo de guardia es requerido'; return }
  if (!form.valor || form.valor <= 0) { error.value = 'El valor debe ser mayor a 0'; return }
  saving.value = true; error.value = ''
  try {
    await api(`/sigarh/mantenimiento/guardias-valorizadas/${id.value}`, { method: 'PATCH', body: {
      tipo_guardia_id: form.tipo_guardia_id || null,
      grupo_ocupacional_id: form.grupo_ocupacional_id || null,
      nivel_remunerativo_id: form.nivel_remunerativo_id || null,
      valor: form.valor, is_active: form.is_active
    }})
    router.push(`/sigarh/mantenimiento/guardias-valorizadas?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const [data, tg, go, nr] = await Promise.all([
      api<any>(`/sigarh/mantenimiento/guardias-valorizadas/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/tipos-guardia'),
      api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
      api<any[]>('/sigarh/mantenimiento/niveles-remunerativos'),
    ])
    form.tipo_guardia_id = data.tipo_guardia_id || ''
    form.grupo_ocupacional_id = data.grupo_ocupacional_id || ''
    form.nivel_remunerativo_id = data.nivel_remunerativo_id || ''
    form.valor = data.valor || 0
    form.is_active = data.is_active
    tiposGuardia.value = tg; gruposOcupacionales.value = go; nivelesRemunerativos.value = nr
  } catch (e: any) { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>