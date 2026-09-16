<script setup lang="ts">
const empleado = defineModel<string>({default: ''})
const { api } = useApi()
const empleados = ref<{id: string; nombre: string}[]>([])
const error = ref('')
async function cargar() {
  error.value = ''
  try { empleados.value = await api('/sigarh/mantenimiento/personal-catalogo') }
  catch (e) { error.value = apiErr(e, 'No se pudieron cargar los empleados') }
}
onMounted(cargar)
</script>
<template>
  <div class="form-group full-width">
    <label class="form-label">Empleado vinculado</label>
    <select v-model="empleado" class="input-clinical"><option value="">Sin vincular</option><option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre }}</option></select>
    <p class="field-hint">Para una cuenta médica debes elegir el empleado que tiene la programación aprobada.</p>
    <p v-if="error" role="alert">{{ error }} <button type="button" @click="cargar">Reintentar</button></p>
  </div>
</template>
