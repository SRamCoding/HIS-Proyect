<template>
  <div class="widget widget-tip">
    <div class="widget-content">
      <div class="tip-content">
        <UIcon name="i-heroicons-light-bulb" class="tip-icon" style="color: var(--amber)" />
        <div>
          <p class="tip-title">Consejo</p>
          <p class="tip-text">{{ text }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ text: string }>()
</script>
