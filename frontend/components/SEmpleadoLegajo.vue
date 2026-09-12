<script setup lang="ts">
const form = defineModel<any>({ required: true })
</script>

<template>
  <div class="form-group full-width space-y-3">
    <p class="form-label">Legajo, formación y contacto de emergencia</p>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <label>Número de legajo<input v-model="form.numero_legajo" class="input-clinical" maxlength="50" /></label>
      <label>Documento del vínculo laboral<input v-model="form.documento_vinculo_laboral" class="input-clinical" maxlength="255" placeholder="Contrato o resolución" /></label>
      <label>Título o formación acreditada<input v-model="form.titulo_profesional" class="input-clinical" maxlength="255" /></label>
      <label>Institución de formación<input v-model="form.institucion_formacion" class="input-clinical" maxlength="255" /></label>
      <label>Fecha del título<input v-model="form.fecha_titulo" type="date" class="input-clinical" /></label>
      <label>Contacto de emergencia<input v-model="form.contacto_emergencia_nombre" class="input-clinical" maxlength="150" /></label>
      <label>Teléfono de emergencia<input v-model="form.contacto_emergencia_telefono" class="input-clinical" maxlength="20" type="tel" /></label>
    </div>
    <p class="field-hint">Completa la formación y los documentos según el puesto. Estos datos no sustituyen los documentos del legajo.</p>
  </div>
</template>
