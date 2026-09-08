<template>
  <div class="emergencia-triaje-container">
    <div class="emergencia-triaje-grid">
      <!-- Main Content -->
      <div class="emergencia-triaje-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="link('/app/emergencia/admisiones')" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-heart" class="w-3.5 h-3.5" />
              Admisiones
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Triaje</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--amber-soft)">
              <UIcon name="i-heroicons-clipboard-document-list" class="w-6 h-6" style="color: var(--amber)" />
            </div>
            <div>
              <h1 class="page-title">Triaje de Emergencia</h1>
              <p class="page-subtitle">Registra los signos vitales y prioridad del paciente</p>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="cargando" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--amber)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando información de la admisión...</p>
        </div>

        <template v-else-if="admision">
          <!-- Patient Info Card -->
          <div class="patient-info-card">
            <div class="patient-info-header">
              <div class="patient-avatar" :style="{ background: getColorPaciente(admision.paciente_nombre) }">
                <span>{{ getInitials(admision.paciente_nombre) }}</span>
              </div>
              <div class="patient-info">
                <span class="patient-name">{{ admision.paciente_nombre }}</span>
                <div class="patient-details">
                  <span v-if="admision.paciente_dni" class="patient-dni font-mono-data">DNI: {{ admision.paciente_dni }}</span>
                  <span v-else class="patient-dni">NN</span>
                  <span class="patient-separator">•</span>
                  <span class="patient-cuenta font-mono-data">Cuenta: {{ admision.numero_cuenta }}</span>
                  <span class="patient-separator">•</span>
                  <span class="patient-servicio">{{ admision.servicio_emergencia }}</span>
                </div>
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
              <div class="card-header-icon" style="background: var(--amber-soft)">
                <UIcon name="i-heroicons-clipboard-document-list" class="w-4 h-4" style="color: var(--amber)" />
              </div>
              <div>
                <h3 class="card-title">Signos Vitales y Evaluación</h3>
                <p class="card-subtitle">Ingresa los datos del triaje del paciente</p>
              </div>
            </div>

            <div class="form-grid">
              <!-- Prioridad -->
              <div class="form-group full-width">
                <label class="form-label">Prioridad <span class="required">*</span></label>
                <div class="prioridad-group">
                  <button
                    v-for="p in prioridades"
                    :key="p.value"
                    class="prioridad-btn"
                    :class="[
                      form.prioridad === p.value ? p.class : '',
                      form.prioridad === p.value ? 'prioridad-btn--active' : ''
                    ]"
                    @click="form.prioridad = p.value"
                  >
                    <span class="prioridad-label">{{ p.label }}</span>
                    <span class="prioridad-desc">{{ p.desc }}</span>
                  </button>
                </div>
                <p class="field-hint">I = grave/inmediata, II = urgente, III = leve</p>
              </div>

              <!-- Signos Vitales -->
              <div class="form-group">
                <label class="form-label">Pulso (lat/min)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-heart" class="input-icon" />
                  <input v-model.number="form.pulso" type="number" class="input-clinical" placeholder="Ej: 72" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Frec. Respiratoria (rpm)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-arrows-up-down" class="input-icon" />
                  <input v-model.number="form.frecuencia_respiratoria" type="number" class="input-clinical" placeholder="Ej: 16" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Temperatura (°C)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-thermometer" class="input-icon" />
                  <input v-model.number="form.temperatura" type="number" step="0.1" class="input-clinical" placeholder="Ej: 36.5" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Peso (kg)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-scale" class="input-icon" />
                  <input v-model.number="form.peso" type="number" step="0.1" class="input-clinical" placeholder="Ej: 70.5" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Presión Arterial</label>
                <div class="presion-group">
                  <div class="input-wrapper presion-input">
                    <UIcon name="i-heroicons-arrow-up" class="input-icon" />
                    <input v-model.number="form.presion_sistolica" type="number" class="input-clinical" placeholder="Sist" />
                  </div>
                  <span class="presion-separator">/</span>
                  <div class="input-wrapper presion-input">
                    <UIcon name="i-heroicons-arrow-down" class="input-icon" />
                    <input v-model.number="form.presion_diastolica" type="number" class="input-clinical" placeholder="Diast" />
                  </div>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Talla (cm)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-arrows-up-down" class="input-icon" />
                  <input v-model.number="form.talla" type="number" step="0.1" class="input-clinical" placeholder="Ej: 170" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Frec. Cardiaca (lat/min)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-heart" class="input-icon" />
                  <input v-model.number="form.frecuencia_cardiaca" type="number" class="input-clinical" placeholder="Ej: 75" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Saturación O₂ (%)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-beaker" class="input-icon" />
                  <input v-model.number="form.saturacion_o2" type="number" step="0.1" class="input-clinical" placeholder="Ej: 98" />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Observación</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea v-model="form.observacion" class="input-clinical" rows="2" placeholder="Observaciones adicionales del triaje..." />
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="form-actions">
              <div class="action-group">
                <button class="btn-secondary" @click="navigateTo(link('/app/emergencia/admisiones'))">
                  <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
                  Salir
                </button>
                <button class="btn-primary" style="background: var(--alert)" :disabled="!form.prioridad || guardando" @click="guardar">
                  <UIcon v-if="guardando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                  {{ guardando ? 'Guardando...' : 'Guardar Triaje' }}
                </button>
              </div>
            </div>
          </section>
        </template>
      </div>

      <!-- Sidebar Widgets -->
      <div class="emergencia-triaje-sidebar">
        <!-- Info Widget -->
        <div class="widget widget-info">
          <div class="widget-header">
            <UIcon name="i-heroicons-information-circle" class="widget-icon" style="color: var(--amber)" />
            <h4 class="widget-title">Información</h4>
          </div>
          <div class="widget-content">
            <ul class="info-list">
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--amber)" />
                <span>La prioridad determina la urgencia de atención</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--amber)" />
                <span>Los signos vitales ayudan a clasificar al paciente</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--amber)" />
                <span>Prioridad I: atención inmediata (rojo)</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--amber)" />
                <span>Prioridad II: urgente (ámbar) • Prioridad III: leve (verde)</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Resumen Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Resumen del Triaje</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Paciente</span>
              <span class="summary-value">{{ admision?.paciente_nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Prioridad</span>
              <span class="summary-value">
                <span v-if="form.prioridad" class="prioridad-badge" :class="getPrioridadClass(form.prioridad)">
                  Prioridad {{ form.prioridad }}
                </span>
                <span v-else>—</span>
              </span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Pulso</span>
              <span class="summary-value">{{ form.pulso || '—' }} lat/min</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Temperatura</span>
              <span class="summary-value">{{ form.temperatura || '—' }} °C</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Presión Arterial</span>
              <span class="summary-value">
                {{ form.presion_sistolica || '—' }}/{{ form.presion_diastolica || '—' }}
              </span>
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
                  Un triaje preciso es fundamental para priorizar 
                  la atención de pacientes en emergencia.
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
              <span class="stat-label">Prioridad</span>
              <span class="stat-number" :style="{ color: form.prioridad ? 'var(--teal)' : 'var(--ink-soft)' }">
                {{ form.prioridad ? '✓' : '—' }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Signos Vitales</span>
              <span class="stat-number">{{ signosCompletos }}/8</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Observación</span>
              <span class="stat-number" :style="{ color: form.observacion ? 'var(--teal)' : 'var(--ink-soft)' }">
                {{ form.observacion ? '✓' : '—' }}
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
const route = useRoute()

const admisionId = route.params.id as string

const prioridades = [
  { value: 'I', label: 'I', desc: 'Grave', class: 'prioridad-roja' },
  { value: 'II', label: 'II', desc: 'Urgente', class: 'prioridad-amber' },
  { value: 'III', label: 'III', desc: 'Leve', class: 'prioridad-verde' },
]

const cargando = ref(true)
const guardando = ref(false)
const error = ref('')
const admision = ref<any>(null)

const form = reactive({
  prioridad: '',
  pulso: null,
  temperatura: null,
  presion_sistolica: null,
  presion_diastolica: null,
  frecuencia_cardiaca: null,
  frecuencia_respiratoria: null,
  peso: null,
  talla: null,
  saturacion_o2: null,
  observacion: '',
})

const signosCompletos = computed(() => {
  let count = 0
  if (form.pulso !== null) count++
  if (form.temperatura !== null) count++
  if (form.presion_sistolica !== null && form.presion_diastolica !== null) count++
  if (form.frecuencia_cardiaca !== null) count++
  if (form.frecuencia_respiratoria !== null) count++
  if (form.peso !== null) count++
  if (form.talla !== null) count++
  if (form.saturacion_o2 !== null) count++
  return count
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

const getPrioridadClass = (prioridad: string) => {
  const map: Record<string, string> = {
    I: 'prioridad-badge-roja',
    II: 'prioridad-badge-amber',
    III: 'prioridad-badge-verde',
  }
  return map[prioridad] || ''
}

async function guardar() {
  if (!form.prioridad) {
    error.value = 'Selecciona una prioridad'
    return
  }
  error.value = ''
  guardando.value = true
  try {
    await api(`/app/emergencia/triaje/${admisionId}`, {
      method: 'POST',
      body: form,
    })
    await navigateTo(link(`/app/emergencia/atencion/${admisionId}`))
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar el triaje'
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  try {
    admision.value = await api(`/app/emergencia/admisiones/${admisionId}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar la admisión'
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
.emergencia-triaje-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.emergencia-triaje-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.emergencia-triaje-main {
  min-width: 0;
}

.emergencia-triaje-sidebar {
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

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Patient Info Card */
.patient-info-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.patient-info-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.patient-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.patient-info {
  display: flex;
  flex-direction: column;
}

.patient-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
}

.patient-details {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: var(--ink-soft);
  flex-wrap: wrap;
}

.patient-separator {
  color: var(--line);
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
  border-color: var(--amber);
  box-shadow: 0 0 0 3px var(--amber-soft);
}

.input-clinical::placeholder {
  color: var(--ink-soft);
  opacity: 0.6;
}

.input-clinical[type="number"] {
  -moz-appearance: textfield;
}

.input-clinical[type="number"]::-webkit-inner-spin-button,
.input-clinical[type="number"]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.field-hint {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  margin-top: 0.25rem;
}

/* Prioridad */
.prioridad-group {
  display: flex;
  gap: 0.5rem;
}

.prioridad-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  border: 2px solid var(--line);
  background: var(--paper);
  cursor: pointer;
  transition: all 0.2s ease;
  min-width: 80px;
  gap: 0.25rem;
}

.prioridad-btn:hover {
  border-color: var(--ink-soft);
}

.prioridad-btn--active {
  border-color: currentColor;
}

.prioridad-label {
  font-size: 1.125rem;
  font-weight: 700;
}

.prioridad-desc {
  font-size: 0.625rem;
  font-weight: 500;
}

.prioridad-roja {
  color: var(--alert);
  background: var(--alert-soft);
  border-color: var(--alert);
}

.prioridad-amber {
  color: var(--amber);
  background: var(--amber-soft);
  border-color: var(--amber);
}

.prioridad-verde {
  color: var(--green);
  background: var(--green-soft);
  border-color: var(--green);
}

/* Presión Arterial */
.presion-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.presion-input {
  flex: 1;
}

.presion-separator {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink-soft);
}

/* Prioridad Badge */
.prioridad-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 600;
}

.prioridad-badge-roja {
  background: var(--alert-soft);
  color: var(--alert);
}

.prioridad-badge-amber {
  background: var(--amber-soft);
  color: var(--amber);
}

.prioridad-badge-verde {
  background: var(--green-soft);
  color: var(--green);
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

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
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

.summary-divider {
  height: 1px;
  background: var(--line);
  margin: 0.5rem 0;
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
.animate-spin {
  animation: spin 1s linear infinite;
}

/* Responsive */
@media (max-width: 1024px) {
  .emergencia-triaje-grid {
    grid-template-columns: 1fr;
  }

  .emergencia-triaje-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .emergencia-triaje-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .emergencia-triaje-sidebar {
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

  .prioridad-group {
    flex-wrap: wrap;
  }

  .prioridad-btn {
    flex: 1;
    min-width: 60px;
    padding: 0.5rem 0.75rem;
  }

  .presion-group {
    flex-direction: column;
  }

  .presion-separator {
    display: none;
  }

  .patient-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .patient-separator {
    display: none;
  }
}

@media (max-width: 480px) {
  .patient-info-header {
    flex-direction: column;
    align-items: flex-start;
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

  .prioridad-btn {
    min-width: 50px;
    padding: 0.375rem 0.5rem;
  }

  .prioridad-label {
    font-size: 0.875rem;
  }
}
</style>