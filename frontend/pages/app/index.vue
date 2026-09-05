<!-- frontend/pages/app/index.vue -->
<template>
  <div class="p-6">
    <h1 class="text-lg font-semibold mb-1" style="color: var(--ink)">Escritorio</h1>
    <p class="text-sm mb-6" style="color: var(--ink-soft)">Panel Hospitalario</p>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      <component
        :is="tieneAlguno([grupo.modulo]) ? 'NuxtLink' : 'div'"
        v-for="grupo in grupos"
        :key="grupo.label"
        :to="tieneAlguno([grupo.modulo]) ? link(grupo.items[0]?.path || '/app') : undefined"
        class="p-4 flex items-center gap-3"
        :style="tieneAlguno([grupo.modulo])
          ? 'background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); text-decoration: none; cursor: pointer;'
          : 'background: var(--mist); border: 1px solid var(--line); border-radius: var(--radius); opacity: 0.5; cursor: not-allowed;'"
      >
        <div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(30,58,95,0.08)">
          <UIcon :name="grupo.icon || 'i-heroicons-folder'" class="w-5 h-5" style="color: var(--navy)" />
        </div>
        <div class="flex-1">
          <span class="text-sm font-medium block" style="color: var(--ink)">{{ grupo.label }}</span>
          <span v-if="!tieneAlguno([grupo.modulo])" class="text-xs" style="color: var(--ink-soft)">No activo</span>
        </div>
      </component>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const authStore = useAuthStore()
const { link, grupos } = useHospitalNav()

const tieneAlguno = (codes: string[]) =>
  codes.some(c => authStore.user?.active_modules?.includes(c) ?? false)
</script>