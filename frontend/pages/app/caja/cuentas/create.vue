<script setup lang="ts">
// Cuentas es una vista de consulta de saldos; el cobro se hace desde Cobro por Paciente.
definePageMeta({ layout: 'app', middleware: ['auth', 'panel'] })
await navigateTo('/app/caja/cobro-por-paciente')
</script>
<template><div /></template>
