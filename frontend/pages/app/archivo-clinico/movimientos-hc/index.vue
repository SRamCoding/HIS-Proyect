<template>
  <ArchivoClinicoPanel title="Movimientos de historias clínicas" />
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth', 'panel'] })
</script>
