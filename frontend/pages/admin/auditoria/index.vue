<template>
  <div>
    <div class="mb-6">
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Auditoría del ERP</h1>
      <p class="text-sm" style="color: var(--ink-soft)">
        Registro de acciones a nivel de todo el sistema: creación/edición de hospitales, catálogo de módulos, e inicios de sesión.
      </p>
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <!-- Buscador -->
      <div class="flex justify-end px-4 py-3" style="border-bottom: 1px solid var(--line)">
        <input v-model="search" class="input-clinical max-w-xs" placeholder="Buscar..." />
      </div>

      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>

      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Fecha</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Usuario</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Acción</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Tipo</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Sobre</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">IP</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="log in logsFiltrados" :key="log.id" style="border-bottom: 1px solid var(--line)">
            <td class="px-5 py-3 text-xs" style="color: var(--ink-soft)">{{ formatDate(log.created_at) }}</td>
            <td class="px-5 py-3 font-medium" style="color: var(--ink)">{{ log.user_name || 'Sistema' }}</td>
            <td class="px-5 py-3" style="color: var(--ink)">{{ log.description || log.action }}</td>
            <td class="px-5 py-3">
              <span
                class="text-xs px-2 py-0.5 rounded font-medium"
                :style="accionColor(log.action)"
              >{{ log.action }}</span>
            </td>
            <td class="px-5 py-3" style="color: var(--ink-soft)">{{ log.model || '—' }}</td>
            <td class="px-5 py-3 text-xs" style="color: var(--ink-soft)">{{ log.ip_address || '—' }}</td>
          </tr>
          <tr v-if="!logsFiltrados.length">
            <td colspan="6" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">
              Sin registros de auditoría.
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Paginación simple -->
      <div v-if="logs.length" class="flex items-center justify-between px-5 py-3" style="border-top: 1px solid var(--line)">
        <p class="text-xs" style="color: var(--ink-soft)">
          Mostrando {{ logsFiltrados.length }} de {{ logs.length }} registros
        </p>
        <div class="flex gap-1">
          <button
            class="px-3 py-1 text-xs rounded"
            style="border: 1px solid var(--line); color: var(--ink-soft)"
            :disabled="page === 1"
            @click="page--"
          >Anterior</button>
          <span class="px-3 py-1 text-xs" style="color: var(--ink)">{{ page }}</span>
          <button
            class="px-3 py-1 text-xs rounded"
            style="border: 1px solid var(--line); color: var(--ink-soft)"
            :disabled="page * perPage >= logs.length"
            @click="page++"
          >Siguiente</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface AuditLog {
  id: string
  user_name: string | null
  tenant_name: string | null
  action: string
  model: string | null
  description: string | null
  ip_address: string | null
  created_at: string
}

const { api } = useApi()
const logs = ref<AuditLog[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const page = ref(1)
const perPage = 10

const formatDate = (d: string) => new Date(d).toLocaleString('es-PE', {
  day: '2-digit', month: '2-digit', year: 'numeric',
  hour: '2-digit', minute: '2-digit', second: '2-digit'
})

const accionColor = (action: string) => {
  const map: Record<string, string> = {
    login: 'background: #e8f4fd; color: #1a6fa8',
    logout: 'background: #f0f0f0; color: #555',
    login_failed: 'background: #fde8e8; color: #a81a1a',
    created: 'background: #e8f8f0; color: #1a7a45',
    updated: 'background: #fdf0e8; color: #a85c1a',
    deleted: 'background: #fde8e8; color: #a81a1a',
  }
  return map[action] || 'background: #f0f0f0; color: #555'
}

const logsFiltrados = computed(() => {
  let list = logs.value
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(l =>
      l.user_name?.toLowerCase().includes(q) ||
      l.action?.toLowerCase().includes(q) ||
      l.description?.toLowerCase().includes(q)
    )
  }
  const start = (page.value - 1) * perPage
  return list.slice(start, start + perPage)
})

onMounted(async () => {
  try {
    logs.value = await api<AuditLog[]>('/admin/auditoria?limit=500')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexion'
  } finally {
    loading.value = false
  }
})
</script>