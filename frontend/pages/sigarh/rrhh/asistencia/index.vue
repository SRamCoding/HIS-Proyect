<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
          <span>SIGARH</span><span>/</span><span>Recursos Humanos</span><span>/</span><span>Registro de Asistencia</span>
        </div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">Registro de Asistencia</h1>
        <p class="text-sm" style="color: var(--ink-soft)">Control de asistencia diaria del personal</p>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/asistencia/create?tenant=${tenantId}`" class="btn-primary">
        + Registrar Asistencia
      </NuxtLink>
    </div>

    <div class="flex gap-3 mb-4">
      <input v-model="filtroFecha" type="date" class="input-clinical max-w-xs" @change="cargar" />
      <select v-model="filtroEmpleado" class="input-clinical max-w-xs" @change="cargar">
        <option value="">Todos los empleados</option>
        <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre_completo }}</option>
      </select>
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Empleado</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Fecha</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Entrada</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Salida</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Estado</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Observacion</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" style="border-bottom: 1px solid var(--line)">
            <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ item.empleado_nombre || '—' }}</td>
            <td class="px-5 py-3 font-mono text-xs" style="color: var(--ink-soft)">{{ item.fecha }}</td>
            <td class="px-5 py-3 font-mono text-xs" style="color: var(--ink-soft)">{{ item.hora_entrada || '—' }}</td>
            <td class="px-5 py-3 font-mono text-xs" style="color: var(--ink-soft)">{{ item.hora_salida || '—' }}</td>
            <td class="px-5 py-3">
              <span class="text-xs px-2 py-0.5 rounded font-medium" :style="estadoColor(item.estado)">
                {{ item.estado }}
              </span>
            </td>
            <td class="px-5 py-3 text-xs" style="color: var(--ink-soft)">{{ item.observacion || '—' }}</td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="6" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">Sin registros de asistencia.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
interface Item {
  id: string
  empleado_nombre: string | null
  fecha: string
  hora_entrada: string | null
  hora_salida: string | null
  estado: string
  observacion: string | null
}
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const empleados = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const filtroFecha = ref('')
const filtroEmpleado = ref('')

const estadoColor = (estado: string) => {
  const map: Record<string, string> = {
    presente: 'background: #e8f8f0; color: #1a7a45',
    ausente: 'background: #fde8e8; color: #a81a1a',
    tardanza: 'background: #fdf0e8; color: #a85c1a',
    justificado: 'background: #e8f4fd; color: #1a6fa8',
  }
  return map[estado] || 'background: var(--mist); color: var(--ink-soft)'
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams()
    if (filtroFecha.value) params.append('fecha', filtroFecha.value)
    if (filtroEmpleado.value) params.append('empleado_id', filtroEmpleado.value)
    const query = params.toString() ? `?${params.toString()}` : ''
    items.value = await api<Item[]>(`/sigarh/rrhh/asistencia${query}`)
  } catch (e: any) { error.value = e?.data?.detail || 'Error de conexion' }
  finally { loading.value = false }
}

onMounted(async () => {
  filtroFecha.value = new Date().toISOString().split('T')[0]
  const [_, emp] = await Promise.all([cargar(), api<any[]>('/sigarh/rrhh/empleados')])
  empleados.value = emp
})
</script>