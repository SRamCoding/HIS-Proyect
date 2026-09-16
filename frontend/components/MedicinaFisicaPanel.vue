<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-user" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">MEDICINA FÍSICA Y REHABILITACIÓN</span>
          <h1 class="page-title">{{ titulo }}</h1>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <!-- ═══════════ SESIONES M. FÍSICA ═══════════ -->
    <template v-if="mode === 'sesiones-m-fisica'">
      <section class="panel">
        <div class="card-header-row"><h2 class="results-title">Nueva programación</h2></div>
        <form class="editor-form" @submit.prevent="crearProgramacion">
          <div class="form-grid">
            <div class="form-group"><label class="form-label">Programa</label>
              <select v-model="nuevaProgramacion.programa_id" class="input-clinical" required>
                <option value="" disabled>Seleccione un programa</option>
                <option v-for="p in programas" :key="p.id" :value="p.id">{{ p.nombre }}</option>
              </select>
            </div>
            <div class="form-group"><label class="form-label">Tecnólogo</label>
              <select v-model="nuevaProgramacion.tecnologo_id" class="input-clinical" required>
                <option value="" disabled>Seleccione un tecnólogo</option>
                <option v-for="t in tecnologosDelPrograma" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
            <div class="form-group"><label class="form-label">Fecha</label><input v-model="nuevaProgramacion.fecha" type="date" class="input-clinical" required /></div>
            <div class="form-group"><label class="form-label">Turno</label>
              <select v-model="nuevaProgramacion.turno" class="input-clinical"><option value="MAÑANA">Mañana</option><option value="TARDE">Tarde</option><option value="NOCHE">Noche</option></select>
            </div>
            <div class="form-group"><label class="form-label">Hora inicio</label><input v-model="nuevaProgramacion.hora_inicio" type="time" class="input-clinical" required /></div>
            <div class="form-group"><label class="form-label">Hora fin</label><input v-model="nuevaProgramacion.hora_fin" type="time" class="input-clinical" required /></div>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy || !programas.length"><UIcon name="i-heroicons-check" class="w-4 h-4" />Crear</button></div>
          <p v-if="!programas.length" class="field-hint">Configure primero un programa en la pestaña Programas.</p>
        </form>
      </section>

      <section class="panel search-panel">
        <div class="search-grid"><div class="search-field"><label class="form-label">Fecha</label><input v-model="filtroFecha" type="date" class="input-clinical" @change="cargarProgramaciones" /></div></div>
      </section>

      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <template v-else>
        <section v-for="p in programaciones" :key="p.id" class="panel">
          <div class="card-header-row">
            <div>
              <strong>{{ p.programa_nombre }}</strong> — {{ p.tecnologo_nombre }} · {{ p.turno }} ({{ p.hora_inicio }}–{{ p.hora_fin }})
              <span class="field-hint">{{ p.cupos_usados }}/{{ p.cupos_totales }} cupos usados</span>
            </div>
            <span class="badge" :class="p.estado === 'activo' ? 'badge-ok' : 'badge-off'">{{ p.estado }}</span>
          </div>
          <form class="row-actions" style="margin-bottom:0.75rem" @submit.prevent="reservar(p)">
            <input v-model="reservaPorProg[p.id]" class="input-clinical input-sm" placeholder="ID de paciente" />
            <select v-model="horaPorProg[p.id]" class="input-clinical input-sm">
              <option v-for="s in slotsOf(p)" :key="s" :value="s">{{ s }}</option>
            </select>
            <button class="btn-secondary btn-sm" :disabled="busy || p.estado !== 'activo'" type="submit"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Reservar</button>
          </form>
          <table class="lab-table">
            <thead><tr><th>Hora</th><th>Paciente</th><th>Estado</th><th>EVA dolor</th><th></th></tr></thead>
            <tbody>
              <tr v-for="s in sesionesPorProgramacion[p.id] || []" :key="s.id">
                <td>{{ s.hora_inicio }}</td><td>{{ s.paciente_nombre }} ({{ s.paciente_dni }})</td>
                <td><span class="badge" :class="s.estado === 'atendida' ? 'badge-ok' : s.estado === 'programada' ? 'badge-pendiente' : 'badge-off'">{{ s.estado }}</span></td>
                <td>{{ s.escala_dolor_eva ?? '—' }}</td>
                <td v-if="s.estado === 'programada'">
                  <button class="btn-secondary btn-sm" :disabled="busy" @click="ejecutar(s, 'atendida')">Atendida</button>
                  <button class="btn-secondary btn-sm" :disabled="busy" @click="ejecutar(s, 'no_asistio')">No asistió</button>
                </td>
              </tr>
              <tr v-if="!(sesionesPorProgramacion[p.id] || []).length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Sin sesiones agendadas.</td></tr>
            </tbody>
          </table>
        </section>
        <p v-if="!programaciones.length" class="field-hint">Sin programaciones para esta fecha.</p>
      </template>
    </template>

    <!-- ═══════════ PROGRAMAS ═══════════ -->
    <template v-else-if="mode === 'programas'">
      <section class="panel">
        <div class="card-header-row"><h2 class="results-title">Nuevo programa</h2></div>
        <form class="editor-form" @submit.prevent="crearPrograma">
          <div class="form-grid">
            <div class="form-group"><label class="form-label">Nombre</label><input v-model="nuevoPrograma.nombre" class="input-clinical" placeholder="Fisioterapia, Terapia Ocupacional…" required /></div>
            <div class="form-group"><label class="form-label">Duración de sesión (min)</label><input v-model.number="nuevoPrograma.duracion_sesion_minutos" type="number" min="5" class="input-clinical" /></div>
            <div class="form-group full-width"><label class="form-label">Descripción</label><textarea v-model="nuevoPrograma.descripcion" class="input-clinical" rows="2"></textarea></div>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Crear programa</button></div>
        </form>
      </section>
      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ programas.length }} programas</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Nombre</th><th>Duración</th><th>Tecnólogos</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              <tr v-for="p in programas" :key="p.id">
                <td>{{ p.nombre }}</td><td>{{ p.duracion_sesion_minutos }} min</td>
                <td>{{ p.tecnologos.map((t:any) => t.nombre).join(', ') || '—' }}</td>
                <td><span class="badge" :class="p.is_active ? 'badge-ok' : 'badge-off'">{{ p.is_active ? 'Activo' : 'Inactivo' }}</span></td>
                <td><button class="btn-secondary btn-sm" :disabled="busy" @click="toggleActivo(p)">{{ p.is_active ? 'Desactivar' : 'Activar' }}</button></td>
              </tr>
              <tr v-if="!programas.length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Sin programas configurados.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <!-- ═══════════ TABLERO CONTROL ═══════════ -->
    <template v-else-if="mode === 'tablero-control'">
      <section class="panel search-panel">
        <div class="search-grid"><div class="search-field"><label class="form-label">Fecha</label><input v-model="filtroFecha" type="date" class="input-clinical" @change="cargarTablero" /></div></div>
      </section>
      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <template v-else-if="tablero">
        <section class="stats-row">
          <div class="stat-card"><div class="stat-icon" style="background:var(--teal-soft)"><UIcon name="i-heroicons-calendar" class="w-5 h-5" style="color:var(--teal)" /></div><div class="stat-body"><span class="stat-num">{{ tablero.total_cupos }}</span><span class="stat-label">Cupos totales</span></div></div>
          <div class="stat-card"><div class="stat-icon" style="background:var(--green-soft)"><UIcon name="i-heroicons-check-badge" class="w-5 h-5" style="color:var(--green)" /></div><div class="stat-body"><span class="stat-num">{{ tablero.total_usados }}</span><span class="stat-label">Cupos usados</span></div></div>
          <div v-for="(cnt, est) in tablero.por_estado_sesion" :key="est" class="stat-card"><div class="stat-icon" style="background:var(--mist)"><UIcon name="i-heroicons-tag" class="w-5 h-5" style="color:var(--ink-soft)" /></div><div class="stat-body"><span class="stat-num">{{ cnt }}</span><span class="stat-label">{{ est }}</span></div></div>
        </section>
        <section class="panel results-panel">
          <div class="results-header"><h2 class="results-title">Programaciones del día</h2></div>
          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th>Programa</th><th>Tecnólogo</th><th>Turno</th><th>Cupos</th><th>Estado</th></tr></thead>
              <tbody>
                <tr v-for="p in tablero.programaciones" :key="p.id">
                  <td>{{ p.programa_nombre }}</td><td>{{ p.tecnologo_nombre }}</td><td>{{ p.turno }} ({{ p.hora_inicio }}–{{ p.hora_fin }})</td>
                  <td>{{ p.cupos_usados }}/{{ p.cupos_totales }}</td>
                  <td><span class="badge" :class="p.estado === 'activo' ? 'badge-ok' : 'badge-off'">{{ p.estado }}</span></td>
                </tr>
                <tr v-if="!tablero.programaciones.length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Sin programaciones para esta fecha.</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </template>

    <!-- ═══════════ TECNÓLOGO POR PROGRAMA ═══════════ -->
    <template v-else-if="mode === 'tecnologo-por-programa'">
      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <section v-else v-for="p in programas" :key="p.id" class="panel">
        <div class="card-header-row"><h2 class="results-title">{{ p.nombre }}</h2></div>
        <div class="row-actions" style="margin-bottom:0.75rem">
          <select v-model="empleadoPorPrograma[p.id]" class="input-clinical input-sm">
            <option value="" disabled>Seleccione un empleado</option>
            <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre }}</option>
          </select>
          <button class="btn-secondary btn-sm" :disabled="busy || !empleadoPorPrograma[p.id]" @click="asignar(p)"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Asignar</button>
        </div>
        <table class="lab-table">
          <thead><tr><th>Tecnólogo</th><th></th></tr></thead>
          <tbody>
            <tr v-for="t in p.tecnologos" :key="t.id"><td>{{ t.nombre }}</td><td><button class="btn-secondary btn-sm" :disabled="busy" @click="desasignar(p, t)">Quitar</button></td></tr>
            <tr v-if="!p.tecnologos.length"><td colspan="2" style="text-align:center;color:var(--ink-soft)">Sin tecnólogos asignados.</td></tr>
          </tbody>
        </table>
      </section>
    </template>

    <!-- ═══════════ REPROGRAMACIONES BLOQUE ═══════════ -->
    <template v-else-if="mode === 'reprogramaciones-bloque'">
      <section class="panel">
        <div class="card-header-row"><h2 class="results-title">Reprogramar sesiones en bloque</h2></div>
        <form class="editor-form" @submit.prevent="reprogramarBloque">
          <div class="form-grid">
            <div class="form-group full-width"><label class="form-label">IDs de sesión a mover (separados por coma)</label><input v-model="bloque.sesion_ids" class="input-clinical" placeholder="uuid1, uuid2" required /></div>
            <div class="form-group full-width"><label class="form-label">ID de la programación destino</label><input v-model="bloque.programacion_mf_id" class="input-clinical" required /></div>
            <div class="form-group full-width"><label class="form-label">Mensaje (opcional)</label><input v-model="bloque.mensaje" class="input-clinical" /></div>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />Reprogramar</button></div>
        </form>
        <p class="field-hint" style="margin-top:0.75rem">Busque los IDs en Sesiones M. Física o Tablero de Control.</p>
      </section>
      <section v-if="resultadoBloque.length" class="panel results-panel">
        <div class="results-header"><h2 class="results-title">Sesiones reprogramadas</h2></div>
        <table class="lab-table">
          <thead><tr><th>Paciente</th><th>Nueva programación</th><th>Nueva hora</th></tr></thead>
          <tbody><tr v-for="s in resultadoBloque" :key="s.id"><td>{{ s.paciente_nombre }}</td><td>{{ s.programacion_mf_id }}</td><td>{{ s.hora_inicio }}</td></tr></tbody>
        </table>
      </section>
    </template>

    <!-- ═══════════ BLOQUEO DE PROGRAMACIÓN ═══════════ -->
    <template v-else-if="mode === 'bloqueo-programacion'">
      <section class="panel search-panel">
        <div class="search-grid"><div class="search-field"><label class="form-label">Fecha</label><input v-model="filtroFecha" type="date" class="input-clinical" @change="cargarProgramaciones" /></div></div>
      </section>
      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <section v-else class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ programaciones.length }} programaciones</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Programa</th><th>Tecnólogo</th><th>Turno</th><th>Estado</th><th>Motivo</th><th></th></tr></thead>
            <tbody>
              <tr v-for="p in programaciones" :key="p.id">
                <td>{{ p.programa_nombre }}</td><td>{{ p.tecnologo_nombre }}</td><td>{{ p.turno }} ({{ p.hora_inicio }}–{{ p.hora_fin }})</td>
                <td><span class="badge" :class="p.estado === 'activo' ? 'badge-ok' : 'badge-off'">{{ p.estado }}</span></td>
                <td>{{ p.motivo_bloqueo || '—' }}</td>
                <td>
                  <button v-if="p.estado === 'activo'" class="btn-secondary btn-sm" :disabled="busy" @click="bloquear(p)"><UIcon name="i-heroicons-lock-closed" class="w-4 h-4" />Bloquear</button>
                  <button v-if="p.estado === 'bloqueado'" class="btn-secondary btn-sm" :disabled="busy" @click="desbloquear(p)"><UIcon name="i-heroicons-lock-open" class="w-4 h-4" />Desbloquear</button>
                </td>
              </tr>
              <tr v-if="!programaciones.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">Sin programaciones para esta fecha.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'sesiones-m-fisica' | 'programas' | 'tablero-control' | 'tecnologo-por-programa' | 'reprogramaciones-bloque' | 'bloqueo-programacion'
const props = defineProps<{ mode: Mode }>()
const { api } = useApi()
const endpoint = '/app/medicina-fisica'

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)

function hoy() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date())
}
function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}

const titulo = computed(() => ({
  'sesiones-m-fisica': 'Sesiones M. Física',
  programas: 'Programas',
  'tablero-control': 'Tablero de Control',
  'tecnologo-por-programa': 'Tecnólogo por Programa',
  'reprogramaciones-bloque': 'Reprogramaciones en Bloque',
  'bloqueo-programacion': 'Bloqueo de Programación',
}[props.mode]))

const programas = ref<any[]>([])
const empleados = ref<any[]>([])
const filtroFecha = ref(hoy())

async function cargarProgramas() {
  programas.value = await api(endpoint + '/programas')
}
async function cargarEmpleados() {
  empleados.value = await api(endpoint + '/empleados')
}

// Sesiones M. Física
const programaciones = ref<any[]>([])
const sesionesPorProgramacion = reactive<Record<string, any[]>>({})
const nuevaProgramacion = reactive({ programa_id: '', tecnologo_id: '', fecha: hoy(), turno: 'MAÑANA', hora_inicio: '', hora_fin: '' })
const reservaPorProg = reactive<Record<string, string>>({})
const horaPorProg = reactive<Record<string, string>>({})

const tecnologosDelPrograma = computed(() => programas.value.find(p => p.id === nuevaProgramacion.programa_id)?.tecnologos || [])

function slotsOf(p: any): string[] {
  const slots: string[] = []
  let [h, m] = p.hora_inicio.split(':').map(Number)
  const [hf, mf] = p.hora_fin.split(':').map(Number)
  const fin = hf * 60 + mf
  while (h * 60 + m < fin) {
    slots.push(`${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}`)
    m += p.tiempo_sesion_minutos
    h += Math.floor(m / 60); m = m % 60
  }
  return slots
}

async function cargarProgramaciones() {
  loading.value = true; error.value = ''
  try {
    programaciones.value = await api(endpoint + '/programaciones', { query: { fecha: filtroFecha.value } })
    await Promise.all(programaciones.value.map(async (p: any) => {
      sesionesPorProgramacion[p.id] = await api(endpoint + '/sesiones-m-fisica', { query: { programacion_mf_id: p.id } })
      if (!horaPorProg[p.id]) horaPorProg[p.id] = slotsOf(p)[0] || ''
    }))
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function crearProgramacion() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/programaciones', { method: 'POST', body: nuevaProgramacion })
    notice.value = 'Programación creada.'
    Object.assign(nuevaProgramacion, { programa_id: '', tecnologo_id: '', fecha: hoy(), turno: 'MAÑANA', hora_inicio: '', hora_fin: '' })
    await cargarProgramaciones()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function reservar(p: any) {
  const patient_id = reservaPorProg[p.id]
  const hora_inicio = horaPorProg[p.id]
  if (!patient_id || !hora_inicio) return
  const slots = slotsOf(p)
  const idx = slots.indexOf(hora_inicio)
  const dur = p.tiempo_sesion_minutos
  let [h, m] = hora_inicio.split(':').map(Number)
  const total = h * 60 + m + dur
  const hora_fin = `${String(Math.floor(total / 60) % 24).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/sesiones-m-fisica', { method: 'POST', body: { programacion_mf_id: p.id, patient_id, hora_inicio, hora_fin } })
    notice.value = 'Sesión reservada.'
    reservaPorProg[p.id] = ''
    await cargarProgramaciones()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function ejecutar(s: any, estado: string) {
  let escala_dolor_eva, actividades_realizadas
  if (estado === 'atendida') {
    const evaStr = prompt('Escala de dolor EVA (0-10, opcional):')
    escala_dolor_eva = evaStr ? parseInt(evaStr) : undefined
    actividades_realizadas = prompt('Actividades realizadas (opcional):') || undefined
  }
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/sesiones-m-fisica/' + s.id + '/ejecutar', { method: 'POST', body: { estado, escala_dolor_eva, actividades_realizadas } })
    notice.value = 'Sesión actualizada.'
    await cargarProgramaciones()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

// Programas
const nuevoPrograma = reactive({ nombre: '', descripcion: '', duracion_sesion_minutos: 30 })
async function crearPrograma() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/programas', { method: 'POST', body: { ...nuevoPrograma, descripcion: nuevoPrograma.descripcion || undefined } })
    notice.value = 'Programa creado.'
    Object.assign(nuevoPrograma, { nombre: '', descripcion: '', duracion_sesion_minutos: 30 })
    await cargarProgramas()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}
async function toggleActivo(p: any) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/programas/' + p.id, { method: 'PATCH', body: { is_active: !p.is_active } })
    notice.value = 'Programa actualizado.'
    await cargarProgramas()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

// Tecnólogo por Programa
const empleadoPorPrograma = reactive<Record<string, string>>({})
async function asignar(p: any) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/programas/' + p.id + '/tecnologos', { method: 'POST', body: { empleado_id: empleadoPorPrograma[p.id] } })
    notice.value = 'Tecnólogo asignado.'
    empleadoPorPrograma[p.id] = ''
    await cargarProgramas()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}
async function desasignar(p: any, t: any) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/programas/' + p.id + '/tecnologos/' + t.id, { method: 'DELETE' })
    notice.value = 'Tecnólogo desasignado.'
    await cargarProgramas()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

// Tablero de Control
const tablero = ref<any>(null)
async function cargarTablero() {
  loading.value = true; error.value = ''
  try { tablero.value = await api(endpoint + '/tablero-control', { query: { fecha: filtroFecha.value } }) }
  catch (e) { error.value = err(e) } finally { loading.value = false }
}

// Reprogramaciones en Bloque
const bloque = reactive({ sesion_ids: '', programacion_mf_id: '', mensaje: '' })
const resultadoBloque = ref<any[]>([])
async function reprogramarBloque() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    const sesion_ids = bloque.sesion_ids.split(',').map(s => s.trim()).filter(Boolean)
    resultadoBloque.value = await api(endpoint + '/sesiones-m-fisica/acciones/reprogramar-bloque', {
      method: 'POST', body: { sesion_ids, programacion_mf_id: bloque.programacion_mf_id, mensaje: bloque.mensaje || undefined },
    })
    notice.value = `${resultadoBloque.value.length} sesión(es) reprogramada(s).`
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

// Bloqueo de Programación
async function bloquear(p: any) {
  const motivo = prompt('Motivo del bloqueo:')
  if (!motivo) return
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/programaciones/' + p.id + '/bloquear', { method: 'POST', body: { motivo } })
    notice.value = 'Programación bloqueada.'
    await cargarProgramaciones()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}
async function desbloquear(p: any) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/programaciones/' + p.id + '/desbloquear', { method: 'POST' })
    notice.value = 'Programación desbloqueada.'
    await cargarProgramaciones()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

onMounted(async () => {
  if (props.mode === 'sesiones-m-fisica') { await Promise.all([cargarProgramas(), cargarProgramaciones()]) }
  else if (props.mode === 'programas') await cargarProgramas()
  else if (props.mode === 'tablero-control') await cargarTablero()
  else if (props.mode === 'tecnologo-por-programa') { loading.value = true; await Promise.all([cargarProgramas(), cargarEmpleados()]); loading.value = false }
  else if (props.mode === 'bloqueo-programacion') await cargarProgramaciones()
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
.btn-secondary { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { padding: 0.375rem 0.625rem; font-size: 0.75rem; margin-left: 0.375rem; }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; flex-wrap: wrap; gap: 0.5rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; }
.search-field { display: flex; flex-direction: column; gap: 0.25rem; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.input-sm { width: auto; padding: 0.375rem 0.5rem; font-size: 0.75rem; display: inline-block; }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); white-space: nowrap; }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.row-actions { display: flex; align-items: center; gap: 0.375rem; flex-wrap: wrap; }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; white-space: nowrap; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-off { color: var(--ink-soft); background: var(--mist); }
.badge-pendiente { color: var(--amber); background: var(--amber-soft); }
.editor-form { display: flex; flex-direction: column; gap: 1rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }

.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { display: flex; align-items: center; gap: 1rem; padding: 1.125rem 1.25rem; border-radius: var(--radius-lg); border: 1px solid var(--line); background: var(--paper); box-shadow: var(--shadow-sm); }
.stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-body { display: flex; flex-direction: column; min-width: 0; }
.stat-num { font-size: 1.375rem; font-weight: 700; color: var(--ink); line-height: 1.2; }
.stat-label { font-size: 0.8125rem; color: var(--ink-soft); }

@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .form-grid, .search-grid { grid-template-columns: 1fr; }
}
</style>
