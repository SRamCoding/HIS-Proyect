<script setup lang="ts">
// Censo Diario es un reporte, no tiene alta manual.
definePageMeta({ layout: 'app', middleware: ['auth', 'panel'] })
await navigateTo('/app/hospitalizacion/censo-diario')
</script>
<template><div /></template>
