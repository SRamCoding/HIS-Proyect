<!-- frontend/pages/admin/reportes/exportar.vue -->
<template>
  <div>
    <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
      <span>Reportes</span><span>/</span><span>Exportar Datos</span>
    </div>
    <h1 class="text-lg font-semibold mb-1" style="color: var(--ink)">Exportar Datos</h1>
    <p class="text-sm mb-4" style="color: var(--ink-soft)">
      Descarga cualquier tabla del sistema en formato CSV.
    </p>

    <div class="p-4 mb-4" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <label class="text-xs block mb-1" style="color: var(--ink-soft)">Selecciona qué exportar</label>
      <select v-model="tabla" class="input-clinical w-full max-w-xs">
        <option value="hospitales">Hospitales</option>
        <option value="usuarios">Usuarios</option>
        <option value="auditoria">Auditoría del ERP</option>
      </select>

      <div v-if="tabla === 'auditoria'" class="mt-3">
        <label class="text-xs block mb-1" style="color: var(--ink-soft)">Límite de registros</label>
        <select v-model.number="auditLimit" class="input-clinical w-full max-w-xs">
          <option :value="100">Últimos 100</option>
          <option :value="500">Últimos 500</option>
          <option :value="1000">Últimos 1000</option>
        </select>
      </div>

      <div class="mt-4">
        <button class="btn-primary" :disabled="loading" @click="exportar">
          {{ loading ? 'Generando...' : 'Descargar CSV' }}
        </button>
      </div>

      <p v-if="error" class="text-sm mt-3" style="color: var(--alert)">{{ error }}</p>
      <p v-if="success" class="text-sm mt-3" style="color: var(--teal)">Archivo descargado correctamente.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Hospital {
  id: string
  name: string
  domain: string
  hospital_level: string | null
  is_active: boolean
  active_modules: string[]
  created_at: string
}

interface UsuarioConHospital {
  id: string
  name: string
  email: string
  role: string
  panel: string
  is_active: boolean
  tenant_name: string
  tenant_id: string | null
  created_at: string
}

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

const tabla = ref<'hospitales' | 'usuarios' | 'auditoria'>('hospitales')
const auditLimit = ref(500)
const loading = ref(false)
const error = ref('')
const success = ref(false)

const downloadCsv = (headers: string[], rows: string[][], filename: string) => {
  const csv = [
    headers.join(','),
    ...rows.map(r => r.map(v => `"${String(v ?? '').replace(/"/g, '""')}"`).join(',')),
  ].join('\n')
  const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

const exportar = async () => {
  loading.value = true
  error.value = ''
  success.value = false
  const today = new Date().toISOString().slice(0, 10)

  try {
    if (tabla.value === 'hospitales') {
      const data = await api<Hospital[]>('/admin/hospitales')
      downloadCsv(
        ['Nombre', 'Dominio', 'Nivel', 'Estado', 'Módulos Activos', 'Total Módulos', 'Registrado'],
        data.map(h => [
          h.name,
          h.domain,
          h.hospital_level || '—',
          h.is_active ? 'Activo' : 'Inactivo',
          h.active_modules.join(' | '),
          String(h.active_modules.length),
          formatDate(h.created_at),
        ]),
        `hospitales_${today}.csv`
      )
    } else if (tabla.value === 'usuarios') {
      const data = await api<UsuarioConHospital[]>('/admin/usuarios/con-hospital')
      downloadCsv(
        ['Nombre', 'Email', 'Rol', 'Panel', 'Estado', 'Hospital', 'Registrado'],
        data.map(u => [
          u.name,
          u.email,
          u.role,
          u.panel,
          u.is_active ? 'Activo' : 'Inactivo',
          u.tenant_name,
          u.created_at, // ya viene formateado del backend (dd/mm/yyyy)
        ]),
        `usuarios_${today}.csv`
      )
    } else {
      const data = await api<AuditLog[]>(`/admin/auditoria?limit=${auditLimit.value}`)
      downloadCsv(
        ['Fecha', 'Usuario', 'Hospital', 'Acción', 'Modelo', 'Descripción', 'IP'],
        data.map(l => [
          formatDate(l.created_at),
          l.user_name || 'Sistema',
          l.tenant_name || '—',
          l.action,
          l.model || '—',
          l.description || '',
          l.ip_address || '—',
        ]),
        `auditoria_${today}.csv`
      )
    }
    success.value = true
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo generar el archivo'
  } finally {
    loading.value = false
  }
}
</script>