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
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true; error.value = ''
  try {
    await api('/sigarh/rrhh/especialidades', { method: 'POST', body: { nombre: form.nombre, codigo: form.codigo || null, descripcion: form.descripcion || null, is_active: form.is_active } })
    if (otro) Object.assign(form, { nombre: '', codigo: '', descripcion: '', is_active: true })
    else router.push(`/sigarh/rrhh/especialidades?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo crear') }
  finally { saving.value = false }
}
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/especialidades?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Especialidades</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Nueva</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--purple-soft)"><UIcon name="i-heroicons-academic-cap" class="w-6 h-6" style="color: var(--purple)" /></div>
          <div><h1 class="page-title">Crear Especialidad</h1><p class="page-subtitle">Define una especialidad médica</p></div>
        </div>
      </div>

      <SFormCard title="Datos de la Especialidad" subtitle="Ingresa los datos de la nueva especialidad"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--purple-soft)" icon-color="var(--purple)" :error="error">
        <div class="form-group full-width">
          <label class="form-label">Nombre <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-academic-cap" class="input-icon" /><input v-model="form.nombre" class="input-clinical" maxlength="100" placeholder="Ej: Cardiología" @focus="error = ''" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Código interno</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-barcode" class="input-icon" /><input v-model="form.codigo" class="input-clinical font-mono-data" maxlength="20" placeholder="Ej: CARD" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Estado</label>
          <div class="status-toggle"><span class="toggle-label">Especialidad Activa</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }"><span class="toggle-slider" /></button>
          </div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Descripción / Notas</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.descripcion" class="input-clinical" rows="3" placeholder="Alcance de la especialidad..." /></div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Crear" saving-text="Creando..."
            :cancel-to="`/sigarh/rrhh/especialidades?tenant=${tenantId}`" :show-create-another="true"
            @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetInfo :items="['Una persona puede tener varias especialidades', 'Se asignan en la ficha del empleado y en Consultorios', 'Solo las especialidades activas aparecen en los selectores', 'El listado muestra cuántos empleados tienen cada especialidad']" />
      <SWidgetTip text="Usa nombres estandarizados (RENAES) para facilitar reportes y la asignación de médicos a consultorios." />
    </template>
  </SFormLayout>
</template>
