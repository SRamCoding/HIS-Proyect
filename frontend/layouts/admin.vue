<!-- layouts/admin.vue -->
<template>
  <div class="min-h-screen flex" style="background: var(--mist)">
    <aside
      class="w-60 flex flex-col shrink-0"
      style="background: var(--navy); color: white"
    >
      <div class="h-16 flex items-center gap-2 px-5 border-b" style="border-color: rgba(255,255,255,0.1)">
        <div class="w-7 h-7 rounded flex items-center justify-center" style="background: var(--teal)">
          <span class="text-xs font-bold">+</span>
        </div>
        <span class="font-semibold text-sm">ERP Hospitalario</span>
      </div>

      <nav class="flex-1 px-3 py-4 space-y-0.5">
        <p class="px-3 text-xs font-medium mb-2" style="color: #7fa1b3">PANEL ADMIN</p>
        <NuxtLink v-for="item in navItems" :key="item.to" :to="item.to" class="nav-link">
          {{ item.label }}
        </NuxtLink>
      </nav>

      <div class="p-3 border-t" style="border-color: rgba(255,255,255,0.1)">
        <div class="px-3 py-2 rounded mb-1" style="background: rgba(255,255,255,0.05)">
          <p class="text-sm font-medium truncate">{{ authStore.user?.name }}</p>
          <p class="text-xs truncate" style="color: #7fa1b3">{{ authStore.user?.email }}</p>
        </div>
        <button @click="handleLogout" class="nav-link w-full text-left">
          Cerrar sesión
        </button>
      </div>
    </aside>

    <div class="flex-1 flex flex-col min-w-0">
      <header
        class="h-16 flex items-center px-6 shrink-0"
        style="background: var(--paper); border-bottom: 1px solid var(--line)"
      >
        <h2 class="text-sm font-medium" style="color: var(--ink-soft)">
          {{ route.meta.title || 'Panel Administrativo' }}
        </h2>
      </header>

      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const route = useRoute()

const navItems = [
  { label: 'Dashboard', to: '/admin' },
  { label: 'Hospitales', to: '/admin/hospitales' },
  { label: 'Usuarios', to: '/admin/usuarios' },
  { label: 'Módulos', to: '/admin/modulos' },
  { label: 'Auditoría', to: '/admin/auditoria' },
]

const handleLogout = async () => {
  await authStore.logout()
  await navigateTo('/login')
}
</script>

<style scoped>
.nav-link {
  display: block;
  padding: 0.55rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #c3d6df;
  transition: background 0.15s ease;
}
.nav-link:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}
.nav-link.router-link-active {
  background: var(--teal);
  color: white;
  font-weight: 500;
}
</style>