<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')

interface Empleado {
  id: string; dni: string; nombre_completo: string; email?: string
  cargo_laboral: string | null; modalidad: string | null
  is_active: boolean; fecha_ingreso: string | null; antiguedad: string | null
}
const empleados = ref<Empleado[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const filtro = ref('all')

const activos = computed(() => empleados.value.filter(e => e.is_active).length)
const avgAntiguedad = computed(() => {
  let total = 0, n = 0
  empleados.value.forEach(e => {
    const m = e.antiguedad?.match(/(\d+)\s*año/)
    if (m) { total += parseInt(m[1]); n++ }
  })
  if (!n) return '—'
  const a = Math.round(total / n)
  return `${a} año${a !== 1 ? 's' : ''}`
})

const filtrados = computed(() => {
  let r = empleados.value
  if (filtro.value === 'active') r = r.filter(e => e.is_active)
  else if (filtro.value === 'inactive') r = r.filter(e => !e.is_active)
  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    r = r.filter(e => e.nombre_completo.toLowerCase().includes(q) || e.dni.includes(q) || (e.cargo_laboral || '').toLowerCase().includes(q))
  }
  return r
})

const iniciales = (n: string) => n.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
const avatarColor = (n: string) => {
  const c = ['var(--teal-soft)', 'var(--purple-soft)', 'var(--navy-soft)', 'var(--amber-soft)', 'var(--green-soft)', 'var(--orange-soft)']
  let h = 0
  for (let i = 0; i < n.length; i++) h = n.charCodeAt(i) + ((h << 5) - h)
  return c[Math.abs(h) % c.length]
}

const eliminar = async (e: Empleado) => {
  if (!confirm(`Eliminar al empleado "${e.nombre_completo}"? Esta acción no se puede deshacer.`)) return
  try { await api(`/sigarh/rrhh/empleados/${e.id}`, { method: 'DELETE' }); empleados.value = empleados.value.filter(x => x.id !== e.id) }
  catch (err: any) { error.value = apiErr(err, 'No se pudo eliminar') }
}
const cargar = async () => {
  loading.value = true; error.value = ''
  try { empleados.value = await api<Empleado[]>('/sigarh/rrhh/empleados') }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
onMounted(cargar)
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--teal)" /></div>
        <div><h1 class="page-title">Empleados</h1><p class="page-subtitle">Personal registrado en el hospital</p></div>
      </div>
      <NuxtLink :to="`/sigarh/rrhh/empleados/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Empleado</NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><div class="sigarh-stat-value">{{ empleados.length }}</div><div class="sigarh-stat-label">Total</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)"><UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" /></div>
        <div><div class="sigarh-stat-value">{{ activos }}</div><div class="sigarh-stat-label">Activos</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)"><UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" /></div>
        <div><div class="sigarh-stat-value">{{ empleados.length - activos }}</div><div class="sigarh-stat-label">Inactivos</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)"><UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--purple)" /></div>
        <div><div class="sigarh-stat-value">{{ avgAntiguedad }}</div><div class="sigarh-stat-label">Antigüedad media</div></div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar por nombre, DNI o cargo..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button @click="filtro = 'all'" class="sigarh-filter-btn" :class="{ active: filtro === 'all' }">Todos <span class="sigarh-filter-count">{{ empleados.length }}</span></button>
            <button @click="filtro = 'active'" class="sigarh-filter-btn" :class="{ active: filtro === 'active' }">Activos <span class="sigarh-filter-count">{{ activos }}</span></button>
            <button @click="filtro = 'inactive'" class="sigarh-filter-btn" :class="{ active: filtro === 'inactive' }">Inactivos <span class="sigarh-filter-count">{{ empleados.length - activos }}</span></button>
          </div>
        </div>
        <span class="sigarh-result-count">{{ filtrados.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" /><p style="color: var(--ink-soft)">Cargando empleados...</p></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!filtrados.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-users" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" />
        <div><p style="font-weight: 600; color: var(--ink); margin: 0">Sin empleados</p><p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0">Comienza registrando el personal del hospital</p></div>
        <NuxtLink :to="`/sigarh/rrhh/empleados/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo</NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr><th style="width: 28%">Empleado</th><th style="width: 12%">DNI</th><th style="width: 20%">Cargo</th><th style="width: 14%">Modalidad</th><th style="width: 12%">Antigüedad</th><th style="width: 9%">Estado</th><th style="width: 5%; text-align: right">Acciones</th></tr></thead>
          <tbody>
            <tr v-for="e in filtrados" :key="e.id">
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" :style="{ background: avatarColor(e.nombre_completo), fontWeight: 600, fontSize: '0.7rem', color: 'var(--ink)' }">{{ iniciales(e.nombre_completo) }}</div>
                  <div>
                    <span class="sigarh-item-name">{{ e.nombre_completo }}</span>
                    <div v-if="e.email" style="font-size: 0.72rem; color: var(--ink-soft)">{{ e.email }}</div>
                  </div>
                </div>
              </td>
              <td><span class="sigarh-code-badge">{{ e.dni }}</span></td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ e.cargo_laboral || '-' }}</td>
              <td><span v-if="e.modalidad" class="badge badge--neutral" style="text-transform: capitalize">{{ e.modalidad }}</span><span v-else style="color: var(--ink-soft)">-</span></td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ e.antiguedad || '-' }}</td>
              <td><span class="badge" :class="e.is_active ? 'badge--ok' : 'badge--neutral'">{{ e.is_active ? 'Activo' : 'Inactivo' }}</span></td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/rrhh/empleados/${e.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" /></NuxtLink>
                  <button class="sigarh-action-btn danger" title="Eliminar" @click="eliminar(e)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">Mostrando <strong>{{ filtrados.length }}</strong> de <strong>{{ empleados.length }}</strong> empleados</div>
      </div>
    </div>
  </div>
</template>
