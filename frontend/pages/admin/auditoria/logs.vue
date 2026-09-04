<!-- frontend/pages/admin/auditoria/logs.vue -->
<template>
  <div>
    <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
      <span>Logs del Sistema</span><span>/</span><span>Listado</span>
    </div>
    <h1 class="text-lg font-semibold mb-4" style="color: var(--ink)">
      Logs del Sistema {{ selectedLabel ? `(${selectedLabel})` : '' }}
    </h1>

    <!-- Selector -->
    <div class="mb-4 flex items-center gap-3">
      <label class="text-sm" style="color: var(--ink-soft)">Ver logs de:</label>
      <select v-model="selected" class="input-clinical max-w-xs" @change="onChangeSelected">
        <option value="__global__">— BD Central (administración global) —</option>
        <option v-for="h in hospitales" :key="h.id" :value="h.id">
          {{ h.name }} ({{ h.domain }})
        </option>
      </select>
      <span v-if="selected === '__global__'" class="badge badge--ok">BD Central activa</span>
      <span v-else class="badge badge--ok">Hospital activo</span>
    </div>

    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Fecha y Hora</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Canal</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Evento</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Modelo</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Usuario</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Descripción</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Cambios</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="log in logs" :key="log.id">
            <tr style="border-bottom: 1px solid var(--line)">
              <td class="px-5 py-3" style="color: var(--ink)">
                <div>{{ relativeTime(log.created_at) }}</div>
                <div class="text-xs" style="color: var(--ink-soft)">{{ formatDate(log.created_at) }}</div>
              </td>
              <td class="px-5 py-3">
                <span class="badge badge--neutral">default</span>
              </td>
              <td class="px-5 py-3">
                <span class="badge badge--neutral">{{ log.action }}</span>
              </td>
              <td class="px-5 py-3" style="color: var(--ink-soft)">
                {{ log.model || '—' }}
                <span v-if="log.model_id" class="text-xs block">ID: {{ log.model_id }}</span>
              </td>
              <td class="px-5 py-3 font-medium" style="color: var(--ink)">
                {{ log.user_name || 'Sistema' }}
              </td>
              <td class="px-5 py-3" style="color: var(--ink-soft)">{{ log.description || '—' }}</td>
              <td class="px-5 py-3">
                <span v-if="!log.old_values && !log.new_values" style="color: var(--ink-soft)">—</span>
                <button
                  v-else
                  class="text-sm font-medium"
                  style="color: var(--teal)"
                  @click="toggleExpand(log.id)"
                >
                  {{ expanded === log.id ? 'Ocultar' : 'Ver cambios' }}
                </button>
              </td>
            </tr>
            <tr v-if="expanded === log.id" style="border-bottom: 1px solid var(--line); background: var(--mist)">
              <td colspan="7" class="px-5 py-3">
                <div class="grid grid-cols-2 gap-4 text-xs">
                  <div>
                    <p class="font-medium mb-1" style="color: var(--ink-soft)">Valores anteriores</p>
                    <pre class="p-2 rounded" style="background: var(--paper); overflow-x: auto">{{ pretty(log.old_values) }}</pre>
                  </div>
                  <div>
                    <p class="font-medium mb-1" style="color: var(--ink-soft)">Valores nuevos</p>
                    <pre class="p-2 rounded" style="background: var(--paper); overflow-x: auto">{{ pretty(log.new_values) }}</pre>
                  </div>
                </div>
              </td>
            </tr>
          </template>
          <tr v-if="!logs.length">
            <td colspan="7" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">
              Sin registros para esta selección.
            </td>
          </tr>
        </tbody>
      </table>
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
  model_id: string | null
  description: string | null
  old_values: Record<string, any> | null
  new_values: Record<string, any> | null
  ip_address: string | null
  created_at: string
}

interface Hospital {
  id: string
  name: string
  domain: string
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const hospitales = ref<Hospital[]>([])
const selected = ref<string>((route.query.tenant as string) || '__global__')
const logs = ref<AuditLog[]>([])
const loading = ref(true)
const error = ref('')
const expanded = ref<string | null>(null)

const selectedLabel = computed(() => {
  if (selected.value === '__global__') return 'BD Central'
  const h = hospitales.value.find(h => h.id === selected.value)
  return h ? h.name : ''
})

const toggleExpand = (id: string) => {
  expanded.value = expanded.value === id ? null : id
}

const pretty = (val: Record<string, any> | null) => {
  if (!val) return '(vacío)'
  return JSON.stringify(val, null, 2)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric',
    hour: '2-digit', minute: '2-digit', second: '2-digit',
  })
}

const relativeTime = (date: string) => {
  const diffMs = Date.now() - new Date(date).getTime()
  const seconds = Math.floor(diffMs / 1000)
  if (seconds < 60) return `hace ${seconds} segundos`
  const minutes = Math.floor(seconds / 60)
  if (minutes < 60) return `hace ${minutes} minuto${minutes === 1 ? '' : 's'}`
  const hours = Math.floor(minutes / 60)
  if (hours < 24) return `hace ${hours} hora${hours === 1 ? '' : 's'}`
  const days = Math.floor(hours / 24)
  return `hace ${days} día${days === 1 ? '' : 's'}`
}

const onChangeSelected = () => {
  expanded.value = null
  router.replace({ query: { ...route.query, tenant: selected.value === '__global__' ? undefined : selected.value } })
  loadLogs()
}

const loadHospitales = async () => {
  try {
    hospitales.value = await api<Hospital[]>('/admin/hospitales')
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar la lista de hospitales'
  }
}

const loadLogs = async () => {
  loading.value = true
  error.value = ''
  try {
    if (selected.value === '__global__') {
      logs.value = await api<AuditLog[]>('/admin/auditoria?only_global=true&limit=500')
    } else {
      logs.value = await api<AuditLog[]>(`/admin/auditoria/hospital/${selected.value}?limit=500`)
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadHospitales()
  await loadLogs()
})
</script>