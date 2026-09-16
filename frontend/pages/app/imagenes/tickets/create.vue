<script setup lang="ts">
// Tickets es una vista de impresión sobre las atenciones ya agendadas; el
// registro de un estudio nuevo se hace desde Atenciones.
definePageMeta({ layout: 'app', middleware: ['auth', 'panel'] })
await navigateTo('/app/imagenes/atenciones/create')
</script>
<template><div /></template>
