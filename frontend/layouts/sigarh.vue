  <template>
    <div class="min-h-screen flex" style="background: var(--mist)">

      <!-- SIDEBAR -->
      <aside
        class="flex flex-col shrink-0 transition-all duration-300"
        :style="{ width: collapsed ? '64px' : '240px', background: 'var(--navy)', color: 'white' }"
      >
        <!-- Logo -->
        <div class="h-16 flex items-center gap-2 px-4 shrink-0 border-b" style="border-color: rgba(255,255,255,0.08)">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center shrink-0 overflow-hidden bg-white/95 shadow-sm ring-1 ring-white/20">
            <img src="/logo-sigarh.png" alt="SIGARH" class="w-full h-full object-cover" />
          </div>
          <span v-if="!collapsed" class="font-semibold text-sm tracking-wide">SIGARH</span>
        </div>

        <!-- Nav -->
        <nav class="flex-1 overflow-y-auto overflow-x-hidden py-3 space-y-0.5 px-2">

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
        class="w-full flex items-center justify-between px-3 py-1.5 rounded-lg transition-colors hover:bg-white/5"
        style="color: #7fa1b3"
        @click="toggleGrupo(grupo.label)"
      >
        <div class="flex items-center gap-2">
          <UIcon :name="grupo.icon || 'i-heroicons-folder'" class="w-3.5 h-3.5" />
          <span class="text-xs font-semibold uppercase tracking-widest">{{ grupo.label }}</span>
        </div>
        <UIcon
          :name="grupoAbierto(grupo.label) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'"
          class="w-3 h-3"
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
              class="w-full flex items-center justify-between px-3 py-1.5 rounded-lg transition-colors hover:bg-white/5 nav-sub"
              style="color: #5a8fa8"
              @click="toggleSubgrupo(grupo.label + item.label)"
            >
              <div class="flex items-center gap-2">
                <UIcon :name="item.icon || 'i-heroicons-folder'" class="w-3.5 h-3.5" />
                <span class="text-xs font-semibold">{{ item.label }}</span>
              </div>
              <UIcon
                :name="subgrupoAbierto(grupo.label + item.label) ? 'i-heroicons-chevron-down' : 'i-heroicons-chevron-right'"
                class="w-3 h-3"
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
          <div v-if="!collapsed" class="px-3 py-2 rounded-lg mb-1" style="background: rgba(255,255,255,0.05)">
            <p class="text-sm font-medium truncate">{{ authStore.user?.name }}</p>
            <p class="text-xs truncate" style="color: #7fa1b3">{{ authStore.user?.email }}</p>
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
            <button class="p-2 rounded-lg hover:bg-black/5 transition-colors" title="Ayuda">
              <UIcon name="i-heroicons-question-mark-circle" class="w-5 h-5" style="color: #7a8894" />
            </button>

            <button class="relative p-2 rounded-lg hover:bg-black/5 transition-colors" title="Notificaciones">
              <UIcon name="i-heroicons-bell" class="w-5 h-5" style="color: #7a8894" />
              <span class="absolute top-1.5 right-1.5 w-2 h-2 rounded-full" style="background: var(--teal)" />
            </button>

            <button class="p-2 rounded-lg hover:bg-black/5 transition-colors" title="Configuración">
              <UIcon name="i-heroicons-cog-6-tooth" class="w-5 h-5" style="color: #7a8894" />
            </button>

            <div class="w-px h-6 mx-1" style="background: #e6ebef" />

            <!-- Usuario -->
            <button class="flex items-center gap-2 pl-1.5 pr-3 py-1.5 rounded-full hover:bg-black/5 transition-colors">
              <div class="w-7 h-7 rounded-full flex items-center justify-center text-xs font-semibold text-white shrink-0" style="background: var(--teal)">
                {{ inicialesUsuario }}
              </div>
              <span class="hidden lg:block text-sm font-medium" style="color: var(--navy)">
                {{ authStore.user?.name || 'Usuario' }}
              </span>
              <UIcon name="i-heroicons-chevron-down" class="hidden lg:block w-3.5 h-3.5" style="color: #9aa7b1" />
            </button>
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
  const { link, activo, gruposVisibles } = useSigarhNav()
  const route = useRoute()
  // Estado subgrupos (Cambio de Turno, Papeletas, etc.)
  const subgruposAbiertos = ref<Record<string, boolean>>({})

  function subgrupoAbierto(key: string): boolean {
    return subgruposAbiertos.value[key] !== false // abierto por defecto
  }

  function toggleSubgrupo(key: string) {
    subgruposAbiertos.value[key] = !subgrupoAbierto(key)
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

  // Sidebar colapsado
  const collapsed = ref(false)

  // Estado de grupos abiertos — todos abiertos por defecto
  const gruposAbiertos = ref<Record<string, boolean>>({})

  function grupoAbierto(label: string): boolean {
    return gruposAbiertos.value[label] !== false // abierto por defecto
  }

  function toggleGrupo(label: string) {
    gruposAbiertos.value[label] = !grupoAbierto(label)
  }

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

  const handleLogout = async () => {
    await authStore.logout()
    await navigateTo('/login')
  }
  </script>

  <style scoped>
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
  </style>