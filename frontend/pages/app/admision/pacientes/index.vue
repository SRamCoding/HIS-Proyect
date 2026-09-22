<template>
  <div class="pacientes-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon">
          <UIcon name="i-heroicons-user-group" class="w-5 h-5" />
        </div>
        <div>
          <h1 class="page-title">Pacientes</h1>
          <p class="page-subtitle">Gestión de pacientes del hospital</p>
        </div>
      </div>
      <NuxtLink :to="link('/app/admision/pacientes/create')" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Paciente
      </NuxtLink>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <div class="search-card">
        <div class="search-header">
          <UIcon name="i-heroicons-magnifying-glass" class="search-header-icon" />
          <label for="patient-search" class="search-header-title">Buscar pacientes</label>
        </div>
        <div class="search-body">
          <div class="search-input-wrapper">
            <UIcon name="i-heroicons-user" class="search-input-icon" />
            <input
              id="patient-search"
              v-model="q"
              type="text"
              placeholder="DNI, Nro Historia, nombres o apellidos..."
              class="search-input"
              @keyup.enter="buscar"
            />
          </div>
          <div class="search-actions">
            <button class="btn-clear" @click="limpiar">
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
              Limpiar
            </button>
            <button class="btn-search" :disabled="cargando" @click="buscar">
              <UIcon v-if="cargando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <UIcon v-else name="i-heroicons-magnifying-glass" class="w-4 h-4" />
              {{ cargando ? 'Buscando...' : 'Buscar' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-banner" role="alert">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="cargando && !resultados.length" class="loading-state">
      <div class="loading-spinner">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>
      <p style="color: var(--ink-soft)">Buscando pacientes...</p>
    </div>

    <!-- Results Table -->
    <div v-if="resultados.length" class="table-card" :aria-busy="cargando">
      <div class="table-header">
        <div class="table-header-left">
          <span class="table-title">{{ q.trim() ? 'Resultados de búsqueda' : 'Todos los pacientes' }}</span>
          <span class="table-count">{{ total }} paciente{{ total === 1 ? '' : 's' }}</span>
        </div>
      </div>
      <div class="table-responsive">
        <table class="pacientes-table">
          <caption class="sr-only">Listado de pacientes: documento, historia clínica, nombre, edad, seguro y acciones</caption>
          <thead>
            <tr>
              <th class="col-dni">
                <span class="th-content">DNI</span>
              </th>
              <th class="col-record">
                <span class="th-content">Nro Historia</span>
              </th>
              <th class="col-name">
                <span class="th-content">Nombre completo</span>
              </th>
              <th class="col-age">
                <span class="th-content">Edad</span>
              </th>
              <th class="col-insurance">
                <span class="th-content">Seguro</span>
              </th>
              <th class="col-actions">
                <span class="th-content">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="p in resultados"
              :key="p.id"
              class="table-row"
            >
              <td class="col-dni" data-label="DNI">
                <span class="dni-text font-mono-data">{{ p.dni || 'NN' }}</span>
              </td>
              <td class="col-record" data-label="Historia clínica">
                <span class="record-text font-mono-data">{{ p.record_number || '—' }}</span>
              </td>
              <td class="col-name">
                <div class="name-cell">
                  <div class="patient-avatar" :style="{ background: getPatientColor(p.full_name) }">
                    <span>{{ getInitials(p.full_name) }}</span>
                  </div>
                  <span class="name-text">{{ p.full_name }}</span>
                </div>
              </td>
              <td class="col-age" data-label="Edad">
                <span class="age-badge">{{ p.age }}</span>
              </td>
              <td class="col-insurance" data-label="Seguro">
                <span class="insurance-text">{{ p.insurance_type || '—' }}</span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <NuxtLink
                    :to="link(`/app/admision/pacientes/${p.id}`)"
                    class="action-btn action-view"
                    :aria-label="`Ver paciente ${p.full_name}`"
                    title="Ver paciente"
                  >
                    <UIcon name="i-heroicons-eye" class="w-5 h-5" />
                  </NuxtLink>
                  <NuxtLink
                    :to="link(`/app/admision/pacientes/${p.id}`)"
                    class="action-btn action-edit"
                    :aria-label="`Editar paciente ${p.full_name}`"
                    title="Editar paciente"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-5 h-5" />
                  </NuxtLink>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div class="table-footer">
        <span class="pagination-info">
          Página {{ page }} de {{ totalPages }} · {{ total }} paciente{{ total === 1 ? '' : 's' }} en total
        </span>
        <div class="pagination-controls">
          <button class="pagination-btn" :disabled="page <= 1 || cargando" @click="irPagina(page - 1)">
            <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
            Anterior
          </button>
          <button class="pagination-btn" :disabled="page >= totalPages || cargando" @click="irPagina(page + 1)">
            Siguiente
            <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!cargando" class="empty-state">
      <div class="empty-icon" style="background: var(--mist)">
        <UIcon name="i-heroicons-user-group" class="w-12 h-12" style="color: var(--ink-soft)" />
      </div>
      <h3 style="color: var(--ink)">{{ q.trim() ? 'No se encontraron pacientes' : 'No hay pacientes registrados' }}</h3>
      <p style="color: var(--ink-soft)">
        {{ q.trim() ? 'No hay pacientes que coincidan con tu búsqueda' : 'Aún no se registró ningún paciente en este hospital' }}
      </p>
      <button v-if="q.trim()" class="btn-secondary" @click="limpiar">
        <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
        Limpiar búsqueda
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()
const { link } = useHospitalNav()

const q = ref('')
const resultados = ref<any[]>([])
const cargando = ref(false)
const error = ref('')
const page = ref(1)
const pageSize = 20
const total = ref(0)
const totalPages = computed(() => Math.max(1, Math.ceil(total.value / pageSize)))

const getInitials = (name: string) => {
  if (!name || name === '—') return '?'
  return name
    .split(' ')
    .map((word: string) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getPatientColor = (name: string) => {
  // --pink-soft y --blue-soft no existen en ningun lado del sistema de
  // variables (ver assets/css/main.css): esos dos avatares salian con fondo
  // transparente para cualquier paciente cuyo hash cayera en esos indices.
  const colors = [
    'var(--teal-soft)',
    'var(--purple-soft)',
    'var(--navy-soft)',
    'var(--amber-soft)',
    'var(--green-soft)',
    'var(--orange-soft)',
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

async function cargar() {
  const texto = q.value.trim()
  if (texto && texto.length < 2) {
    error.value = 'Ingresa al menos 2 caracteres'
    return
  }
  error.value = ''
  cargando.value = true
  try {
    const query: Record<string, any> = { page: page.value, page_size: pageSize }
    if (texto) query.q = texto
    const data = await api<{ items: any[]; total: number }>('/app/admision/buscar', { query })
    resultados.value = data.items
    total.value = data.total
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar pacientes'
  } finally {
    cargando.value = false
  }
}

function buscar() {
  page.value = 1
  cargar()
}

function irPagina(p: number) {
  if (p < 1 || p > totalPages.value) return
  page.value = p
  cargar()
}

function limpiar() {
  q.value = ''
  page.value = 1
  cargar()
}

onMounted(cargar)
</script>

<style scoped>
/* Colores y tipografía: heredados de .app-shell (assets/css/hospital-theme.css). */
.pacientes-container {
  padding: 24px 32px 40px;
  min-height: 100%;
  background: var(--mist);
  color: var(--ink);
}
.page-header { display: flex; align-items: center; justify-content: space-between; gap: 20px; margin-bottom: 22px; }
.header-left { display: flex; align-items: center; gap: 16px; min-width: 0; }
.header-icon { width: 46px; height: 46px; display: grid; place-items: center; flex-shrink: 0; border-radius: 12px; color: var(--teal); background: var(--teal-soft); }
.page-title { margin: 0; font-size: 1.5rem; font-weight: 600; line-height: 1.2; letter-spacing: -0.01em; }
.page-subtitle { margin: 5px 0 0; font-size: .875rem; color: var(--ink-soft); }
.btn-primary, .btn-secondary, .btn-clear, .btn-search, .pagination-btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; min-height: 38px; padding: 8px 16px; border-radius: 8px; font-size: .8125rem; font-weight: 500; border: 1px solid #e1e8ef; background: white; color: var(--ink); cursor: pointer; text-decoration: none; transition: background .15s, border-color .15s; white-space: nowrap; }
.btn-primary, .btn-search { background: var(--teal); border-color: var(--teal); color: white; }.btn-primary:hover, .btn-search:hover:not(:disabled) { background: var(--teal-dark); border-color: var(--teal-dark); }.btn-secondary:hover, .btn-clear:hover, .pagination-btn:hover:not(:disabled) { background: var(--teal-soft); border-color: var(--teal); }
button:disabled { opacity: .55; cursor: wait; }.pagination-btn:disabled { cursor: default; }
a:focus-visible, button:focus-visible { outline: 3px solid var(--teal); outline-offset: 3px; }
.search-section { margin-bottom: 18px; }.search-card { padding: 16px 18px; background: white; border: 1px solid #e1e8ef; border-radius: 14px; box-shadow: 0 2px 6px #243d5904; }
.search-header { display: flex; align-items: center; gap: 8px; margin-bottom: 10px; color: var(--ink-soft); }.search-header-icon { width: 17px; height: 17px; }.search-header-title { font-size: .8125rem; font-weight: 500; }
.search-body { display: flex; align-items: center; gap: 12px; }.search-input-wrapper { position: relative; flex: 1; min-width: 0; }.search-input-icon { position: absolute; top: 50%; left: 13px; transform: translateY(-50%); width: 18px; height: 18px; color: var(--ink-soft); pointer-events: none; }
.search-input { width: 100%; height: 42px; border: 1px solid #dce6ef; border-radius: 8px; background: var(--mist); padding: 8px 14px 8px 40px; font-size: .8125rem; color: var(--ink); outline: none; }.search-input:focus { border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }.search-input::placeholder { color: var(--ink-soft); }
.search-actions { display: flex; gap: 8px; }.search-actions button { height: 42px; }
.table-card { background: white; border: 1px solid #e1e8ef; border-radius: 14px; overflow: hidden; box-shadow: 0 2px 6px #243d5904; }
.table-header { display: flex; align-items: center; justify-content: space-between; padding: 16px 18px; border-bottom: 1px solid #e7edf3; }.table-header-left { display: flex; align-items: center; flex-wrap: wrap; gap: 10px; }.table-title { font-size: 1rem; font-weight: 600; }.table-count { padding: 4px 9px; border-radius: 6px; color: var(--ink-soft); background: var(--mist); font-size: .75rem; }
.table-responsive { overflow-x: auto; }.pacientes-table { width: 100%; border-collapse: collapse; font-size: .8125rem; }.pacientes-table th { text-align: left; background: var(--mist); color: var(--ink-soft); font-size: .6875rem; font-weight: 500; text-transform: uppercase; letter-spacing: .04em; padding: 11px 16px; border-bottom: 1px solid #e1e8ef; }.pacientes-table td { padding: 10px 16px; border-bottom: 1px solid #edf1f6; vertical-align: middle; }.table-row:last-child td { border-bottom: 0; }.table-row:hover { background: var(--teal-soft); }
.col-dni { width: 12%; }.col-record { width: 17%; }.col-name { width: 34%; }.col-age { width: 8%; }.col-insurance { width: 17%; }.col-actions { width: 12%; }.pacientes-table th.col-actions { text-align: right; }
.dni-text, .record-text { font-family: inherit; font-size: .8125rem; font-variant-numeric: tabular-nums; color: var(--ink-soft); white-space: nowrap; }
.name-cell { display: flex; align-items: center; gap: 10px; }.patient-avatar { width: 30px; height: 30px; flex-shrink: 0; border-radius: 9px; display: grid; place-items: center; font-size: .625rem; font-weight: 500; color: var(--ink); background: var(--teal-soft); }.name-text { font-size: .8125rem; font-weight: 400; overflow-wrap: anywhere; }
.age-badge { color: var(--ink-soft); font-size: .8125rem; }.insurance-text { display: inline-block; padding: 4px 8px; border-radius: 6px; background: var(--mist); color: var(--ink-soft); font-size: .6875rem; }
.action-buttons { display: flex; justify-content: flex-end; gap: 6px; }.action-btn { display: grid; place-items: center; width: 32px; height: 32px; border-radius: 7px; border: 1px solid #e2eaf4; color: var(--ink-soft); background: white; transition: background .15s; }.action-btn:hover { color: var(--teal); background: var(--teal-soft); }.action-btn .iconify { width: 16px; height: 16px; }
.table-footer { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 14px; padding: 14px 18px; border-top: 1px solid #e7edf3; }.pagination-info { font-size: .75rem; color: var(--ink-soft); }.pagination-controls { display: flex; gap: 8px; }.pagination-btn { min-height: 34px; padding: 6px 12px; font-size: .75rem; }
.error-banner { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; padding: 12px 16px; border: 1px solid #f3d3d8; border-radius: 10px; color: #ad2b40; background: #fff3f5; font-size: .8125rem; }
.loading-state, .empty-state { display: flex; flex-direction: column; align-items: center; gap: 14px; padding: 48px 20px; text-align: center; background: white; border: 1px solid #e1e8ef; border-radius: 14px; font-size: .875rem; }.empty-icon { width: 64px; height: 64px; border-radius: 50%; display: grid; place-items: center; }.empty-state h3 { font-size: 1rem; font-weight: 500; }
@media(max-width: 1100px) { .pacientes-table td, .pacientes-table th { padding-left: 10px; padding-right: 10px; }.col-record { width: auto; }.search-body { flex-wrap: wrap; }.search-input-wrapper { flex-basis: 100%; }.search-actions { margin-left: auto; } }
@media(max-width: 767px) { .pacientes-container { padding: 16px; }.page-header { align-items: flex-start; flex-direction: column; gap: 14px; }.search-card { padding: 14px; }.search-actions { width: 100%; }.search-actions button { flex: 1; min-width: 0; padding: 8px; }.table-header { padding: 14px; }.table-responsive { overflow: visible; }.pacientes-table, .pacientes-table tbody { display: block; }.pacientes-table thead { display: none; }.table-row { display: flex; flex-direction: column; padding: 14px; gap: 9px; border-bottom: 1px solid #e7edf3; }.pacientes-table td { display: flex; align-items: center; justify-content: space-between; gap: 12px; width: 100%; padding: 0; border: 0; }.pacientes-table td[data-label]::before { content: attr(data-label); color: #60758a; font-size: .75rem; }.pacientes-table .col-name { order: -1; margin-bottom: 4px; }.pacientes-table .col-actions { justify-content: flex-end; }.action-btn { width: 38px; height: 38px; }.table-footer { padding: 14px; }.pagination-controls { width: 100%; justify-content: space-between; }.record-text { white-space: normal; overflow-wrap: anywhere; }.name-cell { min-width: 0; } }
</style>