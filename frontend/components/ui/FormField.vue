<!-- components/ui/FormField.vue -->
<template>
  <div class="form-group" :class="{ 'full-width': fullWidth }">
    <label v-if="label" class="form-label" :for="fieldId" :style="{ color: 'var(--ink)' }">
      {{ label }}
      <span v-if="required" class="required" style="color: var(--alert)">*</span>
    </label>

    <div class="input-wrapper" :style="{ position: 'relative' }">
      <UIcon v-if="icon" :name="icon" class="input-icon" :style="{
        position: 'absolute',
        left: '0.75rem',
        top: '50%',
        transform: 'translateY(-50%)',
        width: '1rem',
        height: '1rem',
        color: 'var(--ink-soft)'
      }" />

      <input
        v-if="type === 'text' || type === 'email' || type === 'password' || type === 'number' || type === 'date' || type === 'time'"
        :id="fieldId"
        :type="type"
        :value="modelValue"
        @input="$emit('update:modelValue', ($event.target as HTMLInputElement).value)"
        class="input-clinical"
        :class="{ 'input-error': error }"
        :placeholder="placeholder"
        :disabled="disabled"
        :required="required"
        :min="min"
        :max="max"
        :step="step"
        :style="{ paddingLeft: icon ? '2.5rem' : '0.875rem' }"
      />

      <textarea
        v-else-if="type === 'textarea'"
        :id="fieldId"
        :value="modelValue"
        @input="$emit('update:modelValue', ($event.target as HTMLTextAreaElement).value)"
        class="input-clinical"
        :class="{ 'input-error': error }"
        :placeholder="placeholder"
        :rows="rows"
        :disabled="disabled"
        :required="required"
        :style="{ paddingLeft: icon ? '2.5rem' : '0.875rem', paddingTop: icon ? '0.75rem' : '0.625rem' }"
      />

      <select
        v-else-if="type === 'select'"
        :id="fieldId"
        :value="modelValue"
        @change="$emit('update:modelValue', ($event.target as HTMLSelectElement).value)"
        class="input-clinical"
        :class="{ 'input-error': error }"
        :disabled="disabled"
        :required="required"
        :style="{ paddingLeft: icon ? '2.5rem' : '0.875rem' }"
      >
        <slot />
      </select>
    </div>

    <span v-if="error" class="error-message" style="color: var(--alert); font-size: 0.75rem; margin-top: 0.25rem">
      {{ error }}
    </span>
    <p v-if="hint" class="field-hint" style="color: var(--ink-soft); font-size: 0.6875rem; margin-top: 0.25rem">
      {{ hint }}
    </p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  modelValue: any
  label?: string
  type?: 'text' | 'email' | 'password' | 'number' | 'date' | 'time' | 'textarea' | 'select'
  icon?: string
  placeholder?: string
  required?: boolean
  error?: string
  hint?: string
  fullWidth?: boolean
  disabled?: boolean
  rows?: number
  min?: number
  max?: number
  step?: number
}>()

defineEmits<{
  (e: 'update:modelValue', value: any): void
}>()

// id único para asociar <label for> con el input/select/textarea (accesibilidad + click-to-focus)
const fieldId = useId()
</script>

<style scoped>
.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.form-group.full-width {
  grid-column: 1 / -1;
}
.form-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}
.required {
  color: var(--alert);
}
.input-wrapper {
  position: relative;
}
.input-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--ink-soft);
}
.input-clinical {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}
.input-clinical:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}
.input-clinical.input-error {
  border-color: var(--alert);
}
.input-clinical.input-error:focus {
  box-shadow: 0 0 0 3px var(--alert-soft);
}
.input-clinical:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.input-clinical::placeholder {
  color: var(--ink-soft);
  opacity: 0.6;
}
.input-clinical[type="date"],
.input-clinical[type="time"] {
  color-scheme: light;
}
.input-clinical[type="number"] {
  -moz-appearance: textfield;
}
.input-clinical[type="number"]::-webkit-outer-spin-button,
.input-clinical[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.input-clinical[type="password"] {
  letter-spacing: 0.15em;
}
</style>