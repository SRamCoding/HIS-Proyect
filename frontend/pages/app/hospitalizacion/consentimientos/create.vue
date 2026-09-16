<script setup lang="ts">
// Los consentimientos se registran dentro de una hospitalización ya admitida.
definePageMeta({ layout: 'app', middleware: ['auth', 'panel'] })
await navigateTo('/app/hospitalizacion/hospitalizaciones')
</script>
<template><div /></template>
