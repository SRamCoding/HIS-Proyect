<!-- components/ui/ToggleSwitch.vue -->
<template>
  <div class="status-toggle" :style="{ 
    display: 'flex', 
    alignItems: 'center', 
    justifyContent: 'space-between',
    padding: '0.75rem 1rem',
    borderRadius: '8px',
    background: 'var(--mist)'
  }">
    <span class="toggle-label" style="font-size: 0.875rem; font-weight: 500; color: var(--ink)">
      {{ label }}
    </span>
    <button
      type="button"
      role="switch"
      :aria-checked="modelValue"
      @click="$emit('update:modelValue', !modelValue)"
      class="toggle-switch"
      :class="{ 'toggle-active': modelValue }"
      :style="{ 
        position: 'relative',
        width: '44px',
        height: '24px',
        borderRadius: '12px',
        background: modelValue ? 'var(--teal)' : 'var(--line)',
        border: 'none',
        cursor: 'pointer',
        transition: 'background 0.3s ease',
        padding: 0
      }"
    >
      <span class="toggle-slider" :style="{
        position: 'absolute',
        top: '2px',
        left: modelValue ? '22px' : '2px',
        width: '20px',
        height: '20px',
        borderRadius: '50%',
        background: 'white',
        transition: 'transform 0.3s ease, left 0.3s ease',
        boxShadow: '0 1px 3px rgba(0,0,0,0.2)'
      }" />
    </button>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  modelValue: boolean
  label: string
}>()

defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()
</script>