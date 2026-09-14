<script setup lang="ts">
const props = defineProps<{ tenantId: string }>()
const empleado = defineModel<string>({ default: '' })
const { api } = useApi()
const opciones = ref<{ id: string; nombre: string }[]>([])
const error = ref('')
let solicitud = 0
watch(() => props.tenantId, async (id, previo) => {
  const actual = ++solicitud
  if (previo) empleado.value = ''
  opciones.value = []
  error.value = ''
  if (!id) return
  try {
    const datos = await api<{ id: string; nombre: string }[]>(`/admin/usuarios/empleados-disponibles?tenant_id=${id}`)
    if (actual === solicitud) opciones.value = datos
  } catch { if (actual === solicitud) error.value = 'No se pudieron cargar los empleados.' }
}, { immediate: true })
</script>
<template>
  <div class="form-group full-width">
    <label class="form-label">Empleado vinculado a la cuenta</label>
    <select v-model="empleado" class="input-clinical" :disabled="!tenantId">
      <option value="">Sin vincular</option>
      <option v-for="e in opciones" :key="e.id" :value="e.id">{{ e.nombre }}</option>
    </select>
    <p class="field-hint">Una cuenta con rol Médico requiere este vínculo para cerrar sus atenciones.</p>
    <p v-if="error" role="alert">{{ error }}</p>
  </div>
</template>
