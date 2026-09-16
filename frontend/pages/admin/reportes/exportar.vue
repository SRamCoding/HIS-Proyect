<!-- frontend/pages/admin/reportes/exportar.vue -->
<template>
  <div class="auditoria-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-arrow-down-tray" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <h1 class="page-title">Exportar Datos</h1>
          <p class="page-subtitle">Descarga hospitales, usuarios o el registro de auditoría en formato CSV.</p>
        </div>
      </div>
    </div>

    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1.5rem; max-width: 420px;">
      <label class="detail-label">Selecciona qué exportar</label>
      <select v-model="tabla" class="input-clinical" style="width: 100%;">
        <option value="hospitales">Hospitales</option>
        <option value="usuarios">Usuarios</option>
        <option value="auditoria">Auditoría del ERP</option>
      </select>

      <div v-if="tabla === 'auditoria'" style="margin-top: 0.75rem;">
        <label class="detail-label">Límite de registros</label>
        <select v-model.number="auditLimit" class="input-clinical" style="width: 100%;">
          <option :value="100">Últimos 100</option>
          <option :value="500">Últimos 500</option>
          <option :value="1000">Últimos 1000</option>
        </select>
      </div>

      <div style="margin-top: 1rem;">
        <button class="btn-primary" :disabled="loading" @click="exportar">
          {{ loading ? 'Generando...' : 'Descargar CSV' }}
        </button>
      </div>

      <p v-if="error" style="color: var(--alert); font-size: 0.875rem; margin-top: 0.75rem;">{{ error }}</p>
      <p v-if="success" style="color: var(--teal); font-size: 0.875rem; margin-top: 0.75rem;">Archivo descargado correctamente.</p>
      <p v-if="successWarning" style="color: var(--amber); font-size: 0.875rem; margin-top: 0.5rem;">{{ successWarning }}</p>
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
const successWarning = ref('')

// Si una celda empieza con =, +, -, @ o un tab, Excel/Sheets puede
// interpretarla como formula al abrir el CSV ("inyeccion de formulas" via
// exports). Se antepone un apostrofe para forzar que se lea como texto.
const celdaSegura = (v: string) => /^[=+\-@\t]/.test(v) ? `'${v}` : v

const downloadCsv = (headers: string[], rows: string[][], filename: string) => {
  const csv = [
    headers.join(','),
    ...rows.map(r => r.map(v => `"${celdaSegura(String(v ?? '')).replace(/"/g, '""')}"`).join(',')),
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

// La auditoria si necesita hora exacta (para reconstruir el orden de los
// eventos) -- reducirla a dia/mes/año, como formatDate, perdia esa parte.
const formatDateTime = (date: string) => {
  return new Date(date).toLocaleString('es-PE', {
    day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit',
  })
}

const exportar = async () => {
  loading.value = true
  error.value = ''
  success.value = false
  successWarning.value = ''
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
      // /admin/usuarios/con-hospital ahora pagina (para no mandar de una
      // el listado completo a la pantalla interactiva) -- el CSV SI
      // necesita todo, asi que se recorren las paginas hasta juntarlas.
      const PAGE_SIZE = 200
      let offset = 0
      let total = Infinity
      const items: UsuarioConHospital[] = []
      let hospitalesNoDisponibles: string[] = []
      while (offset < total) {
        const resp = await api<{ items: UsuarioConHospital[]; total: number; hospitales_no_disponibles: string[]; es_parcial: boolean }>(
          `/admin/usuarios/con-hospital?limit=${PAGE_SIZE}&offset=${offset}`
        )
        items.push(...resp.items)
        total = resp.total
        if (resp.es_parcial) hospitalesNoDisponibles = [...new Set([...hospitalesNoDisponibles, ...resp.hospitales_no_disponibles])]
        offset += PAGE_SIZE
        if (resp.items.length === 0) break // corta si la BD cambio entre paginas y ya no hay mas
      }
      downloadCsv(
        ['Nombre', 'Email', 'Rol', 'Panel', 'Estado', 'Hospital', 'Registrado'],
        items.map(u => [
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
      if (hospitalesNoDisponibles.length) {
        successWarning.value = `Atención: no se pudo consultar ${hospitalesNoDisponibles.join(', ')}. El CSV no incluye esos hospitales.`
      }
    } else {
      // /admin/auditoria tiene un limite maximo de 200 por pagina (antes
      // esta pantalla pedia hasta 1000 de una sola vez, y silenciosamente
      // se recortaba a 200). Se recorren paginas hasta juntar la cantidad
      // que el usuario eligio o hasta agotar el historial real.
      const PAGE_SIZE = 200
      const objetivo = auditLimit.value
      const items: AuditLog[] = []
      let offset = 0
      while (items.length < objetivo) {
        const resp = await api<{ items: AuditLog[]; total: number }>(
          `/admin/auditoria?limit=${Math.min(PAGE_SIZE, objetivo - items.length)}&offset=${offset}`
        )
        items.push(...resp.items)
        offset += PAGE_SIZE
        if (resp.items.length === 0 || items.length >= resp.total) break
      }
      downloadCsv(
        ['Fecha y hora', 'Usuario', 'Hospital', 'Acción', 'Modelo', 'Descripción', 'IP'],
        items.map(l => [
          formatDateTime(l.created_at),
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
    error.value = apiErr(e, 'No se pudo generar el archivo')
  } finally {
    loading.value = false
  }
}
</script>