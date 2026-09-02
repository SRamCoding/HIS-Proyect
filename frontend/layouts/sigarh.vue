<template>
  <div class="min-h-screen flex" style="background: var(--mist)">
    <aside class="w-64 flex flex-col shrink-0" style="background: var(--navy); color: white">
      <div class="h-16 flex items-center gap-2 px-5 border-b" style="border-color: rgba(255,255,255,0.1)">
        <div class="w-7 h-7 rounded flex items-center justify-center" style="background: var(--teal)">
          <span class="text-xs font-bold">S</span>
        </div>
        <span class="font-semibold text-sm">SIGARH</span>
      </div>

      <nav class="flex-1 px-3 py-4 overflow-y-auto space-y-3">
        <NuxtLink :to="link('/sigarh')" class="nav-link" :class="activo('/sigarh')">
          Escritorio
        </NuxtLink>

        <div v-for="grupo in gruposVisibles" :key="grupo.label">
          <p class="nav-group-label">{{ grupo.label }}</p>
          <div class="space-y-0.5">
            <NuxtLink
              v-for="item in grupo.items"
              :key="item.path"
              :to="link(item.path)"
              class="nav-link nav-sub"
              :class="activo(item.path)"
            >
              {{ item.label }}
            </NuxtLink>
          </div>
        </div>
      </nav>

      <div class="p-3 border-t" style="border-color: rgba(255,255,255,0.1)">
        <div class="px-3 py-2 rounded mb-1" style="background: rgba(255,255,255,0.05)">
          <p class="text-sm font-medium truncate">{{ authStore.user?.name }}</p>
          <p class="text-xs truncate" style="color: #7fa1b3">{{ authStore.user?.email }}</p>
        </div>
        <button @click="handleLogout" class="nav-link w-full text-left">Cerrar sesion</button>
      </div>
    </aside>

    <div class="flex-1 flex flex-col min-w-0">
      <header class="h-16 flex items-center px-6 shrink-0" style="background: var(--paper); border-bottom: 1px solid var(--line)">
        <h2 class="text-sm font-medium" style="color: var(--ink-soft)">Panel SIGARH</h2>
      </header>
      <main class="flex-1 overflow-y-auto p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const { link, activo, gruposVisibles } = useSigarhNav()

const handleLogout = async () => {
  await authStore.logout()
  await navigateTo('/login')
}
</script>

<style scoped>
.nav-group-label {
  padding: 0 0.75rem;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: #7fa1b3;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #c3d6df;
  transition: background 0.15s ease;
  text-decoration: none;
}
.nav-link:hover {
  background: rgba(255, 255, 255, 0.08);
  color: white;
}
.nav-active {
  background: var(--teal) !important;
  color: white !important;
  font-weight: 500;
}
.nav-sub {
  padding-left: 1rem;
  font-size: 0.8rem;
}
</style>