<template>
  <div class="triaje-create-container">
    <div class="triaje-create-grid">
      <!-- Main Content -->
      <div class="triaje-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="link('/app/consulta-externa/triaje')" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-clipboard-document-check" class="w-3.5 h-3.5" />
              Panel de Triaje
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Registrar Triaje</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--blue-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--blue)" />
            </div>
            <div>
              <h1 class="page-title">Registrar Triaje</h1>
              <p class="page-subtitle">Registro de signos vitales y evaluación del paciente</p>
            </div>
          </div>
        </div>

        <!-- Success Message -->
        <div v-if="exito" class="success-banner">
          <UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />
          {{ exito }}
        </div>

        <!-- Error Message -->
        <div v-if="error" class="error-banner">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
          {{ error }}
        </div>

        <!-- Loading State -->
        <div v-if="cargando" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--blue)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando datos de la cita...</p>
        </div>

        <!-- Form Content -->
        <template v-else-if="cita">
          <!-- Patient Info Card -->
          <section class="form-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--blue-soft)">
                <UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--blue)" />
              </div>
              <div>
                <h3 class="card-title">Información del Paciente</h3>
                <p class="card-subtitle">Datos de la cita seleccionada para triaje</p>
              </div>
            </div>

            <div class="patient-info-grid">
              <div class="patient-avatar" :style="{ background: getPacienteColor(cita.paciente_nombre) }">
                <span>{{ getInitials(cita.paciente_nombre) }}</span>
              </div>
              <div class="patient-details">
                <div class="patient-name">{{ cita.paciente_nombre }}</div>
                <div class="patient-meta">
                  <span class="patient-meta-item">
                    <UIcon name="i-heroicons-identification" class="w-3.5 h-3.5" />
                    DNI: {{ cita.paciente_dni || 'NN' }}
                  </span>
                  <span class="patient-meta-separator">·</span>
                  <span class="patient-meta-item">
                    <UIcon name="i-heroicons-star" class="w-3.5 h-3.5" />
                    {{ cita.especialidad_nombre || cita.servicio_nombre || '—' }}
                  </span>
                  <span class="patient-meta-separator">·</span>
                  <span class="patient-meta-item">
                    <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
                    {{ cita.hora_inicio }}
                  </span>
                </div>
              </div>
              <span class="patient-status" style="background: var(--blue-soft); color: var(--blue)">
                <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
                Pendiente de Triaje
              </span>
            </div>
          </section>

          <!-- Form Card -->
          <section class="form-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--blue-soft)">
                <UIcon name="i-heroicons-heart" class="w-4 h-4" style="color: var(--blue)" />
              </div>
              <div>
                <h3 class="card-title">Signos Vitales y Medidas</h3>
                <p class="card-subtitle">Ingresa los valores del triaje del paciente</p>
              </div>
            </div>

            <div class="form-grid">
              <!-- Pulso -->
              <div class="form-group">
                <label class="form-label">Pulso <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-heart" class="input-icon" />
                  <input
                    v-model.number="form.pulso"
                    type="number"
                    class="input-clinical"
                    :class="{ 'input-error': errors.pulso }"
                    placeholder="60-100"
                    @change="errors.pulso = ''"
                  />
                </div>
                <span v-if="errors.pulso" class="error-message">{{ errors.pulso }}</span>
                <p class="field-hint">Registra el valor medido; la interpretación depende de la edad y el contexto.</p>
              </div>

              <!-- Frecuencia Respiratoria -->
              <div class="form-group">
                <label class="form-label">Frecuencia Respiratoria <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-wind" class="input-icon" />
                  <input
                    v-model.number="form.frecuencia_respiratoria"
                    type="number"
                    class="input-clinical"
                    :class="{ 'input-error': errors.frecuencia_respiratoria }"
                    placeholder="30-60"
                    @change="errors.frecuencia_respiratoria = ''"
                  />
                </div>
                <span v-if="errors.frecuencia_respiratoria" class="error-message">{{ errors.frecuencia_respiratoria }}</span>
                <p class="field-hint">Registra el valor medido; la interpretación depende de la edad y el contexto.</p>
              </div>

              <!-- Temperatura -->
              <div class="form-group">
                <label class="form-label">Temperatura (°C) <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-thermometer" class="input-icon" />
                  <input
                    v-model.number="form.temperatura"
                    type="number"
                    step="0.1"
                    class="input-clinical"
                    :class="{ 'input-error': errors.temperatura }"
                    placeholder="36.1-37.7"
                    @change="errors.temperatura = ''"
                  />
                </div>
                <span v-if="errors.temperatura" class="error-message">{{ errors.temperatura }}</span>
                <p class="field-hint">Registra el valor medido; la interpretación depende de la edad y el contexto.</p>
              </div>

              <!-- Peso -->
              <div class="form-group">
                <label class="form-label">Peso (Kg)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-scale" class="input-icon" />
                  <input
                    v-model.number="form.peso"
                    type="number"
                    step="0.1"
                    class="input-clinical"
                    placeholder="Peso en Kg"
                  />
                </div>
                <p class="field-hint">Peso del paciente en kilogramos</p>
              </div>

              <!-- Presión Arterial (full width) -->
              <div class="form-group full-width">
                <label class="form-label">Presión Arterial <span class="required">*</span></label>
                <div class="presion-grid">
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-arrow-trending-up" class="input-icon" />
                    <input
                      v-model.number="form.presion_sistolica"
                      type="number"
                      class="input-clinical"
                      :class="{ 'input-error': errors.presion_sistolica }"
                      placeholder="Sistólica"
                      @change="errors.presion_sistolica = ''"
                    />
                  </div>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-arrow-trending-down" class="input-icon" />
                    <input
                      v-model.number="form.presion_diastolica"
                      type="number"
                      class="input-clinical"
                      :class="{ 'input-error': errors.presion_diastolica }"
                      placeholder="Diastólica"
                      @change="errors.presion_diastolica = ''"
                    />
                  </div>
                </div>
                <span v-if="errors.presion_sistolica" class="error-message">{{ errors.presion_sistolica }}</span>
                <span v-if="errors.presion_diastolica" class="error-message">{{ errors.presion_diastolica }}</span>
                <p class="field-hint">Registra el valor medido; la interpretación depende de la edad y el contexto.</p>
              </div>

              <!-- Talla -->
              <div class="form-group">
                <label class="form-label">Talla (cm)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-arrows-up-down" class="input-icon" />
                  <input
                    v-model.number="form.talla"
                    type="number"
                    step="0.1"
                    class="input-clinical"
                    placeholder="Talla en cm"
                  />
                </div>
                <p class="field-hint">Talla del paciente en centímetros</p>
              </div>

              <!-- Frecuencia Cardiaca -->
              <div class="form-group">
                <label class="form-label">Frecuencia Cardiaca <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-heart" class="input-icon" />
                  <input
                    v-model.number="form.frecuencia_cardiaca"
                    type="number"
                    class="input-clinical"
                    :class="{ 'input-error': errors.frecuencia_cardiaca }"
                    placeholder="80-205"
                    @change="errors.frecuencia_cardiaca = ''"
                  />
                </div>
                <span v-if="errors.frecuencia_cardiaca" class="error-message">{{ errors.frecuencia_cardiaca }}</span>
                <p class="field-hint">Registra el valor medido; la interpretación depende de la edad y el contexto.</p>
              </div>

              <!-- Perímetro Cefálico -->
              <div class="form-group">
                <label class="form-label">Perímetro Cefálico (cm)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-circle-stack" class="input-icon" />
                  <input
                    v-model.number="form.perimetro_cefalico"
                    type="number"
                    step="0.1"
                    class="input-clinical"
                    placeholder="cm"
                  />
                </div>
                <p class="field-hint">Perímetro cefálico en centímetros</p>
              </div>

              <!-- Perímetro Abdominal -->
              <div class="form-group">
                <label class="form-label">Perímetro Abdominal (cm)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-circle-stack" class="input-icon" />
                  <input
                    v-model.number="form.perimetro_abdominal"
                    type="number"
                    step="0.1"
                    class="input-clinical"
                    placeholder="cm"
                  />
                </div>
                <p class="field-hint">Perímetro abdominal en centímetros</p>
              </div>

              <!-- SO2 -->
              <div class="form-group">
                <label class="form-label">SO₂ (%)</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-beaker" class="input-icon" />
                  <input
                    v-model.number="form.saturacion_o2"
                    type="number"
                    step="0.1"
                    class="input-clinical"
                    placeholder="%"
                  />
                </div>
                <p class="field-hint">Registra el valor medido; la interpretación depende de la edad y el contexto.</p>
              </div>
            </div>

            <!-- IMC Preview -->
            <div v-if="form.peso && form.talla" class="preview-section">
              <div class="imc-preview">
                <div class="imc-icon" style="background: var(--blue-soft)">
                  <UIcon name="i-heroicons-calculator" class="w-5 h-5" style="color: var(--blue)" />
                </div>
                <div class="imc-info">
                  <span class="imc-label">IMC calculado</span>
                  <span class="imc-value">{{ calcularIMC(form.peso, form.talla) }}</span>
                </div>
                <span class="imc-status" :style="getIMCStyle(calcularIMC(form.peso, form.talla))">
                  {{ getIMCStatus(calcularIMC(form.peso, form.talla)) }}
                </span>
              </div>
            </div>

            <!-- Actions -->
            <div class="form-actions">
              <div class="action-group">
                <button
                  class="btn-primary"
                  :disabled="guardando"
                  @click="guardar"
                >
                  <UIcon v-if="guardando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                  {{ guardando ? 'Guardando...' : 'Guardar Triaje' }}
                </button>
                <NuxtLink
                  :to="link('/app/consulta-externa/triaje')"
                  class="btn-cancel"
                >
                  Cancelar
                </NuxtLink>
              </div>
            </div>
          </section>
        </template>

        <!-- Not Found -->
        <div v-else-if="!cargando" class="empty-state">
          <div class="empty-icon" style="background: var(--mist)">
            <UIcon name="i-heroicons-clipboard-document-check" class="w-12 h-12" style="color: var(--ink-soft)" />
          </div>
          <h3 style="color: var(--ink)">No se encontró la cita</h3>
          <p style="color: var(--ink-soft)">La cita que buscas no existe o ha sido eliminada</p>
          <NuxtLink :to="link('/app/consulta-externa/triaje')" class="btn-cancel">
            <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
            Volver al Panel
          </NuxtLink>
        </div>
      </div>

      <!-- Sidebar Widgets -->
      <div class="triaje-create-sidebar">
        <!-- Info Widget -->
        <div class="widget widget-info">
          <div class="widget-header">
            <UIcon name="i-heroicons-information-circle" class="widget-icon" style="color: var(--blue)" />
            <h4 class="widget-title">Información</h4>
          </div>
          <div class="widget-content">
            <ul class="info-list">
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--blue)" />
                <span>Los campos con * son obligatorios</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--blue)" />
                <span>Registra las mediciones reales, incluso si están alteradas</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--blue)" />
                <span>El IMC se calcula automáticamente con peso y talla</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--blue)" />
                <span>El triaje quedará registrado en el historial del paciente</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--blue)" />
            <h4 class="widget-title">Resumen del Triaje</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Paciente</span>
              <span class="summary-value">{{ cita?.paciente_nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">DNI</span>
              <span class="summary-value font-mono-data">{{ cita?.paciente_dni || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Especialidad</span>
              <span class="summary-value">{{ cita?.especialidad_nombre || cita?.servicio_nombre || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Pulso</span>
              <span class="summary-value">{{ form.pulso || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Temp.</span>
              <span class="summary-value">{{ form.temperatura || '—' }} °C</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Peso / Talla</span>
              <span class="summary-value">{{ form.peso || '—' }} kg / {{ form.talla || '—' }} cm</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">IMC</span>
              <span class="summary-value">{{ form.peso && form.talla ? calcularIMC(form.peso, form.talla) : '—' }}</span>
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
                  Asegúrate de registrar todos los signos vitales correctamente. 
                  Los valores fuera de rango pueden indicar condiciones que requieren atención prioritaria.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats Widget -->
        <div class="widget widget-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Estado del Formulario</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Campos completos</span>
              <span class="stat-number">{{ filledFields }}/{{ totalFields }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Campos obligatorios</span>
              <span class="stat-number">{{ requiredFields }}/{{ totalRequired }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">IMC</span>
              <span class="stat-number" :style="{ color: form.peso && form.talla ? 'var(--blue)' : 'var(--ink-soft)' }">
                {{ form.peso && form.talla ? calcularIMC(form.peso, form.talla) : '—' }}
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
const citaId = route.query.cita as string

// Estado
const cargando = ref(true)
const guardando = ref(false)
const error = ref('')
const exito = ref('')
const cita = ref<any>(null)

// Errores
const errors = reactive({
  pulso: '',
  frecuencia_respiratoria: '',
  temperatura: '',
  presion_sistolica: '',
  presion_diastolica: '',
  frecuencia_cardiaca: '',
})

// Formulario
const form = reactive({
  pulso: null as number | null,
  temperatura: null as number | null,
  presion_sistolica: null as number | null,
  presion_diastolica: null as number | null,
  frecuencia_cardiaca: null as number | null,
  frecuencia_respiratoria: null as number | null,
  peso: null as number | null,
  talla: null as number | null,
  perimetro_abdominal: null as number | null,
  perimetro_cefalico: null as number | null,
  saturacion_o2: null as number | null,
})

// Computed
const filledFields = computed(() => {
  let count = 0
  if (form.pulso !== null && form.pulso !== '') count++
  if (form.frecuencia_respiratoria !== null && form.frecuencia_respiratoria !== '') count++
  if (form.temperatura !== null && form.temperatura !== '') count++
  if (form.presion_sistolica !== null && form.presion_sistolica !== '') count++
  if (form.presion_diastolica !== null && form.presion_diastolica !== '') count++
  if (form.frecuencia_cardiaca !== null && form.frecuencia_cardiaca !== '') count++
  if (form.peso !== null && form.peso !== '') count++
  if (form.talla !== null && form.talla !== '') count++
  if (form.perimetro_abdominal !== null && form.perimetro_abdominal !== '') count++
  if (form.perimetro_cefalico !== null && form.perimetro_cefalico !== '') count++
  if (form.saturacion_o2 !== null && form.saturacion_o2 !== '') count++
  return count
})

const totalFields = 11

const requiredFields = computed(() => {
  let count = 0
  if (form.pulso !== null && form.pulso !== '') count++
  if (form.frecuencia_respiratoria !== null && form.frecuencia_respiratoria !== '') count++
  if (form.temperatura !== null && form.temperatura !== '') count++
  if (form.presion_sistolica !== null && form.presion_sistolica !== '') count++
  if (form.presion_diastolica !== null && form.presion_diastolica !== '') count++
  if (form.frecuencia_cardiaca !== null && form.frecuencia_cardiaca !== '') count++
  return count
})

const totalRequired = 6

// Helpers
const getInitials = (name: string) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map((word: string) => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getPacienteColor = (name: string) => {
  const colors = [
    'var(--blue-soft)',
    'var(--purple-soft)',
    'var(--teal-soft)',
    'var(--amber-soft)',
    'var(--green-soft)',
    'var(--pink-soft)',
    'var(--navy-soft)',
    'var(--orange-soft)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const calcularIMC = (peso: number, talla: number) => {
  if (!peso || !talla || talla <= 0) return '—'
  const imc = peso / ((talla / 100) ** 2)
  return imc.toFixed(1)
}

const getIMCStatus = (imc: string) => {
  const value = parseFloat(imc)
  if (isNaN(value)) return '—'
  if (value < 18.5) return 'Bajo peso'
  if (value < 25) return 'Normal'
  if (value < 30) return 'Sobrepeso'
  return 'Obesidad'
}

const getIMCStyle = (imc: string) => {
  const value = parseFloat(imc)
  if (isNaN(value)) return {}
  if (value < 18.5) return { background: 'var(--amber-soft)', color: 'var(--amber)' }
  if (value < 25) return { background: 'var(--green-soft)', color: 'var(--green)' }
  if (value < 30) return { background: 'var(--amber-soft)', color: 'var(--amber)' }
  return { background: 'var(--alert-soft)', color: 'var(--alert)' }
}

// Validación
function validar(): boolean {
  let valid = true
  const obligatorios = ['pulso', 'frecuencia_respiratoria', 'temperatura', 'presion_sistolica', 'presion_diastolica', 'frecuencia_cardiaca']
  for (const [campo, valor] of Object.entries(form)) {
    const vacio = valor === null || valor === undefined || valor === ''
    let mensaje = ''
    if (vacio && obligatorios.includes(campo)) mensaje = 'Registra la medición realizada'
    else if (!vacio && (!Number.isFinite(Number(valor)) || Number(valor) < 0)) mensaje = 'Ingresa un número válido sin valores negativos'
    else if (!vacio && ['peso', 'talla', 'temperatura', 'perimetro_abdominal', 'perimetro_cefalico'].includes(campo) && Number(valor) === 0) mensaje = 'La medición debe ser mayor que cero'
    else if (campo === 'saturacion_o2' && !vacio && Number(valor) > 100) mensaje = 'La saturación debe estar entre 0 y 100 %'
    ;(errors as any)[campo] = mensaje
    if (mensaje) valid = false
  }
  return valid
}

// Funciones
async function guardar() {
  if (guardando.value || !validar()) return

  error.value = ''
  exito.value = ''
  guardando.value = true
  try {
    await api(`/app/consulta-externa/triaje/${citaId}`, { method: 'POST', body: form })
    exito.value = 'Triaje registrado correctamente'
    setTimeout(() => navigateTo(link(`/app/consulta-externa/triaje?fecha=${cita.value?.fecha || ''}`)), 1500)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar el triaje'
  } finally {
    guardando.value = false
  }
}

// Lifecycle
onMounted(async () => {
  if (!citaId) {
    error.value = 'Falta indicar la cita (parámetro ?cita=)'
    cargando.value = false
    return
  }
  try {
    cita.value = await api(`/app/consulta-externa/citas/${citaId}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar la cita'
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
/* ============================================
   Mismos estilos que Agregar Programación
   ============================================ */
.triaje-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.triaje-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.triaje-create-main {
  min-width: 0;
}

.triaje-create-sidebar {
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

/* Success Banner */
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

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Form Card */
.form-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
  animation: slideIn 0.3s ease;
  margin-bottom: 1.5rem;
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

/* Patient Info */
.patient-info-grid {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.25rem;
  background: var(--mist);
  border-radius: var(--radius);
  border: 1px solid var(--line);
  flex-wrap: wrap;
}

.patient-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.patient-details {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 150px;
}

.patient-name {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
}

.patient-meta {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8125rem;
  color: var(--ink-soft);
  flex-wrap: wrap;
}

.patient-meta-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.patient-meta-separator {
  color: var(--line);
}

.patient-status {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  flex-shrink: 0;
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
  border-color: var(--blue);
  box-shadow: 0 0 0 3px var(--blue-soft);
}

.input-clinical.input-error {
  border-color: var(--alert);
}

.input-clinical.input-error:focus {
  box-shadow: 0 0 0 3px var(--alert-soft);
}

.input-clinical:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.error-message {
  display: block;
  font-size: 0.75rem;
  color: var(--alert);
  margin-top: 0.25rem;
}

.field-hint {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  margin-top: 0.25rem;
}

/* Presión Grid */
.presion-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

/* IMC Preview */
.preview-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.imc-preview {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background: var(--mist);
  border-radius: var(--radius);
  border: 1px solid var(--line);
}

.imc-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.imc-info {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.imc-label {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.imc-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--ink);
}

.imc-status {
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
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
  background: var(--blue);
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: var(--blue-dark);
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

/* Empty State */
.empty-state {
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

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state h3 {
  font-size: 1.125rem;
  margin: 0;
}

.empty-state p {
  margin: 0;
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

/* Stats Widget */
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

/* Responsive */
@media (max-width: 1024px) {
  .triaje-create-grid {
    grid-template-columns: 1fr;
  }

  .triaje-create-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .triaje-create-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .triaje-create-sidebar {
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

  .patient-info-grid {
    flex-direction: column;
    text-align: center;
  }

  .patient-meta {
    justify-content: center;
  }

  .patient-status {
    align-self: center;
  }

  .presion-grid {
    grid-template-columns: 1fr;
  }

  .imc-preview {
    flex-direction: column;
    text-align: center;
  }
}

@media (max-width: 480px) {
  .summary-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .summary-value {
    max-width: 100%;
    text-align: left;
  }

  .patient-meta {
    flex-direction: column;
    align-items: center;
  }

  .patient-meta-separator {
    display: none;
  }
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
</style>