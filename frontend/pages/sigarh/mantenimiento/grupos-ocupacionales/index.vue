<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
          <span>SIGARH</span><span>/</span><span>Mantenimiento</span><span>/</span><span>Grupos Ocupacionales</span>
        </div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">Grupos Ocupacionales</h1>
        <p class="text-sm" style="color: var(--ink-soft)">Grupos ocupacionales del personal</p>
      </div>
      <NuxtLink :to="`/sigarh/mantenimiento/grupos-ocupacionales/create?tenant=${tenantId}`" class="btn-primary">
        + Nuevo Grupo
      </NuxtLink>
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Nombre</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Codigo</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Descripcion</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Estado</th>
            <th class="text-right font-medium px-5 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id" style="border-bottom: 1px solid var(--line)">
            <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ item.nombre }}</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ item.codigo || '—' }}</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ item.descripcion || '—' }}</td>
            <td class="px-5 py-3">
              <span class="badge" :class="item.is_active ? 'badge--ok' : 'badge--neutral'">
                {{ item.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-5 py-3 text-right">
              <NuxtLink :to="`/sigarh/mantenimiento/grupos-ocupacionales/${item.id}?tenant=${tenantId}`" class="text-sm font-medium mr-3" style="color: var(--teal)">Editar</NuxtLink>
              <button class="text-sm font-medium" style="color: var(--alert)" @click="confirmarEliminar(item)">Eliminar</button>
            </td>
          </tr>
          <tr v-if="!items.length">
            <td colspan="5" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">Sin grupos ocupacionales registrados.</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
interface Item { id: string; nombre: string; codigo: string | null; descripcion: string | null; is_active: boolean }
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const cargar = async () => {
  loading.value = true
  error.value = ''
  try { items.value = await api<Item[]>('/sigarh/mantenimiento/grupos-ocupacionales') }
  catch (e: any) { error.value = e?.data?.detail || 'Error de conexion' }
  finally { loading.value = false }
}
const confirmarEliminar = async (item: Item) => {
  if (!confirm(`¿Eliminar "${item.nombre}"?`)) return
  try { await api(`/sigarh/mantenimiento/grupos-ocupacionales/${item.id}`, { method: 'DELETE' }); items.value = items.value.filter(i => i.id !== item.id) }
  catch (e: any) { error.value = e?.data?.detail || 'No se pudo eliminar' }
}
onMounted(cargar)
</script>