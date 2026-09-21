<!-- layouts/admin.vue -->
<template>
  <!-- Al cerrar sesion se DESMONTA todo el contenido protegido (este bloque
       es la unica raiz que queda) en vez de solo taparlo con un overlay.
       Ganarle por z-index a un <Teleport to="body"> (los modales de SIGARH
       lo usan) es posible en teoria, pero fragil: depende de que ningun
       ancestro entre medio cree su propio contexto de apilamiento, un
       detalle facil de romper sin darse cuenta con un cambio de estilos
       futuro. Y aunque se tape visualmente, un elemento que sigue montado
       sigue siendo alcanzable por teclado (Tab) -- desmontar evita ambos
       problemas de raiz en vez de depender de ganar la pulseada de CSS. -->
  <div v-if="loggingOut" class="h-screen flex items-center justify-center" style="background: var(--mist)">
    <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
  </div>
  <div v-else class="h-screen flex overflow-hidden" style="background: var(--mist)">
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
        <button class="ml-auto p-1.5 rounded-lg hover:bg-white/10 md:hidden" aria-label="Cerrar menú" @click="mobileOpen = false">
          <UIcon name="i-heroicons-x-mark" class="w-5 h-5" style="color: rgba(255,255,255,0.7)" aria-hidden="true" />
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
        <button @click="handleLogout" class="nav-link w-full text-left" :class="{ 'nav-collapsed': collapsedDesktop }" title="Cierra la sesión en todos los dispositivos donde hayas iniciado sesión, no solo en este">
          <UIcon name="i-heroicons-arrow-left-on-rectangle" class="nav-icon" />
          <span :class="{ 'md:hidden': collapsed }">Cerrar sesion</span>
        </button>
      </div>
    </aside>

    <!-- Contenido -->
    <div class="flex-1 flex flex-col min-w-0 h-screen overflow-hidden">
  <header
    class="h-16 flex items-center gap-2 sm:gap-4 px-3 sm:px-6 shrink-0"
    style="background: var(--paper); border-bottom: 1px solid var(--line)"
  >
    <!-- Hamburguesa móvil -->
    <button
      class="p-2 rounded-lg hover:bg-[var(--mist)] transition-colors md:hidden"
      aria-label="Abrir menú"
      @click="mobileOpen = true"
    >
      <UIcon name="i-heroicons-bars-3" class="w-5 h-5" style="color: var(--ink-soft)" aria-hidden="true" />
    </button>

    <!-- Colapsar sidebar (solo escritorio) -->
    <button
      class="p-2 rounded-lg hover:bg-[var(--mist)] transition-colors hidden md:block"
      :aria-label="collapsed ? 'Expandir menú lateral' : 'Contraer menú lateral'"
      :aria-pressed="collapsed"
      @click="collapsed = !collapsed"
    >
      <UIcon
        :name="collapsed ? 'i-heroicons-bars-3' : 'i-heroicons-chevron-double-left'"
        class="w-5 h-5"
        style="color: var(--ink-soft)"
        aria-hidden="true"
      />
    </button>

    <h2 class="text-sm font-medium shrink-0 truncate hidden sm:block" style="color: var(--ink-soft)">
      {{ route.meta.title || 'Panel Administrativo' }}
    </h2>

    <div class="search-wrapper relative flex-1 max-w-sm ml-0 sm:ml-4 hidden sm:block">
      <div class="flex items-center gap-2 px-3 py-1.5 rounded-full" style="background: var(--mist); border: 1px solid var(--line)">
        <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4 shrink-0" style="color: var(--ink-soft)" aria-hidden="true" />
        <input
          v-model="searchQuery"
          type="search"
          aria-label="Buscar hospitales o cuentas admin"
          placeholder="Buscar hospitales, cuentas admin..."
          class="bg-transparent border-none outline-none text-sm w-full"
          style="color: var(--ink);"
          @focus="searchOpen = true"
          @keydown.esc="searchOpen = false"
          @keydown.enter="irAlPrimerResultado"
        />
        <UIcon v-if="searchLoading" name="i-heroicons-arrow-path" class="w-3.5 h-3.5 shrink-0 animate-spin" style="color: var(--ink-soft)" />
      </div>
      <div v-if="searchOpen && searchQuery.trim().length >= 2" class="search-panel">
        <div v-if="!searchLoading && searchError" class="notif-empty" style="color: var(--alert)">
          No se pudo buscar. Intenta de nuevo.
        </div>
        <div v-else-if="!searchLoading && !searchResultados.hospitales.length && !searchResultados.usuarios.length" class="notif-empty">
          Sin resultados para "{{ searchQuery }}"
        </div>
        <template v-else>
          <div v-if="searchResultados.hospitales.length" class="search-group-label">Hospitales</div>
          <NuxtLink
            v-for="h in searchResultados.hospitales" :key="'h-' + h.id"
            :to="`/admin/hospitales/${h.id}`" class="search-item" @click="cerrarBusqueda"
          >
            <UIcon name="i-heroicons-building-office-2" class="w-4 h-4 shrink-0" style="color: var(--navy)" />
            <div class="min-w-0">
              <p class="search-item-title">{{ h.name }}</p>
              <p class="search-item-sub">{{ h.domain }}</p>
            </div>
          </NuxtLink>
          <div v-if="searchResultados.usuarios.length" class="search-group-label">Cuentas admin</div>
          <NuxtLink
            v-for="u in searchResultados.usuarios" :key="'u-' + u.id"
            :to="`/admin/usuarios/${u.id}${u.tenant_id ? `?tenant_id=${u.tenant_id}` : ''}`" class="search-item" @click="cerrarBusqueda"
          >
            <UIcon name="i-heroicons-user-circle" class="w-4 h-4 shrink-0" style="color: var(--teal)" />
            <div class="min-w-0">
              <p class="search-item-title">{{ u.name }}</p>
              <p class="search-item-sub">{{ u.email }}</p>
            </div>
          </NuxtLink>
        </template>
      </div>
    </div>

    <div class="ml-auto flex items-center gap-1">
      <div class="notif-wrapper relative">
        <button
          class="relative p-2 rounded-lg hover:bg-[var(--mist)] transition-colors"
          :aria-label="notifUnread > 0 ? `Notificaciones, ${notifUnread} sin leer` : 'Notificaciones'"
          aria-haspopup="true"
          :aria-expanded="notifOpen"
          @click="toggleNotifs"
        >
          <UIcon name="i-heroicons-bell" class="w-5 h-5" style="color: var(--ink-soft)" aria-hidden="true" />
          <span v-if="notifUnread > 0" class="notif-badge" aria-hidden="true">{{ notifUnread > 9 ? '9+' : notifUnread }}</span>
        </button>
        <div v-if="notifOpen" class="notif-panel">
          <div class="notif-panel-header">
            <span>Notificaciones</span>
            <button v-if="notifUnread > 0" class="notif-mark-all" @click="marcarTodasLeidas">Marcar todas leídas</button>
          </div>
          <div v-if="notifLoading" class="notif-empty">Cargando...</div>
          <div v-else-if="notifError" class="notif-empty" style="color: var(--alert)">
            No se pudieron cargar las notificaciones.
            <button class="notif-mark-all" style="display: block; margin: 0.35rem auto 0" @click="cargarNotificaciones">Reintentar</button>
          </div>
          <div v-else-if="!notificaciones.length" class="notif-empty">Sin notificaciones</div>
          <ul v-else class="notif-list">
            <li
              v-for="n in notificaciones"
              :key="n.id"
              class="notif-item"
              :class="{ unread: !n.is_read }"
              @click="abrirNotif(n)"
            >
              <span class="notif-dot" :class="`notif-dot--${n.nivel}`" />
              <div class="notif-item-body">
                <p class="notif-title">{{ n.titulo }}</p>
                <p v-if="n.cuerpo" class="notif-desc">{{ n.cuerpo }}</p>
                <p class="notif-time">{{ formatRelativo(n.created_at) }}</p>
              </div>
            </li>
          </ul>
          <button v-if="!notifLoading && notificaciones.length < notifTotal" class="notif-cargar-mas" @click="cargarMasNotificaciones">
            <UIcon v-if="notifLoadingMas" name="i-heroicons-arrow-path" class="w-3.5 h-3.5 animate-spin" />
            <span>Cargar más</span>
          </button>
        </div>
      </div>
      <div class="settings-wrapper relative">
        <button
          class="p-2 rounded-lg hover:bg-[var(--mist)] transition-colors"
          aria-label="Configuración"
          aria-haspopup="true"
          :aria-expanded="settingsOpen"
          @click="settingsOpen = !settingsOpen"
        >
          <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5" style="color: var(--ink-soft)" aria-hidden="true" />
        </button>
        <div v-if="settingsOpen" class="settings-menu">
          <NuxtLink to="/admin/perfil" class="settings-item" @click="settingsOpen = false">
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
      <main class="flex-1 overflow-y-auto p-3 sm:p-6">
        <slot />
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
const authStore = useAuthStore()
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const collapsed = ref(false)
const mobileOpen = ref(false)

interface Notificacion {
  id: string
  titulo: string
  cuerpo: string | null
  nivel: string
  link: string | null
  is_read: boolean
  created_at: string
}

const notifOpen = ref(false)
const notifLoading = ref(false)
const notifLoadingMas = ref(false)
const notifError = ref(false)
const notifUnread = ref(0)
const notifTotal = ref(0)
const notificaciones = ref<Notificacion[]>([])
const NOTIF_PAGE_SIZE = 20
let notifTimer: ReturnType<typeof setInterval> | null = null

const cargarContadorNotif = async () => {
  try {
    const r = await api<{ count: number }>('/admin/notificaciones/no-leidas')
    notifUnread.value = r.count
  } catch {
    // silencioso: el contador no debe interrumpir el resto del panel
  }
}

const cargarNotificaciones = async () => {
  notifLoading.value = true
  notifError.value = false
  try {
    const r = await api<{ items: Notificacion[]; total: number }>(`/admin/notificaciones?limit=${NOTIF_PAGE_SIZE}`)
    notificaciones.value = r.items
    notifTotal.value = r.total
  } catch {
    // Antes esto tambien vaciaba la lista y la campana terminaba mostrando
    // "Sin notificaciones" igual que si de verdad no hubiera ninguna --
    // un fallo de red o del backend se leia como bandeja vacia. notifError
    // distingue ambos casos y ofrece reintentar en vez de mentir.
    notificaciones.value = []
    notifTotal.value = 0
    notifError.value = true
  } finally {
    notifLoading.value = false
  }
}

// Antes solo se podian ver las ultimas 20 notificaciones, sin forma de ver
// nada mas viejo -- el backend ya soporta offset, esto solo lo aprovecha.
const cargarMasNotificaciones = async () => {
  notifLoadingMas.value = true
  try {
    const r = await api<{ items: Notificacion[]; total: number }>(
      `/admin/notificaciones?limit=${NOTIF_PAGE_SIZE}&offset=${notificaciones.value.length}`
    )
    notificaciones.value.push(...r.items)
    notifTotal.value = r.total
  } catch {
    // si falla, el boton "Cargar mas" simplemente sigue disponible para reintentar
  } finally {
    notifLoadingMas.value = false
  }
}

const toggleNotifs = async () => {
  notifOpen.value = !notifOpen.value
  if (notifOpen.value) await cargarNotificaciones()
}

const marcarTodasLeidas = async () => {
  try {
    await api('/admin/notificaciones/leer-todas', { method: 'PATCH' })
    notificaciones.value.forEach(n => { n.is_read = true })
    notifUnread.value = 0
  } catch {
    // si falla, se queda como estaba -- no hay nada que revertir
  }
}

const abrirNotif = async (n: Notificacion) => {
  if (!n.is_read) {
    try {
      await api(`/admin/notificaciones/${n.id}/leer`, { method: 'PATCH' })
      n.is_read = true
      notifUnread.value = Math.max(0, notifUnread.value - 1)
    } catch {
      // no bloquea la navegacion si falla marcar como leida
    }
  }
  notifOpen.value = false
  if (n.link) router.push(n.link)
}

const formatRelativo = (fecha: string) => {
  const minutos = Math.floor((Date.now() - new Date(fecha).getTime()) / 60000)
  if (minutos < 1) return 'hace un momento'
  if (minutos < 60) return `hace ${minutos} min`
  const horas = Math.floor(minutos / 60)
  if (horas < 24) return `hace ${horas} h`
  return `hace ${Math.floor(horas / 24)} d`
}

const settingsOpen = ref(false)

interface SearchHospital { id: string; name: string; domain: string }
interface SearchUsuario { id: string; name: string; email: string; tenant_id: string | null }

const searchQuery = ref('')
const searchOpen = ref(false)
const searchLoading = ref(false)
const searchError = ref(false)
const searchResultados = reactive<{ hospitales: SearchHospital[]; usuarios: SearchUsuario[] }>({ hospitales: [], usuarios: [] })
let searchDebounce: ReturnType<typeof setTimeout> | null = null
// Se descartan respuestas que ya no son la ultima pedida: sin esto, una
// busqueda lenta ("hospital") podia resolver DESPUES de una mas reciente y
// mas especifica ("hospital-tuman"), pisando resultados correctos con unos
// obsoletos.
let searchToken = 0

watch(searchQuery, (valor) => {
  if (searchDebounce) clearTimeout(searchDebounce)
  // El token avanza YA, en cuanto cambia el texto -- no cuando arranca la
  // peticion 300ms despues. Si incrementara adentro del setTimeout, una
  // respuesta todavia en vuelo de la busqueda anterior podia colarse como
  // "vigente" durante la ventana de debounce del siguiente tecleo, porque
  // el token de esa respuesta y el token actual todavia coincidian.
  const miToken = ++searchToken
  const termino = valor.trim()
  if (termino.length < 2) {
    searchResultados.hospitales = []
    searchResultados.usuarios = []
    searchError.value = false
    searchLoading.value = false
    return
  }
  searchDebounce = setTimeout(async () => {
    searchLoading.value = true
    searchError.value = false
    try {
      const r = await api<{ hospitales: SearchHospital[]; usuarios: SearchUsuario[] }>(`/admin/buscar?q=${encodeURIComponent(termino)}`)
      if (miToken !== searchToken) return
      searchResultados.hospitales = r.hospitales
      searchResultados.usuarios = r.usuarios
    } catch {
      if (miToken !== searchToken) return
      searchResultados.hospitales = []
      searchResultados.usuarios = []
      searchError.value = true
    } finally {
      if (miToken === searchToken) searchLoading.value = false
    }
  }, 300)
})

const cerrarBusqueda = () => {
  searchOpen.value = false
  searchQuery.value = ''
}

const irAlPrimerResultado = () => {
  const primero = searchResultados.hospitales[0]
  if (primero) { router.push(`/admin/hospitales/${primero.id}`); cerrarBusqueda(); return }
  const usuario = searchResultados.usuarios[0]
  if (usuario) {
    router.push(`/admin/usuarios/${usuario.id}${usuario.tenant_id ? `?tenant_id=${usuario.tenant_id}` : ''}`)
    cerrarBusqueda()
  }
}

const cerrarMenusSiFuera = (e: MouseEvent) => {
  const target = e.target as HTMLElement
  if (notifOpen.value && !target.closest('.notif-wrapper')) notifOpen.value = false
  if (settingsOpen.value && !target.closest('.settings-wrapper')) settingsOpen.value = false
  if (searchOpen.value && !target.closest('.search-wrapper')) searchOpen.value = false
}

// Escape cierra el desplegable abierto (campana/configuracion) sin
// necesitar el mouse -- la busqueda ya lo hacia con @keydown.esc en su
// propio input, pero estos dos paneles no tenian ninguna salida de teclado.
const cerrarMenusConEscape = (e: KeyboardEvent) => {
  if (e.key !== 'Escape') return
  notifOpen.value = false
  settingsOpen.value = false
}

onMounted(() => {
  cargarContadorNotif()
  notifTimer = setInterval(cargarContadorNotif, 45000)
  document.addEventListener('click', cerrarMenusSiFuera)
  document.addEventListener('keydown', cerrarMenusConEscape)
})
onUnmounted(() => {
  if (notifTimer) clearInterval(notifTimer)
  if (searchDebounce) clearTimeout(searchDebounce)
  document.removeEventListener('click', cerrarMenusSiFuera)
  document.removeEventListener('keydown', cerrarMenusConEscape)
})

// En móvil el sidebar siempre se muestra expandido (nunca en modo icono),
// así que "collapsed" solo afecta el ancho/labels en escritorio (md:).
const collapsedDesktop = computed(() => collapsed.value)

watch(() => route.path, () => { mobileOpen.value = false })

function onNavClick(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (target.closest('a')) mobileOpen.value = false
}

const loggingOut = ref(false)

const handleLogout = async () => {
  loggingOut.value = true
  const revocadoEnServidor = await authStore.logout()
  await navigateTo(revocadoEnServidor ? '/login' : '/login?aviso=logout_sin_confirmar')
}
</script>

<style scoped>
.notif-badge {
  position: absolute;
  top: 2px;
  right: 2px;
  min-width: 16px;
  height: 16px;
  padding: 0 3px;
  border-radius: 8px;
  background: var(--alert, #dc2626);
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
  width: 340px;
  max-width: calc(100vw - 2rem);
  max-height: 420px;
  display: flex;
  flex-direction: column;
  background: var(--paper, #fff);
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  z-index: 50;
}
.search-panel {
  position: absolute;
  top: calc(100% + 0.5rem);
  left: 0;
  width: 100%;
  min-width: 320px;
  max-height: 360px;
  overflow-y: auto;
  background: var(--paper, #fff);
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
  z-index: 50;
  padding: 0.375rem;
}
.search-group-label {
  padding: 0.5rem 0.625rem 0.25rem;
  font-size: 0.6875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--ink-soft, #6b7280);
}
.search-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.625rem;
  border-radius: 8px;
  text-decoration: none;
  transition: background 0.15s ease;
}
.search-item:hover {
  background: var(--mist, #f3f4f6);
}
.search-item-title {
  margin: 0;
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--ink, #111827);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.search-item-sub {
  margin: 0;
  font-size: 0.75rem;
  color: var(--ink-soft, #6b7280);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.notif-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid var(--line, #e5e7eb);
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--ink, #111827);
}
.notif-mark-all {
  font-size: 0.6875rem;
  font-weight: 500;
  color: var(--teal, #0891b2);
  background: none;
  border: none;
  cursor: pointer;
}
.notif-empty {
  padding: 2rem 1rem;
  text-align: center;
  font-size: 0.8125rem;
  color: var(--ink-soft, #6b7280);
}
.notif-list {
  overflow-y: auto;
  list-style: none;
  margin: 0;
  padding: 0;
}
.notif-cargar-mas {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.375rem;
  width: 100%;
  padding: 0.625rem;
  border: none;
  border-top: 1px solid var(--line, #e5e7eb);
  background: none;
  color: var(--teal, #0891b2);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
}
.notif-cargar-mas:hover {
  background: var(--mist, #f3f4f6);
}
.notif-item {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  padding: 0.75rem 1rem;
  cursor: pointer;
  border-bottom: 1px solid var(--line, #e5e7eb);
  transition: background 0.15s ease;
}
.notif-item:last-child {
  border-bottom: none;
}
.notif-item:hover {
  background: var(--mist, #f3f4f6);
}
.notif-item.unread {
  background: var(--teal-soft, #ecfeff);
}
.notif-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-top: 0.375rem;
  flex-shrink: 0;
  background: var(--ink-soft, #9ca3af);
}
.notif-dot--exito { background: var(--green, #16a34a); }
.notif-dot--error { background: var(--alert, #dc2626); }
.notif-dot--alerta { background: var(--amber, #d97706); }
.notif-dot--info { background: var(--teal, #0891b2); }
.notif-item-body {
  min-width: 0;
}
.notif-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--ink, #111827);
  margin: 0;
}
.notif-desc {
  font-size: 0.75rem;
  color: var(--ink-soft, #6b7280);
  margin: 0.125rem 0 0 0;
}
.notif-time {
  font-size: 0.6875rem;
  color: var(--ink-soft, #9ca3af);
  margin: 0.25rem 0 0 0;
}

.settings-menu {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 200px;
  display: flex;
  flex-direction: column;
  padding: 0.375rem;
  background: var(--paper, #fff);
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
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
  color: var(--ink, #111827);
  text-decoration: none;
  cursor: pointer;
  width: 100%;
  text-align: left;
}
.settings-item:hover {
  background: var(--mist, #f3f4f6);
}
.settings-item--danger {
  color: var(--alert, #dc2626);
}

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