<!-- pages/index.vue -->
<template>
  <div />
</template>

<script setup lang="ts">
const authStore = useAuthStore()

if (authStore.isAuthenticated) {
  await navigateTo(authStore.panelRoute)
} else {
  await navigateTo('/login')
}
</script>