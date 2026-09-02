<template>
  <div>
    <h1 class="text-lg font-semibold" style="color: var(--ink)">En construcción</h1>
    <p class="text-sm mt-1" style="color: var(--ink-soft)">Esta sección estará disponible próximamente.</p>
  </div>
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })
</script>