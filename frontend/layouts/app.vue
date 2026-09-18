<!-- frontend/layouts/app.vue -->
<template>
  <div class="h-screen flex overflow-hidden app-shell" style="background: var(--mist)">

    <!-- SIDEBAR -->
    <aside
      class="flex flex-col shrink-0 transition-all duration-300"
      :style="{ width: collapsed ? '64px' : '250px', background: 'var(--navy)', color: 'white' }"
    >
      <!-- Logo -->
      <div class="h-16 flex items-center gap-2.5 px-4 shrink-0 border-b" style="border-color: rgba(255,255,255,0.08)">
        <div class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 overflow-hidden bg-white/95 shadow-sm ring-1 ring-white/20">
          <img src="/sigarh.png" alt="Hospital" class="w-full h-full object-cover" />
        </div>
        <span v-if="!collapsed" class="font-semibold text-sm tracking-wide truncate">PANEL HOSPITALARIO</span>
      </div>

      <!-- Nav -->
      <nav ref="navRef" class="flex-1 overflow-y-auto overflow-x-hidden py-3 px-2 sidebar-scroll">

        <!-- Escritorio -->
        <NuxtLink :to="link('/app')" class="nav-link mb-2" :class="activo('/app')">
          <UIcon name="i-heroicons-home" class="w-4 h-4 shrink-0" />
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
      <div class="p-2 border-t shrink-0" style="border-color: rgba(255,255,255,0.08)">
        <div v-if="!collapsed" class="px-3 py-2.5 rounded-lg mb-1.5 flex items-center gap-2.5" style="background: rgba(255,255,255,0.05)">
          <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold shrink-0" style="background: var(--teal); color: white">
            {{ inicialesUsuario }}
          </div>
          <div class="min-w-0">
            <p class="text-sm font-medium truncate">{{ authStore.user?.name }}</p>
            <p class="text-xs truncate" style="color: #7fa1b3">{{ authStore.user?.email }}</p>
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
        class="h-16 flex items-center gap-4 px-6 shrink-0 bg-white relative"
        style="border-bottom: 1px solid #e6ebef; box-shadow: inset 16px 0 12px -12px rgba(15, 35, 55, 0.08)"
      >
        <button
          class="p-2 rounded-lg hover:bg-black/5 transition-colors shrink-0"
          @click="collapsed = !collapsed"
        >
          <UIcon
            :name="collapsed ? 'i-heroicons-bars-3' : 'i-heroicons-chevron-double-left'"
            class="w-5 h-5"
            style="color: #7a8894"
          />
        </button>

        <div class="hidden md:flex items-center gap-2 text-sm shrink-0">
          <span>{{ saludoEmoji }}</span>
          <span style="color: #9aa7b1">{{ saludoHora }}</span>
        </div>

        <div class="flex-1 max-w-sm ml-2">
          <div class="flex items-center gap-2 px-3 py-1.5 rounded-full"
            style="background: #f1f4f6; border: 1px solid #e6ebef">
            <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4 shrink-0" style="color: #9aa7b1" />
            <input
              placeholder="Buscar..."
              class="bg-transparent border-none outline-none text-sm w-full"
              style="color: var(--navy)"
            />
          </div>
        </div>

        <div class="ml-auto flex items-center gap-1 shrink-0">
          <button class="p-2 rounded-lg hover:bg-black/5 transition-colors" title="Ayuda">
            <UIcon name="i-heroicons-question-mark-circle" class="w-5 h-5" style="color: #7a8894" />
          </button>

          <div class="notif-wrapper relative">
            <button class="relative p-2 rounded-lg hover:bg-black/5 transition-colors" title="Pendientes" @click="notifOpen = !notifOpen">
              <UIcon name="i-heroicons-bell" class="w-5 h-5" style="color: #7a8894" />
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

          <NuxtLink :to="link('/app/perfil')" class="p-2 rounded-lg hover:bg-black/5 transition-colors flex" title="Configuración">
            <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5" style="color: #7a8894" />
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
              <UIcon name="i-heroicons-chevron-down" class="hidden lg:block w-3.5 h-3.5" style="color: #9aa7b1" />
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
const authStore = useAuthStore()
const { link, activo, gruposVisibles, rutaMenuActual } = useHospitalNav()
const { api } = useApi()
const route = useRoute()
const collapsed = ref(false)
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
    navRef.value?.querySelector('.nav-active')?.scrollIntoView({ block: 'center', behavior: 'smooth' })
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
/* Identidad de color exclusiva del panel hospitalario: un solo azul
   (cornflower #6495ED) para todo. Se sobreescriben las variables SOLO
   dentro de este layout (".app-shell"): como son custom properties de
   CSS, heredan hacia cualquier página/componente hijo renderizado adentro
   sin tocar la paleta global que usan Admin y SIGARH.
   --navy/--navy-hover/--navy-soft: fondo del sidebar y sus estados.
   --teal/--teal-dark/--teal-soft: acento (botones, íconos, activos) en
   todas las páginas de /app/*. Misma familia de azul, solo varía el tono
   para mantener contraste. */
.app-shell {
  --navy: #3e5c93;
  --navy-hover: #324a76;
  --navy-soft: #ecf2fd;
  --teal: #6495ed;
  --teal-dark: #3e5c93;
  --teal-soft: #ecf2fd;
}

/* Links generales (Escritorio, submódulos, cerrar sesión) */
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
  font-size: 0.7rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
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
</style>