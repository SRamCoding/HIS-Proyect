<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const form = reactive({ nombre: '', fecha: '', tipo: 'nacional', is_active: true })

const handleCreate = async (otro: boolean) => {
  if (!form.nombre.trim()) { error.value = 'La descripción es requerida'; return }
  if (!form.fecha) { error.value = 'La fecha es requerida'; return }
  saving.value = true; error.value = ''
  try {
    await api('/sigarh/rrhh/feriados', { method: 'POST', body: { ...form } })
    if (otro) Object.assign(form, { nombre: '', fecha: '', tipo: 'nacional', is_active: true })
    else router.push(`/sigarh/rrhh/feriados?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo crear') }
  finally { saving.value = false }
}
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/feriados?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Días Feriados</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Nuevo</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-calendar" class="w-6 h-6" style="color: var(--navy)" /></div>
          <div><h1 class="page-title">Nuevo Feriado</h1><p class="page-subtitle">Registra una fecha especial del calendario</p></div>
        </div>
      </div>

      <SFormCard title="Datos del Feriado" subtitle="Ingresa la descripción y la fecha"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">
        <div class="form-group full-width">
          <label class="form-label">Descripción <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar-days" class="input-icon" /><input v-model="form.nombre" class="input-clinical" maxlength="150" placeholder="Ej: Aniversario institucional" @focus="error = ''" /></div>
          <p class="field-hint">Máximo 150 caracteres</p>
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
          <SFormActions :saving="saving" save-text="Crear" saving-text="Creando..."
            :cancel-to="`/sigarh/rrhh/feriados?tenant=${tenantId}`" :show-create-another="true"
            @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetInfo :items="['El calendario de feriados es centralizado', 'Asistencia avisa al elegir un feriado, pero permite registrar', 'La generación de programación médica omite las fechas feriadas', 'No implica una prohibición general de trabajar ese día']" />
      <SWidgetTip text="Registra los feriados con anticipación: la programación de roles del mes los tiene en cuenta al generarse." />
    </template>
  </SFormLayout>
</template>
