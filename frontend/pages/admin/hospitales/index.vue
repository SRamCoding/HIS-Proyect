<!-- pages/admin/hospitales/index.vue -->
<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">Hospitales</h1>
        <p class="text-sm" style="color: var(--ink-soft)">Establecimientos registrados en la plataforma</p>
      </div>
      <button class="btn-primary" @click="showCreateModal = true">
        + Nuevo hospital
      </button>
    </div>

    <div class="mb-4">
      <input
        v-model="search"
        type="text"
        placeholder="Buscar por nombre…"
        class="input-clinical max-w-xs"
      />
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando…</div>

      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">
        No se pudo cargar la lista: {{ error }}
      </div>

      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Nombre</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Nivel MINSA</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Módulos</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Estado</th>
            <th class="text-right font-medium px-5 py-3" style="color: var(--ink-soft)">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="h in filteredHospitales"
            :key="h.id"
            style="border-bottom: 1px solid var(--line)"
          >
            <td class="px-5 py-3" style="color: var(--ink)">
              <NuxtLink :to="`/admin/hospitales/${h.id}`" class="font-medium hover:underline" style="color: var(--ink)">
                {{ h.nombre }}
              </NuxtLink>
            </td>
            <td class="px-5 py-3 font-mono-data" style="color: var(--ink-soft)">{{ h.nivel_minsa ?? '—' }}</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ h.modulos_count ?? 0 }}</td>
            <td class="px-5 py-3">
              <span class="badge" :class="h.activo ? 'badge--ok' : 'badge--neutral'">
                {{ h.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-5 py-3 text-right">
              <button
                class="text-sm font-medium"
                :style="{ color: h.activo ? 'var(--alert)' : 'var(--teal)' }"
                :disabled="togglingId === h.id"
                @click="handleToggle(h)"
              >
                {{ togglingId === h.id ? '...' : h.activo ? 'Desactivar' : 'Activar' }}
              </button>
            </td>
          </tr>
          <tr v-if="!filteredHospitales.length">
            <td colspan="5" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">
              {{ search ? 'Sin resultados para tu búsqueda.' : 'Sin hospitales registrados todavía.' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Modal crear hospital -->
    <div
      v-if="showCreateModal"
      class="fixed inset-0 flex items-center justify-center p-4 z-50"
      style="background: rgba(16, 28, 36, 0.5)"
      @click.self="showCreateModal = false"
    >
      <div class="w-full max-w-md p-6" style="background: var(--paper); border-radius: var(--radius)">
        <h3 class="text-base font-semibold mb-4" style="color: var(--ink)">Nuevo hospital</h3>

        <form @submit.prevent="handleCreate" class="space-y-4">
          <div>
            <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">Nombre</label>
            <input v-model="newHospital.nombre" required class="input-clinical" />
          </div>

          <div>
            <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">Nivel MINSA</label>
            <input v-model="newHospital.nivel_minsa" class="input-clinical" placeholder="Ej: II-1" />
          </div>

          <div v-if="createError" class="text-sm rounded px-3 py-2" style="background: var(--alert-soft); color: var(--alert)">
            {{ createError }}
          </div>

          <div class="flex gap-2 justify-end pt-2">
            <button type="button" class="text-sm font-medium px-3 py-2" style="color: var(--ink-soft)" @click="showCreateModal = false">
              Cancelar
            </button>
            <button type="submit" :disabled="creating" class="btn-primary">
              {{ creating ? 'Creando…' : 'Crear hospital' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Hospital {
  id: string
  nombre: string
  nivel_minsa?: string
  modulos_count?: number
  activo: boolean
}

const { api } = useApi()

const hospitales = ref<Hospital[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const togglingId = ref<string | null>(null)

const showCreateModal = ref(false)
const creating = ref(false)
const createError = ref('')
const newHospital = reactive({ nombre: '', nivel_minsa: '' })

const filteredHospitales = computed(() => {
  if (!search.value.trim()) return hospitales.value
  const q = search.value.toLowerCase()
  return hospitales.value.filter((h) => h.nombre.toLowerCase().includes(q))
})

const loadHospitales = async () => {
  loading.value = true
  error.value = ''
  try {
    hospitales.value = await api<Hospital[]>('/admin/hospitales')
  } catch (e: any) {
    error.value = e?.data?.detail || 'error de conexión'
  } finally {
    loading.value = false
  }
}

const handleToggle = async (h: Hospital) => {
  togglingId.value = h.id
  try {
    await api(`/admin/hospitales/${h.id}/toggle`, { method: 'PATCH' })
    h.activo = !h.activo
  } catch (e: any) {
    error.value = e?.data?.detail || 'no se pudo actualizar el estado'
  } finally {
    togglingId.value = null
  }
}

const handleCreate = async () => {
  creating.value = true
  createError.value = ''
  try {
    const created = await api<Hospital>('/admin/hospitales', {
      method: 'POST',
      body: newHospital,
    })
    hospitales.value.unshift(created)
    showCreateModal.value = false
    newHospital.nombre = ''
    newHospital.nivel_minsa = ''
  } catch (e: any) {
    createError.value = e?.data?.detail || 'no se pudo crear el hospital'
  } finally {
    creating.value = false
  }
}

onMounted(loadHospitales)
</script>