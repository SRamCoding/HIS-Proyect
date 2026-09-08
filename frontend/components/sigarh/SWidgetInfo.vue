<template>
  <div class="widget widget-info">
    <div class="widget-header">
      <UIcon name="i-heroicons-information-circle" class="widget-icon" style="color: var(--teal)" />
      <h4 class="widget-title">Información</h4>
    </div>
    <div class="widget-content">
      <ul class="info-list">
        <li v-for="item in items" :key="item" class="info-item">
          <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
          <span>{{ item }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ items: string[] }>()
</script>
