  <template>
    <!-- Al cerrar sesion se DESMONTA todo el contenido protegido (esta es
         la unica raiz que queda) en vez de solo taparlo con un overlay.
         Ganarle por z-index a un <Teleport to="body"> (SModal lo usa) es
         posible en teoria, pero fragil: depende de que ningun ancestro
         entre medio cree su propio contexto de apilamiento, un detalle
         facil de romper sin darse cuenta con un cambio de estilos futuro.
         Y aunque se tape visualmente, un elemento que sigue montado sigue
         siendo alcanzable por teclado -- desmontar evita ambos problemas
         de raiz en vez de depender de ganar la pulseada de CSS. -->
    <div v-if="loggingOut" class="h-screen flex items-center justify-center" style="background: var(--mist)">
      <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
    </div>
    <div v-else class="h-screen overflow-hidden flex" style="background: var(--mist)">

      <!-- SIDEBAR -->
      <aside
        class="h-screen flex flex-col shrink-0 transition-all duration-300"
        :style="{ width: collapsed ? '64px' : '240px', background: '#fff', color: 'var(--ink)' }"
      >
        <!-- Logo -->
        <div class="h-16 flex items-center gap-2 px-4 shrink-0 border-b" style="border-color: rgba(255,255,255,0.08)">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 overflow-hidden bg-white/95 shadow-sm ring-1 ring-white/20">
            <img src="/logo-sigarh.png" alt="SIGARH" class="w-full h-full object-cover" />
          </div>
          <span v-if="!collapsed" class="font-semibold text-sm tracking-wide">SIGARH</span>
        </div>

        <!-- Nav -->
        <nav ref="navRef" class="sigarh-nav flex-1 overflow-y-auto overflow-x-hidden py-3 space-y-0.5 px-2">

    <!-- Escritorio -->
    <NuxtLink :to="link('/sigarh')" class="nav-link" :class="activo('/sigarh')">
      <UIcon name="i-heroicons-home" class="w-4 h-4 shrink-0" />
      <span v-if="!collapsed" class="truncate">Escritorio</span>
    </NuxtLink>

    <!-- Grupos -->
    <div v-for="grupo in gruposVisibles" :key="grupo.label" class="pt-1">

      <!-- Cabecera grupo principal -->
      <button
        v-if="!collapsed"
        class="w-full flex items-start justify-between gap-2 px-3 py-1.5 rounded-lg transition-colors hover:bg-white/5 text-left"
        style="color: #7fa1b3"
        @click="toggleGrupo(grupo.label)"
      >
        <div class="flex items-start gap-2 min-w-0">
          <UIcon :name="grupo.icon || 'i-heroicons-folder'" class="w-3.5 h-3.5 shrink-0 mt-0.5" />
          <span class="text-xs font-medium">{{ grupo.label }}</span>
        </div>
        <UIcon
          :name="grupoAbierto(grupo.label) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'"
          class="w-3 h-3 shrink-0 mt-0.5"
        />
      </button>
      <div v-else class="mx-3 my-1 border-t" style="border-color: rgba(255,255,255,0.08)" />

      <!-- Items del grupo -->
      <div v-show="grupoAbierto(grupo.label) || collapsed" class="space-y-0.5 mt-0.5">
        <template v-for="item in grupo.items" :key="item.label">

          <!-- SUBGRUPO colapsable (Cambio de Turno, Papeletas) -->
          <template v-if="item.subgrupo">
            <button
              v-if="!collapsed"
              class="w-full flex items-start justify-between gap-2 px-3 py-1.5 rounded-lg transition-colors hover:bg-white/5 nav-sub text-left"
              style="color: #5a8fa8"
              @click="toggleSubgrupo(grupo.label + item.label)"
            >
              <div class="flex items-start gap-2 min-w-0">
                <UIcon :name="item.icon || 'i-heroicons-folder'" class="w-3.5 h-3.5 shrink-0 mt-0.5" />
                <span class="text-xs font-semibold">{{ item.label }}</span>
              </div>
              <UIcon
                :name="subgrupoAbierto(grupo.label + item.label) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'"
                class="w-3 h-3 shrink-0 mt-0.5"
              />
            </button>

            <!-- Children del subgrupo -->
            <div v-show="subgrupoAbierto(grupo.label + item.label) || collapsed" class="space-y-0.5">
              <NuxtLink
                v-for="child in item.children"
                :key="child.path"
                :to="link(child.path)"
                class="nav-link nav-sub-deep"
                :class="activo(child.path)"
              >
                <UIcon :name="child.icon || 'i-heroicons-chevron-right'" class="w-3 h-3 shrink-0 opacity-60" />
                <span v-if="!collapsed" class="truncate">{{ child.label }}</span>
              </NuxtLink>
            </div>
          </template>

          <!-- Item normal -->
          <NuxtLink
            v-else
            :to="link(item.path)"
            class="nav-link nav-sub"
            :class="activo(item.path)"
          >
            <UIcon :name="item.icon || 'i-heroicons-chevron-right'" class="w-3.5 h-3.5 shrink-0 opacity-60" />
            <span v-if="!collapsed" class="truncate">{{ item.label }}</span>
          </NuxtLink>

        </template>
      </div>
    </div>
  </nav>

        <!-- Footer usuario -->
        <div class="p-2 border-t shrink-0" style="border-color: rgba(255,255,255,0.08)">
          <NuxtLink
            :to="link('/sigarh/perfil')"
            class="flex items-center gap-2.5 rounded-lg mb-1 px-2.5 py-2 hover:bg-white/10 transition-colors"
            :class="{ 'justify-center': collapsed }"
            style="background: rgba(255,255,255,0.05)"
          >
            <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold text-white shrink-0" style="background: var(--teal)">
              {{ inicialesUsuario }}
            </div>
            <div v-if="!collapsed" class="min-w-0">
              <p class="text-sm font-medium truncate">{{ authStore.user?.name }}</p>
              <p class="text-xs truncate" style="color: #7fa1b3">{{ authStore.user?.email }}</p>
            </div>
          </NuxtLink>
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
          <!-- Toggle sidebar -->
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

          <!-- Saludo -->
          <div class="hidden md:flex items-center gap-2 text-sm shrink-0">
            <span>{{ saludoEmoji }}</span>
            <span style="color: #9aa7b1">{{ saludoHora }}</span>
          </div>

          <!-- Buscador -->
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

          <!-- Acciones derecha -->
          <div class="ml-auto flex items-center gap-1 shrink-0">
            <a
              href="https://atencionalcliente.techquk.com/"
              target="_blank"
              rel="noopener noreferrer"
              class="p-2 rounded-lg hover:bg-black/5 transition-colors"
              title="Ayuda"
            >
              <UIcon name="i-heroicons-question-mark-circle" class="w-5 h-5" style="color: #7a8894" />
            </a>

            <div class="notif-wrapper relative">
              <button
                class="relative p-2 rounded-lg hover:bg-black/5 transition-colors"
                :aria-label="notifUnread > 0 ? `Notificaciones, ${notifUnread} sin leer` : 'Notificaciones'"
                aria-haspopup="true"
                :aria-expanded="notifOpen"
                @click="toggleNotifs"
              >
                <UIcon name="i-heroicons-bell" class="w-5 h-5" style="color: #7a8894" aria-hidden="true" />
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

            <div class="w-px h-6 mx-1" style="background: #e6ebef" />

            <!-- Usuario: mismo menu (Configuracion + Cerrar sesion) accesible
                 desde el engranaje o desde el nombre -- antes ninguno de los
                 dos hacia nada, ni siquiera dejaba cerrar sesion desde aca. -->
            <div class="settings-wrapper relative">
              <button
                class="flex items-center gap-2 pl-1.5 pr-3 py-1.5 rounded-full hover:bg-black/5 transition-colors"
                aria-haspopup="true"
                :aria-expanded="settingsOpen"
                @click="settingsOpen = !settingsOpen"
              >
                <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold text-white shrink-0" style="background: var(--teal)">
                  {{ inicialesUsuario }}
                </div>
                <span class="hidden lg:block text-sm font-medium" style="color: var(--navy)">
                  {{ authStore.user?.name || 'Usuario' }}
                </span>
                <UIcon name="i-heroicons-chevron-down" class="hidden lg:block w-3.5 h-3.5" style="color: #9aa7b1" />
              </button>
              <div v-if="settingsOpen" class="settings-menu">
                <NuxtLink :to="link('/sigarh/perfil')" class="settings-item" @click="settingsOpen = false">
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
import '~/assets/css/sigarh-theme.css'
useHead({ bodyAttrs: { class: 'sigarh-theme' }, link: [{ rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600&display=swap' }] })

  const authStore = useAuthStore()
  const { api } = useApi()
  const router = useRouter()
  const { link, activo, gruposVisibles, rutaMenuActual } = useSigarhNav()
  const route = useRoute()
  const navRef = ref<HTMLElement | null>(null)
  // Estado subgrupos (Cambio de Turno, Papeletas, etc.)
  const subgruposAbiertos = ref<Record<string, boolean>>({})

  function subgrupoAbierto(key: string): boolean {
    return subgruposAbiertos.value[key] === true
  }

  function toggleSubgrupo(key: string) {
    const abrir = !subgrupoAbierto(key)
    subgruposAbiertos.value = { [key]: abrir }
  }
  // Saludo dinámico según la hora del día
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
  // Iniciales del usuario para el avatar
  const inicialesUsuario = computed(() => {
    const nombre = authStore.user?.name || ''
    return nombre
      .split(' ')
      .filter(Boolean)
      .slice(0, 2)
      .map((p: string) => p[0]?.toUpperCase())
      .join('') || 'U'
  })

  // Notificaciones (campana del header) -- mismo patron que layouts/admin.vue,
  // pero contra /sigarh/notificaciones (bandeja compartida en la BD FISICA
  // de este hospital, no la central).
  interface NotificacionSigarh {
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
  const notificaciones = ref<NotificacionSigarh[]>([])
  const NOTIF_PAGE_SIZE = 20
  let notifTimer: ReturnType<typeof setInterval> | null = null

  const cargarContadorNotif = async () => {
    try {
      const r = await api<{ count: number }>('/sigarh/notificaciones/no-leidas')
      notifUnread.value = r.count
    } catch {
      // silencioso: el contador no debe interrumpir el resto del panel
    }
  }

  const cargarNotificaciones = async () => {
    notifLoading.value = true
    notifError.value = false
    try {
      const r = await api<{ items: NotificacionSigarh[]; total: number }>(`/sigarh/notificaciones?limit=${NOTIF_PAGE_SIZE}`)
      notificaciones.value = r.items
      notifTotal.value = r.total
    } catch {
      notificaciones.value = []
      notifTotal.value = 0
      notifError.value = true
    } finally {
      notifLoading.value = false
    }
  }

  const cargarMasNotificaciones = async () => {
    notifLoadingMas.value = true
    try {
      const r = await api<{ items: NotificacionSigarh[]; total: number }>(
        `/sigarh/notificaciones?limit=${NOTIF_PAGE_SIZE}&offset=${notificaciones.value.length}`
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
      await api('/sigarh/notificaciones/leer-todas', { method: 'PATCH' })
      notificaciones.value.forEach(n => { n.is_read = true })
      notifUnread.value = 0
    } catch {
      // si falla, se queda como estaba -- no hay nada que revertir
    }
  }

  const abrirNotif = async (n: NotificacionSigarh) => {
    if (!n.is_read) {
      try {
        await api(`/sigarh/notificaciones/${n.id}/leer`, { method: 'PATCH' })
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

  const cerrarMenusSiFuera = (e: MouseEvent) => {
    const target = e.target as HTMLElement
    if (notifOpen.value && !target.closest('.notif-wrapper')) notifOpen.value = false
    if (settingsOpen.value && !target.closest('.settings-wrapper')) settingsOpen.value = false
  }

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
    document.removeEventListener('click', cerrarMenusSiFuera)
    document.removeEventListener('keydown', cerrarMenusConEscape)
  })

  // Sidebar colapsado
  const collapsed = ref(false)

  // Estado de grupos abiertos — todos abiertos por defecto
  const gruposAbiertos = ref<Record<string, boolean>>({})

  function grupoAbierto(label: string): boolean {
    return gruposAbiertos.value[label] === true
  }

  function toggleGrupo(label: string) {
    const abrir = !grupoAbierto(label)
    gruposAbiertos.value = { [label]: abrir }
  }

  function sincronizarMenu() {
    const ruta = rutaMenuActual.value
    const grupo = gruposVisibles.value.find((g: any) => g.items.some((item: any) =>
      item.subgrupo
        ? item.children.some((child: any) => child.path === ruta)
        : item.path === ruta
    ))
    gruposAbiertos.value = grupo ? { [grupo.label]: true } : {}

    const subgrupo = grupo?.items.find((item: any) =>
      item.subgrupo && item.children.some((child: any) => child.path === ruta)
    ) as any
    subgruposAbiertos.value = subgrupo ? { [`${grupo!.label}${subgrupo.label}`]: true } : {}

    nextTick(() => {
      navRef.value?.querySelector('.nav-active')?.scrollIntoView({ block: 'center', behavior: 'smooth' })
    })
  }

  watch(
    [() => route.path, () => gruposVisibles.value.map((g: any) => g.label).join('|')],
    sincronizarMenu,
    { immediate: true },
  )

  // Icono por nombre de item
  function iconoItem(label: string): string {
    const mapa: Record<string, string> = {
      'Empleados': 'i-heroicons-users',
      'Especialidades': 'i-heroicons-academic-cap',
      'Dias Feriados': 'i-heroicons-calendar',
      'Registro de Asistencia': 'i-heroicons-clipboard-document-check',
      'Tolerancias': 'i-heroicons-clock',
      'Motivos de Justificacion': 'i-heroicons-document-text',
      'Justificaciones e Inasistencias': 'i-heroicons-exclamation-circle',
      'Justificacion y Vacaciones': 'i-heroicons-sun',
      'Tramitar Licencia': 'i-heroicons-paper-airplane',
      'Estado Licencia': 'i-heroicons-list-bullet',
      'Tramitar Cambio de Turno': 'i-heroicons-arrows-right-left',
      'Estado Cambio Turno': 'i-heroicons-list-bullet',
      'Tramitar Papeleta': 'i-heroicons-paper-airplane',
      'Estado de Papeletas': 'i-heroicons-list-bullet',
      'Prof. Salud - Medicos': 'i-heroicons-user-group',
      'Otros Prof. de la Salud': 'i-heroicons-user-group',
      'Examenes de Laboratorio': 'i-heroicons-beaker',
      'Examenes de Imagenologia': 'i-heroicons-photo',
      'Diagnosticos CIE-10': 'i-heroicons-document-magnifying-glass',
      'Paquetes': 'i-heroicons-archive-box',
      'Tiempos Procedimientos': 'i-heroicons-clock',
      'Registro de Raciones': 'i-heroicons-clipboard-document-list',
      'Generar Reportes': 'i-heroicons-chart-bar',
      'Entrega de Raciones': 'i-heroicons-check-circle',
      'Cambios de Turno': 'i-heroicons-arrows-right-left',
      'Pisos': 'i-heroicons-building-office',
      'Salas': 'i-heroicons-building-office-2',
      'Camas': 'i-heroicons-home',
      'Consultorios': 'i-heroicons-building-storefront',
      'Almacenes / Farmacias': 'i-heroicons-archive-box',
      'Medicamentos e Insumos': 'i-heroicons-beaker',
      'Seguros': 'i-heroicons-shield-check',
      'Cajas': 'i-heroicons-banknotes',
      'Tarifario': 'i-heroicons-currency-dollar',
    }
    return mapa[label] || 'i-heroicons-chevron-right'
  }

  const loggingOut = ref(false)

  const handleLogout = async () => {
    loggingOut.value = true
    // Capturar el tenant ANTES de logout(): borra authStore.user, y sin el
    // tenant en la URL el siguiente login no manda X-Tenant-ID y el backend
    // cae al fallback por dominio (404 o, peor, el hospital equivocado).
    const tenantId = route.query.tenant as string || authStore.user?.tenant_id || ''
    const revocadoEnServidor = await authStore.logout()
    const query: Record<string, string> = {}
    if (tenantId) query.tenant = tenantId
    if (!revocadoEnServidor) query.aviso = 'logout_sin_confirmar'
    await navigateTo({ path: '/sigarh/login', query })
  }
  </script>

  <style scoped>
  .sigarh-nav {
    scrollbar-width: none; /* Firefox */
    -ms-overflow-style: none; /* IE/Edge legacy */
  }
  .sigarh-nav::-webkit-scrollbar {
    display: none; /* Chrome/Edge/Safari */
  }
  .nav-link {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.45rem 0.75rem;
    border-radius: 7px;
    font-size: 0.82rem;
    color: rgba(255, 255, 255, 0.65);
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
    padding-left: 1rem;
    font-size: 0.8rem;
  }
  .nav-sub-deep {
    padding-left: 1.75rem;
    font-size: 0.78rem;
  }

  /* Notificaciones y menu de usuario (mismo patron visual que layouts/admin.vue) */
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
    background: #fff;
    border-radius: 12px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.25);
    overflow: hidden;
    z-index: 50;
  }
  .notif-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1rem;
    border-bottom: 1px solid #e6ebef;
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--navy);
  }
  .notif-mark-all {
    font-size: 0.6875rem;
    font-weight: 500;
    color: var(--teal);
    background: none;
    border: none;
    cursor: pointer;
  }
  .notif-empty {
    padding: 2rem 1rem;
    text-align: center;
    font-size: 0.8125rem;
    color: #7a8894;
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
    border-top: 1px solid #e6ebef;
    background: none;
    color: var(--teal);
    font-size: 0.75rem;
    font-weight: 600;
    cursor: pointer;
  }
  .notif-cargar-mas:hover {
    background: #f3f4f6;
  }
  .notif-item {
    display: flex;
    align-items: flex-start;
    gap: 0.625rem;
    padding: 0.75rem 1rem;
    cursor: pointer;
    border-bottom: 1px solid #e6ebef;
    transition: background 0.15s ease;
  }
  .notif-item:last-child {
    border-bottom: none;
  }
  .notif-item:hover {
    background: #f3f4f6;
  }
  .notif-item.unread {
    background: #ecfeff;
  }
  .notif-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    margin-top: 0.375rem;
    flex-shrink: 0;
    background: #9ca3af;
  }
  .notif-dot--exito { background: #16a34a; }
  .notif-dot--error { background: #dc2626; }
  .notif-dot--alerta { background: #d97706; }
  .notif-dot--info { background: var(--teal); }
  .notif-item-body {
    min-width: 0;
  }
  .notif-title {
    font-size: 0.8125rem;
    font-weight: 600;
    color: var(--navy);
    margin: 0;
  }
  .notif-desc {
    font-size: 0.75rem;
    color: #7a8894;
    margin: 0.125rem 0 0 0;
  }
  .notif-time {
    font-size: 0.6875rem;
    color: #9aa7b1;
    margin: 0.25rem 0 0 0;
  }
  .settings-menu {
    position: absolute;
    top: calc(100% + 0.5rem);
    right: 0;
    width: 180px;
    display: flex;
    flex-direction: column;
    padding: 0.375rem;
    background: #fff;
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
    color: var(--navy);
    text-decoration: none;
    cursor: pointer;
    width: 100%;
    text-align: left;
  }
  .settings-item:hover {
    background: #f3f4f6;
  }
  .settings-item--danger {
    color: #dc2626;
  }
  </style>
