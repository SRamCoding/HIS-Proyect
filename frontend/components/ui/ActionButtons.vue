<!-- components/ui/ActionButtons.vue -->
<template>
  <div class="action-buttons" :style="{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: '0.25rem' }">
    <button
      v-for="action in actions"
      :key="action.label"
      class="action-btn"
      :style="{
        display: 'inline-flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: '32px',
        height: '32px',
        borderRadius: '6px',
        border: '1px solid transparent',
        background: 'transparent',
        color: action.color || 'var(--ink-soft)',
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        textDecoration: 'none'
      }"
      :title="action.title || action.label"
      @click="action.onClick"
    >
      <UIcon :name="action.icon" class="w-4 h-4" />
    </button>
  </div>
</template>

<script setup lang="ts">
interface Action {
  label: string
  icon: string
  title?: string
  color?: string
  onClick: () => void
}

defineProps<{
  actions: Action[]
}>()
</script>

<style scoped>
.action-btn:hover {
  background: var(--mist);
}
</style>