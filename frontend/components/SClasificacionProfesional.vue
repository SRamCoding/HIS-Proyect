<script setup lang="ts">
const props = defineProps<{
  profesionId: string
  numeroColegiatura: string
  habilitado: boolean
}>()
const emit = defineEmits(['update:profesionId', 'update:numeroColegiatura', 'update:habilitado', 'grupo', 'medico'])
const { api } = useApi()
const profesiones = ref<any[]>([])
const error = ref('')
const seleccionada = computed(() => profesiones.value.find(p => p.id === props.profesionId))
watch(seleccionada, p => emit('medico', p?.codigo === 'MED'))
function seleccionar(event: Event) {
  const value = (event.target as HTMLSelectElement).value
  emit('update:profesionId', value)
  const p = profesiones.value.find(p => p.id === value)
  if (p) emit('grupo', p.grupo_ocupacional_id)
}
onMounted(async () => {
  try { profesiones.value = await api('/sigarh/mantenimiento/profesiones?limit=500') }
  catch (e: any) { error.value = apiErr(e, 'No se pudo cargar profesiones') }
})
</script>

<template>
  <div class="form-group full-width">
    <label class="form-label">Profesión o formación ocupacional</label>
    <select :value="profesionId" class="input-clinical" @change="seleccionar">
      <option value="">Selecciona la profesión</option>
      <option v-for="p in profesiones.filter(p => p.is_active || p.id === profesionId)" :key="p.id" :value="p.id">{{ p.nombre }}{{ p.is_active ? '' : ' (inactiva)' }}</option>
    </select>
    <p class="field-hint">El grupo ocupacional se asigna según la profesión. Las profesiones son comunes a todas las categorías de hospital.</p>
    <p v-if="error" class="error-message">{{ error }}</p>
  </div>
  <div class="form-group">
    <label class="form-label">Colegio profesional</label>
    <input :value="seleccionada?.colegio_profesional || 'No aplica'" class="input-clinical" readonly />
  </div>
  <div class="form-group">
    <label class="form-label">Número de colegiatura</label>
    <input :value="numeroColegiatura" class="input-clinical" maxlength="50" :disabled="!seleccionada?.colegio_profesional" @input="emit('update:numeroColegiatura', ($event.target as HTMLInputElement).value)" />
    <label class="flex items-center gap-2 mt-2 text-sm"><input :checked="habilitado" type="checkbox" :disabled="!seleccionada?.colegio_profesional" @change="emit('update:habilitado', ($event.target as HTMLInputElement).checked)" /> Habilitación verificada por RR. HH.</label>
  </div>
</template>
