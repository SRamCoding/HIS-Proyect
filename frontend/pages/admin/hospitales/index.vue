<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">Hospitales</h1>
        <p class="text-sm" style="color: var(--ink-soft)">Establecimientos registrados en la plataforma</p>
      </div>
      <NuxtLink to="/admin/hospitales/create" class="btn-primary">+ Nuevo hospital</NuxtLink>
    </div>

    <div class="mb-4">
      <input v-model="search" type="text" placeholder="Buscar por nombre..." class="input-clinical max-w-xs" />
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>

      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Nombre</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Dominio</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Nivel</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Modulos</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Estado</th>
            <th class="text-right font-medium px-5 py-3" style="color: var(--ink-soft)">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="h in filteredHospitales" :key="h.id" style="border-bottom: 1px solid var(--line)">
            <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ h.name }}</td>
            <td class="px-5 py-3 text-xs" style="color: var(--ink-soft)">{{ h.domain }}</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ h.hospital_level ?? '-' }}</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ h.active_modules?.length ?? 0 }}</td>
            <td class="px-5 py-3">
              <span class="badge" :class="h.is_active ? 'badge--ok' : 'badge--neutral'">
                {{ h.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-5 py-3 text-right" style="position: relative">
              <button
                class="text-sm font-medium px-3 py-1 rounded"
                style="border: 1px solid var(--line); color: var(--ink)"
                @click="toggleMenu(h.id)"
              >
                Acciones
              </button>

              <div
                v-if="menuAbierto === h.id"
                style="position: absolute; right: 16px; top: 40px; z-index: 50; width: 160px; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); box-shadow: 0 4px 12px rgba(0,0,0,0.1)"
              >
                <button class="block w-full text-left px-4 py-2 text-sm" style="color: var(--ink)" @click="irA(h, '')">
                  Ver landing
                </button>
                <button class="block w-full text-left px-4 py-2 text-sm" style="color: var(--ink)" @click="irA(h, '/app')">
                  Panel admin
                </button>
                <button class="block w-full text-left px-4 py-2 text-sm" style="color: var(--ink)" @click="irA(h, '/sigarh')">
                  Panel SIGARH
                </button>
                <NuxtLink
                  :to="`/admin/hospitales/${h.id}`"
                  class="block px-4 py-2 text-sm"
                  style="color: var(--teal)"
                  @click="menuAbierto = null"
                >
                  Editar
                </NuxtLink>
                <button
                  class="block w-full text-left px-4 py-2 text-sm"
                  style="color: var(--alert)"
                  @click="handleToggle(h); menuAbierto = null"
                >
                  {{ h.is_active ? 'Desactivar' : 'Activar' }}
                </button>
              </div>
            </td>
          </tr>
          <tr v-if="!filteredHospitales.length">
            <td colspan="6" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">
              {{ search ? 'Sin resultados.' : 'Sin hospitales registrados.' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="menuAbierto" style="position: fixed; inset: 0; z-index: 40" @click="menuAbierto = null" />
  </div>
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

const { api } = useApi()
const hospitales = ref<Hospital[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const togglingId = ref<string | null>(null)
const menuAbierto = ref<string | null>(null)

const filteredHospitales = computed(() => {
  if (!search.value.trim()) return hospitales.value
  const q = search.value.toLowerCase()
  return hospitales.value.filter(h => h.name.toLowerCase().includes(q))
})

const toggleMenu = (id: string) => {
  menuAbierto.value = menuAbierto.value === id ? null : id
}

const irA = (hospital: Hospital, path: string) => {
  if (path === '') {
    window.open(`http://localhost:3000?tenant=${hospital.id}`, '_blank')
  } else if (path === '/sigarh') {
    window.open(`http://localhost:3000/sigarh/login?tenant=${hospital.id}`, '_blank')
  } else {
    window.open(`http://localhost:3000${path}?tenant=${hospital.id}`, '_blank')
  }
  menuAbierto.value = null
}

const loadHospitales = async () => {
  loading.value = true
  error.value = ''
  try {
    hospitales.value = await api<Hospital[]>('/admin/hospitales')
  } catch (e: any) {
    error.value = e?.data?.detail || 'error de conexion'
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
    error.value = e?.data?.detail || 'no se pudo actualizar el estado'
  } finally {
    togglingId.value = null
  }
}

onMounted(loadHospitales)
</script>