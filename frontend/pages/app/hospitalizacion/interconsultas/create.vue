<script setup lang="ts">
// Las interconsultas se solicitan dentro de una hospitalización ya admitida.
definePageMeta({ layout: 'app', middleware: ['auth', 'panel'] })
await navigateTo('/app/hospitalizacion/hospitalizaciones')
</script>
<template><div /></template>
