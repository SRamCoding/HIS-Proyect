<script setup lang="ts">
// Comprobantes de Pago es una vista de consulta/reimpresión; el cobro se registra en Cobro por Paciente.
definePageMeta({ layout: 'app', middleware: ['auth', 'panel'] })
await navigateTo('/app/caja/cobro-por-paciente')
</script>
<template><div /></template>
