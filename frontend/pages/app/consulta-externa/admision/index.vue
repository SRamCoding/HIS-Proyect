<template>
  <div class="citas-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-calendar" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Agendamiento de Citas</h1>
          <p class="page-subtitle">Consulta Externa · Gestión de citas médicas</p>
        </div>
      </div>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Programaciones Activas -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--teal)">
        <div class="stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ programaciones.length }}</span>
          <span class="stat-label">Programaciones Activas</span>
        </div>
      </div>

      <!-- Total Cupos -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-list-bullet" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ totalCupos }}</span>
          <span class="stat-label">Total Cupos</span>
        </div>
      </div>

      <!-- Cupos Disponibles -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--blue-soft)">
        <div class="stat-icon" style="background: var(--blue-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--blue)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ cuposDisponibles }}</span>
          <span class="stat-label">Cupos Disponibles</span>
        </div>
      </div>

      <!-- Cupos Ocupados -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-clock" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ cuposOcupados }}</span>
          <span class="stat-label">Cupos Ocupados</span>
        </div>
      </div>
    </div>

    <!-- Filter Section -->
    <div class="filter-section">
      <div class="filter-card">
        <div class="filter-header">
          <UIcon name="i-heroicons-funnel" class="filter-header-icon" />
          <span class="filter-header-title">Filtros de Búsqueda</span>
        </div>
        <div class="filter-body">
          <div class="filter-group">
            <div class="filter-item">
              <label class="filter-label">Servicio</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-building-office-2" class="input-icon-small" />
                <select v-model="filtros.servicio_id" class="input-clinical-small" @change="cargarProgramaciones">
                  <option value="">Todos los servicios</option>
                  <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                </select>
              </div>
            </div>
            <div class="filter-item">
              <label class="filter-label">Especialidad</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-star" class="input-icon-small" />
                <select v-model="filtros.especialidad_id" class="input-clinical-small" @change="cargarProgramaciones">
                  <option value="">Todas las especialidades</option>
                  <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
                </select>
              </div>
            </div>
            <div class="filter-item">
              <label class="filter-label">Fecha</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-calendar" class="input-icon-small" />
                <input v-model="filtros.fecha" type="date" class="input-clinical-small" @change="cargarProgramaciones" />
              </div>
            </div>
            <button class="btn-clear-filter" @click="limpiarFiltros">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
              Limpiar filtros
            </button>
          </div>
          <div class="filter-result">
            <span class="result-count">{{ programaciones.length }} programaciones</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Main Grid -->
    <div class="citas-grid">
      <!-- Programaciones -->
      <div class="programaciones-card">
        <div class="card-header-simple">
          <h3 class="card-title-simple">Consultorios / Programaciones</h3>
          <span class="card-badge">{{ programaciones.length }} activas</span>
        </div>

        <div v-if="cargandoProg" class="loading-state-small">
          <div class="loading-spinner-small">
            <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando programaciones...</p>
        </div>

        <div v-else-if="!programaciones.length" class="empty-state-small">
          <UIcon name="i-heroicons-calendar-days" class="w-10 h-10" style="color: var(--ink-soft)" />
          <span>No hay programaciones para estos filtros</span>
        </div>

        <div v-else class="programaciones-list">
          <button
            v-for="p in programaciones"
            :key="p.id"
            class="programacion-item"
            :class="{ 'programacion-item--selected': progSeleccionada?.id === p.id }"
            @click="seleccionarProgramacion(p)"
          >
            <div class="programacion-header">
              <span class="programacion-titulo">{{ p.servicio_nombre || p.especialidad_nombre || 'Sin servicio' }}</span>
              <span class="programacion-estado" :class="p.estado === 'activo' ? 'estado-activo' : 'estado-inactivo'">
                {{ p.estado === 'activo' ? 'Activa' : 'Inactiva' }}
              </span>
            </div>
            <div class="programacion-medico">
              <UIcon name="i-heroicons-user" class="w-3.5 h-3.5" />
              {{ p.medico_nombre }}
            </div>
            <div class="programacion-horario">
              <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
              {{ p.hora_inicio }} - {{ p.hora_fin }} · {{ p.turno }}
            </div>
            <div v-if="p.descripcion" class="programacion-obs">
              <UIcon name="i-heroicons-document-text" class="w-3.5 h-3.5" />
              {{ p.descripcion }}
            </div>
          </button>
        </div>
      </div>

      <!-- Cupos -->
      <div class="cupos-card">
        <div class="card-header-simple">
          <h3 class="card-title-simple">
            Cupos
            <span v-if="progSeleccionada" class="cupos-fecha">{{ formatFecha(progSeleccionada.fecha) }}</span>
          </h3>
          <span v-if="progSeleccionada" class="card-badge">
            {{ cuposDisponibles }} disponibles · {{ cuposOcupados }} ocupados
          </span>
        </div>

        <div v-if="!progSeleccionada" class="empty-state-small">
          <UIcon name="i-heroicons-hand-raised" class="w-10 h-10" style="color: var(--ink-soft)" />
          <span>Selecciona una programación para ver sus cupos</span>
        </div>

        <div v-else-if="cargandoCupos" class="loading-state-small">
          <div class="loading-spinner-small">
            <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando cupos...</p>
        </div>

        <div v-else-if="!cupos.length" class="empty-state-small">
          <UIcon name="i-heroicons-clock" class="w-10 h-10" style="color: var(--ink-soft)" />
          <span>No hay cupos disponibles para esta programación</span>
        </div>

        <div v-else class="cupos-list">
          <div
            v-for="(c, idx) in cupos"
            :key="c.hora_inicio"
            class="cupo-item"
            :class="c.disponible ? 'cupo-disponible' : 'cupo-ocupado'"
          >
            <div class="cupo-info">
              <span class="cupo-numero">{{ idx + 1 }}</span>
              <span class="cupo-horario font-mono-data">{{ c.hora_inicio }} - {{ c.hora_fin }}</span>
              <span v-if="!c.disponible" class="cupo-paciente">
                <UIcon name="i-heroicons-user" class="w-3.5 h-3.5" />
                {{ c.paciente_nombre }}
              </span>
            </div>
            <button
              v-if="c.disponible"
              class="btn-citar"
              @click="abrirCitarPaciente(c)"
            >
              <UIcon name="i-heroicons-plus" class="w-3.5 h-3.5" />
              Citar
            </button>
            <button
              v-else
              class="btn-ver-cita"
              @click="verCita(c.cita_id)"
            >
              <UIcon name="i-heroicons-eye" class="w-3.5 h-3.5" />
              Ver Cita
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Modal Citar Paciente -->
    <div v-if="mostrarModal" class="modal-overlay" @click.self="mostrarModal = false">
      <div class="modal-content modal-lg" style="background: var(--paper); border-radius: var(--radius-lg)">
        <div class="modal-header">
          <div class="modal-icon" style="background: var(--amber-soft)">
            <UIcon name="i-heroicons-user-plus" class="w-6 h-6" style="color: var(--amber)" />
          </div>
          <div>
            <h3 class="modal-title">Citar Paciente</h3>
            <p class="modal-subtitle">Registra una nueva cita para el paciente</p>
          </div>
          <button class="modal-close" @click="cerrarModal">
            <UIcon name="i-heroicons-x-mark" class="w-5 h-5" style="color: var(--ink-soft)" />
          </button>
        </div>

        <div class="modal-tabs">
          <button
            class="modal-tab"
            :class="{ 'modal-tab--active': tabModal === 'paciente' }"
            @click="tabModal = 'paciente'"
          >
            <UIcon name="i-heroicons-user" class="w-4 h-4" />
            Datos del Paciente
          </button>
          <button
            class="modal-tab"
            :class="{ 'modal-tab--active': tabModal === 'cita' }"
            @click="tabModal = 'cita'"
          >
            <UIcon name="i-heroicons-document-text" class="w-4 h-4" />
            Datos de la Cita
          </button>
        </div>

        <div class="modal-body">
          <!-- Error Modal -->
          <div v-if="errorModal" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ errorModal }}
          </div>

          <!-- Tab Paciente -->
          <div v-show="tabModal === 'paciente'">
            <div class="search-paciente">
              <div class="input-wrapper">
                <UIcon name="i-heroicons-magnifying-glass" class="input-icon" />
                <input
                  v-model="dniBusqueda"
                  type="text"
                  placeholder="Buscar por DNI..."
                  class="input-clinical"
                  @keyup.enter="buscarPaciente"
                />
              </div>
              <button
                class="btn-search"
                :disabled="buscandoPaciente"
                @click="buscarPaciente"
              >
                <UIcon v-if="buscandoPaciente" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-magnifying-glass" class="w-4 h-4" />
                {{ buscandoPaciente ? 'Buscando...' : 'Buscar' }}
              </button>
            </div>

            <!-- Paciente Seleccionado -->
            <div v-if="pacienteSeleccionado" class="paciente-seleccionado">
              <div class="paciente-avatar" :style="{ background: getPatientColor(pacienteSeleccionado.full_name) }">
                <span>{{ getInitials(pacienteSeleccionado.full_name) }}</span>
              </div>
              <div class="paciente-info">
                <span class="paciente-nombre">{{ pacienteSeleccionado.full_name }}</span>
                <span class="paciente-dni">DNI: {{ pacienteSeleccionado.dni || 'NN' }}</span>
                <span class="paciente-hc">HC: {{ pacienteSeleccionado.record_number || '—' }}</span>
              </div>
              <button class="paciente-remover" @click="pacienteSeleccionado = null">
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
              </button>
            </div>

            <!-- Creación Rápida -->
            <div v-else-if="mostrarCreacionRapida" class="creacion-rapida">
              <p class="creacion-rapida-title">
                <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" style="color: var(--amber)" />
                No se encontró el paciente. Regístralo rápidamente:
              </p>
              <div class="creacion-rapida-grid">
                <div class="form-group">
                  <label class="form-label">Primer Nombre <span class="required">*</span></label>
                  <input v-model="nuevoPaciente.first_name" class="input-clinical" placeholder="Primer Nombre" />
                </div>
                <div class="form-group">
                  <label class="form-label">Apellido Paterno <span class="required">*</span></label>
                  <input v-model="nuevoPaciente.last_name_paterno" class="input-clinical" placeholder="Ap. Paterno" />
                </div>
                <div class="form-group">
                  <label class="form-label">Apellido Materno <span class="required">*</span></label>
                  <input v-model="nuevoPaciente.last_name_materno" class="input-clinical" placeholder="Ap. Materno" />
                </div>
                <div class="form-group">
                  <label class="form-label">Fecha Nacimiento <span class="required">*</span></label>
                  <input v-model="nuevoPaciente.birth_date" type="date" class="input-clinical" />
                </div>
                <div class="form-group">
                  <label class="form-label">Sexo <span class="required">*</span></label>
                  <select v-model="nuevoPaciente.gender" class="input-clinical">
                    <option value="">Sexo...</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                </div>
              </div>
              <button
                class="btn-crear-paciente"
                :disabled="creandoPaciente"
                @click="crearPacienteRapido"
              >
                <UIcon v-if="creandoPaciente" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-plus" class="w-4 h-4" />
                {{ creandoPaciente ? 'Registrando...' : 'Registrar y usar este paciente' }}
              </button>
            </div>

            <div v-else class="empty-paciente">
              <UIcon name="i-heroicons-user" class="w-12 h-12" style="color: var(--ink-soft)" />
              <span>Busca un paciente por DNI para continuar</span>
            </div>
          </div>

          <!-- Tab Cita -->
          <div v-show="tabModal === 'cita'" v-if="cupoSeleccionado">
            <div class="cita-resumen">
              <div class="cita-resumen-item">
                <span class="cita-resumen-label">Servicio</span>
                <span class="cita-resumen-value">{{ progSeleccionada?.servicio_nombre || '—' }}</span>
              </div>
              <div class="cita-resumen-item">
                <span class="cita-resumen-label">Especialidad</span>
                <span class="cita-resumen-value">{{ progSeleccionada?.especialidad_nombre || '—' }}</span>
              </div>
              <div class="cita-resumen-item">
                <span class="cita-resumen-label">Médico</span>
                <span class="cita-resumen-value">{{ progSeleccionada?.medico_nombre }}</span>
              </div>
              <div class="cita-resumen-item">
                <span class="cita-resumen-label">Fecha/Hora</span>
                <span class="cita-resumen-value font-mono-data">{{ formatFecha(progSeleccionada?.fecha) }} {{ cupoSeleccionado.hora_inicio }}</span>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group full-width">
                <label class="form-label">Tipo de Consulta</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" />
                  <input v-model="formCita.tipo_consulta" class="input-clinical" placeholder="Ej: Primera vez, Control, Emergencia" />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Observación</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea v-model="formCita.observacion" class="input-clinical" rows="2" placeholder="Observaciones adicionales..." />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Fuente Financiamiento</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-currency-dollar" class="input-icon" />
                  <input v-model="formCita.fuente_financiamiento" class="input-clinical" placeholder="SIS, EsSalud, Particular..." />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Producto/Plan</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document" class="input-icon" />
                  <input v-model="formCita.producto_plan" class="input-clinical" placeholder="Plan de salud" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="cerrarModal">Cancelar</button>
          <button
            class="btn-primary"
            :disabled="!pacienteSeleccionado || guardandoCita"
            @click="guardarCita"
          >
            <UIcon v-if="guardandoCita" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
            {{ guardandoCita ? 'Guardando...' : 'Guardar Cita' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()
const { link } = useHospitalNav()

const servicios = ref<any[]>([])
const especialidades = ref<any[]>([])
const programaciones = ref<any[]>([])
const progSeleccionada = ref<any>(null)
const cupos = ref<any[]>([])
const cargandoProg = ref(false)
const cargandoCupos = ref(false)
const error = ref('')

const filtros = reactive({
  servicio_id: '',
  especialidad_id: '',
  fecha: new Date().toISOString().slice(0, 10),
})

const totalCupos = computed(() => cupos.value.length)
const cuposDisponibles = computed(() => cupos.value.filter(c => c.disponible).length)
const cuposOcupados = computed(() => cupos.value.filter(c => !c.disponible).length)

// Modal
const mostrarModal = ref(false)
const tabModal = ref<'paciente' | 'cita'>('paciente')
const cupoSeleccionado = ref<any>(null)
const errorModal = ref('')
const guardandoCita = ref(false)

const dniBusqueda = ref('')
const buscandoPaciente = ref(false)
const pacienteSeleccionado = ref<any>(null)
const mostrarCreacionRapida = ref(false)
const creandoPaciente = ref(false)

const nuevoPaciente = reactive({
  first_name: '',
  last_name_paterno: '',
  last_name_materno: '',
  birth_date: '',
  gender: '',
})

const formCita = reactive({
  tipo_consulta: '',
  observacion: '',
  fuente_financiamiento: '',
  producto_plan: '',
})

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
  const colors = [
    'var(--teal-soft)',
    'var(--purple-soft)',
    'var(--navy-soft)',
    'var(--amber-soft)',
    'var(--green-soft)',
    'var(--pink-soft)',
    'var(--blue-soft)',
    'var(--orange-soft)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const formatFecha = (fecha: string) => {
  if (!fecha) return '—'
  const d = new Date(fecha)
  return d.toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const limpiarFiltros = () => {
  filtros.servicio_id = ''
  filtros.especialidad_id = ''
  filtros.fecha = new Date().toISOString().slice(0, 10)
  cargarProgramaciones()
}

const cargarProgramaciones = async () => {
  cargandoProg.value = true
  error.value = ''
  progSeleccionada.value = null
  cupos.value = []
  try {
    const params = new URLSearchParams()
    if (filtros.servicio_id) params.set('servicio_id', filtros.servicio_id)
    if (filtros.especialidad_id) params.set('especialidad_id', filtros.especialidad_id)
    if (filtros.fecha) params.set('fecha', filtros.fecha)
    programaciones.value = await api(`/app/consulta-externa/programacion-medica?${params}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar programaciones'
  } finally {
    cargandoProg.value = false
  }
}

const seleccionarProgramacion = async (p: any) => {
  progSeleccionada.value = p
  cargandoCupos.value = true
  try {
    cupos.value = await api(`/app/consulta-externa/citas/cupos/${p.id}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar cupos'
  } finally {
    cargandoCupos.value = false
  }
}

const abrirCitarPaciente = (cupo: any) => {
  cupoSeleccionado.value = cupo
  mostrarModal.value = true
  tabModal.value = 'paciente'
  pacienteSeleccionado.value = null
  mostrarCreacionRapida.value = false
  dniBusqueda.value = ''
  errorModal.value = ''
  formCita.tipo_consulta = ''
  formCita.observacion = ''
  formCita.fuente_financiamiento = ''
  formCita.producto_plan = ''
}

const cerrarModal = () => {
  mostrarModal.value = false
}

const buscarPaciente = async () => {
  if (!dniBusqueda.value) return
  buscandoPaciente.value = true
  errorModal.value = ''
  mostrarCreacionRapida.value = false
  try {
    pacienteSeleccionado.value = await api(`/app/gestion-pacientes/dni/${dniBusqueda.value}`)
  } catch (e: any) {
    if (e?.status === 404) {
      mostrarCreacionRapida.value = true
    } else {
      errorModal.value = e?.data?.detail || 'Error al buscar paciente'
    }
  } finally {
    buscandoPaciente.value = false
  }
}

const crearPacienteRapido = async () => {
  if (!nuevoPaciente.first_name || !nuevoPaciente.last_name_paterno ||
      !nuevoPaciente.last_name_materno || !nuevoPaciente.birth_date || !nuevoPaciente.gender) {
    errorModal.value = 'Completa todos los campos del registro rápido'
    return
  }
  creandoPaciente.value = true
  errorModal.value = ''
  try {
    pacienteSeleccionado.value = await api('/app/gestion-pacientes/', {
      method: 'POST',
      body: {
        ...nuevoPaciente,
        dni: dniBusqueda.value,
        full_name: `${nuevoPaciente.first_name} ${nuevoPaciente.last_name_paterno} ${nuevoPaciente.last_name_materno}`.trim(),
      },
    })
    mostrarCreacionRapida.value = false
  } catch (e: any) {
    errorModal.value = e?.data?.detail || 'Error al registrar paciente'
  } finally {
    creandoPaciente.value = false
  }
}

const guardarCita = async () => {
  if (!pacienteSeleccionado.value || !cupoSeleccionado.value || !progSeleccionada.value) return
  guardandoCita.value = true
  errorModal.value = ''
  try {
    await api('/app/consulta-externa/citas', {
      method: 'POST',
      body: {
        programacion_medica_id: progSeleccionada.value.id,
        patient_id: pacienteSeleccionado.value.id,
        hora_inicio: cupoSeleccionado.value.hora_inicio,
        hora_fin: cupoSeleccionado.value.hora_fin,
        ...formCita,
      },
    })
    mostrarModal.value = false
    await seleccionarProgramacion(progSeleccionada.value)
  } catch (e: any) {
    errorModal.value = e?.data?.detail || 'Error al guardar la cita'
  } finally {
    guardandoCita.value = false
  }
}

const verCita = (citaId: string) => {
  navigateTo(link(`/app/consulta-externa/admision/${citaId}`))
}

onMounted(async () => {
  try {
    servicios.value = await api('/app/consulta-externa/programacion-medica/servicios')
    especialidades.value = await api('/app/consulta-externa/programacion-medica/especialidades')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar catálogos'
  }
  await cargarProgramaciones()
})
</script>

<style scoped>
.citas-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
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

/* Widgets Grid */
.widgets-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-widget {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.stat-widget:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Filter Section */
.filter-section {
  margin-bottom: 1.5rem;
}

.filter-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.filter-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1.25rem;
  background: var(--mist);
  border-bottom: 1px solid var(--line);
}

.filter-header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: var(--ink-soft);
}

.filter-header-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.filter-body {
  padding: 1.25rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  flex: 1;
}

.filter-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  white-space: nowrap;
}

.input-wrapper-small {
  position: relative;
  min-width: 180px;
}

.input-icon-small {
  position: absolute;
  left: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  width: 0.875rem;
  height: 0.875rem;
  color: var(--ink-soft);
}

.input-clinical-small {
  width: 100%;
  padding: 0.375rem 0.625rem 0.375rem 2rem;
  border-radius: 6px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.8125rem;
  transition: all 0.2s ease;
}

.input-clinical-small:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.input-clinical-small[type="date"] {
  color-scheme: light;
}

.btn-clear-filter {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear-filter:hover {
  background: var(--mist);
}

.filter-result {
  display: flex;
  align-items: center;
}

.result-count {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Error Banner */
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

/* Citas Grid */
.citas-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.programaciones-card,
.cupos-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.25rem 1.5rem;
  box-shadow: var(--shadow-sm);
}

.card-header-simple {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.card-title-simple {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-badge {
  font-size: 0.625rem;
  font-weight: 500;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  background: var(--green-soft);
  color: var(--green);
}

.cupos-fecha {
  font-weight: 400;
  color: var(--ink-soft);
  font-size: 0.75rem;
}

/* Loading State Small */
.loading-state-small {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  gap: 0.75rem;
}

.loading-spinner-small {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Empty State Small */
.empty-state-small {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  gap: 0.5rem;
  color: var(--ink-soft);
  font-size: 0.875rem;
}

.empty-state-small .w-10 {
  opacity: 0.5;
}

/* Programaciones List */
.programaciones-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 500px;
  overflow-y: auto;
}

.programacion-item {
  text-align: left;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: var(--paper);
  cursor: pointer;
  transition: all 0.15s ease;
}

.programacion-item:hover {
  background: var(--mist);
}

.programacion-item--selected {
  border-color: var(--teal);
  background: var(--teal-soft);
  box-shadow: 0 0 0 2px var(--teal-soft);
}

.programacion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.25rem;
}

.programacion-titulo {
  font-weight: 500;
  color: var(--ink);
}

.programacion-estado {
  font-size: 0.625rem;
  font-weight: 600;
  padding: 0.0625rem 0.375rem;
  border-radius: 10px;
}

.estado-activo {
  background: var(--green-soft);
  color: var(--green);
}

.estado-inactivo {
  background: var(--mist);
  color: var(--ink-soft);
}

.programacion-medico,
.programacion-horario,
.programacion-obs {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin-top: 0.125rem;
}

.programacion-obs {
  color: var(--ink-soft);
  font-style: italic;
}

/* Cupos List */
.cupos-list {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  max-height: 500px;
  overflow-y: auto;
}

.cupo-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  transition: all 0.15s ease;
}

.cupo-disponible {
  background: var(--paper);
}

.cupo-disponible:hover {
  background: var(--mist);
}

.cupo-ocupado {
  background: var(--mist);
  opacity: 0.7;
}

.cupo-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.cupo-numero {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.625rem;
  font-weight: 700;
  background: var(--mist);
  color: var(--ink-soft);
}

.cupo-horario {
  font-size: 0.8125rem;
  color: var(--ink);
}

.cupo-paciente {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.btn-citar {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-citar:hover {
  background: var(--teal-dark);
}

.btn-ver-cita {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 6px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-ver-cita:hover {
  background: var(--mist);
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  max-width: 680px;
  width: 100%;
  max-height: 90vh;
  overflow-y: auto;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.modal-lg {
  max-width: 680px;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  position: relative;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

.modal-close {
  position: absolute;
  top: -0.25rem;
  right: -0.25rem;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--mist);
}

.modal-tabs {
  display: flex;
  gap: 0.25rem;
  border-bottom: 1px solid var(--line);
  margin-bottom: 1.25rem;
}

.modal-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink-soft);
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s ease;
}

.modal-tab:hover {
  color: var(--ink);
}

.modal-tab--active {
  color: var(--teal);
  border-bottom-color: var(--teal);
}

.modal-body {
  margin-bottom: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

/* Search Paciente */
.search-paciente {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.search-paciente .input-wrapper {
  flex: 1;
}

.btn-search {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-search:hover:not(:disabled) {
  background: var(--teal-dark);
}

.btn-search:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Paciente Seleccionado */
.paciente-seleccionado {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  background: var(--green-soft);
  border: 1px solid var(--green-soft);
}

.paciente-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.paciente-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.paciente-nombre {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.paciente-dni,
.paciente-hc {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.paciente-remover {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--alert);
  cursor: pointer;
  transition: all 0.2s ease;
}

.paciente-remover:hover {
  background: var(--alert-soft);
}

/* Creación Rápida */
.creacion-rapida {
  padding: 1rem;
  border-radius: var(--radius);
  border: 1px solid var(--amber-soft);
  background: var(--amber-soft);
}

.creacion-rapida-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--amber);
  margin-bottom: 0.75rem;
}

.creacion-rapida-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
}

.creacion-rapida-grid .form-group {
  margin-bottom: 0.5rem;
}

.btn-crear-paciente {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  margin-top: 0.5rem;
}

.btn-crear-paciente:hover:not(:disabled) {
  background: var(--teal-dark);
}

.btn-crear-paciente:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Empty Paciente */
.empty-paciente {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  gap: 0.5rem;
  color: var(--ink-soft);
}

/* Cita Resumen */
.cita-resumen {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  background: var(--mist);
  margin-bottom: 1rem;
}

.cita-resumen-item {
  display: flex;
  flex-direction: column;
}

.cita-resumen-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
}

.cita-resumen-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
}

/* Form en modal */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  margin-bottom: 0.5rem;
}

.required {
  color: var(--alert);
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
  padding: 0.625rem 0.875rem;
  padding-left: 2.5rem;
  border-radius: 8px;
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

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .citas-container {
    padding: 1rem 1.5rem;
  }

  .citas-grid {
    grid-template-columns: 1fr;
  }

  .filter-body {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-group {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-item {
    flex-direction: column;
    align-items: stretch;
  }

  .input-wrapper-small {
    min-width: auto;
  }

  .filter-result {
    justify-content: flex-end;
  }
}

@media (max-width: 768px) {
  .citas-container {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .widgets-grid {
    grid-template-columns: 1fr 1fr;
  }

  .creacion-rapida-grid {
    grid-template-columns: 1fr;
  }

  .cita-resumen {
    grid-template-columns: 1fr;
  }

  .modal-content {
    margin: 1rem;
    max-height: 95vh;
  }

  .modal-tabs {
    flex-direction: column;
    gap: 0.25rem;
  }

  .modal-tab {
    border-bottom: 1px solid var(--line);
  }

  .modal-tab--active {
    border-bottom-color: var(--teal);
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .search-paciente {
    flex-direction: column;
  }

  .btn-search {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .widgets-grid {
    grid-template-columns: 1fr;
  }

  .cupo-item {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .cupo-info {
    flex-wrap: wrap;
  }

  .btn-citar,
  .btn-ver-cita {
    width: 100%;
    justify-content: center;
  }
}
</style>