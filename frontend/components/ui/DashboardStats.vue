<!-- components/ui/DashboardStats.vue -->
<template>
  <div class="stats-grid" :style="{ display: 'grid', gridTemplateColumns: `repeat(${items.length}, 1fr)`, gap: '1rem', marginBottom: '1.5rem' }">
    <div
      v-for="(item, index) in items"
      :key="index"
      class="stat-widget"
      :style="{
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        padding: '1.25rem 1.5rem',
        borderRadius: 'var(--radius)',
        border: '1px solid var(--line)',
        boxShadow: 'var(--shadow-sm)',
        background: 'var(--paper)',
        borderLeft: `4px solid ${item.color || 'var(--teal)'}`,
        transition: 'all 0.2s ease'
      }"
    >
      <div v-if="item.icon" class="stat-icon" :style="{
        width: '44px',
        height: '44px',
        borderRadius: '12px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        flexShrink: 0,
        background: item.iconBg || 'var(--mist)'
      }">
        <UIcon :name="item.icon" class="w-5 h-5" :style="{ color: item.iconColor || 'var(--ink-soft)' }" />
      </div>
      <div class="stat-content" :style="{ display: 'flex', flexDirection: 'column' }">
        <span class="stat-value" style="font-size: 1.5rem; font-weight: 700; color: var(--ink); line-height: 1.2">
          {{ item.value }}
        </span>
        <span class="stat-label" style="font-size: 0.8125rem; color: var(--ink-soft)">
          {{ item.label }}
        </span>
        <span v-if="item.sub" class="stat-sub" style="font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem">
          {{ item.sub }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface StatItem {
  label: string
  value: string | number
  icon?: string
  iconColor?: string
  iconBg?: string
  color?: string
  sub?: string
}

defineProps<{
  items: StatItem[]
}>()
</script>