<!-- frontend/layouts/app.vue -->
<template>
  <div class="h-screen flex overflow-hidden app-shell" :class="{ 'app-compact-tables': preferences.compactTables, 'app-reduce-motion': preferences.reduceMotion }" style="background: var(--mist)">

    <!-- SIDEBAR -->
    <aside
      class="hospital-sidebar flex flex-col shrink-0 transition-all duration-300"
      :style="{ width: collapsed ? '64px' : '250px', background: '#ffffff', color: '#081b3d' }"
    >
      <!-- Logo -->
      <NuxtLink :to="link('/app')" class="hospital-brand" :class="{ 'hospital-brand--collapsed': collapsed }" aria-label="Panel hospitalario, ir al escritorio">
        <span class="hospital-brand-mark" aria-hidden="true">
          <svg viewBox="0 0 32 32" fill="none">
            <path d="M11 4h10v7h7v10h-7v7H11v-7H4V11h7V4Z" stroke="currentColor" stroke-width="1.6" stroke-linejoin="round" />
            <path d="M12 16h8M16 12v8" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" />
          </svg>
        </span>
        <span v-if="!collapsed" class="hospital-brand-copy">
          <span class="hospital-brand-title">Panel hospitalario</span>
          <span class="hospital-brand-caption">Gestión asistencial</span>
        </span>
      </NuxtLink>

      <!-- Nav -->
      <nav ref="navRef" class="flex-1 overflow-y-auto overflow-x-hidden py-3 px-2 sidebar-scroll">

        <!-- Escritorio -->
        <NuxtLink :to="link('/app')" class="nav-link desktop-link mb-2" :class="activo('/app')" aria-label="Escritorio">
          <UIcon name="i-heroicons-squares-2x2" class="w-4 h-4 shrink-0" />
          <span v-if="!collapsed" class="truncate">Escritorio</span>
        </NuxtLink>

        <div class="nav-divider" />

        <!-- Grupos -->
        <div
          v-for="grupo in gruposVisibles"
          :key="grupo.label"
          class="nav-group"
        >
          <!-- Cabecera grupo principal -->
          <button
            v-if="!collapsed"
            class="nav-group-header"
            @click="toggleGrupo(grupo.label)"
          >
            <span class="nav-group-icon">
              <UIcon :name="grupo.icon || 'i-heroicons-folder'" class="w-3.5 h-3.5" />
            </span>
            <span class="nav-group-label">{{ grupo.label }}</span>
            <UIcon
              :name="grupoAbierto(grupo.label) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'"
              class="w-3 h-3 shrink-0 nav-group-chevron"
            />
          </button>
          <button
            v-else
            class="nav-group-header-collapsed"
            :title="grupo.label"
            @click="toggleGrupo(grupo.label)"
          >
            <UIcon :name="grupo.icon || 'i-heroicons-folder'" class="w-4 h-4" />
          </button>

          <!-- Items del grupo -->
          <div v-show="grupoAbierto(grupo.label) || collapsed" class="nav-group-items">
            <NuxtLink
              v-for="item in grupo.items"
              :key="item.path"
              :to="link(item.path)"
              class="nav-link nav-sub"
              :class="activo(item.path)"
            >
              <UIcon :name="item.icon || 'i-heroicons-chevron-right'" class="w-3.5 h-3.5 shrink-0 opacity-60" />
              <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
            </NuxtLink>
          </div>
        </div>
      </nav>

      <!-- Footer usuario -->
      <div class="sidebar-footer p-2 border-t shrink-0">
        <div v-if="!collapsed" class="sidebar-user-card mb-1.5 flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold shrink-0" style="background: var(--teal); color: white">
            {{ inicialesUsuario }}
          </div>
          <div class="min-w-0">
            <p class="text-sm font-medium truncate" style="color: var(--navy)">{{ authStore.user?.name }}</p>
            <p class="text-xs truncate" style="color: #63758b">{{ authStore.user?.email }}</p>
          </div>
        </div>
        <button @click="handleLogout"
          class="nav-link w-full justify-center gap-2"
          :class="collapsed ? 'px-0' : ''">
          <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-4 h-4 shrink-0" />
          <span v-if="!collapsed">Cerrar sesión</span>
        </button>
      </div>
    </aside>

    <!-- CONTENIDO -->
    <div class="flex-1 flex flex-col min-w-0">

      <!-- Header -->
      <header
        class="hospital-topbar h-16 flex items-center gap-4 px-6 shrink-0 bg-white relative"
        style="border-bottom: 1px solid #e6ebef; box-shadow: 0 3px 12px rgba(15, 35, 55, 0.025)"
      >
        <button
          class="p-2 rounded-lg hover:bg-black/5 transition-colors shrink-0"
          @click="collapsed = !collapsed"
        >
          <UIcon
            :name="collapsed ? 'i-heroicons-bars-3' : 'i-heroicons-chevron-double-left'"
            class="w-5 h-5"
            style="color: #63758b"
          />
        </button>

        <div class="hidden md:flex items-center text-sm shrink-0 greeting-pill">
          <UIcon name="i-heroicons-sun" class="w-4 h-4" style="color: #009eb2" />
          <span>{{ saludoHora }}</span>
        </div>

        <div class="flex-1 max-w-sm ml-2">
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full"
            style="background: #f1f4f6; border: 1px solid #e6ebef">
            <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4 shrink-0" style="color: #63758b" />
            <input
              placeholder="Buscar..."
              class="bg-transparent border-none outline-none text-sm w-full"
              style="color: var(--navy)"
            />
          </div>
        </div>

        <div class="ml-auto flex items-center gap-1 shrink-0">
          <button class="p-2 rounded-lg hover:bg-black/5 transition-colors" title="Ayuda">
            <UIcon name="i-heroicons-question-mark-circle" class="w-5 h-5" style="color: #63758b" />
          </button>

          <div class="notif-wrapper relative">
            <button class="relative p-2 rounded-lg hover:bg-black/5 transition-colors" title="Pendientes" @click="notifOpen = !notifOpen">
              <UIcon name="i-heroicons-bell" class="w-5 h-5" style="color: #63758b" />
              <span v-if="totalPendientes > 0" class="notif-badge">{{ totalPendientes > 9 ? '9+' : totalPendientes }}</span>
            </button>
            <div v-if="notifOpen" class="notif-panel">
              <div class="notif-panel-header">
                <span>Pendientes de hoy</span>
              </div>
              <div v-if="cargandoPendientes" class="notif-empty">Cargando...</div>
              <div v-else-if="!pendientes.length" class="notif-empty">Sin pendientes por ahora.</div>
              <ul v-else class="notif-list">
                <li
                  v-for="p in pendientes"
                  :key="p.label"
                  class="notif-item"
                  @click="notifOpen = false; navigateTo(link(p.path))"
                >
                  <span class="notif-dot" :style="{ background: p.color }" />
                  <div class="notif-item-body">
                    <p class="notif-title">{{ p.valor }} {{ p.label }}</p>
                  </div>
                </li>
              </ul>
            </div>
          </div>

          <NuxtLink :to="link('/app/ajustes')" class="p-2 rounded-lg hover:bg-black/5 transition-colors flex" title="Ajustes del panel hospitalario" aria-label="Ajustes del panel hospitalario">
            <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5" style="color: #63758b" />
          </NuxtLink>

          <div class="w-px h-6 mx-1" style="background: #e6ebef" />

          <div class="settings-wrapper relative">
            <button class="flex items-center gap-2 pl-1.5 pr-3 py-1.5 rounded-full hover:bg-black/5 transition-colors" @click="profileOpen = !profileOpen">
              <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold text-white shrink-0" style="background: var(--teal)">
                {{ inicialesUsuario }}
              </div>
              <span class="hidden lg:block text-sm font-medium" style="color: var(--navy)">
                {{ authStore.user?.name || 'Usuario' }}
              </span>
              <UIcon name="i-heroicons-chevron-down" class="hidden lg:block w-3.5 h-3.5" style="color: #63758b" />
            </button>
            <div v-if="profileOpen" class="settings-menu">
              <NuxtLink :to="link('/app/perfil')" class="settings-item" @click="profileOpen = false">
                <UIcon name="i-heroicons-user-circle" class="w-4 h-4" />
                Mi Perfil
              </NuxtLink>
              <button class="settings-item settings-item--danger" @click="handleLogout">
                <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-4 h-4" />
                Cerrar Sesión
              </button>
            </div>
          </div>
        </div>
      </header>

      <!-- Página -->
      <main class="flex-1 overflow-y-auto">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
// Poppins se carga globalmente via assets/css/hospital-theme.css -- no hace
// falta useHead() acá ni en ninguna página del panel hospitalario.
const authStore = useAuthStore()
const { link, activo, gruposVisibles, rutaMenuActual } = useHospitalNav()
const { api } = useApi()
const route = useRoute()
const collapsed = ref(false)
const { preferences, storageKey, load: loadPreferences } = useHospitalPreferences()
watch(() => preferences.value.collapsedSidebar, value => { collapsed.value = value })
watch(storageKey, () => { if (import.meta.client) loadPreferences() })
const navRef = ref<HTMLElement | null>(null)
const notifOpen = ref(false)
const profileOpen = ref(false)
const cargandoPendientes = ref(false)
interface Pendiente { label: string; valor: number; path: string; color: string }
const pendientes = ref<Pendiente[]>([])
const totalPendientes = computed(() => pendientes.value.reduce((acc, p) => acc + p.valor, 0))

async function cargarPendientes() {
  cargandoPendientes.value = true
  try {
    if (authStore.user?.role === 'medico') {
      const d = await api<any>('/app/dashboard/medico')
      pendientes.value = [
        d.kpis.citas_hoy_pendientes > 0 && { label: 'citas por atender hoy', valor: d.kpis.citas_hoy_pendientes, path: '/app/admision/programacion-medica', color: '#6495ed' },
      ].filter(Boolean) as Pendiente[]
    } else {
      const d = await api<any>('/app/dashboard/resumen')
      pendientes.value = [
        d.kpis.citas_hoy_pendientes > 0 && { label: 'citas por atender hoy', valor: d.kpis.citas_hoy_pendientes, path: '/app/consulta-externa/citas-por-confirmar', color: '#6495ed' },
        d.kpis.emergencias_en_atencion > 0 && { label: 'emergencias en atención', valor: d.kpis.emergencias_en_atencion, path: '/app/emergencia/atenciones', color: '#c13f2c' },
        d.kpis.lab_pendientes > 0 && { label: 'órdenes de laboratorio pendientes', valor: d.kpis.lab_pendientes, path: '/app/laboratorio/ordenes', color: '#b8862b' },
        d.kpis.recetas_pendientes > 0 && { label: 'recetas pendientes', valor: d.kpis.recetas_pendientes, path: '/app/farmacia/recetas', color: '#1e7d4f' },
      ].filter(Boolean) as Pendiente[]
    }
  } catch {
    pendientes.value = []
  } finally {
    cargandoPendientes.value = false
  }
}

function cerrarMenusSiFuera(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (notifOpen.value && !target.closest('.notif-wrapper')) notifOpen.value = false
  if (profileOpen.value && !target.closest('.settings-wrapper')) profileOpen.value = false
}

let pendientesTimer: any
onMounted(() => {
  loadPreferences()
  collapsed.value = preferences.value.collapsedSidebar
  cargarPendientes()
  pendientesTimer = setInterval(cargarPendientes, 45000)
  document.addEventListener('click', cerrarMenusSiFuera)
})
onUnmounted(() => {
  if (pendientesTimer) clearInterval(pendientesTimer)
  document.removeEventListener('click', cerrarMenusSiFuera)
})

// Acordeon: un solo grupo abierto a la vez -- con ~22 grupos y varios items
// cada uno, tenerlos todos abiertos de entrada obligaba a bajar mucho para
// encontrar donde uno esta parado. Al navegar, se abre solo el grupo de la
// ruta actual y se hace scroll hasta el item activo.
const gruposAbiertos = ref<Record<string, boolean>>({})

function grupoAbierto(label: string): boolean {
  return gruposAbiertos.value[label] === true
}

function toggleGrupo(label: string) {
  const abrir = !grupoAbierto(label)
  gruposAbiertos.value = abrir ? { [label]: true } : {}
}

function sincronizarMenu() {
  const ruta = rutaMenuActual.value
  const grupo = gruposVisibles.value.find(g => g.items.some(item => item.path === ruta))
  gruposAbiertos.value = grupo ? { [grupo.label]: true } : {}
  nextTick(() => {
    navRef.value?.querySelector('.nav-active')?.scrollIntoView({ block: 'center', behavior: preferences.value.reduceMotion ? 'auto' : 'smooth' })
  })
}

watch(
  [() => route.path, () => gruposVisibles.value.map(g => g.label).join('|')],
  sincronizarMenu,
  { immediate: true },
)

const horaActual = new Date().getHours()
const saludoHora = computed(() => {
  if (horaActual < 12) return 'Buenos días'
  if (horaActual < 19) return 'Buenas tardes'
  return 'Buenas noches'
})
const saludoEmoji = computed(() => {
  if (horaActual < 12) return '☀️'
  if (horaActual < 19) return '🌤️'
  return '🌙'
})

const inicialesUsuario = computed(() => {
  const nombre = authStore.user?.name || ''
  return nombre
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((p: string) => p[0]?.toUpperCase())
    .join('') || 'U'
})

const handleLogout = async () => {
  // Capturar el tenant ANTES de logout(): borra authStore.user, y sin el
  // tenant en la URL el siguiente login no manda X-Tenant-ID y el backend
  // cae al fallback por dominio (404 o el hospital equivocado). Ademas
  // redirigia a /login (panel admin) en vez de /app/login.
  const tenantId = route.query.tenant as string || authStore.user?.tenant_id || ''
  await authStore.logout()
  await navigateTo(tenantId ? `/app/login?tenant=${tenantId}` : '/app/login')
}
</script>

<style scoped>
@media (min-width: 768px) {
  .app-compact-tables :deep(main table td),
  .app-compact-tables :deep(main table th) {
    padding-top: 6px !important;
    padding-bottom: 6px !important;
  }
}
.app-reduce-motion :deep(*),
.app-reduce-motion :deep(*::before),
.app-reduce-motion :deep(*::after) {
  animation-duration: .01ms !important;
  animation-iteration-count: 1 !important;
  transition-duration: .01ms !important;
  scroll-behavior: auto !important;
}
/* La identidad de color y tipografía de TODO el panel hospitalario
   (sidebar, topbar y cada página bajo /app/*) vive en un solo archivo:
   assets/css/hospital-theme.css (".app-shell"). No redefinir --ink/--teal/
   etc localmente en páginas nuevas -- ya se heredan desde acá. Antes cada
   página (Dashboard, Panel de Camas, Citados, Pacientes...) repetía el
   mismo bloque de variables en su propio <style scoped>; quedó centralizado
   para que un cambio de paleta futuro se haga una sola vez. */

/* Links generales (Escritorio, submódulos, cerrar sesión) */
.hospital-brand { display:flex; align-items:center; gap:11px; min-height:76px; padding:14px 18px; flex-shrink:0; color:white; text-decoration:none; border-bottom:1px solid rgba(255,255,255,.12); }
.hospital-brand--collapsed { justify-content:center; padding:14px 0; }
.hospital-brand-mark { display:flex; align-items:center; justify-content:center; width:32px; height:36px; flex-shrink:0; color:#e3edfc; }
.hospital-brand-mark svg { width:32px; height:32px; }
.hospital-brand-copy { display:flex; flex-direction:column; gap:4px; min-width:0; }
.hospital-brand-title { font-size:14px; line-height:1.3; font-weight:600; letter-spacing:-.15px; }
.hospital-brand-caption { font-size:11px; line-height:1.4; color:#cfdbef; }
.hospital-brand:focus-visible { outline:2px solid white; outline-offset:-4px; }
.desktop-link.nav-active { background:rgba(255,255,255,.12) !important; box-shadow:inset 3px 0 0 #bfd4fa; border-radius:4px; }
.nav-link {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.82rem;
  color: rgba(255, 255, 255, 0.88);
  transition: background 0.15s ease, color 0.15s ease;
  text-decoration: none;
  width: 100%;
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
  padding-left: 2.1rem;
  gap: 0.55rem;
  font-size: 0.8rem;
}

/* Separador entre Escritorio y los grupos */
.nav-divider {
  height: 1px;
  margin: 0.5rem 0.5rem 0.75rem;
  background: rgba(255, 255, 255, 0.08);
}

/* Grupo de módulo */
.nav-group {
  margin-bottom: 0.15rem;
  border-radius: 8px;
}

/* Cabecera del grupo (expandido) */
.nav-group-header {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  width: 100%;
  padding: 0.55rem 0.65rem;
  border-radius: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background 0.15s ease;
  color: #ffffff;
}
.nav-group-header:hover {
  background: rgba(255, 255, 255, 0.06);
}

.nav-group-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 22px;
  height: 22px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.nav-group-label {
  flex: 1;
  text-align: left;
  font-size: 0.8rem;
  font-weight: 600;
  text-transform: none;
  letter-spacing: 0;
  line-height: 1.2;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.nav-group-chevron {
  opacity: 0.6;
}

/* Cabecera del grupo (sidebar colapsado, solo ícono) */
.nav-group-header-collapsed {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  padding: 0.55rem 0;
  border-radius: 8px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #ffffff;
  transition: background 0.15s ease;
}
.nav-group-header-collapsed:hover {
  background: rgba(255, 255, 255, 0.06);
}

/* Items dentro del grupo */
.nav-group-items {
  display: flex;
  flex-direction: column;
  gap: 0.15rem;
  padding-top: 0.15rem;
  padding-bottom: 0.25rem;
}

/* Scroll del sidebar sin barra visible: se puede desplazar con la rueda o
   arrastrando, pero no queda una barra ocupando espacio ni compitiendo con
   el scroll de la derecha (el de la pagina). */
.sidebar-scroll {
  scrollbar-width: none; /* Firefox */
  -ms-overflow-style: none; /* Edge/IE legado */
}
.sidebar-scroll::-webkit-scrollbar {
  display: none; /* Chrome, Safari, Edge Chromium */
}

/* ============ CAMPANA DE PENDIENTES / MENÚ DE PERFIL ============ */
.notif-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 16px;
  height: 16px;
  padding: 0 3px;
  border-radius: 8px;
  background: var(--alert);
  color: white;
  font-size: 0.625rem;
  font-weight: 700;
  line-height: 16px;
  text-align: center;
}
.notif-panel {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 320px;
  max-width: calc(100vw - 2rem);
  max-height: 360px;
  display: flex;
  flex-direction: column;
  background: var(--paper);
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
  overflow: hidden;
  z-index: 50;
}
.notif-panel-header {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--line);
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--ink);
}
.notif-empty {
  padding: 2rem 1rem;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--ink-soft);
}
.notif-list {
  overflow-y: auto;
  list-style: none;
  margin: 0;
  padding: 0;
}
.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid var(--line);
  transition: background 0.15s ease;
}
.notif-item:last-child {
  border-bottom: none;
}
.notif-item:hover {
  background: var(--mist);
}
.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 0.375rem;
  flex-shrink: 0;
}
.notif-item-body {
  min-width: 0;
}
.notif-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.settings-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 200px;
  display: flex;
  flex-direction: column;
  padding: 0.375rem;
  background: var(--paper);
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.18);
  z-index: 50;
}
.settings-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.625rem;
  border-radius: 8px;
  border: none;
  background: none;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  text-decoration: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
}
.settings-item:hover {
  background: var(--mist);
}
.settings-item--danger {
  color: var(--alert);
}
/* Navigation aligned with the hospital dashboard. */
.hospital-sidebar { border-right:1px solid #e4eaf0; }
.hospital-brand { color:#081b3d; border-bottom-color:#e4eaf0; }
.hospital-brand-mark { color:#009eb2; }
.hospital-brand-caption { color:#63758b; }
.hospital-brand-title { font-weight:500; }
.hospital-brand:focus-visible { outline-color:#009eb2; }
.nav-link, .nav-group-header, .nav-group-header-collapsed { color:#354761; }
.nav-link:hover, .nav-group-header:hover, .nav-group-header-collapsed:hover { color:#007e91; background:#f0fafb; }
.nav-group-label { font-weight:500; line-height:1.5; text-transform:none; letter-spacing:0; }
.nav-group-header { padding-top:11px; padding-bottom:11px; border-radius:10px; }
.nav-group-icon { background:transparent; color:#71869b; }
.nav-group-chevron { color:#71869b; opacity:1; }
.nav-active, .desktop-link.nav-active {
  background: var(--teal-soft) !important;
  color: #007e91 !important;
  box-shadow: inset 3px 0 0 var(--teal), 0 1px 4px rgba(0, 158, 178, 0.14);
  border-radius: 10px;
  font-weight: 500;
}
.nav-divider { background:#e4eaf0; }
.sidebar-footer { border-color:#e4eaf0 !important; background:#fafcfd; }
.sidebar-user-card { padding:10px 12px; border-radius:12px; background:var(--teal-soft); }
.hospital-topbar { color:#081b3d; }
.hospital-topbar input::placeholder { color:#63758b; }
.greeting-pill { display:inline-flex; align-items:center; gap:8px; padding:6px 12px; border-radius:999px; background:var(--teal-soft); }
.greeting-pill span { color:#007e91 !important; font-weight:500; }
.hospital-topbar a:focus-visible, .hospital-topbar button:focus-visible, .hospital-sidebar a:focus-visible, .hospital-sidebar button:focus-visible { outline:2px solid #009eb2; outline-offset:-2px; }
@media(max-width:640px) { .hospital-topbar { padding-left:10px; padding-right:10px; gap:8px; } }
</style>
