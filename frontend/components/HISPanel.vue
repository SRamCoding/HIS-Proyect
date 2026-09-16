<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-server-stack" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">HIS · SISTEMA DE INFORMACIÓN EN SALUD</span>
          <h1 class="page-title">{{ mode === 'formato-his' ? 'Formato HIS' : 'Registro HIS de la MicroRed' }}</h1>
        </div>
      </div>
      <button v-if="mode === 'registro-microred'" class="btn-primary" @click="mostrarForm = true"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Nuevo envío</button>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <!-- ═══════════ FORMATO HIS ═══════════ -->
    <template v-if="mode === 'formato-his'">
      <p class="field-hint" style="margin-bottom:1rem">Reporte estadístico de toda atención firmada (cualquier financiador), formato Anexo 4B HIS-MINSA. Una fila por diagnóstico.</p>
      <section class="panel search-panel">
        <form class="search-form" @submit.prevent="cargarFormato">
          <div class="search-grid">
            <div class="search-field"><label class="form-label">Desde</label><input v-model="filtro.fecha_desde" type="date" class="input-clinical" required /></div>
            <div class="search-field"><label class="form-label">Hasta</label><input v-model="filtro.fecha_hasta" type="date" class="input-clinical" required /></div>
          </div>
          <div class="search-actions">
            <button class="btn-secondary" type="button" :disabled="loading" @click="descargarCsv"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />CSV</button>
            <button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button>
          </div>
        </form>
      </section>

      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ filas.length }} registros</h2></div>
        <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
        <div v-else class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Fecha</th><th>Origen</th><th>Paciente</th><th>DNI</th><th>HC</th><th>Edad/Sexo</th><th>Distrito</th><th>Financiador</th><th>Diagnóstico</th><th>Profesional</th><th>Servicio</th></tr></thead>
            <tbody>
              <tr v-for="(f, i) in filas" :key="i">
                <td>{{ formatFecha(f.fecha_atencion) }}</td>
                <td>{{ f.origen === 'CONSULTA_EXTERNA' ? 'C. Externa' : 'Emergencia' }}</td>
                <td>{{ f.paciente_nombre }}</td><td>{{ f.dni || 'NN' }}</td><td>{{ f.historia_clinica || '—' }}</td>
                <td>{{ f.edad }} / {{ f.sexo }}</td><td>{{ f.distrito_procedencia }}</td><td>{{ f.financiador }}</td>
                <td>{{ f.diagnostico_codigo ? `${f.diagnostico_codigo} · ${f.diagnostico_descripcion}` : '—' }}</td>
                <td>{{ f.profesional_nombre || '—' }}</td><td>{{ f.servicio_o_especialidad || '—' }}</td>
              </tr>
              <tr v-if="!filas.length"><td colspan="11" style="text-align:center;color:var(--ink-soft)">Sin registros para este rango de fechas.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <!-- ═══════════ REGISTRO HIS DE LA MICRORED ═══════════ -->
    <template v-else>
      <section v-if="mostrarForm" class="panel">
        <div class="card-header-row"><h2 class="results-title">Nuevo envío HIS</h2><button class="btn-secondary" @click="mostrarForm=false"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
        <form class="editor-form" @submit.prevent="crearEnvio">
          <div class="form-grid">
            <div class="form-group"><label class="form-label">Periodo (AAAA-MM)</label><input v-model="nuevo.periodo" class="input-clinical" placeholder="2026-09" pattern="\d{4}-(0[1-9]|1[0-2])" required /></div>
            <div class="form-group"><label class="form-label">Desde</label><input v-model="nuevo.fecha_desde" type="date" class="input-clinical" required /></div>
            <div class="form-group"><label class="form-label">Hasta</label><input v-model="nuevo.fecha_hasta" type="date" class="input-clinical" required /></div>
            <div class="form-group full-width"><label class="form-label">Observaciones</label><textarea v-model="nuevo.observaciones" class="input-clinical" rows="2"></textarea></div>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Registrar borrador</button></div>
        </form>
      </section>

      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ envios.length }} envíos</h2></div>
        <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
        <div v-else class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Periodo</th><th>Rango</th><th>Registros</th><th>Estado</th><th>Fecha de envío</th><th></th></tr></thead>
            <tbody>
              <tr v-for="e in envios" :key="e.id">
                <td>{{ e.periodo }}</td><td>{{ e.fecha_desde }} — {{ e.fecha_hasta }}</td><td>{{ e.total_registros }}</td>
                <td><span class="badge" :class="e.estado === 'enviado' ? 'badge-ok' : 'badge-pendiente'">{{ e.estado }}</span></td>
                <td>{{ e.fecha_envio ? formatFecha(e.fecha_envio) : '—' }}</td>
                <td><button v-if="e.estado === 'borrador'" class="btn-secondary btn-sm" :disabled="busy" @click="cerrar(e)"><UIcon name="i-heroicons-paper-airplane" class="w-4 h-4" />Marcar enviado</button></td>
              </tr>
              <tr v-if="!envios.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">No hay envíos registrados todavía.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'formato-his' | 'registro-microred'
const props = defineProps<{ mode: Mode }>()
const { api } = useApi()
const endpoint = '/app/his'

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)

function hoy() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date())
}
function primerDiaMes() {
  const d = new Date()
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit' }).format(d) + '-01'
}

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}
function formatFecha(f: string) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// Formato HIS
const filtro = reactive({ fecha_desde: primerDiaMes(), fecha_hasta: hoy() })
const filas = ref<any[]>([])

async function cargarFormato() {
  loading.value = true; error.value = ''
  try {
    filas.value = await api(endpoint + '/formato-his', { query: { fecha_desde: filtro.fecha_desde, fecha_hasta: filtro.fecha_hasta } })
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function descargarCsv() {
  try {
    const blob = await api<Blob>(endpoint + '/formato-his.csv', { query: { fecha_desde: filtro.fecha_desde, fecha_hasta: filtro.fecha_hasta }, responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = 'formato-his.csv'; a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  } catch (e) { error.value = err(e) }
}

// Registro HIS de la MicroRed
const envios = ref<any[]>([])
const mostrarForm = ref(false)
const nuevo = reactive({ periodo: '', fecha_desde: primerDiaMes(), fecha_hasta: hoy(), observaciones: '' })

async function cargarEnvios() {
  loading.value = true; error.value = ''
  try { envios.value = await api(endpoint + '/registro-microred') } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function crearEnvio() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/registro-microred', { method: 'POST', body: { ...nuevo, observaciones: nuevo.observaciones || undefined } })
    notice.value = 'Envío registrado como borrador.'
    mostrarForm.value = false
    Object.assign(nuevo, { periodo: '', fecha_desde: primerDiaMes(), fecha_hasta: hoy(), observaciones: '' })
    await cargarEnvios()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function cerrar(e: any) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/registro-microred/' + e.id + '/cerrar', { method: 'POST', body: {} })
    notice.value = 'Envío marcado como enviado.'
    await cargarEnvios()
  } catch (err_) { error.value = err(err_) } finally { busy.value = false }
}

onMounted(async () => {
  if (props.mode === 'formato-his') await cargarFormato()
  else await cargarEnvios()
})
</script>

<style scoped>
.lab-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.search-form { display: flex; flex-direction: column; gap: 1rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
.search-field { display: flex; flex-direction: column; gap: 0.25rem; }
.search-actions { display: flex; gap: 0.75rem; justify-content: flex-end; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); white-space: nowrap; }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-pendiente { color: var(--amber); background: var(--amber-soft); }
.editor-form { display: flex; flex-direction: column; gap: 1rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid, .form-grid { grid-template-columns: 1fr; }
}
</style>
