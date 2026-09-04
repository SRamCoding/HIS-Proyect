<!-- components/ui/CardBase.vue -->
<template>
  <div class="card-base" :style="{ 
    background: 'var(--paper)', 
    borderRadius: 'var(--radius-lg)', 
    boxShadow: 'var(--shadow-card)',
    border: '1px solid var(--line)',
    padding: padding,
    ...customStyle 
  }">
    <div v-if="title || subtitle" class="card-header" :style="{ marginBottom: headerMargin }">
      <div v-if="title" class="card-title-wrapper">
        <div v-if="icon" class="card-icon" :style="{ background: iconBg || 'var(--mist)' }">
          <UIcon :name="icon" class="w-4 h-4" :style="{ color: iconColor || 'var(--ink-soft)' }" />
        </div>
        <div>
          <h3 class="card-title" style="color: var(--ink)">{{ title }}</h3>
          <p v-if="subtitle" class="card-subtitle" style="color: var(--ink-soft)">{{ subtitle }}</p>
        </div>
      </div>
      <div v-else-if="subtitle" class="card-title-wrapper">
        <p class="card-subtitle" style="color: var(--ink-soft)">{{ subtitle }}</p>
      </div>
      <div v-if="$slots.actions" class="card-actions">
        <slot name="actions" />
      </div>
    </div>
    <div class="card-body">
      <slot />
    </div>
    <div v-if="$slots.footer" class="card-footer" :style="{ borderTop: '1px solid var(--line)', marginTop: '1.5rem', paddingTop: '1rem' }">
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  subtitle?: string
  icon?: string
  iconColor?: string
  iconBg?: string
  padding?: string
  headerMargin?: string
  customStyle?: Record<string, any>
}

const props = withDefaults(defineProps<Props>(), {
  padding: '1.5rem',
  headerMargin: '1.5rem',
  customStyle: () => ({}),
})
</script>

<style scoped>
.card-base {
  transition: all 0.2s ease;
}
.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.card-title-wrapper {
  display: flex;
  align-items: center;
  gap: 1rem;
}
.card-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.card-title {
  font-size: 1rem;
  font-weight: 600;
  margin: 0;
}
.card-subtitle {
  font-size: 0.8125rem;
  margin: 0;
}
.card-body {
  width: 100%;
}
.card-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
</style>