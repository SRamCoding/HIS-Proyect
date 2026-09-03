<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
          <span>SIGARH</span><span>/</span><span>Recursos Humanos</span><span>/</span><span>Tolerancias</span>
        </div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">Tolerancias</h1>
        <p class="text-sm" style="color: var(--ink-soft)">Margenes de tolerancia para marcaciones de asistencia</p>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/tolerancias/create?tenant=${tenantId}`" class="btn-primary">
        + Nueva Tolerancia
      </NuxtLink>
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Nombre</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Min. Entrada</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Min. Salida</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Estado</th>
            <th class="text-right font-medium px-5 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" style="border-bottom: 1px solid var(--line)">
            <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ item.nombre }}</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ item.minutos_entrada }} min</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ item.minutos_salida }} min</td>
            <td class="px-5 py-3">
              <span class="badge" :class="item.is_active ? 'badge--ok' : 'badge--neutral'">
                {{ item.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-5 py-3 text-right">
              <NuxtLink :to="`/sigarh/rrhh/tolerancias/${item.id}?tenant=${tenantId}`" class="text-sm font-medium mr-3" style="color: var(--teal)">Editar</NuxtLink>
              <button class="text-sm font-medium" style="color: var(--alert)" @click="confirmarEliminar(item)">Eliminar</button>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="5" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">Sin tolerancias registradas.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
interface Item { id: string; nombre: string; minutos_entrada: number; minutos_salida: number; is_active: boolean }
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const cargar = async () => {
  loading.value = true
  error.value = ''
  try { items.value = await api<Item[]>('/sigarh/rrhh/tolerancias') }
  catch (e: any) { error.value = e?.data?.detail || 'Error de conexion' }
  finally { loading.value = false }
}
const confirmarEliminar = async (item: Item) => {
  if (!confirm(`¿Eliminar "${item.nombre}"?`)) return
  try { await api(`/sigarh/rrhh/tolerancias/${item.id}`, { method: 'DELETE' }); items.value = items.value.filter(i => i.id !== item.id) }
  catch (e: any) { error.value = e?.data?.detail || 'No se pudo eliminar' }
}
onMounted(cargar)
</script>