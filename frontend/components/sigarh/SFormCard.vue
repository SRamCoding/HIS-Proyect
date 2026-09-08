<template>
  <section class="form-card">
    <div class="card-header">
      <div class="card-header-icon" :style="{ background: iconBg }">
        <UIcon :name="icon" class="w-4 h-4" :style="{ color: iconColor }" />
      </div>
      <div>
        <h3 class="card-title">{{ title }}</h3>
        <p class="card-subtitle">{{ subtitle }}</p>
      </div>
    </div>
    <div v-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>
    <div class="form-grid">
      <slot />
    </div>
    <div class="form-actions">
      <div class="action-group">
        <slot name="actions" />
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  icon?: string
  iconBg?: string
  iconColor?: string
  error?: string
}>()
</script>
