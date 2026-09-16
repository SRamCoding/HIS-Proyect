<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-pencil-square" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">FIRMA ELECTRÓNICA · LEY N.° 30024 (RENHICE) / LEY N.° 27269</span>
          <h1 class="page-title">Bandeja de Firma</h1>
        </div>
      </div>
      <button class="btn-secondary" :disabled="loading" @click="cargar">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': loading }" />Actualizar
      </button>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <section class="panel search-panel">
      <div class="search-actions" style="justify-content:flex-start">
        <button class="btn-secondary btn-sm" :class="{ 'btn-active': tab === 'pendientes' }" @click="tab = 'pendientes'">Pendientes de firma</button>
        <button class="btn-secondary btn-sm" :class="{ 'btn-active': tab === 'trazabilidad' }" @click="tab = 'trazabilidad'; cargarRegistros()">Trazabilidad</button>
      </div>
    </section>

    <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>

    <!-- ═══════════ PENDIENTES ═══════════ -->
    <template v-else-if="tab === 'pendientes'">
      <p class="field-hint" style="margin-bottom:1rem">Documentos clínicos a su cargo que aún no tienen firma electrónica. La firma se aplica solo con cuenta médica vinculada, colegiatura habilitada y N.° CMP/colegiatura registrado.</p>
      <div class="doc-list">
        <div v-for="d in bandeja" :key="d.documento_id" class="doc-card">
          <div class="doc-head">
            <div>
              <span class="badge badge-pendiente">{{ d.origen }}</span>
              <strong>{{ d.paciente_nombre }}</strong> <span class="field-hint">({{ d.paciente_dni }})</span>
            </div>
            <span class="field-hint">{{ formatFechaHora(d.created_at) }}</span>
          </div>
          <p class="doc-resumen">{{ d.resumen || 'Sin motivo registrado.' }}</p>
          <div class="form-actions">
            <button class="btn-primary" :disabled="busy" @click="firmar(d)"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />Firmar electrónicamente</button>
          </div>
        </div>
        <p v-if="!bandeja.length" class="field-hint">No tiene documentos pendientes de firma.</p>
      </div>
    </template>

    <!-- ═══════════ TRAZABILIDAD ═══════════ -->
    <section v-else class="panel results-panel">
      <div class="results-header"><h2 class="results-title">{{ registros.length }} firmas registradas</h2></div>
      <div class="table-responsive">
        <table class="lab-table">
          <thead><tr><th>Fecha</th><th>Tipo</th><th>Paciente</th><th>Firmante</th><th>Colegiatura</th><th>SHA-256</th></tr></thead>
          <tbody>
            <tr v-for="r in registros" :key="r.id">
              <td>{{ formatFechaHora(r.created_at) }}</td>
              <td>{{ r.documento_tipo === 'ATENCION_MEDICA' ? 'Consulta Externa' : 'Emergencia' }}</td>
              <td>{{ r.paciente_nombre }} ({{ r.paciente_dni }})</td>
              <td>{{ r.firmante_nombre }}</td><td>{{ r.numero_colegiatura || '—' }}</td>
              <td class="hash-cell" :title="r.sha256">{{ r.sha256.slice(0, 16) }}…</td>
            </tr>
            <tr v-if="!registros.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">Sin firmas registradas todavía.</td></tr>
          </tbody>
        </table>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const endpoint = '/app/firma-electronica'

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)
const tab = ref<'pendientes' | 'trazabilidad'>('pendientes')

const bandeja = ref<any[]>([])
const registros = ref<any[]>([])

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}
function formatFechaHora(f: string) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

async function cargar() {
  loading.value = true; error.value = ''
  try { bandeja.value = await api(endpoint + '/bandeja') }
  catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function cargarRegistros() {
  loading.value = true; error.value = ''
  try { registros.value = await api(endpoint + '/registros') }
  catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function firmar(d: any) {
  if (!confirm(`¿Confirma la firma electrónica de la atención de ${d.paciente_nombre}? Esta acción no se puede deshacer.`)) return
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/bandeja/firmar', { method: 'POST', body: { documento_tipo: d.documento_tipo, documento_id: d.documento_id } })
    notice.value = 'Documento firmado electrónicamente.'
    await cargar()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

onMounted(cargar)
</script>

<style scoped>
.lab-container { max-width: 1200px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.btn-active { background: var(--teal-soft); border-color: var(--teal); color: var(--teal); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.search-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); white-space: nowrap; }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.hash-cell { font-family: monospace; font-size: 0.75rem; color: var(--ink-soft); cursor: help; }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; white-space: nowrap; }
.badge-pendiente { color: var(--amber); background: var(--amber-soft); margin-right: 0.5rem; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.75rem; }

.doc-list { display: flex; flex-direction: column; gap: 1rem; }
.doc-card { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; box-shadow: var(--shadow-sm); }
.doc-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; }
.doc-resumen { font-size: 0.875rem; color: var(--ink); margin: 0.5rem 0 0 0; }

@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
}
</style>
