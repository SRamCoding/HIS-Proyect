<!-- layouts/admin.vue -->
<template>
  <div class="h-screen flex overflow-hidden" style="background: var(--mist)">
    <aside
      class="flex flex-col shrink-0 h-screen transition-all duration-200"
      :class="collapsed ? 'w-[72px]' : 'w-64'"
      style="background: var(--navy); color: white"
    >
      <!-- Logo -->
      <div
        class="h-16 flex items-center shrink-0 border-b"
        :class="collapsed ? 'justify-center px-0' : 'gap-2.5 px-5'"
        style="border-color: rgba(255,255,255,0.08)"
      >
        <img
          src="/logo.png"
          alt="ERP Hospitalario"
          class="w-8 h-8 rounded-md object-contain shrink-0"
        />
        <span v-if="!collapsed" class="font-semibold text-sm tracking-tight truncate">
          ERP Hospitalario
        </span>
      </div>

      <!-- Nav -->
      <nav class="flex-1 px-3 py-4 overflow-y-auto overflow-x-hidden space-y-5">

        <!-- Escritorio -->
        <NuxtLink
          to="/admin"
          class="nav-link"
          :class="{ 'nav-active': route.path === '/admin', 'nav-collapsed': collapsed }"
        >
          <UIcon name="i-heroicons-squares-2x2" class="nav-icon" />
          <span v-if="!collapsed">Escritorio</span>
        </NuxtLink>

        <!-- Administración Global -->
        <div>
          <p v-if="!collapsed" class="nav-group-label">Administración Global</p>
          <div class="space-y-0.5">
            <NuxtLink
              to="/admin/hospitales"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path.startsWith('/admin/hospitales'), 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-building-office-2" class="nav-icon" />
              <span v-if="!collapsed">Hospitales</span>
            </NuxtLink>
            <NuxtLink
              to="/admin/usuarios?tipo=admin"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/usuarios' && route.query.tipo === 'admin', 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-user-circle" class="nav-icon" />
              <span v-if="!collapsed">Administradores</span>
            </NuxtLink>
            <NuxtLink
              to="/admin/usuarios"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/usuarios' && !route.query.tipo, 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-users" class="nav-icon" />
              <span v-if="!collapsed">Usuarios por Hospital</span>
            </NuxtLink>
          </div>
        </div>

        <!-- Administración de Módulos -->
        <div>
          <p v-if="!collapsed" class="nav-group-label">Administración de Módulos</p>
          <div class="space-y-0.5">
            <NuxtLink
              to="/admin/modulos"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/modulos', 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-squares-plus" class="nav-icon" />
              <span v-if="!collapsed">Catálogo de Módulos</span>
            </NuxtLink>
            <NuxtLink
              to="/admin/modulos/dependencias"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/modulos/dependencias', 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-link" class="nav-icon" />
              <span v-if="!collapsed">Dependencias entre Módulos</span>
            </NuxtLink>
            <NuxtLink
              to="/admin/niveles-hospitalarios"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path.startsWith('/admin/niveles-hospitalarios'), 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-building-library" class="nav-icon" />
              <span v-if="!collapsed">Niveles Hospitalarios</span>
            </NuxtLink>
          </div>
        </div>

        <!-- Reportes del Sistema -->
        <div>
          <p v-if="!collapsed" class="nav-group-label">Reportes del Sistema</p>
          <div class="space-y-0.5">
            <NuxtLink
              to="/admin/reportes/mensuales"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/reportes/mensuales', 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-chart-bar" class="nav-icon" />
              <span v-if="!collapsed">Reportes Mensuales</span>
            </NuxtLink>
            <NuxtLink
              to="/admin/reportes/exportar"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/reportes/exportar', 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-arrow-down-tray" class="nav-icon" />
              <span v-if="!collapsed">Exportar Datos</span>
            </NuxtLink>
          </div>
        </div>

        <!-- Auditorías -->
        <div>
          <p v-if="!collapsed" class="nav-group-label">Auditorías</p>
          <div class="space-y-0.5">
            <NuxtLink
              to="/admin/auditoria"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/auditoria', 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-magnifying-glass" class="nav-icon" />
              <span v-if="!collapsed">Auditoría del ERP</span>
            </NuxtLink>
            <NuxtLink
              to="/admin/auditoria/hospital"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/auditoria/hospital', 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-building-office" class="nav-icon" />
              <span v-if="!collapsed">Auditoría por Hospital</span>
            </NuxtLink>
            <NuxtLink
              to="/admin/auditoria/logs"
              class="nav-link nav-sub"
              :class="{ 'nav-active': route.path === '/admin/auditoria/logs', 'nav-collapsed': collapsed }"
            >
              <UIcon name="i-heroicons-clipboard-document-list" class="nav-icon" />
              <span v-if="!collapsed">Logs de la BD del sistema</span>
            </NuxtLink>
          </div>
        </div>

      </nav>

      <!-- Footer / usuario -->
      <div class="p-3 border-t shrink-0" style="border-color: rgba(255,255,255,0.08)">
        <div
          class="flex items-center gap-2.5 rounded-lg mb-1"
          :class="collapsed ? 'justify-center py-2' : 'px-2.5 py-2'"
          style="background: rgba(255,255,255,0.05)"
        >
          <UAvatar :alt="authStore.user?.name" size="sm" />
          <div v-if="!collapsed" class="min-w-0">
            <p class="text-sm font-medium truncate leading-tight">{{ authStore.user?.name }}</p>
            <p class="text-xs truncate" style="color: #7fa1b3">{{ authStore.user?.email }}</p>
          </div>
        </div>
        <button @click="handleLogout" class="nav-link w-full text-left" :class="{ 'nav-collapsed': collapsed }">
          <UIcon name="i-heroicons-arrow-left-on-rectangle" class="nav-icon" />
          <span v-if="!collapsed">Cerrar sesión</span>
        </button>
      </div>
    </aside>

    <!-- Contenido -->
    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
      <header
        class="h-16 flex items-center gap-4 px-6 shrink-0"
        style="background: var(--paper); border-bottom: 1px solid var(--line)"
      >
        <UButton
          :icon="collapsed ? 'i-heroicons-bars-3' : 'i-heroicons-chevron-double-left'"
          color="gray"
          variant="ghost"
          square
          size="sm"
          @click="collapsed = !collapsed"
        />

        <h2 class="text-sm font-medium shrink-0" style="color: var(--ink-soft)">
          {{ route.meta.title || 'Panel Administrativo' }}
        </h2>

        <UInput
          icon="i-heroicons-magnifying-glass"
          placeholder="Buscar…"
          size="sm"
          class="max-w-sm ml-4"
          :ui="{ rounded: 'rounded-full' }"
        />

        <div class="ml-auto flex items-center gap-2">
          <UButton
            icon="i-heroicons-bell"
            color="gray"
            variant="ghost"
            square
            :ui="{ rounded: 'rounded-full' }"
          />
          <UButton
            icon="i-heroicons-cog-6-tooth"
            color="gray"
            variant="ghost"
            square
            :ui="{ rounded: 'rounded-full' }"
          />
        </div>
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
const collapsed = ref(false)

const handleLogout = async () => {
  await authStore.logout()
  await navigateTo('/login')
}
</script>

<style scoped>
.nav-group-label {
  padding: 0 0.75rem;
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: #7fa1b3;
  text-transform: uppercase;
  margin-bottom: 0.375rem;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
  color: #c3d6df;
  border-left: 3px solid transparent;
  transition: background 0.15s ease, color 0.15s ease;
  text-decoration: none;
  white-space: nowrap;
}
.nav-link:hover {
  background: rgba(255, 255, 255, 0.06);
  color: white;
}
.nav-active {
  background: rgba(45, 212, 191, 0.12) !important;
  border-left-color: var(--teal) !important;
  color: white !important;
  font-weight: 500;
}
.nav-active .nav-icon {
  color: var(--teal);
}
.nav-sub {
  padding-left: 0.875rem;
  font-size: 0.8rem;
}
.nav-collapsed {
  justify-content: center;
  padding-left: 0;
  padding-right: 0;
  border-left: none;
}
.nav-collapsed.nav-sub {
  padding-left: 0;
}
.nav-icon {
  width: 17px;
  height: 17px;
  flex-shrink: 0;
  color: #7fa1b3;
}
</style>