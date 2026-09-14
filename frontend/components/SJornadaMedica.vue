<script setup lang="ts">
const form = defineModel<any>({ required: true })
</script>

<template>
  <div class="form-group full-width space-y-3 rounded-xl border border-slate-200 p-4">
    <p class="form-label">Jornada documentada para programación médica</p>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <label>Horas ordinarias mensuales
        <input v-model="form.jornada_mensual_horas" type="number" min="1" max="150" step="1" class="input-clinical" placeholder="Ej.: 150, según documento laboral" />
      </label>
      <label>Sustento de la jornada
        <input v-model="form.jornada_sustento" maxlength="255" class="input-clinical" placeholder="Contrato, resolución o disposición aplicable" />
      </label>
    </div>
    <p class="field-hint">RR. HH. debe verificar estos datos antes de enviar un rol médico. No asigne 150 horas automáticamente: compruebe el régimen, contrato y si existe un segundo empleo. R.M. 432-2025-MINSA, numerales 5.15 y 5.28.</p>
  </div>
</template>
