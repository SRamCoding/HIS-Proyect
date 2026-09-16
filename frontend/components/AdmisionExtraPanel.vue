<template>
  <div class="lab-container">
    <!-- Altas -->
    <template v-if="mode === 'altas'">
      <div class="page-header">
        <div class="header-left">
          <div class="header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-arrow-right-on-rectangle" class="w-5 h-5" style="color: var(--teal)" />
          </div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ADMISIÓN</span>
            <h1 class="page-title">Altas de Pacientes</h1>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn-secondary btn-sm" @click="cargarAltas"><UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />Actualizar</button>
        </div>
      </div>
      <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
      <p class="field-hint" style="margin-bottom:1rem">Altas registradas en Hospitalización (alta médica) y en Emergencia (destino ALTA). Vista de solo lectura para el cierre administrativo.</p>

      <section class="panel search-panel">
        <form class="search-form" @submit.prevent="cargarAltas">
          <div class="search-grid">
            <div class="search-field"><label class="form-label">Desde</label><input v-model="altasFiltro.fecha_desde" type="date" class="input-clinical" /></div>
            <div class="search-field"><label class="form-label">Hasta</label><input v-model="altasFiltro.fecha_hasta" type="date" class="input-clinical" /></div>
            <div class="search-field"><label class="form-label">Buscar (nombre, DNI)</label><input v-model="altasFiltro.q" class="input-clinical" /></div>
          </div>
          <div class="search-actions"><button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button></div>
        </form>
      </section>

      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ altas.length }} altas</h2></div>
        <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
        <div v-else class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Origen</th><th>Paciente</th><th>DNI</th><th>N.°</th><th>Fecha alta</th><th>Servicio</th><th>Resumen</th></tr></thead>
            <tbody>
              <tr v-for="a in altas" :key="a.origen + a.id">
                <td><span class="badge" :class="a.origen === 'hospitalizacion' ? 'badge-ok' : 'badge-info'">{{ a.origen === 'hospitalizacion' ? 'Hospitalización' : 'Emergencia' }}</span></td>
                <td>{{ a.paciente_nombre }}</td>
                <td>{{ a.paciente_dni || 'NN' }}</td>
                <td>{{ a.numero || '—' }}</td>
                <td>{{ formatFecha(a.fecha_alta) }}</td>
                <td>{{ a.servicio_o_especialidad || '—' }}</td>
                <td class="col-resumen">{{ a.resumen || '—' }}</td>
              </tr>
              <tr v-if="!altas.length"><td colspan="7" style="text-align:center;color:var(--ink-soft)">Sin altas para estos filtros.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <!-- Lista de Espera -->
    <template v-if="mode === 'lista-espera'">
      <div class="page-header">
        <div class="header-left">
          <div class="header-icon" style="background: var(--amber-soft)">
            <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
          </div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ADMISIÓN</span>
            <h1 class="page-title">Lista de Espera</h1>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn-primary" @click="abrirNuevaEspera"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Registrar</button>
        </div>
      </div>
      <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>

      <section class="panel search-panel">
        <form class="search-form" @submit.prevent="cargarEspera">
          <div class="search-grid">
            <div class="search-field">
              <label class="form-label">Estado</label>
              <select v-model="esperaFiltro.estado" class="input-clinical" @change="cargarEspera">
                <option value="pendiente">Pendiente</option><option value="atendido">Atendido</option><option value="cancelado">Cancelado</option>
              </select>
            </div>
            <div class="search-field"><label class="form-label">Buscar (nombre, DNI)</label><input v-model="esperaFiltro.q" class="input-clinical" /></div>
          </div>
          <div class="search-actions"><button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button></div>
        </form>
      </section>

      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ espera.length }} registros</h2></div>
        <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
        <div v-else class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Prioridad</th><th>Paciente</th><th>Servicio/Especialidad</th><th>Motivo</th><th>Registrado</th><th></th></tr></thead>
            <tbody>
              <tr v-for="e in espera" :key="e.id">
                <td><span class="badge" :class="e.prioridad === 'urgente' ? 'badge-off' : 'badge-info'">{{ e.prioridad }}</span></td>
                <td>{{ e.paciente_nombre }} <span class="field-hint">({{ e.paciente_dni || 'NN' }})</span></td>
                <td>{{ e.servicio_nombre || e.especialidad_nombre || '—' }}</td>
                <td class="col-resumen">{{ e.motivo || '—' }}</td>
                <td>{{ formatFecha(e.created_at) }}</td>
                <td class="col-acciones">
                  <template v-if="e.estado === 'pendiente'">
                    <button class="action-btn action-view" title="Atender" @click="abrirAtender(e)"><UIcon name="i-heroicons-check" class="w-4 h-4" /></button>
                    <button class="action-btn" title="Cancelar" @click="cancelar(e)"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" /></button>
                  </template>
                  <span v-else class="badge" :class="e.estado === 'atendido' ? 'badge-ok' : 'badge-off'">{{ e.estado }}</span>
                </td>
              </tr>
              <tr v-if="!espera.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">Sin registros.</td></tr>
            </tbody>
          </table>
        </div>
      </section>

      <!-- Modal: Registrar en lista de espera -->
      <div v-if="modalEspera" class="modal-overlay" @click.self="modalEspera = false">
        <div class="modal-content">
          <div class="modal-header"><h3 class="modal-title">Registrar en Lista de Espera</h3><button class="action-btn" @click="modalEspera = false"><UIcon name="i-heroicons-x-mark" class="w-5 h-5" /></button></div>
          <div v-if="modalError" class="error-banner">{{ modalError }}</div>
          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">DNI del paciente</label>
              <div style="display:flex;gap:0.5rem">
                <input v-model="dniBusqueda" class="input-clinical" placeholder="DNI" @keyup.enter="buscarPacienteEspera" />
                <button type="button" class="btn-secondary" @click="buscarPacienteEspera">Buscar</button>
              </div>
              <p v-if="pacienteEncontrado" class="field-hint">✓ {{ pacienteEncontrado.full_name }}</p>
            </div>
            <div class="form-group">
              <label class="form-label">Servicio</label>
              <select v-model="nuevaEspera.servicio_id" class="input-clinical">
                <option value="">—</option><option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Especialidad</label>
              <select v-model="nuevaEspera.especialidad_id" class="input-clinical">
                <option value="">—</option><option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
              </select>
            </div>
            <div class="form-group">
              <label class="form-label">Prioridad</label>
              <select v-model="nuevaEspera.prioridad" class="input-clinical"><option value="normal">Normal</option><option value="urgente">Urgente</option></select>
            </div>
            <div class="form-group full-width">
              <label class="form-label">Motivo</label>
              <textarea v-model="nuevaEspera.motivo" class="input-clinical" rows="2" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="modalEspera = false">Cancelar</button>
            <button class="btn-primary" :disabled="!pacienteEncontrado || guardando" @click="guardarEspera">{{ guardando ? 'Guardando...' : 'Registrar' }}</button>
          </div>
        </div>
      </div>

      <!-- Modal: Atender -->
      <div v-if="modalAtender" class="modal-overlay" @click.self="modalAtender = null">
        <div class="modal-content">
          <div class="modal-header"><h3 class="modal-title">Atender: {{ modalAtender.paciente_nombre }}</h3><button class="action-btn" @click="modalAtender = null"><UIcon name="i-heroicons-x-mark" class="w-5 h-5" /></button></div>
          <p class="field-hint">Si ya se agendó una cita desde Agendamiento para este paciente, selecciónala para enlazarla. También puedes marcar como atendido sin enlazar ninguna.</p>
          <div v-if="modalError" class="error-banner">{{ modalError }}</div>
          <div class="form-group full-width">
            <label class="form-label">Cita (opcional)</label>
            <select v-model="citaSeleccionada" class="input-clinical">
              <option value="">Sin enlazar cita</option>
              <option v-for="c in citasPaciente" :key="c.id" :value="c.id">{{ formatFecha(c.created_at) }} · {{ c.hora_inicio }} · {{ c.estado }}</option>
            </select>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="modalAtender = null">Cancelar</button>
            <button class="btn-primary" :disabled="guardando" @click="confirmarAtender">{{ guardando ? 'Guardando...' : 'Marcar Atendido' }}</button>
          </div>
        </div>
      </div>
    </template>

    <!-- Anuncios -->
    <template v-if="mode === 'anuncios'">
      <div class="page-header">
        <div class="header-left">
          <div class="header-icon" style="background: var(--navy-soft, rgba(30,58,95,0.08))">
            <UIcon name="i-heroicons-speaker-wave" class="w-5 h-5" style="color: var(--navy)" />
          </div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ADMISIÓN</span>
            <h1 class="page-title">Anuncios</h1>
          </div>
        </div>
        <div class="header-actions">
          <label class="field-hint" style="display:flex;align-items:center;gap:0.375rem;cursor:pointer">
            <input type="checkbox" v-model="verInactivos" @change="cargarAnuncios" /> Ver inactivos
          </label>
          <button class="btn-primary" @click="mostrarFormAnuncio = true"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Publicar</button>
        </div>
      </div>
      <div v-if="error" class="error-banner">{{ error }}</div>

      <section v-if="mostrarFormAnuncio" class="panel">
        <h3 class="results-title" style="margin-bottom:0.75rem">Nuevo anuncio</h3>
        <div v-if="modalError" class="error-banner">{{ modalError }}</div>
        <div class="form-grid">
          <div class="form-group full-width"><label class="form-label">Título</label><input v-model="nuevoAnuncio.titulo" class="input-clinical" maxlength="150" /></div>
          <div class="form-group full-width"><label class="form-label">Contenido</label><textarea v-model="nuevoAnuncio.contenido" class="input-clinical" rows="3" /></div>
        </div>
        <div class="search-actions">
          <button class="btn-secondary" @click="mostrarFormAnuncio = false">Cancelar</button>
          <button class="btn-primary" :disabled="guardando" @click="guardarAnuncio">{{ guardando ? 'Publicando...' : 'Publicar' }}</button>
        </div>
      </section>

      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <div v-else class="anuncios-grid">
        <div v-for="a in anuncios" :key="a.id" class="anuncio-card" :class="{ 'anuncio-inactivo': !a.is_active }">
          <div class="anuncio-head">
            <h3 class="anuncio-titulo">{{ a.titulo }}</h3>
            <button class="action-btn" :title="a.is_active ? 'Desactivar' : 'Reactivar'" @click="toggleAnuncio(a)">
              <UIcon :name="a.is_active ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" />
            </button>
          </div>
          <p class="anuncio-contenido">{{ a.contenido }}</p>
          <p class="field-hint">{{ a.publicado_por || 'Admisión' }} · {{ formatFecha(a.created_at) }}</p>
        </div>
        <p v-if="!anuncios.length" style="color:var(--ink-soft)">No hay anuncios{{ verInactivos ? '' : ' activos' }}.</p>
      </div>
    </template>

    <!-- Mensajito -->
    <template v-if="mode === 'mensajito'">
      <div class="page-header">
        <div class="header-left">
          <div class="header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-paper-airplane" class="w-5 h-5" style="color: var(--teal)" />
          </div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ADMISIÓN</span>
            <h1 class="page-title">Mensajito</h1>
          </div>
        </div>
        <div class="header-actions">
          <button class="btn-primary" @click="abrirNuevoMensaje"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Nuevo mensaje</button>
        </div>
      </div>
      <div v-if="error" class="error-banner">{{ error }}</div>

      <div class="modal-tabs" style="margin-bottom:1rem">
        <button class="modal-tab" :class="{ 'modal-tab--active': tabMsg === 'inbox' }" @click="tabMsg = 'inbox'; cargarMensajes()">Bandeja de entrada</button>
        <button class="modal-tab" :class="{ 'modal-tab--active': tabMsg === 'enviados' }" @click="tabMsg = 'enviados'; cargarMensajes()">Enviados</button>
      </div>

      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <div v-else class="mensajes-list">
        <div v-for="m in mensajes" :key="m.id" class="mensaje-item" :class="{ 'mensaje-no-leido': tabMsg === 'inbox' && !m.leido }">
          <div class="mensaje-head">
            <span class="mensaje-de">{{ tabMsg === 'inbox' ? (m.remitente_nombre || 'Usuario') : ('Para: ' + (m.destinatario_role ? ('rol ' + m.destinatario_role) : 'usuario')) }}</span>
            <span class="field-hint">{{ formatFecha(m.created_at) }}</span>
          </div>
          <p class="mensaje-contenido">{{ m.contenido }}</p>
          <p v-if="m.paciente_nombre" class="field-hint"><UIcon name="i-heroicons-user" class="w-3 h-3" /> {{ m.paciente_nombre }}</p>
          <button v-if="tabMsg === 'inbox' && !m.leido" class="btn-secondary btn-sm" @click="leer(m)">Marcar leído</button>
        </div>
        <p v-if="!mensajes.length" style="color:var(--ink-soft)">Sin mensajes.</p>
      </div>

      <!-- Modal: nuevo mensaje -->
      <div v-if="modalMensaje" class="modal-overlay" @click.self="modalMensaje = false">
        <div class="modal-content">
          <div class="modal-header"><h3 class="modal-title">Nuevo mensaje</h3><button class="action-btn" @click="modalMensaje = false"><UIcon name="i-heroicons-x-mark" class="w-5 h-5" /></button></div>
          <div v-if="modalError" class="error-banner">{{ modalError }}</div>
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Destinatario</label>
              <select v-model="nuevoMensaje.destino" class="input-clinical">
                <option value="">Seleccionar...</option>
                <optgroup label="Por persona">
                  <option v-for="d in destinatarios" :key="d.id" :value="'user:' + d.id">{{ d.name }} ({{ d.role }})</option>
                </optgroup>
                <optgroup label="Por rol (a todos)">
                  <option v-for="r in rolesDisponibles" :key="r" :value="'role:' + r">Rol: {{ r }}</option>
                </optgroup>
              </select>
            </div>
            <div class="form-group full-width">
              <label class="form-label">Mensaje</label>
              <textarea v-model="nuevoMensaje.contenido" class="input-clinical" rows="3" maxlength="500" />
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn-secondary" @click="modalMensaje = false">Cancelar</button>
            <button class="btn-primary" :disabled="!nuevoMensaje.destino || !nuevoMensaje.contenido || guardando" @click="enviarMensaje">{{ guardando ? 'Enviando...' : 'Enviar' }}</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'altas' | 'lista-espera' | 'anuncios' | 'mensajito'
const props = defineProps<{ mode: Mode }>()

const { api } = useApi()

const error = ref('')
const modalError = ref('')
const loading = ref(false)
const guardando = ref(false)

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}

function formatFecha(f: string | null) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

// --- Altas ---
const altas = ref<any[]>([])
const altasFiltro = reactive({ fecha_desde: '', fecha_hasta: '', q: '' })
async function cargarAltas() {
  loading.value = true; error.value = ''
  try {
    const q = Object.fromEntries(Object.entries(altasFiltro).filter(([, v]) => v))
    altas.value = await api('/app/admision/altas', { query: q })
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

// --- Lista de Espera ---
const espera = ref<any[]>([])
const esperaFiltro = reactive({ estado: 'pendiente', q: '' })
const servicios = ref<any[]>([])
const especialidades = ref<any[]>([])
const modalEspera = ref(false)
const dniBusqueda = ref('')
const pacienteEncontrado = ref<any>(null)
const nuevaEspera = reactive({ servicio_id: '', especialidad_id: '', prioridad: 'normal', motivo: '' })
const modalAtender = ref<any>(null)
const citasPaciente = ref<any[]>([])
const citaSeleccionada = ref('')

async function cargarEspera() {
  loading.value = true; error.value = ''
  try {
    const q = Object.fromEntries(Object.entries(esperaFiltro).filter(([, v]) => v))
    espera.value = await api('/app/admision/lista-espera', { query: q })
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function abrirNuevaEspera() {
  modalError.value = ''; dniBusqueda.value = ''; pacienteEncontrado.value = null
  nuevaEspera.servicio_id = ''; nuevaEspera.especialidad_id = ''; nuevaEspera.prioridad = 'normal'; nuevaEspera.motivo = ''
  modalEspera.value = true
  if (!servicios.value.length) {
    try {
      servicios.value = await api('/app/consulta-externa/programacion-medica/servicios')
      especialidades.value = await api('/app/consulta-externa/programacion-medica/especialidades')
    } catch (e) { /* catalogos opcionales */ }
  }
}

async function buscarPacienteEspera() {
  if (!dniBusqueda.value) return
  modalError.value = ''
  try {
    pacienteEncontrado.value = await api(`/app/admision/dni/${dniBusqueda.value}`)
  } catch (e: any) {
    pacienteEncontrado.value = null
    modalError.value = e?.status === 404 ? 'Paciente no encontrado. Regístralo primero en Pacientes.' : err(e)
  }
}

async function guardarEspera() {
  if (!pacienteEncontrado.value) return
  guardando.value = true; modalError.value = ''
  try {
    await api('/app/admision/lista-espera', {
      method: 'POST',
      body: {
        patient_id: pacienteEncontrado.value.id,
        servicio_id: nuevaEspera.servicio_id || null,
        especialidad_id: nuevaEspera.especialidad_id || null,
        prioridad: nuevaEspera.prioridad,
        motivo: nuevaEspera.motivo || null,
      },
    })
    modalEspera.value = false
    await cargarEspera()
  } catch (e) { modalError.value = err(e) } finally { guardando.value = false }
}

async function abrirAtender(e: any) {
  modalAtender.value = e
  modalError.value = ''
  citaSeleccionada.value = ''
  citasPaciente.value = []
  if (e.paciente_dni) {
    try {
      citasPaciente.value = await api('/app/consulta-externa/citas', { query: { dni: e.paciente_dni, estado: 'separada' } })
    } catch (err_) { /* la selección de cita es opcional */ }
  }
}

async function confirmarAtender() {
  if (!modalAtender.value) return
  guardando.value = true; modalError.value = ''
  try {
    await api(`/app/admision/lista-espera/${modalAtender.value.id}/atender`, {
      method: 'POST', body: { cita_id: citaSeleccionada.value || null },
    })
    modalAtender.value = null
    await cargarEspera()
  } catch (e) { modalError.value = err(e) } finally { guardando.value = false }
}

async function cancelar(e: any) {
  try {
    await api(`/app/admision/lista-espera/${e.id}/cancelar`, { method: 'POST' })
    await cargarEspera()
  } catch (e2) { error.value = err(e2) }
}

// --- Anuncios ---
const anuncios = ref<any[]>([])
const verInactivos = ref(false)
const mostrarFormAnuncio = ref(false)
const nuevoAnuncio = reactive({ titulo: '', contenido: '' })

async function cargarAnuncios() {
  loading.value = true; error.value = ''
  try {
    anuncios.value = await api('/app/admision/anuncios', { query: { incluir_inactivos: verInactivos.value } })
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function guardarAnuncio() {
  if (!nuevoAnuncio.titulo || !nuevoAnuncio.contenido) { modalError.value = 'Completa título y contenido'; return }
  guardando.value = true; modalError.value = ''
  try {
    await api('/app/admision/anuncios', { method: 'POST', body: { ...nuevoAnuncio } })
    nuevoAnuncio.titulo = ''; nuevoAnuncio.contenido = ''
    mostrarFormAnuncio.value = false
    await cargarAnuncios()
  } catch (e) { modalError.value = err(e) } finally { guardando.value = false }
}

async function toggleAnuncio(a: any) {
  try {
    await api(`/app/admision/anuncios/${a.id}`, { method: 'PATCH', body: { is_active: !a.is_active } })
    await cargarAnuncios()
  } catch (e) { error.value = err(e) }
}

// --- Mensajito ---
const tabMsg = ref<'inbox' | 'enviados'>('inbox')
const mensajes = ref<any[]>([])
const destinatarios = ref<any[]>([])
const modalMensaje = ref(false)
const nuevoMensaje = reactive({ destino: '', contenido: '' })

const rolesDisponibles = computed(() => [...new Set(destinatarios.value.map((d: any) => d.role))].sort())

async function cargarMensajes() {
  loading.value = true; error.value = ''
  try {
    mensajes.value = await api(`/app/admision/mensajito/${tabMsg.value === 'inbox' ? 'inbox' : 'enviados'}`)
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function leer(m: any) {
  try {
    await api(`/app/admision/mensajito/${m.id}/leido`, { method: 'POST' })
    m.leido = true
  } catch (e) { error.value = err(e) }
}

async function abrirNuevoMensaje() {
  modalError.value = ''
  nuevoMensaje.destino = ''; nuevoMensaje.contenido = ''
  modalMensaje.value = true
  if (!destinatarios.value.length) {
    try { destinatarios.value = await api('/app/admision/mensajito/destinatarios') } catch (e) { /* opcional */ }
  }
}

async function enviarMensaje() {
  guardando.value = true; modalError.value = ''
  try {
    const [tipo, id] = nuevoMensaje.destino.split(':')
    await api('/app/admision/mensajito', {
      method: 'POST',
      body: {
        contenido: nuevoMensaje.contenido,
        destinatario_user_id: tipo === 'user' ? id : null,
        destinatario_role: tipo === 'role' ? id : null,
      },
    })
    modalMensaje.value = false
    if (tabMsg.value === 'enviados') await cargarMensajes()
  } catch (e) { modalError.value = err(e) } finally { guardando.value = false }
}

onMounted(async () => {
  if (props.mode === 'altas') await cargarAltas()
  else if (props.mode === 'lista-espera') await cargarEspera()
  else if (props.mode === 'anuncios') await cargarAnuncios()
  else if (props.mode === 'mensajito') await cargarMensajes()
})
</script>

<style scoped>
.lab-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.header-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.search-form { display: flex; flex-direction: column; gap: 1rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.search-field { display: flex; flex-direction: column; gap: 0.25rem; }
.search-actions { display: flex; gap: 0.75rem; justify-content: flex-end; margin-top: 0.75rem; }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.col-resumen { max-width: 260px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.col-acciones { display: flex; gap: 0.25rem; }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; white-space: nowrap; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-off { color: var(--alert); background: var(--alert-soft); }
.badge-info { color: var(--teal); background: var(--teal-soft); }
.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; color: var(--ink-soft); cursor: pointer; }
.action-btn:hover { background: var(--mist); }
.action-view:hover { color: var(--teal); border-color: var(--teal-soft); background: var(--teal-soft); }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 8px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.375rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.modal-overlay { position: fixed; inset: 0; background: rgba(0,0,0,0.5); backdrop-filter: blur(4px); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 1rem; }
.modal-content { max-width: 560px; width: 100%; max-height: 90vh; overflow-y: auto; padding: 1.5rem; background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-lg); }
.modal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.modal-title { font-size: 1.0625rem; font-weight: 600; color: var(--ink); margin: 0; }
.modal-footer { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid var(--line); }
.modal-tabs { display: flex; gap: 0.25rem; border-bottom: 1px solid var(--line); }
.modal-tab { display: flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; font-size: 0.8125rem; font-weight: 500; color: var(--ink-soft); background: transparent; border: none; border-bottom: 2px solid transparent; cursor: pointer; }
.modal-tab--active { color: var(--teal); border-bottom-color: var(--teal); }
.anuncios-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; }
.anuncio-card { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); padding: 1rem; box-shadow: var(--shadow-sm); }
.anuncio-inactivo { opacity: 0.55; }
.anuncio-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; }
.anuncio-titulo { font-size: 0.9375rem; font-weight: 600; color: var(--ink); margin: 0; }
.anuncio-contenido { font-size: 0.8125rem; color: var(--ink); margin: 0.5rem 0; white-space: pre-wrap; }
.mensajes-list { display: flex; flex-direction: column; gap: 0.75rem; }
.mensaje-item { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); padding: 0.875rem 1rem; }
.mensaje-no-leido { border-left: 3px solid var(--teal); background: var(--teal-soft); }
.mensaje-head { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.mensaje-de { font-size: 0.8125rem; font-weight: 600; color: var(--ink); }
.mensaje-contenido { font-size: 0.875rem; color: var(--ink); margin: 0.25rem 0; }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid, .form-grid { grid-template-columns: 1fr; }
}
</style>
