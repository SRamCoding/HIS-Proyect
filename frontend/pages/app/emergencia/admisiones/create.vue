<template>
  <div class="emergencia-create-container">
    <div class="emergencia-create-grid">
      <!-- Main Content -->
      <div class="emergencia-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="link('/app/emergencia/admisiones')" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-heart" class="w-3.5 h-3.5" />
              Admisiones
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nueva Admisión</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--alert-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--alert)" />
            </div>
            <div>
              <h1 class="page-title">Registrar Admisión de Emergencia</h1>
              <p class="page-subtitle">Ingresa los datos de la admisión de emergencia</p>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="error-banner">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
          {{ error }}
        </div>

        <!-- Form Card -->
        <section class="form-card">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--alert-soft)">
              <UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--alert)" />
            </div>
            <div>
              <h3 class="card-title">Paciente</h3>
              <p class="card-subtitle">Busca o registra al paciente para la admisión</p>
            </div>
          </div>

          <!-- Buscar Paciente -->
          <div v-if="!pacienteSeleccionado" class="buscar-paciente">
            <div class="buscar-input-group">
              <div class="input-wrapper">
                <UIcon name="i-heroicons-identification" class="input-icon" />
                <input
                  v-model="dniBusqueda"
                  type="text"
                  placeholder="DNI del paciente..."
                  class="input-clinical"
                  maxlength="8"
                  @keyup.enter="buscarPaciente"
                />
              </div>
              <button
                class="btn-search"
                :disabled="buscando || !dniBusqueda"
                @click="buscarPaciente"
              >
                <UIcon v-if="buscando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-magnifying-glass" class="w-4 h-4" />
                {{ buscando ? 'Buscando...' : 'Buscar' }}
              </button>
            </div>
            <p class="field-hint">Ingresa el DNI del paciente para buscar en el sistema</p>
          </div>

          <!-- Paciente Seleccionado -->
          <div v-else class="paciente-seleccionado">
            <div class="paciente-info">
              <div class="paciente-avatar" :style="{ background: getColorPaciente(pacienteSeleccionado.full_name) }">
                <span>{{ getInitials(pacienteSeleccionado.full_name) }}</span>
              </div>
              <div class="paciente-datos">
                <span class="paciente-nombre">{{ pacienteSeleccionado.full_name }}</span>
                <span class="paciente-dni">DNI: {{ pacienteSeleccionado.dni || 'NN' }}</span>
              </div>
            </div>
            <button class="btn-remove-paciente" @click="pacienteSeleccionado = null">
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
              Quitar
            </button>
          </div>

          <!-- Creación Rápida -->
          <div v-if="mostrarCreacionRapida" class="creacion-rapida">
            <div class="creacion-header">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" style="color: var(--amber)" />
              <span style="color: var(--amber); font-weight: 500;">No se encontró el paciente. Regístralo rápido:</span>
            </div>
            <div class="creacion-grid">
              <div class="form-group">
                <label class="form-label">Primer Nombre <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <input v-model="nuevoPaciente.first_name" type="text" class="input-clinical" placeholder="Juan" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Apellido Paterno <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <input v-model="nuevoPaciente.last_name_paterno" type="text" class="input-clinical" placeholder="Pérez" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Apellido Materno</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <input v-model="nuevoPaciente.last_name_materno" type="text" class="input-clinical" placeholder="Gómez" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Fecha de Nacimiento <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-calendar" class="input-icon" />
                  <input v-model="nuevoPaciente.birth_date" type="date" class="input-clinical" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Sexo <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-arrows-right-left" class="input-icon" />
                  <select v-model="nuevoPaciente.gender" class="input-clinical">
                    <option value="">Seleccione</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <div class="checkbox-wrapper">
                  <input type="checkbox" v-model="nuevoPaciente.is_nn" id="is_nn" class="checkbox-custom" />
                  <label for="is_nn" class="checkbox-label">No Identificado (NN)</label>
                </div>
              </div>
            </div>
            <button class="btn-registrar-paciente" :disabled="creandoPaciente" @click="crearPacienteRapido">
              <UIcon v-if="creandoPaciente" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
              {{ creandoPaciente ? 'Registrando...' : 'Registrar y usar' }}
            </button>
          </div>
        </section>

        <!-- Datos de la Admisión -->
        <section v-if="pacienteSeleccionado" class="form-card">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: var(--teal)" />
            </div>
            <div>
              <h3 class="card-title">Datos de la Admisión</h3>
              <p class="card-subtitle">Completa la información de la admisión de emergencia</p>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Servicio de Emergencia <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                <select v-model="form.servicio_emergencia" class="input-clinical">
                  <option value="Emergencia General">Emergencia General</option>
                  <option value="Gineco-Obstetricia">Gineco-Obstetricia</option>
                  <option value="Pediatria">Pediatría</option>
                  <option value="Traumatologia">Traumatología</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Fuente de Financiamiento</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-currency-dollar" class="input-icon" />
                <input v-model="form.fuente_financiamiento" type="text" class="input-clinical" placeholder="SIS, Particular..." />
              </div>
            </div>
          </div>

          <!-- Acompañante -->
          <div class="info-section">
            <h4 class="section-title">Acompañante</h4>
            <div class="form-grid">
              <div class="form-group full-width">
                <label class="form-label">Nombre y Apellidos</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <input v-model="form.acompanante_nombre" type="text" class="input-clinical" placeholder="Nombre completo del acompañante" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Documento</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-identification" class="input-icon" />
                  <input v-model="form.acompanante_documento" type="text" class="input-clinical" placeholder="DNI" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Parentesco</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-heart" class="input-icon" />
                  <input v-model="form.acompanante_parentesco" type="text" class="input-clinical" placeholder="Familiar" />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Teléfono</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-phone" class="input-icon" />
                  <input v-model="form.acompanante_telefono" type="text" class="input-clinical" placeholder="+51 987654321" />
                </div>
              </div>
              <div class="form-group full-width">
                <label class="form-label">Dirección</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-home" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <input v-model="form.acompanante_direccion" type="text" class="input-clinical" placeholder="Dirección del acompañante" />
                </div>
              </div>
            </div>
          </div>

          <!-- Observaciones -->
          <div class="info-section">
            <h4 class="section-title">Observaciones</h4>
            <div class="form-grid">
              <div class="form-group full-width">
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea v-model="form.observaciones" class="input-clinical" rows="2" placeholder="Observaciones adicionales..." />
                </div>
              </div>
            </div>
          </div>

          <!-- Actions -->
          <div class="form-actions">
            <div class="action-group">
              <button class="btn-primary" style="background: var(--alert)" :disabled="guardando" @click="registrarAdmision">
                <UIcon v-if="guardando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                {{ guardando ? 'Registrando...' : 'Registrar Admisión' }}
              </button>
              <NuxtLink :to="link('/app/emergencia/admisiones')" class="btn-cancel">
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="emergencia-create-sidebar">
        <!-- Info Widget -->
        <div class="widget widget-info">
          <div class="widget-header">
            <UIcon name="i-heroicons-information-circle" class="widget-icon" style="color: var(--alert)" />
            <h4 class="widget-title">Información</h4>
          </div>
          <div class="widget-content">
            <ul class="info-list">
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--alert)" />
                <span>Busca al paciente por su DNI en el sistema</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--alert)" />
                <span>Si no existe, regístralo rápidamente</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--alert)" />
                <span>La admisión crea un triaje automáticamente</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--alert)" />
                <span>Los datos del acompañante son opcionales</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Resumen Paciente -->
        <div v-if="pacienteSeleccionado" class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-user" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Paciente</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Nombre</span>
              <span class="summary-value">{{ pacienteSeleccionado.full_name || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">DNI</span>
              <span class="summary-value font-mono-data">{{ pacienteSeleccionado.dni || 'NN' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">HC</span>
              <span class="summary-value font-mono-data">{{ pacienteSeleccionado.historia_clinica || '—' }}</span>
            </div>
          </div>
        </div>

        <!-- Tip Widget -->
        <div class="widget widget-tip">
          <div class="widget-content">
            <div class="tip-content">
              <UIcon name="i-heroicons-light-bulb" class="tip-icon" style="color: var(--amber)" />
              <div>
                <p class="tip-title">Consejo</p>
                <p class="tip-text">
                  Verifica los datos del paciente antes de registrar la admisión. 
                  Un triaje completo es esencial para una atención oportuna.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats Widget -->
        <div class="widget widget-quick-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--navy)" />
            <h4 class="widget-title">Estado del Formulario</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Paciente</span>
              <span class="stat-number" :style="{ color: pacienteSeleccionado ? 'var(--green)' : 'var(--ink-soft)' }">
                {{ pacienteSeleccionado ? '✓' : '—' }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Servicio</span>
              <span class="stat-number" :style="{ color: form.servicio_emergencia ? 'var(--teal)' : 'var(--ink-soft)' }">
                {{ form.servicio_emergencia ? '✓' : '—' }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Acompañante</span>
              <span class="stat-number" :style="{ color: form.acompanante_nombre ? 'var(--teal)' : 'var(--ink-soft)' }">
                {{ form.acompanante_nombre ? '✓' : '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })

const { api } = useApi()
const { link } = useHospitalNav()

const dniBusqueda = ref('')
const buscando = ref(false)
const pacienteSeleccionado = ref<any>(null)
const mostrarCreacionRapida = ref(false)
const creandoPaciente = ref(false)
const guardando = ref(false)
const error = ref('')

const nuevoPaciente = reactive({
  first_name: '',
  last_name_paterno: '',
  last_name_materno: '',
  birth_date: '',
  gender: '',
  is_nn: false,
})

const form = reactive({
  servicio_emergencia: 'Emergencia General',
  fuente_financiamiento: '',
  acompanante_nombre: '',
  acompanante_documento: '',
  acompanante_parentesco: '',
  acompanante_telefono: '',
  acompanante_direccion: '',
  observaciones: '',
})

const getInitials = (name: string) => {
  if (!name) return '??'
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getColorPaciente = (name: string) => {
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
  if (!name) return colors[0]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

async function buscarPaciente() {
  if (!dniBusqueda.value || dniBusqueda.value.length < 8) {
    error.value = 'Ingresa un DNI válido de 8 dígitos'
    return
  }
  buscando.value = true
  error.value = ''
  mostrarCreacionRapida.value = false
  try {
    pacienteSeleccionado.value = await api(`/app/gestion-pacientes/dni/${dniBusqueda.value}`)
  } catch (e: any) {
    if (e?.status === 404) {
      mostrarCreacionRapida.value = true
    } else {
      error.value = e?.data?.detail || 'Error al buscar paciente'
    }
  } finally {
    buscando.value = false
  }
}

async function crearPacienteRapido() {
  if (!nuevoPaciente.first_name || !nuevoPaciente.last_name_paterno || !nuevoPaciente.birth_date || !nuevoPaciente.gender) {
    error.value = 'Completa todos los campos requeridos del paciente'
    return
  }
  creandoPaciente.value = true
  error.value = ''
  try {
    pacienteSeleccionado.value = await api('/app/gestion-pacientes/', {
      method: 'POST',
      body: {
        ...nuevoPaciente,
        dni: nuevoPaciente.is_nn ? null : dniBusqueda.value,
      },
    })
    mostrarCreacionRapida.value = false
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al registrar paciente'
  } finally {
    creandoPaciente.value = false
  }
}

async function registrarAdmision() {
  if (!pacienteSeleccionado.value) {
    error.value = 'Selecciona un paciente primero'
    return
  }
  guardando.value = true
  error.value = ''
  try {
    const admision = await api('/app/emergencia/admisiones', {
      method: 'POST',
      body: { patient_id: pacienteSeleccionado.value.id, ...form },
    })
    await navigateTo(link(`/app/emergencia/triaje/${admision.id}`))
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al registrar la admisión'
  } finally {
    guardando.value = false
  }
}
</script>

<style scoped>
.emergencia-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.emergencia-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.emergencia-create-main {
  min-width: 0;
}

.emergencia-create-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Header */
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

/* Form Card */
.form-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  animation: slideIn 0.3s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.card-header-icon {
  width: 40px;
  height: 40px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.card-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.card-subtitle {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  margin: 0;
}

/* Buscar Paciente */
.buscar-paciente {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.buscar-input-group {
  display: flex;
  gap: 0.75rem;
}

.buscar-input-group .input-wrapper {
  flex: 1;
}

.btn-search {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--alert);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-search:hover:not(:disabled) {
  background: var(--alert-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-search:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Paciente Seleccionado */
.paciente-seleccionado {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  background: var(--green-soft);
  border: 1px solid var(--green);
  flex-wrap: wrap;
  gap: 0.75rem;
}

.paciente-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.paciente-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.paciente-datos {
  display: flex;
  flex-direction: column;
}

.paciente-nombre {
  font-weight: 500;
  color: var(--ink);
}

.paciente-dni {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.btn-remove-paciente {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--alert);
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-remove-paciente:hover {
  background: var(--alert-soft);
}

/* Creación Rápida */
.creacion-rapida {
  margin-top: 1rem;
  padding: 1rem;
  border-radius: var(--radius);
  border: 1px solid var(--amber-soft);
  background: var(--amber-soft);
}

.creacion-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.creacion-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.creacion-grid .form-group {
  margin-bottom: 0;
}

.btn-registrar-paciente {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.75rem;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  background: var(--green);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-registrar-paciente:hover:not(:disabled) {
  background: var(--green-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-registrar-paciente:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Form */
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
  border-color: var(--alert);
  box-shadow: 0 0 0 3px var(--alert-soft);
}

.input-clinical::placeholder {
  color: var(--ink-soft);
  opacity: 0.6;
}

.field-hint {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  margin-top: 0.25rem;
}

/* Info Section */
.info-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 1rem 0;
}

/* Checkbox */
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-top: 0.5rem;
}

.checkbox-custom {
  accent-color: var(--teal);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-label {
  font-size: 0.8125rem;
  color: var(--ink);
  cursor: pointer;
}

/* Form Actions */
.form-actions {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.action-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  background: var(--teal);
  color: white;
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

.btn-cancel {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-soft);
  text-decoration: none;
  transition: all 0.2s ease;
}

.btn-cancel:hover {
  background: var(--mist);
}

/* Widgets */
.widget {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  overflow: hidden;
  border: 1px solid var(--line);
}

.widget-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid var(--line);
}

.widget-icon {
  width: 1.25rem;
  height: 1.25rem;
}

.widget-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.widget-content {
  padding: 1rem 1.25rem;
}

/* Info Widget */
.info-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.info-item {
  display: flex;
  align-items: flex-start;
  gap: 0.625rem;
  padding: 0.375rem 0;
  font-size: 0.8125rem;
  color: var(--ink);
}

.info-item-icon {
  width: 1rem;
  height: 1rem;
  margin-top: 0.125rem;
  flex-shrink: 0;
}

/* Summary Widget */
.summary-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
  border-bottom: 1px solid var(--line);
}

.summary-item:last-of-type {
  border-bottom: none;
}

.summary-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.summary-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  max-width: 60%;
  text-align: right;
  word-break: break-word;
}

/* Tip Widget */
.widget-tip {
  background: var(--amber-soft);
  border-color: var(--amber-soft);
}

.tip-content {
  display: flex;
  gap: 0.75rem;
}

.tip-icon {
  width: 1.25rem;
  height: 1.25rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.tip-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.25rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.tip-text {
  font-size: 0.8125rem;
  color: var(--ink);
  margin: 0;
  line-height: 1.5;
}

/* Quick Stats Widget */
.stat-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.375rem 0;
}

.stat-item + .stat-item {
  border-top: 1px solid var(--line);
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.stat-number {
  font-size: 1rem;
  font-weight: 700;
  color: var(--ink);
}

/* Animations */
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Responsive */
@media (max-width: 1024px) {
  .emergencia-create-grid {
    grid-template-columns: 1fr;
  }

  .emergencia-create-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .emergencia-create-container {
    padding: 1rem;
  }

  .form-grid,
  .creacion-grid {
    grid-template-columns: 1fr;
  }

  .emergencia-create-sidebar {
    grid-template-columns: 1fr;
  }

  .action-group {
    flex-direction: column;
    width: 100%;
  }

  .action-group > * {
    width: 100%;
    justify-content: center;
  }

  .buscar-input-group {
    flex-direction: column;
  }

  .btn-search {
    width: 100%;
    justify-content: center;
  }

  .paciente-seleccionado {
    flex-direction: column;
    align-items: flex-start;
  }

  .btn-remove-paciente {
    align-self: flex-end;
  }
}

@media (max-width: 480px) {
  .paciente-info {
    flex-wrap: wrap;
  }

  .summary-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .summary-value {
    max-width: 100%;
    text-align: left;
  }
}
</style>