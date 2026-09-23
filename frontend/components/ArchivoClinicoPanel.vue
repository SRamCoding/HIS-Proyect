<template>
  <div class="archivo-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-folder" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <p class="breadcrumb-label" style="color: var(--ink-soft); font-size: 0.75rem;">Archivo Clínico</p>
          <h1 class="page-title">{{ title }}</h1>
          <p class="page-subtitle">
            {{ props.soloDigitalizadas ? 'Historias clínicas ya digitalizadas y disponibles en electrónico.' : 'Busca una historia para consultar su ubicación, digitalización y traslados.' }}
          </p>
        </div>
      </div>
      <button class="btn-secondary" :disabled="loading || busy" @click="load()">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
        Actualizar
      </button>
    </div>

    <!-- Messages -->
    <div v-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>
    <div v-if="notice" class="success-banner">
      <UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />
      {{ notice }}
    </div>

    <!-- Filters -->
    <section class="panel filters-panel">
      <form class="filters-form" @submit.prevent="search">
        <div class="filters-grid">
          <div class="filter-field">
            <label class="form-label">Paciente, documento o N.° de HC</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-magnifying-glass" class="input-icon" />
              <input
                v-model="filters.q"
                class="input-clinical"
                maxlength="200"
                placeholder="Nombres, apellidos o número"
              />
            </div>
          </div>
          <div class="filter-field">
            <label class="form-label">Ubicación actual</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-map-pin" class="input-icon" />
              <input
                v-model="filters.location"
                class="input-clinical"
                maxlength="50"
                placeholder="Todas las ubicaciones"
              />
            </div>
          </div>
          <div v-if="!props.soloDigitalizadas" class="filter-field">
            <label class="form-label">Digitalización</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document" class="input-icon" />
              <select v-model="filters.digitized" class="input-clinical">
                <option value="">Todas</option>
                <option value="true">Digitalizadas</option>
                <option value="false">Sin digitalizar</option>
              </select>
            </div>
          </div>
        </div>
        <div class="filter-actions">
          <button class="btn-primary" :disabled="loading || busy" @click="search">
            <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
            Buscar
          </button>
          <button type="button" class="btn-secondary" :disabled="loading || busy" @click="clearFilters">
            <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            Limpiar
          </button>
        </div>
      </form>
    </section>

    <!-- Results -->
    <section class="panel results-panel" :aria-busy="loading">
      <div v-if="loading" class="loading-state">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando historias clínicas…</p>
      </div>

      <template v-else>
        <div class="results-header">
          <span class="result-count">{{ total }} historias encontradas</span>
        </div>

        <div class="table-responsive">
          <table class="archivo-table">
            <caption class="sr-only">Historias clínicas del hospital</caption>
            <thead>
              <tr>
                <th>N.° de HC</th>
                <th>Paciente</th>
                <th>Ubicación</th>
                <th>Digitalización</th>
                <th>Acciones</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in items"
                :key="item.id"
                :class="{ 'row-selected': selected?.id === item.id }"
              >
                <td>
                  <span class="record-number font-mono-data">{{ item.record_number }}</span>
                </td>
                <td>
                  <div class="patient-cell">
                    <span class="patient-name">{{ item.patient_name }}</span>
                    <span class="patient-document">{{ item.document_type }}: {{ item.document_number || 'Sin documento' }}</span>
                  </div>
                </td>
                <td>
                  <span class="location-badge">{{ item.location }}</span>
                </td>
                <td>
                  <span class="status-badge" :class="item.is_digitized ? 'status-digitized' : 'status-not-digitized'">
                    <UIcon :name="item.is_digitized ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" />
                    {{ item.is_digitized ? 'Digitalizada' : 'Sin digitalizar' }}
                  </span>
                </td>
                <td>
                  <div class="action-buttons">
                    <button class="action-btn action-view" :disabled="busy" @click="downloadPdf(item, 'ficha')">
                      <UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />
                      Ficha PDF
                    </button>
                    <button class="action-btn action-view" :disabled="busy" @click="downloadPdf(item, 'completa')">
                      <UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />
                      HC completa
                    </button>
                    <button class="action-btn action-view" :disabled="busy" @click="selectRecord(item)">
                      <UIcon name="i-heroicons-eye" class="w-4 h-4" />
                      Ver
                    </button>
                    <button class="action-btn action-digitize" :disabled="busy" @click="digitalize(item)">
                      <UIcon :name="item.is_digitized ? 'i-heroicons-archive-box-x-mark' : 'i-heroicons-archive-box' " class="w-4 h-4" />
                      {{ item.is_digitized ? 'Desmarcar' : 'Marcar' }}
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="!items.length">
                <td colspan="5" style="text-align: center; color: var(--ink-soft);">
                  No se encontraron historias con estos filtros.
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <nav class="pagination" aria-label="Páginas de historias">
          <button class="btn-secondary btn-sm" :disabled="page === 1 || busy" @click="load(page - 1)">
            <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
            Anterior
          </button>
          <span class="page-info">Página {{ page }} de {{ pages }}</span>
          <button class="btn-secondary btn-sm" :disabled="page >= pages || busy" @click="load(page + 1)">
            Siguiente
            <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
          </button>
        </nav>
      </template>
    </section>

    <!-- Detail Panel -->
    <section v-if="selected" class="panel detail-panel" aria-labelledby="historia-title">
      <div class="detail-header">
        <div>
          <h2 id="historia-title" class="detail-title">{{ selected.record_number }} · {{ selected.patient_name }}</h2>
          <p class="detail-subtitle">
            Ubicación actual: <strong>{{ selected.location }}</strong>
          </p>
        </div>
        <button class="btn-secondary" :disabled="busy" @click="closeRecord">
          <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
          Cerrar detalle
        </button>
      </div>

      <!-- Move Form -->
      <form class="move-form" @submit.prevent="move">
        <div class="move-grid">
          <div class="form-group">
            <label class="form-label">Nueva ubicación</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-map-pin" class="input-icon" />
              <input
                v-model="destination"
                class="input-clinical"
                required
                maxlength="50"
                placeholder="Ej. consultorio de medicina"
                :disabled="busy"
              />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Observación del traslado</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea
                v-model="notes"
                class="input-clinical"
                maxlength="2000"
                rows="2"
                placeholder="Detalles del traslado..."
                :disabled="busy"
              />
            </div>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn-primary" :disabled="busy || historyLoading || !destination.trim()">
            <UIcon v-if="busy" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
            {{ busy ? 'Guardando…' : 'Registrar traslado' }}
          </button>
        </div>
        <p class="field-hint">El responsable se registra con tu sesión. Marcar digitalizada indica el estado de la HC; no adjunta documentos.</p>
      </form>

      <!-- Movement History -->
      <div class="history-section">
        <h3 class="section-title">Historial de movimientos</h3>

        <div v-if="historyLoading" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando movimientos…</p>
        </div>

        <div v-else-if="historyError" class="error-banner">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
          {{ historyError }}
          <button class="btn-secondary btn-sm" @click="loadHistory()">Reintentar</button>
        </div>

        <template v-else>
          <div class="table-responsive">
            <table class="archivo-table">
              <thead>
                <tr>
                  <th>Fecha y hora (Lima)</th>
                  <th>Origen</th>
                  <th>Destino</th>
                  <th>Responsable</th>
                  <th>Observación</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="movement in movements" :key="movement.id">
                  <td>{{ dateLabel(movement.created_at) }}</td>
                  <td>{{ movement.from_location }}</td>
                  <td>{{ movement.to_location }}</td>
                  <td>{{ movement.moved_by || 'No registrado' }}</td>
                  <td class="note-cell">{{ movement.notes || '—' }}</td>
                </tr>
                <tr v-if="!movements.length">
                  <td colspan="5" style="text-align: center; color: var(--ink-soft);">
                    Esta historia todavía no tiene traslados registrados.
                  </td>
                </tr>
              </tbody>
            </table>
          </div>

          <nav class="pagination" aria-label="Páginas de movimientos">
            <button class="btn-secondary btn-sm" :disabled="historyPage === 1 || busy" @click="loadHistory(historyPage - 1)">
              <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
              Anterior
            </button>
            <span class="page-info">Página {{ historyPage }} de {{ historyPages }}</span>
            <button class="btn-secondary btn-sm" :disabled="historyPage >= historyPages || busy" @click="loadHistory(historyPage + 1)">
              Siguiente
              <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
            </button>
          </nav>
        </template>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
interface Historia {
  id: string
  patient_id: string
  patient_name: string
  document_type: string
  document_number: string | null
  record_number: string
  location: string
  is_digitized: boolean
  updated_at: string
}

interface Movimiento {
  id: string
  from_location: string
  to_location: string
  moved_by: string | null
  notes: string | null
  created_at: string
}

interface Page<T> {
  items: T[]
  total: number
  page: number
  page_size: number
}

const props = defineProps<{ title: string; soloDigitalizadas?: boolean }>()

const { api } = useApi()

// State
const filters = reactive({ q: '', location: '', digitized: props.soloDigitalizadas ? 'true' : '' })
const applied = ref({ ...filters })
const items = ref<Historia[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = 20
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const loading = ref(false)
const busy = ref(false)
const error = ref('')
const notice = ref('')

const selected = ref<Historia | null>(null)
const movements = ref<Movimiento[]>([])
const historyLoading = ref(false)
const historyError = ref('')
const historyPage = ref(1)
const historyTotal = ref(0)
const historyPages = computed(() => Math.max(1, Math.ceil(historyTotal.value / pageSize)))

const destination = ref('')
const notes = ref('')

let listRequest = 0
let historyRequest = 0

// Utils
function message(e: unknown): string {
  const detail = (e as { data?: { detail?: unknown } })?.data?.detail
  return typeof detail === 'string' ? detail : 'No se pudo completar la operación. Intenta nuevamente.'
}

function dateLabel(value: string) {
  const utc = /(?:Z|[+-]\d{2}:\d{2})$/.test(value) ? value : value + 'Z'
  return new Intl.DateTimeFormat('es-PE', {
    dateStyle: 'short',
    timeStyle: 'short',
    timeZone: 'America/Lima'
  }).format(new Date(utc))
}

// API Methods
async function downloadPdf(item: Historia, alcance: 'ficha' | 'completa') {
  busy.value = true
  error.value = ''
  notice.value = 'Preparando el PDF…'
  try {
    const blob = await api<Blob>(`/app/archivo-clinico/historias/${item.id}/pdf`, {
      query: { alcance }, responseType: 'blob',
    })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `HC-${item.record_number.replace(/[^a-zA-Z0-9-]/g, '_')}-${alcance}.pdf`
    document.body.appendChild(link)
    link.click()
    link.remove()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
    notice.value = 'PDF descargado. Contiene información confidencial del paciente.'
  } catch (e) {
    notice.value = ''
    error.value = message(e)
  } finally {
    busy.value = false
  }
}

async function load(nextPage = page.value) {
  const request = ++listRequest
  loading.value = true
  error.value = ''
  try {
    const result = await api<Page<Historia>>('/app/archivo-clinico/historias', {
      query: {
        q: applied.value.q.trim() || undefined,
        location: applied.value.location.trim() || undefined,
        is_digitized: applied.value.digitized === '' ? undefined : applied.value.digitized === 'true',
        page: nextPage,
        page_size: pageSize,
      }
    })
    if (request !== listRequest) return
    if (nextPage > 1 && !result.items.length) {
      await load(Math.max(1, Math.ceil(result.total / pageSize)))
      return
    }
    items.value = result.items
    total.value = result.total
    page.value = result.page
  } catch (e) {
    if (request === listRequest) {
      items.value = []
      total.value = 0
      error.value = message(e)
    }
  } finally {
    if (request === listRequest) loading.value = false
  }
}

function search() {
  applied.value = { ...filters }
  notice.value = ''
  closeRecord()
  void load(1)
}

function clearFilters() {
  Object.assign(filters, { q: '', location: '', digitized: props.soloDigitalizadas ? 'true' : '' })
  search()
}

function closeRecord() {
  ++historyRequest
  selected.value = null
  historyLoading.value = false
  movements.value = []
  destination.value = ''
  notes.value = ''
}

async function selectRecord(item: Historia) {
  closeRecord()
  selected.value = item
  await loadHistory(1)
}

async function loadHistory(nextPage = historyPage.value) {
  if (!selected.value) return
  const id = selected.value.id
  const request = ++historyRequest
  historyLoading.value = true
  historyError.value = ''
  movements.value = []
  try {
    const result = await api<Page<Movimiento> & { historia: Historia }>(
      '/app/archivo-clinico/historias/' + id + '/movimientos',
      { query: { page: nextPage, page_size: pageSize } }
    )
    if (request !== historyRequest || selected.value?.id !== id) return
    selected.value = result.historia
    movements.value = result.items
    historyTotal.value = result.total
    historyPage.value = result.page
  } catch (e) {
    if (request === historyRequest) historyError.value = message(e)
  } finally {
    if (request === historyRequest) historyLoading.value = false
  }
}

async function digitalize(item: Historia) {
  if (busy.value) return
  busy.value = true
  error.value = ''
  notice.value = ''
  try {
    const updated = await api<Historia>(
      '/app/archivo-clinico/historias/' + item.id + '/digitalizar',
      { method: 'PATCH', body: { is_digitized: !item.is_digitized } }
    )
    if (selected.value?.id === item.id) selected.value = updated
    notice.value = 'Estado de digitalización actualizado.'
    await load()
  } catch (e) {
    error.value = message(e)
  } finally {
    busy.value = false
  }
}

async function move() {
  if (!selected.value || busy.value) return
  const target = destination.value.trim()
  if (!target) return
  if (target.toLowerCase() === selected.value.location.toLowerCase()) {
    error.value = 'La historia ya se encuentra en esa ubicación.'
    return
  }
  busy.value = true
  error.value = ''
  notice.value = ''
  try {
    await api('/app/admision/historia-clinica/mover', {
      method: 'POST',
      body: {
        clinical_record_id: selected.value.id,
        to_location: target,
        notes: notes.value.trim() || null,
      }
    })
    selected.value = { ...selected.value, location: target }
    destination.value = ''
    notes.value = ''
    notice.value = 'Traslado registrado correctamente.'
    await Promise.all([load(), loadHistory(1)])
  } catch (e) {
    error.value = message(e)
  } finally {
    busy.value = false
  }
}

onMounted(() => load())
onBeforeUnmount(() => { ++listRequest; ++historyRequest })
</script>

<style scoped>
.archivo-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.breadcrumb-label {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin: 0 0 0.125rem 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
  line-height: 1.2;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

/* Buttons */
.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: var(--teal-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--mist);
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

/* Messages */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--alert-soft);
  color: var(--alert);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

.success-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--green-soft);
  color: var(--green);
  font-size: 0.875rem;
  margin-bottom: 1.5rem;
}

/* Panels */
.panel {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-sm);
}

/* Filters */
.filters-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.filters-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
}

.filter-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.filter-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

/* Form */
.form-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  margin-bottom: 0.25rem;
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--ink-soft);
}

.input-wrapper textarea + .input-icon {
  top: 0.75rem;
  transform: none;
}

.input-clinical {
  width: 100%;
  padding: 0.5rem 0.75rem;
  padding-left: 2.25rem;
  border-radius: 6px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.input-clinical:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.input-clinical:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.input-clinical::placeholder {
  color: var(--ink-soft);
  opacity: 0.6;
}

.field-hint {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin-top: 0.25rem;
}

/* Results */
.results-header {
  margin-bottom: 1rem;
}

.result-count {
  font-size: 0.875rem;
  color: var(--ink-soft);
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 0.5rem;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Table */
.table-responsive {
  overflow-x: auto;
}

.archivo-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.archivo-table thead {
  background: var(--mist);
}

.archivo-table th {
  padding: 0.625rem 0.75rem;
  text-align: left;
  font-weight: 600;
  color: var(--ink-soft);
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--line);
}

.archivo-table td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
}

.archivo-table tbody tr:hover {
  background: var(--mist);
}

.row-selected {
  background: var(--teal-soft);
}

/* Record Number */
.record-number {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--ink);
}

/* Patient Cell */
.patient-cell {
  display: flex;
  flex-direction: column;
}

.patient-name {
  font-weight: 500;
  color: var(--ink);
}

.patient-document {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

/* Location Badge */
.location-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
  background: var(--navy-soft);
  color: var(--navy);
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.status-digitized {
  background: var(--green-soft);
  color: var(--green);
}

.status-not-digitized {
  background: var(--amber-soft);
  color: var(--amber);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  gap: 0.375rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.625rem;
  border-radius: 4px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-soft);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover:not(:disabled) {
  background: var(--mist);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.action-view:hover:not(:disabled) {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
}

.action-digitize:hover:not(:disabled) {
  color: var(--purple);
  border-color: var(--purple-soft);
  background: var(--purple-soft);
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: flex-end;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

.page-info {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Detail Panel */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.25rem;
}

.detail-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.detail-subtitle {
  font-size: 0.875rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

/* Move Form */
.move-form {
  padding-bottom: 1rem;
  border-bottom: 1px solid var(--line);
  margin-bottom: 1rem;
}

.move-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.75rem;
  flex-wrap: wrap;
}

/* History Section */
.history-section {
  margin-top: 0.5rem;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.75rem 0;
}

.note-cell {
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  max-width: 250px;
}

/* Responsive */
@media (max-width: 1024px) {
  .archivo-container {
    padding: 1rem 1.5rem;
  }

  .filters-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .archivo-container {
    padding: 0.75rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .filters-grid {
    grid-template-columns: 1fr;
  }

  .move-grid {
    grid-template-columns: 1fr;
  }

  .filter-actions {
    flex-wrap: wrap;
  }

  .filter-actions > * {
    flex: 1;
    justify-content: center;
  }

  .detail-header {
    flex-direction: column;
    gap: 0.5rem;
  }

  .action-buttons {
    flex-direction: column;
    gap: 0.25rem;
  }

  .pagination {
    flex-wrap: wrap;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .panel {
    padding: 0.75rem;
  }

  .archivo-table th,
  .archivo-table td {
    padding: 0.375rem 0.5rem;
    font-size: 0.75rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions > * {
    width: 100%;
    justify-content: center;
  }

  .header-left {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>
