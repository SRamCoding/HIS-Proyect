<!-- frontend/pages/app/index.vue -->
<template>
  <SMedicoPanel v-if="authStore.user?.role === 'medico'" />
  <SEnfermeriaPanel v-else-if="authStore.user?.role === 'enfermera'" />
  <DashboardGeneral v-else />
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const authStore = useAuthStore()
</script>
