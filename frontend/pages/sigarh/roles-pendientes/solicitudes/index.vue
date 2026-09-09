<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const { estadoSolicitud, tipoLabel, categoriaLabel } = useRolesTurno()
const tenantId = computed(() => route.query.tenant as string || '')

const items = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const fEstado = ref('')

const roleType = (rt: string | null) => {
  if (!rt) return '—'
  const [cat, tipo] = rt.split('/')
  return `${categoriaLabel(cat)} · ${tipoLabel(tipo)}`
}
const cargar = async () => {
  loading.value = true; error.value = ''
  const q = fEstado.value ? `?status=${fEstado.value}` : ''
  try { items.value = await api<any[]>(`/sigarh/roles-pendientes/solicitudes-modificacion${q}`) }
  catch (e: any) { error.value = e?.data?.detail || 'Error de conexión' }
  finally { loading.value = false }
}
watch(fEstado, cargar)
onMounted(cargar)
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-pencil-square" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <h1 class="page-title">Solicitudes de Modificación</h1>
          <p class="page-subtitle">Incorporaciones de personal a roles ya aprobados</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/roles-pendientes?tenant=${tenantId}`" class="btn-outline">
        <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" /> Bandeja de Roles
      </NuxtLink>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-group">
          <button @click="fEstado = ''" class="sigarh-filter-btn" :class="{ active: fEstado === '' }">Todas</button>
          <button @click="fEstado = 'pendiente'" class="sigarh-filter-btn" :class="{ active: fEstado === 'pendiente' }">Pendientes</button>
          <button @click="fEstado = 'aprobado'" class="sigarh-filter-btn" :class="{ active: fEstado === 'aprobado' }">Aprobadas</button>
          <button @click="fEstado = 'rechazado'" class="sigarh-filter-btn" :class="{ active: fEstado === 'rechazado' }">Rechazadas</button>
        </div>
        <span class="sigarh-result-count">{{ items.length }} solicitudes</span>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--purple)" />
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
      </div>
      <div v-else-if="!items.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-inbox" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <p style="color: var(--ink-soft)">Sin solicitudes</p>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 24%">Modalidad</th>
              <th style="width: 16%">Período</th>
              <th style="width: 20%">Empleado propuesto</th>
              <th style="width: 16%">Solicitado por</th>
              <th style="width: 12%">Estado</th>
              <th style="width: 12%; text-align: right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td style="font-size: 0.8rem">{{ roleType(it.role_type) }}</td>
              <td style="font-size: 0.8125rem">{{ it.rol_periodo || '—' }}</td>
              <td class="sigarh-item-name">{{ it.empleado_nombre || '—' }}</td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.requested_by || '—' }}</td>
              <td><span class="badge" :class="estadoSolicitud(it.status).badge">{{ estadoSolicitud(it.status).label }}</span></td>
              <td style="text-align: right">
                <NuxtLink :to="`/sigarh/roles-pendientes/solicitudes/${it.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Ver">
                  <UIcon name="i-heroicons-eye" class="w-4 h-4" style="color: var(--teal)" />
                </NuxtLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
