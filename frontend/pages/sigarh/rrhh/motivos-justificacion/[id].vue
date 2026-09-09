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
const form = reactive({ nombre: '', codigo: '', descripcion: '', is_active: true })
const usos = ref(0)

const handleSave = async () => {
  if (!form.nombre.trim()) { error.value = 'El nombre del motivo es requerido'; return }
  saving.value = true; error.value = ''
  try {
    await api(`/sigarh/rrhh/motivos-justificacion/${id.value}`, { method: 'PATCH', body: { nombre: form.nombre, codigo: form.codigo || null, descripcion: form.descripcion || null, is_active: form.is_active } })
    router.push(`/sigarh/rrhh/motivos-justificacion?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const d = await api<any>(`/sigarh/rrhh/motivos-justificacion/${id.value}`)
    form.nombre = d.nombre; form.codigo = d.codigo || ''; form.descripcion = d.descripcion || ''; form.is_active = d.is_active
    usos.value = d.usos || 0
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/motivos-justificacion?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Motivos de Justificación</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Editar</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--purple-soft)"><UIcon name="i-heroicons-document-text" class="w-6 h-6" style="color: var(--purple)" /></div>
          <div><h1 class="page-title">{{ form.nombre || 'Editar Motivo' }}</h1><p class="page-subtitle">Actualiza los datos del motivo de justificación</p></div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--purple)" /></div>
      <SFormCard v-else title="Configuración del Motivo" subtitle="Actualiza los datos del motivo"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--purple-soft)" icon-color="var(--purple)" :error="error">
        <div class="form-group full-width">
          <label class="form-label">Nombre <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-tag" class="input-icon" /><input v-model="form.nombre" class="input-clinical" maxlength="150" @focus="error = ''" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Código</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-barcode" class="input-icon" /><input v-model="form.codigo" class="input-clinical font-mono-data" maxlength="20" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Estado</label>
          <div class="status-toggle"><span class="toggle-label">Motivo Activo</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }"><span class="toggle-slider" /></button>
          </div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Descripción</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.descripcion" class="input-clinical" rows="3" /></div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
            :cancel-to="`/sigarh/rrhh/motivos-justificacion?tenant=${tenantId}`" @save="handleSave" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetInfo :items="['Los motivos se eligen al registrar una justificación', 'Solo los motivos activos aparecen en el selector', 'No se puede eliminar un motivo usado en una justificación']" />
      <SWidgetSummary :items="[{ label: 'Nombre', value: form.nombre }, { label: 'Código', value: form.codigo, mono: true }, { divider: true }, { label: 'Usos en justificaciones', value: String(usos) }]" />
      <SWidgetTip text="Si un motivo queda en desuso, desactívalo en lugar de eliminarlo para conservar el historial." />
    </template>
  </SFormLayout>
</template>
