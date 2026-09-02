<!-- pages/admin/index.vue -->
<template>
  <div>
    <div class="mb-6">
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Dashboard</h1>
      <p class="text-sm" style="color: var(--ink-soft)">Resumen general de la plataforma</p>
    </div>

    <!-- Stat cards -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div v-for="i in 4" :key="i" class="stat-card animate-pulse">
        <div class="h-3 w-20 rounded mb-3" style="background: var(--line)" />
        <div class="h-6 w-14 rounded" style="background: var(--line)" />
      </div>
    </div>

    <div v-else-if="error" class="text-sm rounded px-4 py-3 mb-8" style="background: var(--alert-soft); color: var(--alert)">
      No se pudo cargar el dashboard: {{ error }}
    </div>

    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
      <div class="stat-card">
        <p class="text-xs font-medium mb-1" style="color: var(--ink-soft)">Hospitales activos</p>
        <p class="text-2xl font-semibold font-mono-data" style="color: var(--ink)">
          {{ stats?.hospitales_activos ?? '—' }}
        </p>
      </div>

      <div class="stat-card stat-card--ok">
        <p class="text-xs font-medium mb-1" style="color: var(--ink-soft)">Usuarios totales</p>
        <p class="text-2xl font-semibold font-mono-data" style="color: var(--ink)">
          {{ stats?.usuarios_totales ?? '—' }}
        </p>
      </div>

      <div class="stat-card stat-card--warn">
        <p class="text-xs font-medium mb-1" style="color: var(--ink-soft)">Módulos activos</p>
        <p class="text-2xl font-semibold font-mono-data" style="color: var(--ink)">
          {{ stats?.modulos_activos ?? '—' }}
        </p>
      </div>

      <div class="stat-card stat-card--alert">
        <p class="text-xs font-medium mb-1" style="color: var(--ink-soft)">Eventos de auditoría (24h)</p>
        <p class="text-2xl font-semibold font-mono-data" style="color: var(--ink)">
          {{ stats?.eventos_auditoria_24h ?? '—' }}
        </p>
      </div>
    </div>

    <!-- Hospitales recientes -->
    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div class="flex items-center justify-between px-5 py-4" style="border-bottom: 1px solid var(--line)">
        <h2 class="text-sm font-medium" style="color: var(--ink)">Hospitales recientes</h2>
        <NuxtLink to="/admin/hospitales" class="text-sm font-medium" style="color: var(--teal)">
          Ver todos →
        </NuxtLink>
      </div>

      <div v-if="loadingHospitales" class="p-5 text-sm" style="color: var(--ink-soft)">
        Cargando…
      </div>

      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-2.5" style="color: var(--ink-soft)">Nombre</th>
            <th class="text-left font-medium px-5 py-2.5" style="color: var(--ink-soft)">Nivel MINSA</th>
            <th class="text-left font-medium px-5 py-2.5" style="color: var(--ink-soft)">Estado</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="h in hospitalesRecientes"
            :key="h.id"
            style="border-bottom: 1px solid var(--line)"
          >
            <td class="px-5 py-3" style="color: var(--ink)">{{ h.nombre }}</td>
            <td class="px-5 py-3 font-mono-data" style="color: var(--ink-soft)">{{ h.nivel_minsa ?? '—' }}</td>
            <td class="px-5 py-3">
              <span class="badge" :class="h.activo ? 'badge--ok' : 'badge--neutral'">
                {{ h.activo ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
          </tr>
          <tr v-if="!hospitalesRecientes.length">
            <td colspan="3" class="px-5 py-6 text-center text-sm" style="color: var(--ink-soft)">
              Sin hospitales registrados todavía.
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface DashboardStats {
  hospitales_activos: number
  usuarios_totales: number
  modulos_activos: number
  eventos_auditoria_24h: number
}

interface Hospital {
  id: string
  nombre: string
  nivel_minsa?: string
  activo: boolean
}

const { api } = useApi()

const stats = ref<DashboardStats | null>(null)
const hospitalesRecientes = ref<Hospital[]>([])
const loading = ref(true)
const loadingHospitales = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    stats.value = await api<DashboardStats>('/admin/dashboard')
  } catch (e: any) {
    error.value = e?.data?.detail || 'error de conexión'
  } finally {
    loading.value = false
  }

  try {
    const data = await api<Hospital[]>('/admin/hospitales')
    hospitalesRecientes.value = data.slice(0, 5)
  } finally {
    loadingHospitales.value = false
  }
})
</script>