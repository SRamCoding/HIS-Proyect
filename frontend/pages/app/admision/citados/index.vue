<!-- frontend/pages/app/admision/citados/index.vue -->
<template>
  <div class="p-6">
    <h1 class="text-lg font-semibold mb-1" style="color: var(--ink)">Citados</h1>
    <p class="text-sm mb-6" style="color: var(--ink-soft)">Admisión · Listado de pacientes citados</p>

    <div
      class="p-10 flex flex-col items-center justify-center text-center"
      style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius);"
    >
      <div class="w-12 h-12 rounded-lg flex items-center justify-center mb-3" style="background: rgba(30,58,95,0.08)">
        <UIcon name="i-heroicons-calendar" class="w-6 h-6" style="color: var(--navy)" />
      </div>
      <p class="text-sm font-medium mb-1" style="color: var(--ink)">Este módulo está en construcción</p>
      <p class="text-xs" style="color: var(--ink-soft)">Pronto podrás ver aquí a los pacientes citados.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })
</script>