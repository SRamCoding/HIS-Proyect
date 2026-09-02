<template>
  <div>
    <h1 class="text-lg font-semibold" style="color: var(--ink)">Panel SIGARH</h1>
    <p class="text-sm mt-1" style="color: var(--ink-soft)">Tenant: {{ tenantId }}</p>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
</script>