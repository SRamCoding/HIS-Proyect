<!-- components/ui/PageHeader.vue -->
<template>
  <div class="page-header" :style="{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2rem', flexWrap: 'wrap', gap: '1rem' }">
    <div class="header-left" :style="{ display: 'flex', alignItems: 'center', gap: '1rem' }">
      <div v-if="icon" class="header-icon" :style="{ 
        width: '48px', 
        height: '48px', 
        borderRadius: '14px', 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center', 
        flexShrink: 0,
        background: iconBg || 'var(--mist)'
      }">
        <UIcon :name="icon" class="w-6 h-6" :style="{ color: iconColor || 'var(--ink-soft)' }" />
      </div>
      <div>
        <h1 class="page-title" style="font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2">
          {{ title }}
        </h1>
        <p v-if="subtitle" class="page-subtitle" style="font-size: 0.875rem; color: var(--ink-soft); margin: 0.125rem 0 0 0">
          {{ subtitle }}
        </p>
      </div>
    </div>
    <div class="header-actions" :style="{ display: 'flex', gap: '0.75rem', flexShrink: 0 }">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title: string
  subtitle?: string
  icon?: string
  iconColor?: string
  iconBg?: string
}>()
</script>