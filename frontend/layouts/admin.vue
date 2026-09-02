<!-- layouts/admin.vue -->
<template>
  <div class="min-h-screen flex" style="background: var(--mist)">
    <aside class="w-64 flex flex-col shrink-0" style="background: var(--navy); color: white">
      <!-- Logo -->
      <div class="h-16 flex items-center gap-2 px-5 border-b" style="border-color: rgba(255,255,255,0.1)">
        <div class="w-7 h-7 rounded flex items-center justify-center" style="background: var(--teal)">
          <span class="text-xs font-bold">+</span>
        </div>
        <span class="font-semibold text-sm">ERP Hospitalario</span>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-4 overflow-y-auto space-y-4">

        <!-- Escritorio -->
        <NuxtLink to="/admin" class="nav-link" :class="{ 'nav-active': route.path === '/admin' }">
          <span class="nav-icon">⌂</span> Escritorio
        </NuxtLink>

        <!-- Administración Global -->
        <div>
          <p class="nav-group-label">Administración Global</p>
          <div class="space-y-0.5">
            <NuxtLink
              to="/admin/hospitales"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path.startsWith('/admin/hospitales') }"
            >
              <span class="nav-icon">🏥</span> Hospitales
            </NuxtLink>
            <NuxtLink
              to="/admin/usuarios?tipo=admin"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/usuarios' && route.query.tipo === 'admin' }"
            >
              <span class="nav-icon">👤</span> Administradores
            </NuxtLink>
            <NuxtLink
              to="/admin/usuarios"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/usuarios' && !route.query.tipo }"
            >
              <span class="nav-icon">👥</span> Usuarios por Hospital
            </NuxtLink>
          </div>
        </div>

        <!-- Administración de Módulos -->
        <div>
          <p class="nav-group-label">Administración de Módulos</p>
          <div class="space-y-0.5">
            <NuxtLink
              to="/admin/modulos"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/modulos' }"
            >
              <span class="nav-icon">⚙</span> Catálogo de Módulos
            </NuxtLink>
            <NuxtLink
              to="/admin/modulos/dependencias"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/modulos/dependencias' }"
            >
              <span class="nav-icon">🔗</span> Dependencias entre Módulos
            </NuxtLink>
            <NuxtLink
              to="/admin/niveles-hospitalarios"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path.startsWith('/admin/niveles-hospitalarios') }"
            >
              <span class="nav-icon">🏛</span> Niveles Hospitalarios
            </NuxtLink>
          </div>
        </div>

        <!-- Reportes del Sistema -->
        <div>
          <p class="nav-group-label">Reportes del Sistema</p>
          <div class="space-y-0.5">
            <NuxtLink
              to="/admin/reportes/mensuales"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/reportes/mensuales' }"
            >
              <span class="nav-icon">📊</span> Reportes Mensuales
            </NuxtLink>
            <NuxtLink
              to="/admin/reportes/exportar"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/reportes/exportar' }"
            >
              <span class="nav-icon">⬇</span> Exportar Datos
            </NuxtLink>
          </div>
        </div>

        <!-- Auditorías -->
        <div>
          <p class="nav-group-label">Auditorías</p>
          <div class="space-y-0.5">
            <NuxtLink
              to="/admin/auditoria"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/auditoria' }"
            >
              <span class="nav-icon">🔍</span> Auditoría del ERP
            </NuxtLink>
            <NuxtLink
              to="/admin/auditoria/hospital"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/auditoria/hospital' }"
            >
              <span class="nav-icon">🏥</span> Auditoría por Hospital
            </NuxtLink>
            <NuxtLink
              to="/admin/auditoria/logs"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/auditoria/logs' }"
            >
              <span class="nav-icon">📋</span> Logs de la BD del sistema
            </NuxtLink>
          </div>
        </div>

      </nav>

      <!-- Footer -->
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

    <!-- Contenido -->
    <div class="flex-1 flex flex-col min-w-0">
      <header class="h-16 flex items-center px-6 shrink-0" style="background: var(--paper); border-bottom: 1px solid var(--line)">
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
.nav-icon {
  font-size: 0.9rem;
  width: 16px;
  text-align: center;
  flex-shrink: 0;
}
</style>