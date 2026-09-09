<template>
  <div v-if="show" class="preview-section form-group full-width">
    <h4 class="preview-title">Vista Previa</h4>
    <div class="preview-card">
      <div class="preview-icon" :style="{ background: active ? iconBg : 'var(--mist)' }">
        <UIcon :name="icon" class="w-5 h-5" :style="{ color: active ? iconColor : 'var(--ink-soft)' }" />
      </div>
      <div class="preview-info">
        <span class="preview-name">{{ nombre || 'Nombre del registro' }}</span>
        <span class="preview-detail">
          <span v-if="codigo" class="preview-code">{{ codigo }}</span>
          <span v-if="extra" class="preview-department">{{ extra }}</span>
          <span v-if="!codigo && !extra" style="color: var(--ink-soft)">Sin codigo</span>
        </span>
      </div>
      <span class="preview-status" :class="active ? 'preview-active' : 'preview-inactive'">
        <span class="preview-dot" :class="active ? 'dot-active' : 'dot-inactive'" />
        {{ active ? 'Activo' : 'Inactivo' }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  nombre?: string
  codigo?: string
  extra?: string
  active?: boolean
  icon?: string
  iconColor?: string
  iconBg?: string
  show?: boolean
}>(), {
  active: true,
  icon: 'i-heroicons-document',
  iconColor: 'var(--teal)',
  iconBg: 'var(--teal-soft)',
  show: true,
})
</script>
