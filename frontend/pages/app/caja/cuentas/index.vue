<template>
  <div>
    <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
      <span>Caja</span><span>/</span><span>Cuentas</span>
    </div>
    <h1 class="text-lg font-semibold" style="color: var(--ink)">Caja - Cuentas</h1>
    <p class="text-sm mt-1" style="color: var(--ink-soft)">Esta seccion estara disponible proximamente.</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })
</script>
