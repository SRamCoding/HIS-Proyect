<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const route = useRoute()
await navigateTo({ path: '/app/admision/agendamiento', query: route.query }, { replace: true })
</script>

<template><div /></template>
