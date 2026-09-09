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
const form = reactive({ nombre: '', fecha: '', tipo: 'nacional', is_active: true })

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'La descripción es requerida'; return }
  if (!form.fecha) { error.value = 'La fecha es requerida'; return }
  saving.value = true; error.value = ''
  try {
    await api(`/sigarh/rrhh/feriados/${id.value}`, { method: 'PATCH', body: { ...form } })
    router.push(`/sigarh/rrhh/feriados?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const d = await api<any>(`/sigarh/rrhh/feriados/${id.value}`)
    form.nombre = d.nombre; form.fecha = d.fecha; form.tipo = d.tipo || 'nacional'; form.is_active = d.is_active
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/feriados?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Días Feriados</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Editar</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-calendar" class="w-6 h-6" style="color: var(--navy)" /></div>
          <div><h1 class="page-title">{{ form.nombre || 'Editar Feriado' }}</h1><p class="page-subtitle">Actualiza los datos del feriado</p></div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" /></div>
      <SFormCard v-else title="Datos del Feriado" subtitle="Actualiza los datos del feriado"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">
        <div class="form-group full-width">
          <label class="form-label">Descripción <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.nombre" class="input-clinical" maxlength="150" @focus="error = ''" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha" type="date" class="input-clinical" @change="error = ''" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Tipo</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-flag" class="input-icon" />
            <select v-model="form.tipo" class="input-clinical">
              <option value="nacional">Nacional</option><option value="regional">Regional</option><option value="local">Local</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Estado</label>
          <div class="status-toggle"><span class="toggle-label">Feriado Activo</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }"><span class="toggle-slider" /></button>
          </div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
            :cancel-to="`/sigarh/rrhh/feriados?tenant=${tenantId}`" @save="handleSave" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetInfo :items="['El calendario de feriados es centralizado', 'Asistencia avisa al elegir un feriado, pero permite registrar', 'La generación de programación médica omite las fechas feriadas', 'No implica una prohibición general de trabajar ese día']" />
      <SWidgetSummary :items="[{ label: 'Descripción', value: form.nombre }, { label: 'Fecha', value: form.fecha, mono: true }, { label: 'Tipo', value: form.tipo }]" />
      <SWidgetTip text="Desactivar un feriado lo conserva en el historial pero deja de afectar la generación de roles futura." />
    </template>
  </SFormLayout>
</template>
