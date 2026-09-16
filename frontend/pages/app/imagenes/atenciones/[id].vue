<template><ImagenesPanel mode="atenciones" :initial-id="String($route.params.id)" /></template>
<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth', 'panel'] })
</script>
