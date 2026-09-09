<template>
  <div class="emergencia-atencion-container">
    <div class="emergencia-atencion-grid">
      <!-- Main Content -->
      <div class="emergencia-atencion-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="link('/app/emergencia/admisiones')" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-heart" class="w-3.5 h-3.5" />
              Admisiones
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Atención</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-heart" class="w-6 h-6" style="color: var(--teal)" />
            </div>
            <div>
              <h1 class="page-title">Atención de Emergencia</h1>
              <p class="page-subtitle">Registra la atención médica del paciente</p>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="cargando" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando información de la atención...</p>
        </div>

        <template v-else>
          <!-- Error/Success Messages -->
          <div v-if="error" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ error }}
          </div>
          <div v-if="exito" class="success-banner">
            <UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />
            {{ exito }}
          </div>

          <!-- Patient Info Card -->
          <div class="patient-info-card">
            <div class="patient-info-header">
              <div class="patient-avatar" :style="{ background: getColorPaciente(atencion?.paciente_nombre || '') }">
                <span>{{ getInitials(atencion?.paciente_nombre || '') }}</span>
              </div>
              <div class="patient-info">
                <span class="patient-name">{{ atencion?.paciente_nombre || 'Paciente no identificado' }}</span>
                <div class="patient-details">
                  <span v-if="atencion?.paciente_dni" class="patient-dni font-mono-data">DNI: {{ atencion.paciente_dni }}</span>
                  <span v-else class="patient-dni">NN</span>
                  <span class="patient-separator">•</span>
                  <span v-if="firmado" class="patient-status firmado">
                    <UIcon name="i-heroicons-check-badge" class="w-3.5 h-3.5" />
                    Firmado
                  </span>
                  <span v-else class="patient-status pendiente">
                    <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
                    Pendiente
                  </span>
                </div>
              </div>
            </div>
          </div>

          <!-- Triaje Summary -->
          <div v-if="atencion?.triaje" class="triaje-summary">
            <div class="triaje-header">
              <UIcon name="i-heroicons-clipboard-document-list" class="w-4 h-4" style="color: var(--amber)" />
              <span class="triaje-title">Triaje — Prioridad</span>
              <span class="triaje-prioridad" :class="getPrioridadClass(atencion.triaje.prioridad)">
                {{ atencion.triaje.prioridad }}
              </span>
            </div>
            <div class="triaje-signos">
              <span class="signo-item">
                <span class="signo-label">P.A.</span>
                <span class="signo-valor">{{ atencion.triaje.presion_sistolica || '—' }}/{{ atencion.triaje.presion_diastolica || '—' }}</span>
              </span>
              <span class="signo-item">
                <span class="signo-label">Temp.</span>
                <span class="signo-valor">{{ atencion.triaje.temperatura || '—' }}°C</span>
              </span>
              <span class="signo-item">
                <span class="signo-label">SO₂</span>
                <span class="signo-valor">{{ atencion.triaje.saturacion_o2 || '—' }}%</span>
              </span>
              <span class="signo-item">
                <span class="signo-label">Pulso</span>
                <span class="signo-valor">{{ atencion.triaje.pulso || '—' }} lpm</span>
              </span>
              <span class="signo-item">
                <span class="signo-label">FC</span>
                <span class="signo-valor">{{ atencion.triaje.frecuencia_cardiaca || '—' }} lpm</span>
              </span>
            </div>
          </div>

          <!-- Form Card -->
          <section class="form-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h3 class="card-title">Registro de Atención</h3>
                <p class="card-subtitle">Completa la atención médica del paciente</p>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group full-width">
                <label class="form-label">Motivo de Consulta <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.motivo_consulta"
                    class="input-clinical"
                    rows="3"
                    placeholder="Describe el motivo de consulta del paciente..."
                    :disabled="firmado"
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Examen Clínico</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-magnifying-glass" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.examen_clinico"
                    class="input-clinical"
                    rows="3"
                    placeholder="Resultados del examen clínico..."
                    :disabled="firmado"
                  />
                </div>
              </div>

              <!-- Diagnósticos CIE-10 -->
              <div class="form-group full-width">
                <label class="form-label">Diagnósticos CIE-10</label>
                <div v-if="!firmado" class="cie10-search">
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-magnifying-glass" class="input-icon" />
                    <input
                      v-model="buscaCie10"
                      type="text"
                      class="input-clinical"
                      placeholder="Buscar código o descripción..."
                      @input="buscarCie10Debounced"
                    />
                  </div>
                  <ul v-if="resultadosCie10.length" class="cie10-results">
                    <li
                      v-for="r in resultadosCie10"
                      :key="r.id"
                      class="cie10-result-item"
                      @click="agregarDx(r)"
                    >
                      <span class="cie10-codigo font-mono-data">{{ r.codigo_cie10 }}</span>
                      <span class="cie10-descripcion">{{ r.descripcion }}</span>
                    </li>
                  </ul>
                </div>
                <div v-for="(dx, idx) in diagnosticos" :key="idx" class="diagnostico-item">
                  <span class="diagnostico-codigo font-mono-data">{{ dx.codigo_cie10 }}</span>
                  <span class="diagnostico-descripcion">{{ dx.descripcion }}</span>
                  <button
                    v-if="!firmado"
                    class="diagnostico-remove"
                    @click="diagnosticos.splice(idx, 1)"
                  >
                    <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
                  </button>
                </div>
                <p v-if="!diagnosticos.length && !firmado" class="field-hint">Busca y agrega diagnósticos CIE-10</p>
                <p v-if="!diagnosticos.length && firmado" class="field-hint" style="color: var(--ink-soft)">No hay diagnósticos registrados</p>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Plan de Tratamiento</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.plan_tratamiento"
                    class="input-clinical"
                    rows="2"
                    placeholder="Plan de tratamiento indicado..."
                    :disabled="firmado"
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Observaciones</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.observaciones"
                    class="input-clinical"
                    rows="2"
                    placeholder="Observaciones adicionales..."
                    :disabled="firmado"
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Destino <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-arrows-right-left" class="input-icon" />
                  <select v-model="form.destino_atencion" class="input-clinical" :disabled="firmado">
                    <option value="AMBULATORIA">Atención Ambulatoria</option>
                    <option value="HOSPITALIZACION">Hospitalización</option>
                    <option value="REFERENCIA">Referencia</option>
                    <option value="INTERCONSULTA">Interconsulta</option>
                    <option value="ALTA">Alta</option>
                    <option value="FALLECIDO">Fallecido</option>
                  </select>
                </div>
              </div>
            </div>

            <!-- Actions -->
            <div class="form-actions">
              <div class="action-group">
                <button class="btn-secondary" @click="navigateTo(link('/app/emergencia/admisiones'))">
                  <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
                  Volver
                </button>
                <button
                  v-if="!firmado"
                  class="btn-primary"
                  :disabled="guardando"
                  @click="guardar"
                >
                  <UIcon v-if="guardando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                  {{ guardando ? 'Guardando...' : (existe ? 'Guardar Cambios' : 'Registrar Atención') }}
                </button>
                <button
                  v-if="existe && !firmado"
                  class="btn-firmar"
                  :disabled="firmando"
                  @click="firmar"
                >
                  <UIcon v-if="firmando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check-badge" class="w-4 h-4" />
                  {{ firmando ? 'Firmando...' : 'Firmar Atención' }}
                </button>
                <span v-if="firmado" class="firmado-badge">
                  <UIcon name="i-heroicons-check-badge" class="w-4 h-4" />
                  Firmado
                </span>
              </div>
            </div>
          </section>
        </template>
      </div>

      <!-- Sidebar Widgets -->
      <div class="emergencia-atencion-sidebar">
        <!-- Info Widget -->
        <div class="widget widget-info">
          <div class="widget-header">
            <UIcon name="i-heroicons-information-circle" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Información</h4>
          </div>
          <div class="widget-content">
            <ul class="info-list">
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Registra el motivo de consulta y examen clínico</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Agrega diagnósticos desde el catálogo CIE-10</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El destino define el siguiente paso del paciente</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>La atención debe ser firmada para finalizar</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Resumen Widget -->
        <div v-if="existe" class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Resumen de Atención</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Motivo</span>
              <span class="summary-value">{{ form.motivo_consulta ? truncateText(form.motivo_consulta, 30) : '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Destino</span>
              <span class="summary-value">{{ formatearDestino(form.destino_atencion) }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Diagnósticos</span>
              <span class="summary-value">{{ diagnosticos.length }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Estado</span>
              <span class="summary-value">
                <span class="status-badge-mini" :class="firmado ? 'status-firmado' : 'status-pendiente'">
                  <UIcon :name="firmado ? 'i-heroicons-check-badge' : 'i-heroicons-clock'" class="w-3 h-3" />
                  {{ firmado ? 'Firmado' : 'Pendiente' }}
                </span>
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
                  Una atención completa y bien documentada es fundamental 
                  para el seguimiento del paciente en emergencia.
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
              <span class="stat-label">Campos completos</span>
              <span class="stat-number">{{ camposCompletos }}/{{ totalCampos }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Diagnósticos</span>
              <span class="stat-number">{{ diagnosticos.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Estado</span>
              <span class="stat-number" :style="{ color: firmado ? 'var(--green)' : 'var(--amber)' }">
                {{ firmado ? '✓ Firmado' : 'Pendiente' }}
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

const cargando = ref(true)
const guardando = ref(false)
const firmando = ref(false)
const existe = ref(false)
const error = ref('')
const exito = ref('')
const atencion = ref<any>({})
const diagnosticos = ref<any[]>([])
const buscaCie10 = ref('')
const resultadosCie10 = ref<any[]>([])
let debounceTimer: any = null

const firmado = computed(() => atencion.value?.estado === 'firmado')

const form = reactive({
  motivo_consulta: '',
  examen_clinico: '',
  plan_tratamiento: '',
  observaciones: '',
  destino_atencion: 'AMBULATORIA',
})

const camposCompletos = computed(() => {
  let count = 0
  if (form.motivo_consulta) count++
  if (form.examen_clinico) count++
  if (form.plan_tratamiento) count++
  if (form.observaciones) count++
  if (form.destino_atencion) count++
  return count
})

const totalCampos = 5

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
    I: 'prioridad-roja',
    II: 'prioridad-amber',
    III: 'prioridad-verde',
  }
  return map[prioridad] || ''
}

const formatearDestino = (destino: string) => {
  const map: Record<string, string> = {
    AMBULATORIA: 'Ambulatoria',
    HOSPITALIZACION: 'Hospitalización',
    REFERENCIA: 'Referencia',
    INTERCONSULTA: 'Interconsulta',
    ALTA: 'Alta',
    FALLECIDO: 'Fallecido',
  }
  return map[destino] || destino
}

const truncateText = (text: string, maxLength: number) => {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + '...'
}

function buscarCie10Debounced() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (buscaCie10.value.length < 2) {
      resultadosCie10.value = []
      return
    }
    try {
      resultadosCie10.value = await api(
        `/app/consulta-externa/atenciones-medicas/cie10/buscar?q=${encodeURIComponent(buscaCie10.value)}`
      )
    } catch {
      // Silencioso
    }
  }, 300)
}

function agregarDx(r: any) {
  if (diagnosticos.value.some((d) => d.diagnostico_cie10_id === r.id)) return
  diagnosticos.value.push({
    diagnostico_cie10_id: r.id,
    codigo_cie10: r.codigo_cie10,
    descripcion: r.descripcion,
    tipo: 'definitivo',
  })
  buscaCie10.value = ''
  resultadosCie10.value = []
}

async function guardar() {
  if (!form.motivo_consulta) {
    error.value = 'El motivo de consulta es requerido'
    return
  }
  error.value = ''
  exito.value = ''
  guardando.value = true
  try {
    if (existe.value) {
      atencion.value = await api(`/app/emergencia/atenciones/${admisionId}`, {
        method: 'PATCH',
        body: form,
      })
    } else {
      atencion.value = await api(`/app/emergencia/atenciones/${admisionId}`, {
        method: 'POST',
        body: {
          ...form,
          diagnosticos: diagnosticos.value.map((d) => ({
            diagnostico_cie10_id: d.diagnostico_cie10_id,
            tipo: d.tipo,
          })),
        },
      })
      existe.value = true
    }
    exito.value = 'Guardado correctamente'
    setTimeout(() => { exito.value = '' }, 5000)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

async function firmar() {
  if (!form.motivo_consulta) {
    error.value = 'El motivo de consulta es requerido para firmar'
    return
  }
  firmando.value = true
  error.value = ''
  exito.value = ''
  try {
    if (existe.value) {
      atencion.value = await api(`/app/emergencia/atenciones/${admisionId}`, {
        method: 'PATCH',
        body: form,
      })
    } else {
      atencion.value = await api(`/app/emergencia/atenciones/${admisionId}`, {
        method: 'POST',
        body: {
          ...form,
          diagnosticos: diagnosticos.value.map((d) => ({
            diagnostico_cie10_id: d.diagnostico_cie10_id,
            tipo: d.tipo,
          })),
        },
      })
      existe.value = true
    }
    atencion.value = await api(`/app/emergencia/atenciones/${admisionId}/firmar`, {
      method: 'POST',
    })
    exito.value = 'Atención firmada correctamente'
    const rutas: Record<string, string> = {
      HOSPITALIZACION: '/app/emergencia/observacion',
      INTERCONSULTA: '/app/emergencia/interconsultas',
      REFERENCIA: '/app/emergencia/referencias',
    }
    await navigateTo({ path: rutas[form.destino_atencion] || '/app/emergencia/atenciones', query: { tenant: route.query.tenant } })
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al firmar'
  } finally {
    firmando.value = false
  }
}

onMounted(async () => {
  try {
    const data = await api(`/app/emergencia/atenciones/${admisionId}`)
    existe.value = true
    atencion.value = data
    form.motivo_consulta = data.motivo_consulta || ''
    form.examen_clinico = data.examen_clinico || ''
    form.plan_tratamiento = data.plan_tratamiento || ''
    form.observaciones = data.observaciones || ''
    form.destino_atencion = data.destino_atencion || 'AMBULATORIA'
    diagnosticos.value = (data.diagnosticos || []).map((d: any) => ({
      diagnostico_cie10_id: d.diagnostico_cie10_id,
      codigo_cie10: d.codigo_cie10,
      descripcion: d.descripcion,
      tipo: d.tipo,
    }))
  } catch (e: any) {
    if (e?.status === 404) {
      existe.value = false
      try {
        const admisionData = await api(`/app/emergencia/admisiones/${admisionId}`)
        atencion.value = {
          paciente_nombre: admisionData.paciente_nombre,
          paciente_dni: admisionData.paciente_dni,
        }
        try {
          const triajeData = await api(`/app/emergencia/triaje/${admisionId}`)
          atencion.value.triaje = triajeData
        } catch {
          // Sin triaje
        }
      } catch (e2: any) {
        error.value = e2?.data?.detail || 'Error al cargar la admisión'
      }
    } else {
      error.value = e?.data?.detail || 'Error al cargar la atención'
    }
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
.emergencia-atencion-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.emergencia-atencion-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.emergencia-atencion-main {
  min-width: 0;
}

.emergencia-atencion-sidebar {
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

/* Error/Success Banners */
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

.patient-status {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.patient-status.firmado {
  background: var(--green-soft);
  color: var(--green);
}

.patient-status.pendiente {
  background: var(--amber-soft);
  color: var(--amber);
}

/* Triaje Summary */
.triaje-summary {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1rem 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-sm);
}

.triaje-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.triaje-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.triaje-prioridad {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  font-size: 0.75rem;
  font-weight: 700;
  color: white;
}

.prioridad-roja {
  background: var(--alert);
}

.prioridad-amber {
  background: var(--amber);
}

.prioridad-verde {
  background: var(--green);
}

.triaje-signos {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.signo-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.8125rem;
}

.signo-label {
  color: var(--ink-soft);
}

.signo-valor {
  font-weight: 500;
  color: var(--ink);
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
  font-size: 0.6875rem;
  color: var(--ink-soft);
  margin-top: 0.25rem;
}

/* CIE-10 Search */
.cie10-search {
  position: relative;
}

.cie10-results {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  max-height: 200px;
  overflow-y: auto;
  background: var(--paper);
  border: 1px solid var(--line);
  border-radius: 8px;
  margin-top: 0.25rem;
  z-index: 10;
  list-style: none;
  padding: 0;
  box-shadow: var(--shadow-lg);
}

.cie10-result-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: background 0.15s ease;
}

.cie10-result-item:hover {
  background: var(--mist);
}

.cie10-codigo {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--teal);
  flex-shrink: 0;
}

.cie10-descripcion {
  font-size: 0.8125rem;
  color: var(--ink);
}

/* Diagnóstico Item */
.diagnostico-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  background: var(--teal-soft);
  margin-top: 0.5rem;
}

.diagnostico-codigo {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--teal);
  flex-shrink: 0;
}

.diagnostico-descripcion {
  font-size: 0.8125rem;
  color: var(--ink);
  flex: 1;
}

.diagnostico-remove {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.125rem;
  border: none;
  background: transparent;
  color: var(--alert);
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.15s ease;
}

.diagnostico-remove:hover {
  background: var(--alert-soft);
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

.btn-firmar {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  background: var(--amber);
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-firmar:hover:not(:disabled) {
  background: var(--amber-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-firmar:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.firmado-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  background: var(--green-soft);
  color: var(--green);
  font-size: 0.875rem;
  font-weight: 500;
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

/* Status Badge Mini */
.status-badge-mini {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.status-firmado {
  background: var(--green-soft);
  color: var(--green);
}

.status-pendiente {
  background: var(--amber-soft);
  color: var(--amber);
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
  .emergencia-atencion-grid {
    grid-template-columns: 1fr;
  }

  .emergencia-atencion-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .emergencia-atencion-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .emergencia-atencion-sidebar {
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

  .patient-details {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .patient-separator {
    display: none;
  }

  .triaje-signos {
    flex-direction: column;
    gap: 0.25rem;
  }

  .cie10-results {
    position: static;
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

  .diagnostico-item {
    flex-wrap: wrap;
  }
}
</style>
