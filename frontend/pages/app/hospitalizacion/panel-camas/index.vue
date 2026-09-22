<template>
  <div class="panel-camas-container">
    <header class="page-header">
      <div class="header-left">
        <HospitalBedIcon class="header-icon" />
        <div><h1>Panel de Camas</h1><p>Vista general de disponibilidad hospitalaria</p></div>
      </div>
      <button class="refresh-button" :disabled="cargando" @click="cargar">
        <UIcon name="i-heroicons-arrow-path" aria-hidden="true" :class="{ 'animate-spin': cargando }" />
        {{ ultimaActualizacion ? `Actualizado ${ultimaActualizacion}` : 'Actualizar' }}
      </button>
    </header>

    <section class="widgets-grid" aria-label="Resumen de camas">
      <article v-for="stat in indicadores" :key="stat.label" class="stat-widget" :class="stat.tone">
        <div class="stat-icon"><HospitalBedIcon v-if="stat.icon === 'bed'" /><UIcon v-else :name="stat.icon" aria-hidden="true" /></div>
        <div class="stat-content"><span class="stat-label">{{ stat.label }}</span><strong class="stat-value">{{ cargando ? '—' : stat.value }}</strong><span class="stat-note">{{ stat.note }}</span></div>
      </article>
    </section>

    <section class="filter-bar" aria-label="Filtros de camas">
      <label class="filter-field"><UIcon name="i-heroicons-home" aria-hidden="true" /><span><span class="filter-label">Piso</span><select v-model="pisoSeleccionado" @change="cargar"><option value="">Todos los pisos</option><option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option></select></span></label>
      <label class="filter-field"><UIcon name="i-heroicons-building-office-2" aria-hidden="true" /><span><span class="filter-label">Servicio</span><select v-model="servicioSeleccionado"><option value="">Todos los servicios</option><option v-for="servicio in servicios" :key="servicio" :value="servicio">{{ servicio }}</option></select></span></label>
      <label class="filter-field"><UIcon name="i-heroicons-shield-check" aria-hidden="true" /><span><span class="filter-label">Estado</span><select v-model="estadoSeleccionado"><option value="">Todos los estados</option><option v-for="estado in estados" :key="estado" :value="estado">{{ formatEstado(estado) }}</option></select></span></label>
      <label class="search-field"><UIcon name="i-heroicons-magnifying-glass" aria-hidden="true" /><span class="sr-only">Buscar cama, habitación o paciente</span><input v-model="busqueda" type="search" placeholder="Buscar cama o paciente..." /></label>
    </section>

    <div v-if="cargando" class="panel-state" role="status"><UIcon name="i-heroicons-arrow-path" class="animate-spin" aria-hidden="true" /><p>Cargando panel de camas...</p></div>
    <div v-else-if="error" class="panel-state error-state" role="alert"><UIcon name="i-heroicons-exclamation-triangle" aria-hidden="true" /><p>{{ error }}</p><button class="panel-button" @click="cargar">Reintentar</button></div>
    <div v-else-if="!camasFiltradas.length" class="panel-state"><HospitalBedIcon /><p>No se encontraron camas con estos filtros.</p><button class="panel-button" @click="limpiarFiltros">Limpiar filtros</button></div>
    <div v-else class="bed-groups">
      <section v-for="grupo in grupos" :key="grupo.key" class="bed-group">
        <header class="group-header">
          <UIcon name="i-heroicons-building-office-2" class="group-icon" aria-hidden="true" />
          <div class="group-heading"><h2>{{ grupo.nombre }}</h2><p>{{ grupo.salas.join(' · ') || 'Habitaciones sin especificar' }}</p></div>
          <span class="group-availability">{{ grupo.disponibles }} de {{ grupo.camas.length }} disponibles</span>
        </header>
        <div class="camas-grid">
          <button v-for="c in grupo.camas" :key="c.id" class="cama-card" :style="{ '--state-color': getEstadoColor(c.estado), '--state-soft': getEstadoSoft(c.estado) }" :aria-label="`Ver detalle de cama ${c.codigo}, ${formatEstado(c.estado)}`" @click="verDetalle(c)">
            <span class="cama-header"><HospitalBedIcon class="bed-icon" /><strong class="cama-codigo">{{ c.codigo }}</strong><span class="cama-estado-badge"><span class="state-dot" />{{ formatEstado(c.estado) }}</span></span>
            <span class="cama-body">
              <span class="cama-info"><UIcon name="i-heroicons-building-office" aria-hidden="true" />{{ c.sala_nombre || 'Habitación sin especificar' }}</span>
              <span v-if="c.tipo_cama" class="cama-info"><UIcon name="i-heroicons-tag" aria-hidden="true" /><span class="type-tag">{{ c.tipo_cama }}</span></span>
              <span v-if="c.estado === 'OCUPADA' && c.paciente_nombre" class="patient-strip"><UIcon name="i-heroicons-user" aria-hidden="true" /><span><strong>{{ c.paciente_nombre }}</strong><small v-if="c.fecha_ingreso">Ingreso: {{ formatFechaHora(c.fecha_ingreso) }}</small></span></span>
              <span v-else-if="c.estado === 'MANTENIMIENTO'" class="patient-strip"><UIcon name="i-heroicons-wrench-screwdriver" aria-hidden="true" />En mantenimiento</span>
            </span>
            <span class="cama-footer">Ver detalle <UIcon name="i-heroicons-arrow-right" aria-hidden="true" /></span>
          </button>
        </div>
      </section>
    </div>
    <!-- Modal Detalle -->
    <div v-if="camaDetalle" class="modal-overlay" @click.self="camaDetalle = null">
      <div class="modal-container modal-detalle">
        <!-- Modal Header -->
        <div class="modal-header" :style="{ background: getEstadoColor(camaDetalle.estado) }">
          <div class="modal-header-left">
            <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: white" />
            <span class="modal-title">Cama {{ camaDetalle.codigo }}</span>
          </div>
          <button class="modal-close" @click="camaDetalle = null">
            <UIcon name="i-heroicons-x-mark" class="w-5 h-5" />
          </button>
        </div>

        <!-- Modal Body -->
        <div class="modal-body">
          <div class="detalle-grid">
            <div class="detalle-item">
              <span class="detalle-label">Sala</span>
              <span class="detalle-value">{{ camaDetalle.sala_nombre || '—' }}</span>
            </div>
            <div class="detalle-item">
              <span class="detalle-label">Tipo</span>
              <span class="detalle-value">{{ camaDetalle.tipo_cama || '—' }}</span>
            </div>
            <div class="detalle-item">
              <span class="detalle-label">Estado</span>
              <span class="detalle-value">
                <span class="estado-badge-modal" :class="{
                  'badge-disponible': camaDetalle.estado === 'DISPONIBLE',
                  'badge-ocupada': camaDetalle.estado === 'OCUPADA',
                  'badge-mantenimiento': camaDetalle.estado === 'MANTENIMIENTO',
                  'badge-reservada': camaDetalle.estado === 'RESERVADA',
                }">
                  {{ camaDetalle.estado }}
                </span>
              </span>
            </div>
            <div v-if="camaDetalle.piso_nombre" class="detalle-item">
              <span class="detalle-label">Piso</span>
              <span class="detalle-value">{{ camaDetalle.piso_nombre }}</span>
            </div>
          </div>

          <!-- Información de paciente si está ocupada -->
          <div v-if="camaDetalle.estado === 'OCUPADA'" class="paciente-info-modal">
            <div class="paciente-info-header">
              <UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--teal, #0d9488)" />
              <span class="paciente-info-title">Información del Paciente</span>
            </div>
            <div class="paciente-info-grid">
              <div class="paciente-info-item">
                <span class="paciente-info-label">Paciente</span>
                <span class="paciente-info-value">{{ camaDetalle.paciente_nombre || '—' }}</span>
              </div>
              <div class="paciente-info-item">
                <span class="paciente-info-label">DNI</span>
                <span class="paciente-info-value font-mono-data">{{ camaDetalle.paciente_dni || 'NN' }}</span>
              </div>
              <div class="paciente-info-item">
                <span class="paciente-info-label">N° Hospitalización</span>
                <span class="paciente-info-value">{{ camaDetalle.numero_hospitalizacion || '—' }}</span>
              </div>
              <div class="paciente-info-item">
                <span class="paciente-info-label">Ingreso</span>
                <span class="paciente-info-value">{{ camaDetalle.fecha_ingreso ? formatFechaHora(camaDetalle.fecha_ingreso) : '—' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Modal Footer -->
        <div class="modal-footer">
          <button class="btn-modal-secondary" @click="camaDetalle = null">
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()

// Estado
const pisos = ref<any[]>([])
const camas = ref<any[]>([])
const pisoSeleccionado = ref('')
const cargando = ref(false)
const error = ref('')
const camaDetalle = ref<any>(null)
const servicioSeleccionado = ref('')
const estadoSeleccionado = ref('')
const busqueda = ref('')
const ultimaActualizacion = ref('')
const pisoPorCama = ref<Record<string, string>>({})
let cargaActual = 0

// Computed
const disponibles = computed(() => camas.value.filter(c => c.estado === 'DISPONIBLE').length)
const ocupadas = computed(() => camas.value.filter(c => c.estado === 'OCUPADA').length)
const mantenimiento = computed(() => camas.value.filter(c => c.estado === 'MANTENIMIENTO').length)
const reservadas = computed(() => camas.value.filter(c => c.estado === 'RESERVADA').length)
const porcentaje = (cantidad: number) => camas.value.length ? Math.round(cantidad / camas.value.length * 100) : 0
const indicadores = computed(() => [
  { label: 'Total', value: camas.value.length, note: pisoSeleccionado.value ? 'Camas en este piso' : 'Camas en el hospital', icon: 'bed', tone: '' },
  { label: 'Disponibles', value: disponibles.value, note: `${porcentaje(disponibles.value)}% del total`, icon: 'bed', tone: 'tone-green' },
  { label: 'Ocupadas', value: ocupadas.value, note: `${porcentaje(ocupadas.value)}% del total`, icon: 'i-heroicons-user', tone: 'tone-red' },
  { label: 'Reservadas', value: reservadas.value, note: `${porcentaje(reservadas.value)}% del total`, icon: 'i-heroicons-calendar-days', tone: 'tone-amber' },
  { label: 'Mantenimiento', value: mantenimiento.value, note: `${porcentaje(mantenimiento.value)}% del total`, icon: 'i-heroicons-wrench-screwdriver', tone: 'tone-blue' },
  { label: 'Ocupación', value: `${porcentaje(ocupadas.value)}%`, note: `${ocupadas.value} de ${camas.value.length} camas`, icon: 'i-heroicons-chart-pie', tone: '' },
])
const servicios = computed(() => [...new Set(camas.value.map(c => c.servicio_nombre).filter(Boolean))].sort() as string[])
const estados = computed(() => [...new Set(['DISPONIBLE', 'OCUPADA', 'RESERVADA', 'MANTENIMIENTO', ...camas.value.map(c => c.estado)])])
const normalizar = (value: string) => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es').trim()
const camasFiltradas = computed(() => camas.value.filter(c =>
  (!servicioSeleccionado.value || c.servicio_nombre === servicioSeleccionado.value) &&
  (!estadoSeleccionado.value || c.estado === estadoSeleccionado.value) &&
  (!busqueda.value.trim() || normalizar([c.codigo, c.nombre, c.sala_nombre, c.paciente_nombre].filter(Boolean).join(' ')).includes(normalizar(busqueda.value)))
))
const grupos = computed(() => {
  const result = new Map<string, { key: string; nombre: string; salas: string[]; camas: any[]; disponibles: number }>()
  for (const cama of camasFiltradas.value) {
    const pisoId = pisoPorCama.value[String(cama.id)] || ''
    const piso = pisos.value.find(p => String(p.id) === pisoId)?.nombre || 'Piso sin especificar'
    const servicio = cama.servicio_nombre || 'Servicio sin especificar'
    const key = JSON.stringify([pisoId, servicio])
    if (!result.has(key)) result.set(key, { key, nombre: `${piso} · ${servicio}`, salas: [], camas: [], disponibles: 0 })
    const grupo = result.get(key)!
    grupo.camas.push(cama)
    if (cama.estado === 'DISPONIBLE') grupo.disponibles++
    if (cama.sala_nombre && !grupo.salas.includes(cama.sala_nombre)) grupo.salas.push(cama.sala_nombre)
  }
  return [...result.values()]
})

async function limpiarFiltros() {
  pisoSeleccionado.value = ''
  servicioSeleccionado.value = ''
  estadoSeleccionado.value = ''
  busqueda.value = ''
  await cargar()
}

// Helpers
const formatFechaHora = (fecha: string) => {
  if (!fecha) return '—'
  return new Date(fecha).toLocaleString('es-PE')
}

const getEstadoColor = (estado: string) => {
  const map: Record<string, string> = {
    'DISPONIBLE': '#16a34a',
    'OCUPADA': '#dc2626',
    'MANTENIMIENTO': '#2563eb',
    'RESERVADA': '#d97706'
  }
  return map[estado] || '#1e293b'
}

const getEstadoSoft = (estado: string) => {
  const map: Record<string, string> = {
    'DISPONIBLE': '#dcfce7',
    'OCUPADA': '#fee2e2',
    'MANTENIMIENTO': '#dbeafe',
    'RESERVADA': '#fef3c7'
  }
  return map[estado] || '#f1f5f9'
}

const formatEstado = (estado: string) => {
  const map: Record<string, string> = {
    'DISPONIBLE': 'Disponible',
    'OCUPADA': 'Ocupada',
    'MANTENIMIENTO': 'Mantenimiento',
    'RESERVADA': 'Reservada'
  }
  return map[estado] || estado
}

// Funciones
async function cargar() {
  const carga = ++cargaActual
  const piso = pisoSeleccionado.value
  cargando.value = true
  error.value = ''
  try {
    const params = piso ? `?piso_id=${encodeURIComponent(piso)}` : ''
    // The existing response omits floor IDs. Resolve them with its existing floor filter.
    const [datos, porPiso] = await Promise.all([
      api<any[]>(`/app/hospitalizacion/panel-camas${params}`),
      piso ? Promise.resolve([]) : Promise.all(pisos.value.map(async p => ({
        id: String(p.id), camas: await api<any[]>(`/app/hospitalizacion/panel-camas?piso_id=${encodeURIComponent(p.id)}`),
      }))),
    ])
    if (carga !== cargaActual) return
    const mapa: Record<string, string> = {}
    if (piso) datos.forEach(c => { mapa[String(c.id)] = piso })
    else porPiso.forEach(p => p.camas.forEach(c => { mapa[String(c.id)] = p.id }))
    pisoPorCama.value = mapa
    camas.value = datos
    ultimaActualizacion.value = new Date().toLocaleTimeString('es-PE', { hour: '2-digit', minute: '2-digit', hour12: false })
  } catch (e: any) {
    if (carga === cargaActual) error.value = e?.data?.detail || 'No pudimos cargar el estado de las camas.'
  } finally {
    if (carga === cargaActual) cargando.value = false
  }
}

function verDetalle(c: any) {
  camaDetalle.value = c
}

// Lifecycle
onMounted(async () => {
  try {
    pisos.value = await api('/app/hospitalizacion/pisos')
  } catch (e: any) { /* silencioso */ }
  await cargar()
  const camaId = typeof route.query.cama === 'string' ? route.query.cama : ''
  if (camaId) camaDetalle.value = camas.value.find(c => String(c.id) === camaId) || null
})
</script>

<style scoped>
/* Colores y tipografía: heredados de .app-shell (assets/css/hospital-theme.css). */
.panel-camas-container {
  padding: 24px 32px 40px;
  min-height: 100%;
  background: var(--mist);
  color: var(--ink);
}
.page-header { display: flex; justify-content: space-between; align-items: center; gap: 20px; margin-bottom: 22px; }
.header-left { display: flex; align-items: center; gap: 18px; min-width: 0; }
.header-icon { width: 46px; height: 46px; color: var(--teal); flex-shrink: 0; }
h1 { margin: 0; font-size: 1.5rem; font-weight: 600; line-height: 1.2; letter-spacing: -0.01em; }
.page-header p { margin: 4px 0 0; color: var(--ink-soft); font-size: 14px; }
.refresh-button { display: flex; align-items: center; gap: 8px; background: #fff; border: 1px solid #e1e8ef; border-radius: 8px; padding: 8px 14px; color: var(--ink-soft); font-size: 13px; cursor: pointer; flex-shrink: 0; transition: border-color .15s, color .15s; }
.refresh-button:hover:not(:disabled) { border-color: var(--teal); color: var(--teal); }
.refresh-button:disabled { opacity: .6; cursor: wait; }
.refresh-button .iconify { width: 18px; height: 18px; }
.widgets-grid { display: grid; grid-template-columns: repeat(6,minmax(0,1fr)); gap: 12px; margin-bottom: 18px; }
.stat-widget { display: flex; align-items: flex-start; gap: 14px; background: white; padding: 16px; border: 1px solid #e1e8ef; border-radius: 14px; box-shadow: 0 2px 5px #243d5903; --accent: var(--teal); --soft: var(--teal-soft); }
.stat-icon { display: grid; place-items: center; width: 46px; height: 46px; flex-shrink: 0; border-radius: 12px; background: var(--soft); color: var(--accent); }
.stat-icon > * { width: 27px; height: 27px; }
.stat-content { display: flex; flex-direction: column; min-width: 0; gap: 4px; }
.stat-label { color: var(--ink-soft); font-size: 0.8125rem; font-weight: 500; }
.stat-value { color: var(--ink); font-size: 1.5rem; line-height: 1.2; font-weight: 600; }
.stat-note { color: var(--ink-soft); font-size: 11px; line-height: 1.4; }
.tone-green { --accent: #009c53; --soft: #e1faed; }.tone-red { --accent: #df2345; --soft: #ffe5ea; }.tone-amber { --accent: #bd7800; --soft: #fff3db; }.tone-blue { --accent: #475972; --soft: #eaeef3; }
.filter-bar { display: grid; grid-template-columns: 1fr 1.15fr 1.15fr 2.4fr; gap: 20px; padding: 12px 14px; margin-bottom: 16px; background: white; border: 1px solid #e1e8ef; border-radius: 14px; box-shadow: 0 4px 12px #243d5905; }
.filter-field, .search-field { display: flex; align-items: center; gap: 10px; border: 1px solid #dfe8f2; border-radius: 8px; padding: 7px 10px; min-width: 0; }
.filter-field > .iconify, .search-field > .iconify { flex-shrink: 0; width: 20px; height: 20px; color: var(--ink-soft); }
.filter-field > span:last-child { flex: 1; min-width: 0; }
.filter-label { display: block; color: var(--ink-soft); font-size: 11px; }
.filter-field select { width: 100%; border: 0; background: transparent; font-size: 12px; color: var(--ink); padding: 2px 14px 0 0; }
.search-field { background: var(--mist); }
.search-field input { width: 100%; min-width: 0; background: transparent; font-size: 13px; outline: none; }
.filter-field:focus-within, .search-field:focus-within { outline: 2px solid var(--teal); outline-offset: 2px; }
.bed-groups { display: grid; gap: 16px; }
.bed-group { background: #fff; border: 1px solid #e1e8ef; border-radius: 14px; padding: 14px; min-width: 0; }
.group-header { display: flex; align-items: center; gap: 12px; margin: 0 0 14px; }
.group-icon { width: 26px; height: 26px; color: var(--teal); flex-shrink: 0; }
.group-heading { min-width: 0; flex: 1; }.group-heading h2 { font-size: 1rem; font-weight: 600; line-height: 1.3; margin: 0; }.group-heading p { color: var(--ink-soft); font-size: 12px; margin: 3px 0 0; overflow-wrap: anywhere; }
.group-availability { font-size: 13px; color: #009c53; font-weight: 600; flex-shrink: 0; }
.camas-grid { display: grid; grid-template-columns: repeat(auto-fill,minmax(220px,1fr)); gap: 14px; }
.cama-card { display: flex; flex-direction: column; min-width: 0; min-height: 174px; background: white; border: 1px solid #e1e8ef; border-left: 4px solid var(--state-color); border-radius: 12px; overflow: hidden; text-align: left; cursor: pointer; box-shadow: 0 2px 5px #243d5905; transition: box-shadow .15s, border-color .15s; }
.cama-card:hover { border-top-color: #9adde3; border-right-color: #9adde3; border-bottom-color: #9adde3; box-shadow: 0 4px 12px rgba(0,158,178,.12); }
.cama-header { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; padding: 12px 12px 8px; }.bed-icon { width: 26px; height: 26px; color: var(--state-color); flex-shrink: 0; }.cama-codigo { font-size: 0.8125rem; font-weight: 500; overflow-wrap: anywhere; }
.cama-estado-badge { display: inline-flex; align-items: center; gap: 5px; margin-left: auto; color: var(--state-color); background: var(--state-soft); border-radius: 999px; padding: 5px 8px; font-size: 0.6875rem; font-weight: 500; }.state-dot { width: 6px; height: 6px; background: currentColor; border-radius: 50%; }
.cama-body { display: flex; flex-direction: column; flex: 1; gap: 5px; padding: 0 12px 8px; }.cama-info { display: flex; gap: 8px; align-items: center; font-size: 0.8125rem; }.cama-info .iconify { color: var(--ink-soft); flex-shrink: 0; width: 15px; height: 15px; }.type-tag { font-size: 10px; color: var(--ink-soft); padding: 3px 7px; background: var(--mist); border-radius: 6px; }
.patient-strip { display: flex; gap: 8px; align-items: center; background: var(--state-soft); border-radius: 6px; padding: 6px; margin-top: 3px; font-size: 11px; }.patient-strip > .iconify { color: var(--state-color); width: 18px; height: 18px; flex-shrink: 0; }.patient-strip strong { display: block; font-weight: 500; overflow-wrap: anywhere; }.patient-strip small { display: block; font-size: 10px; color: var(--ink-soft); margin-top: 2px; }
.cama-footer { display: flex; align-items: center; gap: 8px; padding: 7px 12px; border-top: 1px solid #edf1f6; background: #f8fafd; color: var(--teal); font-size: 11px; font-weight: 500; }.cama-footer .iconify { width: 14px; height: 14px; }
.panel-state { display: flex; flex-direction: column; align-items: center; gap: 16px; padding: 48px 20px; text-align: center; background: white; border: 1px solid #e1e8ef; border-radius: 14px; color: var(--ink-soft); }.panel-state > .iconify, .panel-state > svg { width: 36px; height: 36px; }.error-state { color: #b4233d; }.panel-button { padding: 9px 16px; border: 1px solid #d5e0ec; border-radius: 8px; color: var(--teal); background: white; }
.panel-camas-container button:focus-visible { outline: 3px solid var(--teal); outline-offset: 3px; }
@media (max-width: 1400px) { .stat-widget { gap: 8px; padding: 12px; }.stat-icon { width: 34px; height: 34px; }.stat-icon > * { width: 23px; height: 23px; }.stat-label { font-size: 11px; }.filter-bar { gap: 12px; } }
@media (max-width: 1199px) { .widgets-grid { grid-template-columns: repeat(3,minmax(0,1fr)); }.filter-bar { grid-template-columns: repeat(2,minmax(0,1fr)); } }
@media (max-width: 767px) { .panel-camas-container { padding: 16px; }.page-header { align-items: flex-start; flex-direction: column; gap: 12px; }.header-left { flex-wrap: wrap; }h1 { font-size: 1.5rem; overflow-wrap: anywhere; }.widgets-grid { grid-template-columns: repeat(2,minmax(0,1fr)); }.stat-widget { flex-direction: column; }.filter-bar { grid-template-columns: minmax(0,1fr); }.camas-grid { grid-template-columns: minmax(0,1fr); }.group-header { flex-wrap: wrap; }.group-heading h2 { font-size: 16px; }.group-availability { width: 100%; }.stat-value { font-size: 1.5rem; } }
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 50;
  padding: 1rem;
}

.modal-container {
  background: var(--paper, #ffffff);
  border-radius: var(--radius-lg, 14px);
  box-shadow: var(--shadow-lg, 0 10px 25px rgba(0,0,0,0.15));
  width: 100%;
  max-width: 500px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: modalSlideIn 0.2s ease;
}

@keyframes modalSlideIn {
  from {
    opacity: 0;
    transform: scale(0.95) translateY(10px);
  }
  to {
    opacity: 1;
    transform: scale(1) translateY(0);
  }
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-radius: var(--radius-lg, 14px) var(--radius-lg, 14px) 0 0;
  flex-shrink: 0;
}

.modal-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.modal-title {
  font-size: 1rem;
  font-weight: 600;
  color: white;
}

.modal-close {
  background: transparent;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 6px;
  transition: background 0.2s ease;
}

.modal-close:hover {
  background: rgba(255, 255, 255, 0.15);
}

.modal-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

.detalle-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.detalle-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.detalle-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft, #64748b);
}

.detalle-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink, #1e293b);
}

.estado-badge-modal {
  display: inline-block;
  padding: 0.125rem 0.625rem;
  border-radius: 10px;
  font-size: 0.75rem;
  font-weight: 600;
}

/* Paciente Info Modal */
.paciente-info-modal {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line, #e2e8f0);
}

.paciente-info-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.paciente-info-title {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--ink, #1e293b);
}

.paciente-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.paciente-info-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  padding: 0.375rem;
  border-radius: var(--radius, 10px);
  background: var(--mist, #f1f5f9);
}

.paciente-info-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft, #64748b);
}

.paciente-info-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink, #1e293b);
}

/* Modal Footer */
.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 1rem 1.5rem;
  border-top: 1px solid var(--line, #e2e8f0);
  flex-shrink: 0;
}

.btn-modal-secondary {
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line, #e2e8f0);
  background: var(--paper, #ffffff);
  color: var(--ink, #1e293b);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-modal-secondary:hover {
  background: var(--mist, #f1f5f9);
}


</style>
