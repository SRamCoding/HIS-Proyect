<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })
const route = useRoute()
await navigateTo({ path: '/app/consulta-externa/citas-por-confirmar', query: route.query }, { replace: true })
</script>
<template><div /></template>
