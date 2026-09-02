<template>
  <div>
    <h1 class="text-lg font-semibold mb-2" style="color: var(--ink)">Usuarios</h1>
    <p class="text-sm" style="color: var(--ink-soft)">Listado de usuarios del sistema.</p>
  </div>
</template>
<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })
</script>