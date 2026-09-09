<template><div class="p-6 text-sm text-gray-500">Redirigiendo...</div></template>
<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const route = useRoute()
await navigateTo({ path: '/sigarh/movimientos/licencias', query: route.query })
</script>
