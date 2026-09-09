<template>
  <DestinoPanel
    titulo="Interconsultas desde Emergencia"
    descripcion="Solicitudes derivadas por el médico de emergencia para evaluación de otra especialidad."
    destino="INTERCONSULTA"
  />
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })
</script>
