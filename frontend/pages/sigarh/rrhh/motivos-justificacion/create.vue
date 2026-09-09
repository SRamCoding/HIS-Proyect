<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const form = reactive({ nombre: '', codigo: '', descripcion: '', is_active: true })

const handleCreate = async (otro: boolean) => {
  if (!form.nombre.trim()) { error.value = 'El nombre del motivo es requerido'; return }
  saving.value = true; error.value = ''
  try {
    await api('/sigarh/rrhh/motivos-justificacion', { method: 'POST', body: { nombre: form.nombre, codigo: form.codigo || null, descripcion: form.descripcion || null, is_active: form.is_active } })
    if (otro) Object.assign(form, { nombre: '', codigo: '', descripcion: '', is_active: true })
    else router.push(`/sigarh/rrhh/motivos-justificacion?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo crear el motivo') }
  finally { saving.value = false }
}
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/motivos-justificacion?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Motivos de Justificación</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Nuevo</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--purple-soft)"><UIcon name="i-heroicons-document-text" class="w-6 h-6" style="color: var(--purple)" /></div>
          <div><h1 class="page-title">Crear Motivo de Justificación</h1><p class="page-subtitle">Define un motivo para justificar ausencias del personal</p></div>
        </div>
      </div>

      <SFormCard title="Configuración del Motivo" subtitle="Ingresa los datos del nuevo motivo"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--purple-soft)" icon-color="var(--purple)" :error="error">
        <div class="form-group full-width">
          <label class="form-label">Nombre <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-tag" class="input-icon" /><input v-model="form.nombre" class="input-clinical" maxlength="150" placeholder="Ej: Enfermedad, Comisión de servicios, Permiso personal" @focus="error = ''" /></div>
          <p class="field-hint">Máximo 150 caracteres</p>
        </div>
        <div class="form-group">
          <label class="form-label">Código</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-barcode" class="input-icon" /><input v-model="form.codigo" class="input-clinical font-mono-data" maxlength="20" placeholder="Ej: ENF" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Estado</label>
          <div class="status-toggle"><span class="toggle-label">Motivo Activo</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }"><span class="toggle-slider" /></button>
          </div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Descripción</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.descripcion" class="input-clinical" rows="3" placeholder="Cuándo aplica este motivo, documentos que requiere..." /></div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Crear" saving-text="Creando..."
            :cancel-to="`/sigarh/rrhh/motivos-justificacion?tenant=${tenantId}`" :show-create-another="true"
            @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetInfo :items="['Los motivos se eligen al registrar una justificación', 'Solo los motivos activos aparecen en el selector', 'No se puede eliminar un motivo usado en una justificación', 'El código ayuda a agrupar en reportes']" />
      <SWidgetTip text="Define motivos claros y no muy numerosos: facilita el análisis de ausentismo por causa." />
    </template>
  </SFormLayout>
</template>
