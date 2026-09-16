<script setup lang="ts">
// Reimpresiones es una vista de impresión sobre atenciones ya validadas; el
// registro de un estudio nuevo se hace desde Atenciones.
definePageMeta({ layout: 'app', middleware: ['auth', 'panel'] })
await navigateTo('/app/imagenes/atenciones/create')
</script>
<template><div /></template>
