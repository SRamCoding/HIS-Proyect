<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
          <span>SIGARH</span><span>/</span><span>Recursos Humanos</span><span>/</span><span>Justificaciones e Inasistencias</span>
        </div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">Justificaciones e Inasistencias</h1>
        <p class="text-sm" style="color: var(--ink-soft)">Registro de justificaciones del personal</p>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/justificaciones/create?tenant=${tenantId}`" class="btn-primary">
        + Nueva Justificacion
      </NuxtLink>
    </div>

    <!-- Filtros -->
    <div class="flex gap-3 mb-4">
      <select v-model="filtroEstado" class="input-clinical max-w-xs" @change="cargar">
        <option value="">Todos los estados</option>
        <option value="pendiente">Pendiente</option>
        <option value="aprobado">Aprobado</option>
        <option value="rechazado">Rechazado</option>
      </select>
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Empleado</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Motivo</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Fecha Inicio</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Fecha Fin</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Estado</th>
            <th class="text-right font-medium px-5 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" style="border-bottom: 1px solid var(--line)">
            <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ item.empleado_nombre || '—' }}</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ item.motivo_nombre || '—' }}</td>
            <td class="px-5 py-3 font-mono text-xs" style="color: var(--ink-soft)">{{ item.fecha_inicio }}</td>
            <td class="px-5 py-3 font-mono text-xs" style="color: var(--ink-soft)">{{ item.fecha_fin }}</td>
            <td class="px-5 py-3">
              <span class="text-xs px-2 py-0.5 rounded font-medium" :style="estadoColor(item.estado)">
                {{ item.estado }}
              </span>
            </td>
            <td class="px-5 py-3 text-right">
              <NuxtLink :to="`/sigarh/rrhh/justificaciones/${item.id}?tenant=${tenantId}`" class="text-sm font-medium" style="color: var(--teal)">Ver</NuxtLink>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="6" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">Sin justificaciones registradas.</td>
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
  motivo_nombre: string | null
  fecha_inicio: string
  fecha_fin: string
  estado: string
}
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const filtroEstado = ref('')

const estadoColor = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'background: #fdf0e8; color: #a85c1a',
    aprobado: 'background: #e8f8f0; color: #1a7a45',
    rechazado: 'background: #fde8e8; color: #a81a1a',
  }
  return map[estado] || 'background: var(--mist); color: var(--ink-soft)'
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    const params = filtroEstado.value ? `?estado=${filtroEstado.value}` : ''
    items.value = await api<Item[]>(`/sigarh/rrhh/justificaciones${params}`)
  } catch (e: any) { error.value = e?.data?.detail || 'Error de conexion' }
  finally { loading.value = false }
}
onMounted(cargar)
</script>