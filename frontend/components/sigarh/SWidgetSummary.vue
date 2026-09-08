<template>
  <div class="widget widget-summary">
    <div class="widget-header">
      <UIcon name="i-heroicons-document-text" class="widget-icon" :style="{ color: iconColor }" />
      <h4 class="widget-title">Resumen</h4>
    </div>
    <div class="widget-content">
      <template v-for="(item, i) in items" :key="i">
        <div v-if="item.divider" class="summary-divider" />
        <div v-else class="summary-item">
          <span class="summary-label">{{ item.label }}</span>
          <span class="summary-value" :class="item.mono ? 'font-mono-data' : ''">
            <slot :name="item.slot || item.label" :item="item">
              {{ item.value || '-' }}
            </slot>
          </span>
        </div>
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  items: Array<{ label?: string; value?: string; mono?: boolean; slot?: string; divider?: boolean }>
  iconColor?: string
}>(), {
  iconColor: 'var(--navy)'
})
</script>
