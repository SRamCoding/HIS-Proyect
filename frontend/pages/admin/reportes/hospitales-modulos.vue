<template>
  <div class="auditoria-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-squares-plus" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <h1 class="page-title">Reporte de Hospitales y Módulos</h1>
          <p class="page-subtitle">Módulos activos por cada hospital habilitado en el sistema.</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary" @click="exportCsv">
          <UIcon name="i-heroicons-arrow-down-tray" class="w-4 h-4" />
          Exportar CSV
        </button>
      </div>
    </div>

    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
      <div class="table-toolbar">
        <div class="search-wrapper" style="max-width: 320px;">
          <UIcon name="i-heroicons-magnifying-glass" class="search-icon" />
          <input v-model="search" class="search-input" placeholder="Buscar hospital..." />
        </div>
      </div>
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando reporte...</p>
      </div>
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
      </div>
      <div v-else-if="!filtrados.length" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-squares-plus" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">{{ search ? 'Sin resultados' : 'Sin hospitales activos' }}</h3>
      </div>
      <div v-else class="table-responsive">
        <table class="auditoria-table">
          <thead>
            <tr>
              <th><span class="th-content">Hospital</span></th>
              <th><span class="th-content">Dominio</span></th>
              <th><span class="th-content">Módulos Activos</span></th>
              <th><span class="th-content">Total</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in filtrados" :key="row.domain">
              <td class="user-name">{{ row.hospital_name }}</td>
              <td class="ip-text">{{ row.domain }}</td>
              <td>
                <div class="module-tags-wrap">
                  <span v-for="mod in row.active_modules" :key="mod" class="badge badge--neutral">{{ mod }}</span>
                </div>
              </td>
              <td class="user-name">{{ row.total_modules }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface HospitalModuleReport {
  hospital_name: string
  domain: string
  active_modules: string[]
  total_modules: number
}

const { api } = useApi()

const rows = ref<HospitalModuleReport[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')

const filtrados = computed(() => {
  if (!search.value.trim()) return rows.value
  const q = search.value.toLowerCase()
  return rows.value.filter(r =>
    r.hospital_name.toLowerCase().includes(q) ||
    r.domain.toLowerCase().includes(q)
  )
})

// Mismo escape que ya usa reportes/exportar.vue: una celda que empieza con
// = + - @ o tab puede interpretarse como formula al abrir el CSV en Excel/
// Sheets -- se le antepone un apostrofe para forzarla a texto plano.
const celdaSegura = (v: string) => /^[=+\-@\t]/.test(v) ? `'${v}` : v

const exportCsv = () => {
  const headers = ['Hospital', 'Dominio', 'Módulos Activos', 'Total']
  const rowsCsv = filtrados.value.map(r => [
    r.hospital_name,
    r.domain,
    r.active_modules.join(' | '),
    String(r.total_modules),
  ])
  const csv = [
    headers.join(','),
    ...rowsCsv.map(r => r.map(v => `"${celdaSegura(String(v ?? '')).replace(/"/g, '""')}"`).join(',')),
  ].join('\n')
  const blob = new Blob(['﻿' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `hospitales_modulos_${new Date().toISOString().slice(0, 10)}.csv`
  a.click()
  URL.revokeObjectURL(url)
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    rows.value = await api<HospitalModuleReport[]>('/admin/reportes/hospitales-modulos')
  } catch (e: any) {
    error.value = apiErr(e, 'Error de conexión')
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.module-tags-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  max-width: 320px;
}
</style>