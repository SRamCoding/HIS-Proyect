<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">Niveles Hospitalarios</h1>
        <p class="text-sm" style="color: var(--ink-soft)">Niveles MINSA con sus módulos por defecto</p>
      </div>
      <NuxtLink to="/admin/niveles-hospitalarios/create" class="btn-primary">
        + Crear Nivel
      </NuxtLink>
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Código</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Nombre</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Módulos</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Orden</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Activo</th>
            <th class="text-right font-medium px-5 py-3" style="color: var(--ink-soft)"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="n in niveles" :key="n.id" style="border-bottom: 1px solid var(--line)">
            <td class="px-5 py-3">
              <span
                class="text-xs font-bold px-2 py-1 rounded"
                :style="{ background: n.color || '#6B7280', color: '#fff' }"
              >{{ n.code }}</span>
            </td>
            <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ n.name }}</td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">
              {{ (n.default_modules?.app?.length || 0) + (n.default_modules?.sigarh?.length || 0) }} módulos
            </td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ n.sort_order }}</td>
            <td class="px-5 py-3">
              <span class="badge" :class="n.is_active ? 'badge--ok' : 'badge--neutral'">
                {{ n.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="px-5 py-3 text-right">
              <NuxtLink
                :to="`/admin/niveles-hospitalarios/${n.id}`"
                class="text-sm font-medium"
                style="color: var(--teal)"
              >
                Editar
              </NuxtLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

const { api } = useApi()
const niveles = ref<any[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    niveles.value = await api<any[]>('/admin/niveles-hospitalarios')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexion'
  } finally {
    loading.value = false
  }
})
</script>