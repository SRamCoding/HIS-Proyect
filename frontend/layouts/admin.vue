<!-- layouts/admin.vue -->
<template>
  <div class="h-screen flex overflow-hidden" style="background: var(--mist)">
    <!-- Overlay móvil -->
    <div
      v-if="mobileOpen"
      class="fixed inset-0 z-30 md:hidden"
      style="background: rgba(0,0,0,0.5)"
      @click="mobileOpen = false"
    />

    <aside
      class="flex flex-col shrink-0 h-screen transition-all duration-200 fixed md:relative inset-y-0 left-0 z-40"
      :class="[
        collapsed ? 'md:w-[72px]' : 'md:w-64',
        'w-64',
        mobileOpen ? 'translate-x-0' : '-translate-x-full md:translate-x-0'
      ]"
      style="background: var(--navy); color: white"
    >
      <!-- Logo -->
      <div
        class="h-16 flex items-center shrink-0 border-b"
        :class="collapsed ? 'gap-2.5 px-5 md:justify-center md:px-0' : 'gap-2.5 px-5'"
        style="border-color: rgba(255,255,255,0.08)"
      >
        <img src="/logo.png" alt="ERP Hospitalario" class="w-8 h-8 rounded-md object-contain shrink-0" />
        <span class="font-semibold text-sm tracking-tight truncate" :class="{ 'md:hidden': collapsed }">ERP Hospitalario</span>
        <button class="ml-auto p-1.5 rounded-lg hover:bg-white/10 md:hidden" @click="mobileOpen = false">
          <UIcon name="i-heroicons-x-mark" class="w-5 h-5" style="color: rgba(255,255,255,0.7)" />
        </button>
      </div>

      <!-- Nav -->
      <nav class="sidebar-nav flex-1 px-3 py-4 overflow-y-auto overflow-x-hidden space-y-5" @click="onNavClick">

        <NuxtLink to="/admin" class="nav-link" :class="{ 'nav-active': route.path === '/admin', 'nav-collapsed': collapsedDesktop }">
          <UIcon name="i-heroicons-squares-2x2" class="nav-icon" />
          <span :class="{ 'md:hidden': collapsed }">Escritorio</span>
        </NuxtLink>

        <div>
          <p class="nav-group-label" :class="{ 'md:hidden': collapsed }">Administracion Global</p>
          <div class="space-y-0.5">
            <NuxtLink to="/admin/hospitales" class="nav-link nav-sub" :class="{ 'nav-active': route.path.startsWith('/admin/hospitales'), 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-building-office-2" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Hospitales</span>
            </NuxtLink>
            <NuxtLink to="/admin/usuarios?tipo=admin" class="nav-link nav-sub" :class="{ 'nav-active': route.path === '/admin/usuarios' && route.query.tipo === 'admin', 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-user-circle" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Administradores</span>
            </NuxtLink>
            <NuxtLink to="/admin/usuarios" class="nav-link nav-sub" :class="{ 'nav-active': route.path === '/admin/usuarios' && !route.query.tipo, 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-users" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Usuarios por Hospital</span>
            </NuxtLink>
          </div>
        </div>

        <div>
          <p class="nav-group-label" :class="{ 'md:hidden': collapsed }">Administracion de Modulos</p>
          <div class="space-y-0.5">
            <NuxtLink to="/admin/modulos" class="nav-link nav-sub" :class="{ 'nav-active': route.path === '/admin/modulos', 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-squares-plus" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Catalogo de Modulos</span>
            </NuxtLink>
            <NuxtLink to="/admin/modulos/dependencias" class="nav-link nav-sub" :class="{ 'nav-active': route.path === '/admin/modulos/dependencias', 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-link" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Dependencias entre Modulos</span>
            </NuxtLink>
            <NuxtLink to="/admin/niveles-hospitalarios" class="nav-link nav-sub" :class="{ 'nav-active': route.path.startsWith('/admin/niveles-hospitalarios'), 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-building-library" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Niveles Hospitalarios</span>
            </NuxtLink>
          </div>
        </div>

        <div>
          <p class="nav-group-label" :class="{ 'md:hidden': collapsed }">Reportes del Sistema</p>
          <div class="space-y-0.5">
            <NuxtLink to="/admin/reportes/mensuales" class="nav-link nav-sub" :class="{ 'nav-active': route.path === '/admin/reportes/mensuales', 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-chart-bar" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Reportes Mensuales</span>
            </NuxtLink>
              <NuxtLink to="/admin/reportes/hospitales-modulos" class="nav-link nav-sub" :class="{ 'nav-active': route.path === '/admin/reportes/hospitales-modulos', 'nav-collapsed': collapsedDesktop }">
                <UIcon name="i-heroicons-building-office-2" class="nav-icon" />
                <span :class="{ 'md:hidden': collapsed }">Hospitales y Módulos</span>
              </NuxtLink>
            <NuxtLink to="/admin/reportes/exportar" class="nav-link nav-sub" :class="{ 'nav-active': route.path === '/admin/reportes/exportar', 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-arrow-down-tray" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Exportar Datos</span>
            </NuxtLink>
          </div>
        </div>

        <div>
          <p class="nav-group-label" :class="{ 'md:hidden': collapsed }">Auditorias</p>
          <div class="space-y-0.5">
            <NuxtLink to="/admin/auditoria" class="nav-link nav-sub" :class="{ 'nav-active': route.path === '/admin/auditoria', 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-magnifying-glass" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Auditoria del ERP</span>
            </NuxtLink>
            <NuxtLink to="/admin/auditoria/hospital" class="nav-link nav-sub" :class="{ 'nav-active': route.path === '/admin/auditoria/hospital', 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-building-office" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Auditoria por Hospital</span>
            </NuxtLink>
            <NuxtLink to="/admin/auditoria/logs" class="nav-link nav-sub" :class="{ 'nav-active': route.path === '/admin/auditoria/logs', 'nav-collapsed': collapsedDesktop }">
              <UIcon name="i-heroicons-clipboard-document-list" class="nav-icon" />
              <span :class="{ 'md:hidden': collapsed }">Logs de la BD del sistema</span>
            </NuxtLink>
          </div>
        </div>

      </nav>

      <!-- Footer -->
      <div class="p-3 border-t shrink-0" style="border-color: rgba(255,255,255,0.08)">
        <div
          class="flex items-center gap-2.5 rounded-lg mb-1 px-2.5 py-2"
          :class="{ 'md:justify-center md:py-2': collapsed }"
          style="background: rgba(255,255,255,0.05)"
        >
          <UAvatar :alt="authStore.user?.name" size="sm" />
          <div class="min-w-0" :class="{ 'md:hidden': collapsed }">
            <p class="text-sm font-medium truncate leading-tight">{{ authStore.user?.name }}</p>
            <p class="text-xs truncate" style="color: #7fa1b3">{{ authStore.user?.email }}</p>
          </div>
        </div>
        <button @click="handleLogout" class="nav-link w-full text-left" :class="{ 'nav-collapsed': collapsedDesktop }">
          <UIcon name="i-heroicons-arrow-left-on-rectangle" class="nav-icon" />
          <span :class="{ 'md:hidden': collapsed }">Cerrar sesion</span>
        </button>
      </div>
    </aside>

    <!-- Contenido -->
    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
  <header
    class="h-16 flex items-center gap-2 sm:gap-4 px-3 sm:px-6 shrink-0"
    style="background: var(--navy); border-bottom: 1px solid rgba(255,255,255,0.08)"
  >
    <!-- Hamburguesa móvil -->
    <button
      class="p-2 rounded-lg hover:bg-white/10 transition-colors md:hidden"
      @click="mobileOpen = true"
    >
      <UIcon name="i-heroicons-bars-3" class="w-5 h-5" style="color: rgba(255,255,255,0.6)" />
    </button>

    <!-- Colapsar sidebar (solo escritorio) -->
    <button
      class="p-2 rounded-lg hover:bg-white/10 transition-colors hidden md:block"
      @click="collapsed = !collapsed"
    >
      <UIcon
        :name="collapsed ? 'i-heroicons-bars-3' : 'i-heroicons-chevron-double-left'"
        class="w-5 h-5"
        style="color: rgba(255,255,255,0.6)"
      />
    </button>

    <h2 class="text-sm font-medium shrink-0 truncate hidden sm:block" style="color: rgba(255,255,255,0.5)">
      {{ route.meta.title || 'Panel Administrativo' }}
    </h2>

    <div class="flex-1 max-w-sm ml-0 sm:ml-4 hidden sm:block">
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-full" style="background: rgba(255,255,255,0.08); border: 1px solid rgba(255,255,255,0.12)">
        <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4 shrink-0" style="color: rgba(255,255,255,0.4)" />
        <input
          placeholder="Buscar..."
          class="bg-transparent border-none outline-none text-sm w-full"
          style="color: white;"
        />
      </div>
    </div>

    <div class="ml-auto flex items-center gap-1">
      <button class="p-2 rounded-lg hover:bg-white/10 transition-colors hidden sm:block">
        <UIcon name="i-heroicons-bell" class="w-5 h-5" style="color: rgba(255,255,255,0.6)" />
      </button>
      <button class="p-2 rounded-lg hover:bg-white/10 transition-colors hidden sm:block">
        <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5" style="color: rgba(255,255,255,0.6)" />
      </button>
    </div>
  </header>
      <main class="flex-1 overflow-y-auto p-3 sm:p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const route = useRoute()
const collapsed = ref(false)
const mobileOpen = ref(false)

// En móvil el sidebar siempre se muestra expandido (nunca en modo icono),
// así que "collapsed" solo afecta el ancho/labels en escritorio (md:).
const collapsedDesktop = computed(() => collapsed.value)

watch(() => route.path, () => { mobileOpen.value = false })

function onNavClick(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (target.closest('a')) mobileOpen.value = false
}

const handleLogout = async () => {
  await authStore.logout()
  await navigateTo('/login')
}
</script>

<style scoped>
.sidebar-nav {
  scrollbar-width: none;
  -ms-overflow-style: none;
}
.sidebar-nav::-webkit-scrollbar {
  display: none;
}
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
/* El modo icono-solo del sidebar solo aplica en escritorio; en móvil
   el sidebar es un drawer que siempre muestra las etiquetas completas. */
@media (min-width: 768px) {
  .nav-collapsed {
    justify-content: center;
    padding-left: 0;
    padding-right: 0;
    border-left: none;
  }
  .nav-collapsed.nav-sub {
    padding-left: 0;
  }
}
.nav-icon {
  width: 17px;
  height: 17px;
  flex-shrink: 0;
  color: #7fa1b3;
}
</style>