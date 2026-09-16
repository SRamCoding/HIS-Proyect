<template>
  <ArchivoClinicoPanel title="HC Electrónica" solo-digitalizadas />
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth', 'panel'] })
</script>
