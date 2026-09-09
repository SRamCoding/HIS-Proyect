?<template>
  <div class="atencion-create-container">
    <div class="atencion-create-grid">
      <!-- Main Content -->
      <div class="atencion-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="link('/app/consulta-externa/atenciones-medicas')" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-clipboard-document-list" class="w-3.5 h-3.5" />
              Atenciones Médicas
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">{{ existeAtencion ? 'Editar Atención' : 'Registrar Atención' }}</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" :style="{ background: firmado ? 'var(--green-soft)' : 'var(--teal-soft)' }">
              <UIcon
                name="i-heroicons-clipboard-document"
                class="w-6 h-6"
                :style="{ color: firmado ? 'var(--green)' : 'var(--teal)' }"
              />
            </div>
            <div>
              <h1 class="page-title">{{ atencion.paciente_nombre || 'Atención Médica' }}</h1>
              <p class="page-subtitle">
                <span class="especialidad-display">{{ atencion.especialidad_nombre || atencion.servicio_nombre || 'Sin especialidad' }}</span>
                <span class="separator">·</span>
                <span class="estado-display" :class="firmado ? 'estado-firmado' : 'estado-pendiente'">
                  {{ firmado ? '✓ Firmada' : 'Pendiente de firma' }}
                </span>
              </p>
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

          <!-- Patient Info Card -->
          <section class="form-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h3 class="card-title">Información del Paciente</h3>
                <p class="card-subtitle">Datos generales de la atención médica</p>
              </div>
            </div>

            <div class="info-grid">
              <div class="info-item">
                <span class="info-label">Paciente</span>
                <span class="info-value">{{ atencion.paciente_nombre || '—' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">DNI</span>
                <span class="info-value font-mono-data">{{ atencion.paciente_dni || '—' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Edad</span>
                <span class="info-value">{{ atencion.paciente_edad || '—' }} años</span>
              </div>
              <div class="info-item">
                <span class="info-label">Médico</span>
                <span class="info-value">{{ atencion.medico_nombre || '—' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Especialidad</span>
                <span class="info-value">{{ atencion.especialidad_nombre || atencion.servicio_nombre || '—' }}</span>
              </div>
              <div class="info-item">
                <span class="info-label">Estado</span>
                <span class="info-value">
                  <span class="status-badge-mini" :class="firmado ? 'status-firmado-mini' : 'status-pendiente-mini'">
                    {{ firmado ? 'Firmada' : 'Pendiente' }}
                  </span>
                </span>
              </div>
            </div>
          </section>

          <!-- Antecedentes Card -->
          <section class="form-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--purple-soft)">
                <UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: var(--purple)" />
              </div>
              <div>
                <h3 class="card-title">Antecedentes Personales</h3>
                <p class="card-subtitle">Historial clínico del paciente</p>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Quirúrgico</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-scissors" class="input-icon" />
                  <textarea
                    v-model="antecedentes.antecedente_quirurgico"
                    rows="2"
                    class="input-clinical"
                    :disabled="firmado"
                    placeholder="Procedimientos quirúrgicos previos..."
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Patológico</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-beaker" class="input-icon" />
                  <textarea
                    v-model="antecedentes.antecedente_patologico"
                    rows="2"
                    class="input-clinical"
                    :disabled="firmado"
                    placeholder="Enfermedades crónicas o patologías..."
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Alergias</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-exclamation-circle" class="input-icon" />
                  <textarea
                    v-model="antecedentes.antecedente_alergias"
                    rows="2"
                    class="input-clinical"
                    :disabled="firmado"
                    placeholder="Alergias conocidas..."
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Obstétricos</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-heart" class="input-icon" />
                  <input
                    v-model="antecedentes.antecedentes_obstetricos"
                    class="input-clinical"
                    :disabled="firmado"
                    placeholder="G:0 P:0-0-0-0"
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Familiares</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-users" class="input-icon" />
                  <textarea
                    v-model="antecedentes.antecedente_familiares"
                    rows="2"
                    class="input-clinical"
                    :disabled="firmado"
                    placeholder="Antecedentes familiares relevantes..."
                  />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Otros</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" />
                  <textarea
                    v-model="antecedentes.antecedente_otros"
                    rows="2"
                    class="input-clinical"
                    :disabled="firmado"
                    placeholder="Otra información relevante..."
                  />
                </div>
              </div>
            </div>

            <div v-if="!firmado" class="form-actions-sub">
              <button class="btn-secondary" :disabled="guardandoAntecedentes" @click="guardarAntecedentes">
                <UIcon v-if="guardandoAntecedentes" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                {{ guardandoAntecedentes ? 'Guardando...' : 'Guardar Antecedentes' }}
              </button>
            </div>
          </section>

          <!-- Signos Vitales Card (read-only) -->
          <section class="form-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--blue-soft)">
                <UIcon name="i-heroicons-heart" class="w-4 h-4" style="color: var(--blue)" />
              </div>
              <div>
                <h3 class="card-title">Signos Vitales</h3>
                <p class="card-subtitle">Datos registrados en el triaje</p>
              </div>
            </div>

            <div v-if="atencion.triaje" class="vitales-grid">
              <div class="vital-item">
                <span class="vital-label">Presión Arterial</span>
                <span class="vital-value font-mono-data">{{ atencion.triaje.presion_sistolica || '—' }}/{{ atencion.triaje.presion_diastolica || '—' }}</span>
              </div>
              <div class="vital-item">
                <span class="vital-label">Temperatura</span>
                <span class="vital-value font-mono-data">{{ atencion.triaje.temperatura || '—' }} °C</span>
              </div>
              <div class="vital-item">
                <span class="vital-label">Frec. Cardiaca</span>
                <span class="vital-value font-mono-data">{{ atencion.triaje.frecuencia_cardiaca || '—' }}</span>
              </div>
              <div class="vital-item">
                <span class="vital-label">Frec. Respiratoria</span>
                <span class="vital-value font-mono-data">{{ atencion.triaje.frecuencia_respiratoria || '—' }}</span>
              </div>
              <div class="vital-item">
                <span class="vital-label">Peso</span>
                <span class="vital-value font-mono-data">{{ atencion.triaje.peso || '—' }} kg</span>
              </div>
              <div class="vital-item">
                <span class="vital-label">Talla</span>
                <span class="vital-value font-mono-data">{{ atencion.triaje.talla || '—' }} cm</span>
              </div>
              <div class="vital-item">
                <span class="vital-label">IMC</span>
                <span class="vital-value font-mono-data">{{ atencion.triaje.imc || '—' }}</span>
              </div>
              <div class="vital-item">
                <span class="vital-label">SO₂</span>
                <span class="vital-value font-mono-data">{{ atencion.triaje.saturacion_o2 || '—' }}%</span>
              </div>
            </div>
            <div v-else class="warning-message">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" style="color: var(--amber)" />
              <span style="color: var(--amber)">⚠️ No se registró triaje para esta cita.</span>
            </div>
          </section>

          <!-- Datos Clínicos Card -->
          <section class="form-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-clipboard-document" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h3 class="card-title">Datos Clínicos</h3>
                <p class="card-subtitle">Información médica de la atención</p>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group full-width">
                <label class="form-label">Motivo de Consulta <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.motivo_consulta"
                    rows="3"
                    class="input-clinical"
                    :class="{ 'input-error': errors.motivo_consulta }"
                    :disabled="firmado"
                    placeholder="Motivo por el cual el paciente acude a consulta..."
                  />
                </div>
                <span v-if="errors.motivo_consulta" class="error-message">{{ errors.motivo_consulta }}</span>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Examen Clínico</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-magnifying-glass" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.examen_clinico"
                    rows="4"
                    class="input-clinical"
                    :disabled="firmado"
                    placeholder="Hallazgos del examen clínico..."
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
                </div>
                <ul v-if="resultadosCie10.length" class="cie10-results">
                  <li v-for="r in resultadosCie10" :key="r.id" class="cie10-result-item" @click="agregarDiagnostico(r)">
                    <span class="cie10-result-code">[{{ r.codigo_cie10 }}]</span>
                    <span class="cie10-result-desc">{{ r.descripcion }}</span>
                    <span class="cie10-result-add">
                      <UIcon name="i-heroicons-plus-circle" class="w-4 h-4" style="color: var(--teal)" />
                    </span>
                  </li>
                </ul>
                <div v-if="diagnosticosSeleccionados.length" class="diagnosticos-list">
                  <div v-for="(dx, idx) in diagnosticosSeleccionados" :key="idx" class="diagnostico-item">
                    <div class="diagnostico-info">
                      <span class="diagnostico-code">[{{ dx.codigo_cie10 }}]</span>
                      <span class="diagnostico-desc">{{ dx.descripcion }}</span>
                    </div>
                    <div class="diagnostico-actions">
                      <select v-model="dx.tipo" class="diagnostico-tipo" :disabled="firmado">
                        <option value="presuntivo">Presuntivo</option>
                        <option value="definitivo">Definitivo</option>
                        <option value="repetitivo">Repetitivo</option>
                      </select>
                      <button v-if="!firmado" class="diagnostico-remove" @click="diagnosticosSeleccionados.splice(idx, 1)">
                        <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Plan de Tratamiento</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.plan_tratamiento"
                    rows="3"
                    class="input-clinical"
                    :disabled="firmado"
                    placeholder="Plan de tratamiento y manejo del paciente..."
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Observaciones</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                  <textarea
                    v-model="form.observaciones"
                    rows="2"
                    class="input-clinical"
                    :disabled="firmado"
                    placeholder="Observaciones adicionales..."
                  />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Destino de Atención</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-arrow-right-circle" class="input-icon" />
                  <select v-model="form.destino_atencion" class="input-clinical" :disabled="firmado">
                    <option value="ALTA">Alta / Domicilio</option>
                    <option value="HOSPITALIZACION">Hospitalización</option>
                    <option value="REFERENCIA">Referencia</option>
                    <option value="INTERCONSULTA">Interconsulta</option>
                    <option value="LABORATORIO">Laboratorio</option>
                    <option value="IMAGEN">Imágenes</option>
                    <option value="FARMACIA">Farmacia</option>
                  </select>
                </div>
              </div>
            </div>
          </section>

          <!-- ============================================ -->
          <!-- RECETA DE FARMACIA (Componente) -->
          <!-- ============================================ -->
          <AtencionMedicaRecetaFarmacia
            v-if="form.destino_atencion === 'FARMACIA' && existeAtencion"
            :cita-id="citaId"
            :receta-existente="recetaExistente"
            @receta-generada="recetaExistente = $event"
            @error="error = $event"
          />

          <!-- ============================================ -->
          <!-- HOSPITALIZACIÓN (Componente) -->
          <!-- ============================================ -->
          <AtencionMedicaHospitalizacion 
            v-if="form.destino_atencion === 'HOSPITALIZACION' && existeAtencion"
            :cita-id="citaId"
            :hospitalizacion-existente="hospitalizacionExistente"
            :camas-disponibles="camasDisponibles"
            :especialidades-ingreso="especialidadesIngreso"
            @hospitalizacion-registrada="hospitalizacionExistente = $event"
            @alta-registrada="handleAltaRegistrada"
            @error="error = $event"
          />

          <AtencionMedicaOrdenLaboratorio
  v-if="form.destino_atencion === 'LABORATORIO' && existeAtencion"
  :cita-id="citaId"
  @generada="exito = 'Orden de laboratorio generada correctamente'"
/>


<AtencionMedicaOrdenImagen v-if="form.destino_atencion === 'IMAGEN' && existeAtencion" :cita-id="citaId" @generada="exito = 'Orden de imagen generada correctamente'" />
<AtencionMedicaInterconsultaForm v-if="form.destino_atencion === 'INTERCONSULTA' && existeAtencion" :cita-id="citaId" @generada="exito = 'Interconsulta generada correctamente'" />

<AtencionMedicaReferenciaForm v-if="form.destino_atencion === 'REFERENCIA' && existeAtencion" :cita-id="citaId" @generada="exito = 'Referencia generada correctamente'" />

          <!-- Actions -->
          <section class="form-card" style="margin-bottom: 0;">
            <div class="form-actions">
              <div class="action-group">
                <NuxtLink
                  :to="link('/app/consulta-externa/atenciones-medicas')"
                  class="btn-cancel"
                >
                  <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
                  Volver
                </NuxtLink>
                <button
                  v-if="!firmado"
                  class="btn-primary"
                  :disabled="guardando"
                  @click="guardar"
                >
                  <UIcon v-if="guardando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                  {{ guardando ? 'Guardando...' : (existeAtencion ? 'Guardar Cambios' : 'Registrar Atención') }}
                </button>
                <button
                  v-if="existeAtencion && !firmado"
                  class="btn-firmar"
                  :disabled="firmando"
                  @click="firmarAtencion"
                >
                  <UIcon v-if="firmando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check-badge" class="w-4 h-4" />
                  {{ firmando ? 'Firmando...' : 'Firmar Atención' }}
                </button>
                <span v-if="firmado" class="firmado-badge">
                  <UIcon name="i-heroicons-check-circle" class="w-4 h-4" style="color: var(--green)" />
                  Firmado el {{ new Date(atencion.firmado_at).toLocaleString('es-PE') }}
                </span>
              </div>
            </div>
          </section>
        </template>
      </div>

      <!-- Sidebar Widgets -->
      <div class="atencion-create-sidebar">
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
                <span>El motivo de consulta es obligatorio</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los antecedentes se guardan en el perfil del paciente</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los diagnósticos se buscan en el catálogo CIE-10</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Firmar la atención bloquea la edición</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Si el destino es Farmacia, podrás generar la receta</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Si el destino es Hospitalización, podrás asignar cama</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Resumen de la Atención</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Paciente</span>
              <span class="summary-value">{{ atencion.paciente_nombre || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Motivo</span>
              <span class="summary-value">{{ form.motivo_consulta ? truncateText(form.motivo_consulta, 30) : '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Diagnósticos</span>
              <span class="summary-value">{{ diagnosticosSeleccionados.length }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Destino</span>
              <span class="summary-value">{{ getDestinoLabel(form.destino_atencion) }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Estado</span>
              <span class="summary-value">
                <span class="status-badge-mini" :class="firmado ? 'status-firmado-mini' : 'status-pendiente-mini'">
                  {{ firmado ? 'Firmada' : 'Pendiente' }}
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
                  Completa todos los campos clínicos antes de firmar la atención. 
                  Una vez firmada, no se podrá modificar la información.
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
              <span class="stat-label">Diagnósticos</span>
              <span class="stat-number">{{ diagnosticosSeleccionados.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Estado</span>
              <span class="stat-number" :style="{ color: firmado ? 'var(--green)' : 'var(--amber)' }">
                {{ firmado ? '✓ Firmada' : 'Pendiente' }}
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
const citaId = route.params.id as string

// Estado
const cargando = ref(true)
const guardando = ref(false)
const firmando = ref(false)
const guardandoAntecedentes = ref(false)
const error = ref('')
const exito = ref('')
const existeAtencion = ref(false)
const atencion = ref<any>({})
const patientId = ref('')

// Computed
const firmado = computed(() => atencion.value?.estado === 'firmado')

// Errores
const errors = reactive({
  motivo_consulta: '',
})

// Formulario
const form = reactive({
  motivo_consulta: '',
  examen_clinico: '',
  plan_tratamiento: '',
  observaciones: '',
  destino_atencion: 'ALTA',
})

// Antecedentes
const antecedentes = reactive({
  antecedente_quirurgico: '',
  antecedente_patologico: '',
  antecedente_alergias: '',
  antecedentes_obstetricos: '',
  antecedente_familiares: '',
  antecedente_otros: '',
})

// Diagnósticos
const diagnosticosSeleccionados = ref<any[]>([])
const buscaCie10 = ref('')
const resultadosCie10 = ref<any[]>([])
let debounceTimer: any = null

// Receta de Farmacia
const recetaExistente = ref<any>(null)

// Hospitalización
const hospitalizacionExistente = ref<any>(null)
const camasDisponibles = ref<any[]>([])
const especialidadesIngreso = ref<any[]>([])

// Computed
const filledFields = computed(() => {
  let count = 0
  if (form.motivo_consulta) count++
  if (form.examen_clinico) count++
  if (form.plan_tratamiento) count++
  if (form.observaciones) count++
  if (form.destino_atencion) count++
  return count
})

const totalFields = 5

// Helpers
const getDestinoLabel = (destino: string) => {
  const map: Record<string, string> = {
    'ALTA': 'Alta / Domicilio',
    'HOSPITALIZACION': 'Hospitalización',
    'REFERENCIA': 'Referencia',
    'INTERCONSULTA': 'Interconsulta',
    'LABORATORIO': 'Laboratorio',
    'IMAGEN': 'Imágenes',
    'FARMACIA': 'Farmacia'
  }
  return map[destino] || destino
}

const truncateText = (text: string, max: number) => {
  if (!text) return '—'
  return text.length > max ? text.substring(0, max) + '...' : text
}

// CIE-10
function buscarCie10Debounced() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (buscaCie10.value.length < 2) { resultadosCie10.value = []; return }
    try {
      resultadosCie10.value = await api(`/app/consulta-externa/atenciones-medicas/cie10/buscar?q=${encodeURIComponent(buscaCie10.value)}`)
    } catch (e) { /* silencioso */ }
  }, 300)
}

function agregarDiagnostico(dx: any) {
  if (diagnosticosSeleccionados.value.some((d) => d.diagnostico_cie10_id === dx.id)) return
  diagnosticosSeleccionados.value.push({
    diagnostico_cie10_id: dx.id,
    codigo_cie10: dx.codigo_cie10,
    descripcion: dx.descripcion,
    tipo: 'definitivo'
  })
  buscaCie10.value = ''
  resultadosCie10.value = []
}

function handleAltaRegistrada(data: any) {
  hospitalizacionExistente.value = data
  exito.value = '✅ Alta registrada. La cama quedó disponible.'
  setTimeout(() => {
    navigateTo(link('/app/consulta-externa/atenciones-medicas'))
  }, 2000)
}

// Validación
function validar(): boolean {
  let valid = true
  if (!form.motivo_consulta) {
    errors.motivo_consulta = 'El motivo de consulta es obligatorio'
    valid = false
  } else {
    errors.motivo_consulta = ''
  }
  return valid
}

// Funciones
async function guardarAntecedentes() {
  guardandoAntecedentes.value = true
  error.value = ''
  exito.value = ''
  try {
    await api(`/app/admision/${patientId.value}`, { method: 'PATCH', body: antecedentes })
    exito.value = 'Antecedentes actualizados correctamente'
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar antecedentes'
  } finally {
    guardandoAntecedentes.value = false
  }
}

async function guardar() {
  if (!validar()) return

  error.value = ''
  exito.value = ''
  guardando.value = true
  try {
    if (existeAtencion.value) {
      atencion.value = await api(`/app/consulta-externa/atenciones-medicas/${citaId}`, { method: 'PATCH', body: form })
    } else {
      const payload = {
        ...form,
        diagnosticos: diagnosticosSeleccionados.value.map((d) => ({
          diagnostico_cie10_id: d.diagnostico_cie10_id,
          tipo: d.tipo
        }))
      }
      atencion.value = await api(`/app/consulta-externa/atenciones-medicas/${citaId}`, { method: 'POST', body: payload })
      existeAtencion.value = true
    }
    exito.value = 'Guardado correctamente'
    setTimeout(() => { exito.value = '' }, 3000)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar'
  } finally {
    guardando.value = false
  }
}

async function firmarAtencion() {
  firmando.value = true
  error.value = ''
  exito.value = ''
  try {
    atencion.value = await api(`/app/consulta-externa/atenciones-medicas/${citaId}/firmar`, { method: 'POST' })
    exito.value = '✅ Atención firmada correctamente. Ya no se puede editar.'
    setTimeout(() => {
      navigateTo(link('/app/consulta-externa/atenciones-medicas'))
    }, 2000)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al firmar'
  } finally {
    firmando.value = false
  }
}

// Lifecycle
onMounted(async () => {
  try {
    const cita = await api(`/app/consulta-externa/citas/${citaId}`)
    patientId.value = cita.patient_id

    try {
      const data = await api(`/app/consulta-externa/atenciones-medicas/${citaId}`)
      existeAtencion.value = true
      atencion.value = data
      form.motivo_consulta = data.motivo_consulta
      form.examen_clinico = data.examen_clinico || ''
      form.plan_tratamiento = data.plan_tratamiento || ''
      form.observaciones = data.observaciones || ''
      form.destino_atencion = data.destino_atencion
      diagnosticosSeleccionados.value = data.diagnosticos.map((d: any) => ({
        diagnostico_cie10_id: d.diagnostico_cie10_id,
        codigo_cie10: d.codigo_cie10,
        descripcion: d.descripcion,
        tipo: d.tipo
      }))
      antecedentes.antecedente_quirurgico = data.antecedente_quirurgico || ''
      antecedentes.antecedente_patologico = data.antecedente_patologico || ''
      antecedentes.antecedente_alergias = data.antecedente_alergias || ''
      antecedentes.antecedentes_obstetricos = data.antecedentes_obstetricos || ''
      antecedentes.antecedente_familiares = data.antecedente_familiares || ''
      antecedentes.antecedente_otros = data.antecedente_otros || ''

      // Cargar Receta si aplica
      if (data.destino_atencion === 'FARMACIA') {
        try {
          recetaExistente.value = await api(`/app/consulta-externa/farmacia/recetas/${citaId}`)
        } catch { /* aun no tiene receta generada */ }
      }

      // Cargar Hospitalización si aplica
      if (data.destino_atencion === 'HOSPITALIZACION') {
        try {
          hospitalizacionExistente.value = await api(`/app/consulta-externa/hospitalizacion/${citaId}`)
        } catch { /* aun no tiene hospitalizacion */ }
        try {
          camasDisponibles.value = await api('/app/consulta-externa/hospitalizacion/camas-disponibles')
          especialidadesIngreso.value = await api('/app/consulta-externa/programacion-medica/especialidades')
        } catch { /* silencioso */ }
      }
    } catch (e: any) {
      if (e?.status === 404) {
        existeAtencion.value = false
        atencion.value = {
          paciente_nombre: cita.paciente_nombre,
          paciente_dni: cita.paciente_dni,
          medico_nombre: cita.medico_nombre,
          especialidad_nombre: cita.especialidad_nombre,
          triaje: null
        }
        const paciente = await api(`/app/admision/${cita.patient_id}`)
        atencion.value.paciente_edad = paciente.age
        antecedentes.antecedente_quirurgico = paciente.antecedente_quirurgico || ''
        antecedentes.antecedente_patologico = paciente.antecedente_patologico || ''
        antecedentes.antecedente_alergias = paciente.antecedente_alergias || ''
        antecedentes.antecedentes_obstetricos = paciente.antecedentes_obstetricos || ''
        antecedentes.antecedente_familiares = paciente.antecedente_familiares || ''
        antecedentes.antecedente_otros = paciente.antecedente_otros || ''
        try {
          const triajeData = await api(`/app/consulta-externa/triaje/${citaId}`)
          atencion.value.triaje = triajeData
        } catch { /* sin triaje */ }
      } else {
        error.value = e?.data?.detail || 'Error al cargar la atención'
      }
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar la cita'
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
/* ============================================
   Estilos principales
   ============================================ */
.atencion-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.atencion-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.atencion-create-main {
  min-width: 0;
}

.atencion-create-sidebar {
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
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.especialidad-display {
  font-weight: 500;
}

.separator {
  color: var(--line);
}

.estado-display {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
}

.estado-firmado {
  background: var(--green-soft);
  color: var(--green);
}

.estado-pendiente {
  background: var(--amber-soft);
  color: var(--amber);
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

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  padding: 1rem;
  border-radius: var(--radius);
  background: var(--mist);
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.6875rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
}

.info-value {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

/* Vitales Grid */
.vitales-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 0.75rem;
  padding: 0.5rem 0;
}

.vital-item {
  display: flex;
  flex-direction: column;
  padding: 0.5rem;
  border-radius: var(--radius);
  background: var(--mist);
}

.vital-label {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.vital-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.warning-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  background: var(--amber-soft);
  border: 1px solid var(--amber-soft);
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
  background: var(--mist);
  color: var(--ink-soft);
  cursor: not-allowed;
}

.input-clinical.input-error {
  border-color: var(--alert);
}

.input-clinical.input-error:focus {
  box-shadow: 0 0 0 3px var(--alert-soft);
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

/* CIE-10 Search */
.cie10-search {
  margin-bottom: 0.5rem;
}

.cie10-results {
  list-style: none;
  padding: 0;
  margin: 0 0 0.75rem 0;
  border: 1px solid var(--line);
  border-radius: 6px;
  max-height: 200px;
  overflow-y: auto;
}

.cie10-result-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: background 0.15s ease;
  border-bottom: 1px solid var(--line);
}

.cie10-result-item:last-child {
  border-bottom: none;
}

.cie10-result-item:hover {
  background: var(--mist);
}

.cie10-result-code {
  font-weight: 600;
  color: var(--teal);
  font-size: 0.75rem;
  flex-shrink: 0;
}

.cie10-result-desc {
  flex: 1;
  font-size: 0.8125rem;
  color: var(--ink);
}

.cie10-result-add {
  flex-shrink: 0;
}

/* Diagnosticos List */
.diagnosticos-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.diagnostico-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--line);
  background: var(--paper);
  flex-wrap: wrap;
}

.diagnostico-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
}

.diagnostico-code {
  font-weight: 600;
  color: var(--teal);
  font-size: 0.75rem;
  flex-shrink: 0;
}

.diagnostico-desc {
  font-size: 0.8125rem;
  color: var(--ink);
}

.diagnostico-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.diagnostico-tipo {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  border: 1px solid var(--line);
  background: var(--paper);
  font-size: 0.6875rem;
  color: var(--ink);
}

.diagnostico-remove {
  background: transparent;
  border: none;
  color: var(--alert);
  cursor: pointer;
  padding: 0.25rem;
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

.form-actions-sub {
  margin-top: 1rem;
  padding-top: 1rem;
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
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover:not(:disabled) {
  background: var(--mist);
}

.btn-secondary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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

.firmado-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 8px;
  background: var(--green-soft);
  color: var(--green);
  font-size: 0.8125rem;
  font-weight: 500;
}

/* Status Badge Mini */
.status-badge-mini {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.status-firmado-mini {
  background: var(--green-soft);
  color: var(--green);
}

.status-pendiente-mini {
  background: var(--amber-soft);
  color: var(--amber);
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

/* ============================================
   Estilos para componentes hijos (se importan o se copian)
   ============================================ */
/* Los estilos de RecetaFarmacia y Hospitalizacion 
   se mantienen en sus propios componentes */

/* Responsive */
@media (max-width: 1024px) {
  .atencion-create-grid {
    grid-template-columns: 1fr;
  }

  .atencion-create-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .atencion-create-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .info-grid {
    grid-template-columns: 1fr 1fr;
  }

  .vitales-grid {
    grid-template-columns: 1fr 1fr;
  }

  .atencion-create-sidebar {
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

  .page-subtitle {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }

  .diagnostico-item {
    flex-direction: column;
    align-items: flex-start;
  }

  .diagnostico-actions {
    width: 100%;
    justify-content: flex-start;
  }
}

@media (max-width: 480px) {
  .info-grid {
    grid-template-columns: 1fr;
  }

  .vitales-grid {
    grid-template-columns: 1fr;
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

  .cie10-result-item {
    flex-wrap: wrap;
  }
}
</style>