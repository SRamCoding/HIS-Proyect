<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
          <span>SIGARH</span><span>/</span><span>Recursos Humanos</span><span>/</span><span>Empleados</span>
        </div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">Empleados</h1>
        <p class="text-sm" style="color: var(--ink-soft)">Personal registrado en el hospital</p>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/empleados/create?tenant=${tenantId}`" class="btn-primary">
        + Nuevo Empleado
      </NuxtLink>
    </div>

    <!-- Buscador -->
    <div class="mb-4">
      <input v-model="search" class="input-clinical max-w-xs" placeholder="Buscar por nombre o DNI..." />
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Empleado</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">DNI</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Cargo</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Modalidad</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Antiguedad</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Estado</th>
            <th class="text-right font-medium px-5 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="emp in empleadosFiltrados" :key="emp.id" style="border-bottom: 1px solid var(--line)">
            <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ emp.nombre_completo }}</td>
            <td class="px-5 py-3 font-mono text-xs" style="color: var(--ink-soft)">{{ emp.dni }}</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ emp.cargo_laboral || '—' }}</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ emp.modalidad || '—' }}</td>
            <td class="px-5 py-3 text-xs" style="color: var(--ink-soft)">{{ emp.antiguedad || '—' }}</td>
            <td class="px-5 py-3">
              <span class="badge" :class="emp.is_active ? 'badge--ok' : 'badge--neutral'">
                {{ emp.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-5 py-3 text-right">
              <NuxtLink
                :to="`/sigarh/rrhh/empleados/${emp.id}?tenant=${tenantId}`"
                class="text-sm font-medium mr-3"
                style="color: var(--teal)"
              >Editar</NuxtLink>
              <button class="text-sm font-medium" style="color: var(--alert)" @click="confirmarEliminar(emp)">Eliminar</button>
            </td>
          </tr>
          <tr v-if="!empleadosFiltrados.length">
            <td colspan="7" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">
              {{ search ? 'Sin resultados.' : 'Sin empleados registrados.' }}
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

interface Empleado {
  id: string
  dni: string
  nombre_completo: string
  cargo_laboral: string | null
  modalidad: string | null
  is_active: boolean
  fecha_ingreso: string | null
  antiguedad: string | null
}

const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const empleados = ref<Empleado[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')

const empleadosFiltrados = computed(() => {
  if (!search.value.trim()) return empleados.value
  const q = search.value.toLowerCase()
  return empleados.value.filter(e =>
    e.nombre_completo.toLowerCase().includes(q) ||
    e.dni.includes(q)
  )
})

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    empleados.value = await api<Empleado[]>('/sigarh/rrhh/empleados')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexion'
  } finally {
    loading.value = false
  }
}

const confirmarEliminar = async (emp: Empleado) => {
  if (!confirm(`¿Eliminar a "${emp.nombre_completo}"?`)) return
  try {
    await api(`/sigarh/rrhh/empleados/${emp.id}`, { method: 'DELETE' })
    empleados.value = empleados.value.filter(e => e.id !== emp.id)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar'
  }
}

onMounted(cargar)
</script>