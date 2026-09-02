<!-- layouts/sigarh.vue -->
<template>
  <div class="min-h-screen flex" style="background: var(--mist)">
    <aside class="w-64 flex flex-col shrink-0" style="background: var(--navy); color: white">
      <div class="h-16 flex items-center gap-2 px-5 border-b" style="border-color: rgba(255,255,255,0.1)">
        <div class="w-7 h-7 rounded flex items-center justify-center" style="background: var(--teal)">
          <span class="text-xs font-bold">S</span>
        </div>
        <span class="font-semibold text-sm">SIGARH</span>
      </div>

      <nav class="flex-1 px-3 py-4 overflow-y-auto space-y-4">
        <NuxtLink :to="`/sigarh?tenant=${tenantId}`" class="nav-link">
          Escritorio
        </NuxtLink>

        <div>
          <p class="nav-group-label">Recursos Humanos</p>
          <div class="space-y-0.5">
            <NuxtLink :to="`/sigarh/rrhh?tenant=${tenantId}`" class="nav-link nav-sub">Personal</NuxtLink>
            <NuxtLink :to="`/sigarh/roles-turno?tenant=${tenantId}`" class="nav-link nav-sub">Roles de Turno</NuxtLink>
            <NuxtLink :to="`/sigarh/asistencia?tenant=${tenantId}`" class="nav-link nav-sub">Asistencia</NuxtLink>
            <NuxtLink :to="`/sigarh/movimientos?tenant=${tenantId}`" class="nav-link nav-sub">Movimientos</NuxtLink>
          </div>
        </div>

        <div>
          <p class="nav-group-label">Mantenimiento</p>
          <div class="space-y-0.5">
            <NuxtLink :to="`/sigarh/mantenimiento?tenant=${tenantId}`" class="nav-link nav-sub">Configuracion</NuxtLink>
          </div>
        </div>
      </nav>

      <div class="p-3 border-t" style="border-color: rgba(255,255,255,0.1)">
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
const route = useRoute()
const authStore = useAuthStore()
const tenantId = computed(() => route.query.tenant as string || '')

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