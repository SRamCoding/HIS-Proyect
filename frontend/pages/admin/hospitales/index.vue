<template>
  <div>
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
      <div>
        <h1 class="text-xl font-semibold" style="color: var(--ink)">Hospitales</h1>
        <p class="text-sm" style="color: var(--ink-soft)">Establecimientos registrados en la plataforma</p>
      </div>
      <NuxtLink to="/admin/hospitales/create" class="btn-primary flex items-center justify-center gap-1.5 shrink-0">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo hospital
      </NuxtLink>
    </div>

    <!-- KPIs -->
    <div v-if="!loading && !error" class="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-6">
      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 16px">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" style="background: var(--mist)">
            <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--navy)" />
          </div>
          <div class="min-w-0">
            <p class="text-xl font-bold font-mono-data leading-tight" style="color: var(--ink)">{{ hospitales.length }}</p>
            <p class="text-xs" style="color: var(--ink-soft)">Total hospitales</p>
          </div>
        </div>
      </div>

      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 16px">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" style="background: var(--ok-soft)">
            <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--ok)" />
          </div>
          <div class="min-w-0">
            <p class="text-xl font-bold font-mono-data leading-tight" style="color: var(--ink)">{{ activos }}</p>
            <p class="text-xs" style="color: var(--ink-soft)">Activos</p>
          </div>
        </div>
      </div>

      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 16px">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" style="background: var(--mist)">
            <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--ink-soft)" />
          </div>
          <div class="min-w-0">
            <p class="text-xl font-bold font-mono-data leading-tight" style="color: var(--ink)">{{ inactivos }}</p>
            <p class="text-xs" style="color: var(--ink-soft)">Inactivos</p>
          </div>
        </div>
      </div>

      <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 16px">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 rounded-xl flex items-center justify-center shrink-0" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--teal)" />
          </div>
          <div class="min-w-0">
            <p class="text-xl font-bold font-mono-data leading-tight" style="color: var(--ink)">{{ promedioModulos }}</p>
            <p class="text-xs" style="color: var(--ink-soft)">Módulos / hospital (prom.)</p>
          </div>
        </div>
      </div>
    </div>

    <div class="flex items-center justify-between gap-3 mb-4">
      <UInput
        v-model="search"
        icon="i-heroicons-magnifying-glass"
        placeholder="Buscar por nombre..."
        size="md"
        class="max-w-xs"
        :ui="{ rounded: 'rounded-full' }"
      />
      <p v-if="!loading && !error" class="text-xs shrink-0" style="color: var(--ink-soft)">
        {{ filteredHospitales.length }} de {{ hospitales.length }}
      </p>
    </div>

    <!-- Loading -->
    <div
      v-if="loading"
      class="flex items-center gap-2 p-8 text-sm justify-center"
      style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); color: var(--ink-soft)"
    >
      <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
      Cargando hospitales...
    </div>

    <!-- Error -->
    <div
      v-else-if="error"
      class="flex items-center gap-2 p-6 text-sm"
      style="background: var(--alert-soft); color: var(--alert); border-radius: var(--radius-lg)"
    >
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <template v-else>
      <!-- Tabla — desktop / tablet -->
      <div
        class="hidden md:block overflow-hidden"
        style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)"
      >
        <table class="w-full text-sm">
          <thead>
            <tr style="border-bottom: 1px solid var(--line)">
              <th class="text-left font-semibold px-5 py-3 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Nombre</th>
              <th class="text-left font-semibold px-5 py-3 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Dominio</th>
              <th class="text-left font-semibold px-5 py-3 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Nivel</th>
              <th class="text-left font-semibold px-5 py-3 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Módulos</th>
              <th class="text-left font-semibold px-5 py-3 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Estado</th>
              <th class="text-right font-semibold px-5 py-3 text-xs tracking-wide uppercase" style="color: var(--ink-soft)">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="h in filteredHospitales"
              :key="h.id"
              class="transition-colors"
              style="border-bottom: 1px solid var(--line)"
              @mouseenter="$event.currentTarget.style.background = 'var(--mist)'"
              @mouseleave="$event.currentTarget.style.background = 'transparent'"
            >
              <td class="px-5 py-3.5">
                <div class="flex items-center gap-2.5">
                  <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style="background: var(--mist)">
                    <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" style="color: var(--navy)" />
                  </div>
                  <span class="font-medium" style="color: var(--ink)">{{ h.name }}</span>
                </div>
              </td>
              <td class="px-5 py-3.5 text-xs font-mono-data" style="color: var(--ink-soft)">{{ h.domain }}</td>
              <td class="px-5 py-3.5" style="color: var(--ink-soft)">{{ h.hospital_level ?? '—' }}</td>
              <td class="px-5 py-3.5" style="color: var(--ink-soft)">{{ h.active_modules?.length ?? 0 }}</td>
              <td class="px-5 py-3.5">
                <span class="badge" :class="h.is_active ? 'badge--ok' : 'badge--neutral'">
                  {{ h.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="px-5 py-3.5 text-right">
                <td class="px-5 py-3.5 text-right" style="position: relative">
                  <button
                    class="p-1.5 rounded-lg hover:bg-gray-100 transition-colors"
                    @click.stop="toggleMenu(h.id)"
                  >
                    <UIcon name="i-heroicons-ellipsis-horizontal" class="w-5 h-5" style="color: var(--ink-soft)" />
                  </button>

                  <div
                    v-if="menuAbierto === h.id"
                    style="position: absolute; right: 16px; top: 40px; z-index: 50; width: 180px; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); box-shadow: 0 4px 12px rgba(0,0,0,0.1)"
                  >
                    <button class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50" style="color: var(--ink)" @click="irA(h, ''); menuAbierto = null">Ver landing</button>
                    <button class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50" style="color: var(--ink)" @click="irA(h, '/app'); menuAbierto = null">Panel admin</button>
                    <button class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50" style="color: var(--ink)" @click="irA(h, '/sigarh'); menuAbierto = null">Panel SIGARH</button>
                    <div style="height: 1px; background: var(--line); margin: 4px 0"></div>
                    <button class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50" style="color: var(--teal)" @click="navigateTo(`/admin/hospitales/${h.id}`); menuAbierto = null">Editar</button>
                    <div style="height: 1px; background: var(--line); margin: 4px 0"></div>
                    <button class="block w-full text-left px-4 py-2 text-sm hover:bg-gray-50" style="color: var(--alert)" @click="handleToggle(h); menuAbierto = null">
                      {{ h.is_active ? 'Desactivar' : 'Activar' }}
                    </button>
                  </div>
                </td>
              </td>
            </tr>
            <tr v-if="!filteredHospitales.length">
              <td colspan="6" class="px-5 py-10 text-center text-sm" style="color: var(--ink-soft)">
                {{ search ? 'Sin resultados.' : 'Sin hospitales registrados.' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Cards — mobile -->
      <div class="md:hidden space-y-3">
        <div
          v-for="h in filteredHospitales"
          :key="h.id"
          class="p-4"
          style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)"
        >
          <div class="flex items-start justify-between gap-2 mb-2">
            <div class="flex items-center gap-2.5 min-w-0">
              <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style="background: var(--mist)">
                <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" style="color: var(--navy)" />
              </div>
              <div class="min-w-0">
                <p class="font-medium text-sm truncate" style="color: var(--ink)">{{ h.name }}</p>
                <p class="text-xs font-mono-data truncate" style="color: var(--ink-soft)">{{ h.domain }}</p>
              </div>
            </div>
            <UDropdown :items="accionesDropdown(h)" :popper="{ placement: 'bottom-end' }">
              <UButton icon="i-heroicons-ellipsis-horizontal" color="gray" variant="ghost" square size="sm" />
            </UDropdown>
          </div>
          <div class="flex items-center gap-3 text-xs" style="color: var(--ink-soft)">
            <span>Nivel: {{ h.hospital_level ?? '—' }}</span>
            <span>·</span>
            <span>{{ h.active_modules?.length ?? 0 }} módulos</span>
          </div>
          <span class="badge mt-2" :class="h.is_active ? 'badge--ok' : 'badge--neutral'">
            {{ h.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </div>

        <div
          v-if="!filteredHospitales.length"
          class="p-8 text-center text-sm"
          style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); color: var(--ink-soft)"
        >
          {{ search ? 'Sin resultados.' : 'Sin hospitales registrados.' }}
        </div>
      </div>
    </template>
  </div>
  <div v-if="menuAbierto" style="position: fixed; inset: 0; z-index: 40" @click="menuAbierto = null" />
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Hospital {
  id: string
  name: string
  domain: string
  hospital_level?: string
  active_modules: string[]
  is_active: boolean
  created_at: string
}
const menuAbierto = ref<string | null>(null)

const toggleMenu = (id: string) => {
  menuAbierto.value = menuAbierto.value === id ? null : id
}
const { api } = useApi()
const hospitales = ref<Hospital[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const togglingId = ref<string | null>(null)

const activos = computed(() => hospitales.value.filter(h => h.is_active).length)
const inactivos = computed(() => hospitales.value.filter(h => !h.is_active).length)
const promedioModulos = computed(() => {
  if (!hospitales.value.length) return 0
  const total = hospitales.value.reduce((sum, h) => sum + (h.active_modules?.length ?? 0), 0)
  return Math.round(total / hospitales.value.length)
})

const filteredHospitales = computed(() => {
  if (!search.value.trim()) return hospitales.value
  const q = search.value.toLowerCase()
  return hospitales.value.filter(h => h.name.toLowerCase().includes(q))
})

const irA = (hospital: Hospital, path: string) => {
  if (path === '') {
    window.open(`http://localhost:3000?tenant=${hospital.id}`, '_blank')
  } else if (path === '/sigarh') {
    window.open(`http://localhost:3000/sigarh/login?tenant=${hospital.id}`, '_blank')
  } else {
    window.open(`http://localhost:3000${path}?tenant=${hospital.id}`, '_blank')
  }
}

const loadHospitales = async () => {
  loading.value = true
  error.value = ''
  try {
    hospitales.value = await api<Hospital[]>('/admin/hospitales')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

const handleToggle = async (h: Hospital) => {
  togglingId.value = h.id
  try {
    await api(`/admin/hospitales/${h.id}/toggle?is_active=${!h.is_active}`, { method: 'PATCH' })
    h.is_active = !h.is_active
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo actualizar el estado'
  } finally {
    togglingId.value = null
  }
}

const accionesDropdown = (h: Hospital) => [
  [
    { label: 'Ver landing', icon: 'i-heroicons-globe-alt', click: () => irA(h, '') },
    { label: 'Panel admin', icon: 'i-heroicons-squares-2x2', click: () => irA(h, '/app') },
    { label: 'Panel SIGARH', icon: 'i-heroicons-folder-open', click: () => irA(h, '/sigarh') },
  ],
  [
    { label: 'Editar', icon: 'i-heroicons-pencil-square', click: () => navigateTo(`/admin/hospitales/${h.id}`) },
  ],
  [
    {
      label: h.is_active ? 'Desactivar' : 'Activar',
      icon: h.is_active ? 'i-heroicons-x-circle' : 'i-heroicons-check-circle',
      click: () => handleToggle(h),
    },
  ],
]

onMounted(loadHospitales)
</script>