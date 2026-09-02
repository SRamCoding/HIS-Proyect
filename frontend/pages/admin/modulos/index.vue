<template>
  <div>
    <div class="mb-6">
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Catalogo de Modulos</h1>
      <p class="text-sm" style="color: var(--ink-soft)">Modulos disponibles en el ERP</p>
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Codigo</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Nombre</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Panel</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="m in modulos" :key="m.id" style="border-bottom: 1px solid var(--line)">
            <td class="px-5 py-3 font-mono text-xs" style="color: var(--ink-soft)">{{ m.code }}</td>
            <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ m.name }}</td>
            <td class="px-5 py-3">
              <span class="badge" :class="m.category === 'app' ? 'badge--ok' : 'badge--neutral'">
                {{ m.category === 'app' ? 'Hospitalario' : 'SIGARH' }}
              </span>
            </td>
            <td class="px-5 py-3">
              <span class="badge" :class="m.is_active ? 'badge--ok' : 'badge--neutral'">
                {{ m.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
          </tr>
          <tr v-if="!modulos.length">
            <td colspan="4" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">
              Sin modulos registrados.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Modulo {
  id: string
  code: string
  name: string
  category: string
  is_active: boolean
}

const { api } = useApi()
const modulos = ref<Modulo[]>([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    modulos.value = await api<Modulo[]>('/admin/modulos/catalogo')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexion'
  } finally {
    loading.value = false
  }
})
</script>