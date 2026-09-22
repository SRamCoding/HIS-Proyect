?<template>
  <div class="paciente-edit-container">
    <div class="paciente-edit-grid">
      <!-- Main Content -->
      <div class="paciente-edit-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="link('/app/admision/pacientes')" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-user-group" class="w-3.5 h-3.5" />
              Pacientes
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Editar Paciente</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" :style="{ background: form.is_active !== false ? 'var(--teal-soft)' : 'var(--mist)' }">
              <UIcon
                name="i-heroicons-user"
                class="w-6 h-6"
                :style="{ color: form.is_active !== false ? 'var(--teal)' : 'var(--ink-soft)' }"
              />
            </div>
            <div>
              <h1 class="page-title">{{ form.first_name ? `${form.first_name} ${form.last_name_paterno}` : 'Editar Paciente' }}</h1>
              <p class="page-subtitle">
                <span class="dni-display font-mono-data">{{ form.is_nn ? 'NN' : form.dni || 'Sin DNI' }}</span>
                <span class="separator">·</span>
                <span class="gender-display">{{ form.gender === 'M' ? '♂ Masculino' : form.gender === 'F' ? '♀ Femenino' : '—' }}</span>
                <span class="separator">·</span>
                <span class="age-display">{{ form.birth_date ? calcularEdad(form.birth_date) : '—' }}</span>
              </p>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="cargando" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando información del paciente...</p>
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

          <!-- Form Card -->
          <section class="form-card">
            <!-- Datos de Identificación -->
            <div class="section-block">
              <div class="section-header">
                <div class="section-header-icon" style="background: var(--teal-soft)">
                  <UIcon name="i-heroicons-identification" class="w-4 h-4" style="color: var(--teal)" />
                </div>
                <div>
                  <h4 class="section-title">Identificación</h4>
                  <p class="section-desc">Documento de identidad del paciente</p>
                </div>
              </div>

              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">Tipo de Documento</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-identification" class="input-icon" />
                    <select v-model="form.document_type" class="input-clinical" :disabled="form.is_nn">
                      <option value="DNI">DNI</option>
                      <option value="CE">Carnet de Extranjería</option>
                      <option value="PASAPORTE">Pasaporte</option>
                      <option value="PARTIDA_NACIMIENTO">Partida de Nacimiento</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">N° Documento</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-barcode" class="input-icon" />
                    <input
                      v-model="form.dni"
                      type="text"
                      class="input-clinical font-mono-data"
                      placeholder="Número de documento..."
                      :disabled="form.is_nn"
                    />
                  </div>
                </div>

                <div class="form-group">
                  <div class="checkbox-wrapper">
                    <input type="checkbox" v-model="form.is_nn" id="isNn" class="checkbox-custom" />
                    <label for="isNn" class="checkbox-label">No Identificado (NN)</label>
                  </div>
                </div>
              </div>
            </div>

            <!-- Datos Personales -->
            <div class="section-block">
              <div class="section-header">
                <div class="section-header-icon" style="background: var(--purple-soft)">
                  <UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--purple)" />
                </div>
                <div>
                  <h4 class="section-title">Datos Personales</h4>
                  <p class="section-desc">Información personal del paciente</p>
                </div>
              </div>

              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">Apellido Paterno <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-user" class="input-icon" />
                    <input
                      v-model="form.last_name_paterno"
                      type="text"
                      class="input-clinical"
                      placeholder="Apellido Paterno"
                      :class="{ 'input-error': errors.last_name_paterno }"
                      @focus="errors.last_name_paterno = ''"
                    />
                  </div>
                  <span v-if="errors.last_name_paterno" class="error-message">{{ errors.last_name_paterno }}</span>
                </div>

                <div class="form-group">
                  <label class="form-label">Apellido Materno <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-user" class="input-icon" />
                    <input
                      v-model="form.last_name_materno"
                      type="text"
                      class="input-clinical"
                      placeholder="Apellido Materno"
                      :class="{ 'input-error': errors.last_name_materno }"
                      @focus="errors.last_name_materno = ''"
                    />
                  </div>
                  <span v-if="errors.last_name_materno" class="error-message">{{ errors.last_name_materno }}</span>
                </div>

                <div class="form-group">
                  <label class="form-label">Primer Nombre <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-user" class="input-icon" />
                    <input
                      v-model="form.first_name"
                      type="text"
                      class="input-clinical"
                      placeholder="Primer Nombre"
                      :class="{ 'input-error': errors.first_name }"
                      @focus="errors.first_name = ''"
                    />
                  </div>
                  <span v-if="errors.first_name" class="error-message">{{ errors.first_name }}</span>
                </div>

                <div class="form-group">
                  <label class="form-label">Segundo Nombre</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-user" class="input-icon" />
                    <input
                      v-model="form.second_name"
                      type="text"
                      class="input-clinical"
                      placeholder="Otros Nombres"
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Fecha de Nacimiento <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-calendar" class="input-icon" />
                    <input
                      v-model="form.birth_date"
                      type="date"
                      class="input-clinical"
                      :class="{ 'input-error': errors.birth_date }"
                      @change="errors.birth_date = ''"
                    />
                  </div>
                  <span v-if="errors.birth_date" class="error-message">{{ errors.birth_date }}</span>
                </div>

                <div class="form-group">
                  <label class="form-label">Sexo <span class="required">*</span></label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-arrows-right-left" class="input-icon" />
                    <select
                      v-model="form.gender"
                      class="input-clinical"
                      :class="{ 'input-error': errors.gender }"
                      @change="errors.gender = ''"
                    >
                      <option value="">Seleccionar...</option>
                      <option value="M">Masculino</option>
                      <option value="F">Femenino</option>
                    </select>
                  </div>
                  <span v-if="errors.gender" class="error-message">{{ errors.gender }}</span>
                </div>

                <div class="form-group">
                  <label class="form-label">Estado Civil</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-heart" class="input-icon" />
                    <select v-model="form.marital_status" class="input-clinical">
                      <option value="">No se sabe</option>
                      <option value="SOLTERO">Soltero(a)</option>
                      <option value="CASADO">Casado(a)</option>
                      <option value="VIUDO">Viudo(a)</option>
                      <option value="DIVORCIADO">Divorciado(a)</option>
                      <option value="CONVIVIENTE">Conviviente</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Grado de Instrucción</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-academic-cap" class="input-icon" />
                    <select v-model="form.education_level" class="input-clinical">
                      <option value="">Ninguno</option>
                      <option value="PRIMARIA">Primaria</option>
                      <option value="SECUNDARIA">Secundaria</option>
                      <option value="TECNICA">Técnica</option>
                      <option value="SUPERIOR">Superior</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Ocupación</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-briefcase" class="input-icon" />
                    <select v-model="form.occupation" class="input-clinical">
                      <option value="">Otros no especificados</option>
                      <option value="ESTUDIANTE">Estudiante</option>
                      <option value="EMPLEADO">Empleado</option>
                      <option value="INDEPENDIENTE">Independiente</option>
                      <option value="DESEMPLEADO">Desempleado</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Etnia</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-user-group" class="input-icon" />
                    <select v-model="form.ethnicity" class="input-clinical">
                      <option value="">No especifica</option>
                      <option value="MESTIZO">Mestizo</option>
                      <option value="INDIGENA">Indígena</option>
                      <option value="AFRODESCENDIENTE">Afrodescendiente</option>
                      <option value="BLANCO">Blanco</option>
                      <option value="OTRO">Otro</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Idioma</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-language" class="input-icon" />
                    <select v-model="form.language" class="input-clinical">
                      <option value="ESPANOL">Español</option>
                      <option value="QUECHUA">Quechua</option>
                      <option value="AIMARA">Aimara</option>
                      <option value="OTRO">Otro</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Teléfono</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-phone" class="input-icon" />
                    <input
                      v-model="form.phone"
                      type="text"
                      class="input-clinical"
                      placeholder="Teléfono"
                    />
                  </div>
                  <div class="checkbox-wrapper-small">
                    <input type="checkbox" v-model="form.phone_is_whatsapp" id="whatsapp" class="checkbox-custom-small" />
                    <label for="whatsapp" class="checkbox-label-small">WhatsApp</label>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Email</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-envelope" class="input-icon" />
                    <input
                      v-model="form.email"
                      type="email"
                      class="input-clinical"
                      placeholder="Correo electrónico"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Domicilio -->
            <div class="section-block">
              <div class="section-header">
                <div class="section-header-icon" style="background: var(--navy-soft)">
                  <UIcon name="i-heroicons-home" class="w-4 h-4" style="color: var(--navy)" />
                </div>
                <div>
                  <h4 class="section-title">Domicilio</h4>
                  <p class="section-desc">Ubicación del domicilio del paciente</p>
                </div>
              </div>

              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">Departamento</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-map-pin" class="input-icon" />
                    <select v-model="form.department_id" class="input-clinical" @change="onDeptoChange">
                      <option value="">Seleccionar...</option>
                      <option v-for="d in departamentos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Provincia</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-map-pin" class="input-icon" />
                    <select
                      v-model="form.province_id"
                      class="input-clinical"
                      :disabled="!provincias.length"
                      @change="onProvChange"
                    >
                      <option value="">Seleccionar...</option>
                      <option v-for="p in provincias" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Distrito</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-map-pin" class="input-icon" />
                    <select
                      v-model="form.district_id"
                      class="input-clinical"
                      :disabled="!distritos.length"
                    >
                      <option value="">Seleccionar...</option>
                      <option v-for="d in distritos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Centro Poblado</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                    <input
                      v-model="form.populated_center"
                      type="text"
                      class="input-clinical"
                      placeholder="No indica"
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">País</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-globe-alt" class="input-icon" />
                    <input
                      v-model="form.country"
                      type="text"
                      class="input-clinical"
                      placeholder="Perú"
                    />
                  </div>
                </div>

                <div class="form-group full-width">
                  <label class="form-label">Dirección</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-home-modern" class="input-icon" style="top: 0.75rem; transform: none;" />
                    <input
                      v-model="form.address"
                      type="text"
                      class="input-clinical"
                      placeholder="Dirección completa"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Seguro -->
            <div class="section-block">
              <div class="section-header">
                <div class="section-header-icon" style="background: var(--amber-soft)">
                  <UIcon name="i-heroicons-shield-check" class="w-4 h-4" style="color: var(--amber)" />
                </div>
                <div>
                  <h4 class="section-title">Seguro</h4>
                  <p class="section-desc">Información del seguro del paciente</p>
                </div>
              </div>

              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">Tipo de Seguro</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-shield-check" class="input-icon" />
                    <input
                      v-model="form.insurance_type"
                      type="text"
                      class="input-clinical"
                      placeholder="SIS, EsSalud, Particular..."
                    />
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">N° de Seguro</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-barcode" class="input-icon" />
                    <input
                      v-model="form.insurance_number"
                      type="text"
                      class="input-clinical font-mono-data"
                      placeholder="Número de seguro"
                    />
                  </div>
                </div>
              </div>
            </div>

            <!-- Preview Section -->
            <div class="preview-section">
              <h4 class="preview-title">Vista Previa</h4>
              <div class="preview-card">
                <div class="preview-avatar" :style="{ background: getPatientColor(form.first_name + ' ' + form.last_name_paterno) }">
                  <span>{{ getInitials(form.first_name + ' ' + form.last_name_paterno) }}</span>
                </div>
                <div class="preview-info">
                  <span class="preview-name">{{ form.first_name }} {{ form.last_name_paterno }} {{ form.last_name_materno }}</span>
                  <span class="preview-detail">
                    <span class="preview-dni">{{ form.is_nn ? 'NN' : form.dni || 'Sin DNI' }}</span>
                    <span class="preview-gender">{{ form.gender === 'M' ? '♂' : form.gender === 'F' ? '♀' : '—' }}</span>
                    <span class="preview-age">{{ form.birth_date ? calcularEdad(form.birth_date) : '—' }}</span>
                  </span>
                </div>
                <span class="preview-status preview-active">
                  <span class="preview-dot dot-active" />
                  En edición
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
                  {{ guardando ? 'Guardando...' : 'Guardar Cambios' }}
                </button>
                <NuxtLink
                  :to="link('/app/admision/pacientes')"
                  class="btn-cancel"
                >
                  Cancelar
                </NuxtLink>
              </div>
            </div>
          </section>
        </template>
      </div>

      <!-- Sidebar Widgets -->
      <div class="paciente-edit-sidebar">
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
                <span>Los campos con * son obligatorios</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El DNI no se puede modificar si el paciente está identificado</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>La edad se calcula automáticamente</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Los cambios se reflejan en todos los módulos</span>
              </li>
            </ul>
          </div>
        </div>

        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="summary-item">
              <span class="summary-label">Paciente</span>
              <span class="summary-value">{{ form.first_name ? `${form.first_name} ${form.last_name_paterno}` : '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">DNI</span>
              <span class="summary-value font-mono-data">{{ form.is_nn ? 'NN' : form.dni || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Sexo</span>
              <span class="summary-value">{{ form.gender === 'M' ? 'Masculino' : form.gender === 'F' ? 'Femenino' : '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Edad</span>
              <span class="summary-value">{{ form.birth_date ? calcularEdad(form.birth_date) : '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Seguro</span>
              <span class="summary-value">{{ form.insurance_type || '—' }}</span>
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
                  Verifica que los datos del paciente sean correctos antes de 
                  guardar, especialmente el DNI y la fecha de nacimiento.
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats Widget -->
        <div class="widget widget-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--purple)" />
            <h4 class="widget-title">Estado</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Identificación</span>
              <span class="stat-number" :style="{ color: form.is_nn ? 'var(--amber)' : 'var(--green)' }">
                {{ form.is_nn ? 'NN' : 'Identificado' }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Campos completos</span>
              <span class="stat-number">{{ filledFields }}/{{ totalFields }}</span>
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

const patientId = route.params.id as string

const cargando = ref(true)
const guardando = ref(false)
const error = ref('')
const exito = ref('')

const errors = reactive({
  first_name: '',
  last_name_paterno: '',
  last_name_materno: '',
  birth_date: '',
  gender: '',
})

const form = reactive<any>({
  document_type: 'DNI',
  dni: '',
  is_nn: false,
  first_name: '',
  second_name: '',
  last_name_paterno: '',
  last_name_materno: '',
  birth_date: '',
  gender: '',
  marital_status: '',
  education_level: '',
  occupation: '',
  ethnicity: '',
  language: 'ESPANOL',
  phone: '',
  phone_is_whatsapp: false,
  email: '',
  address: '',
  department_id: '',
  province_id: '',
  district_id: '',
  populated_center: '',
  country: 'Perú',
  insurance_type: '',
  insurance_number: '',
  is_active: true,
})

const departamentos = ref<any[]>([])
const provincias = ref<any[]>([])
const distritos = ref<any[]>([])

const filledFields = computed(() => {
  let count = 0
  if (form.first_name) count++
  if (form.last_name_paterno) count++
  if (form.last_name_materno) count++
  if (form.birth_date) count++
  if (form.gender) count++
  if (!form.is_nn && form.dni) count++
  if (form.phone) count++
  if (form.address) count++
  if (form.department_id) count++
  if (form.insurance_type) count++
  return count
})

const totalFields = 10

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
  // --pink-soft y --blue-soft no existen en el sistema de variables (ver
  // assets/css/main.css) -- mismo bug corregido en pacientes/index.vue.
  const colors = [
    'var(--teal-soft)',
    'var(--purple-soft)',
    'var(--navy-soft)',
    'var(--amber-soft)',
    'var(--green-soft)',
    'var(--orange-soft)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const calcularEdad = (fecha: string) => {
  if (!fecha) return '—'
  const hoy = new Date()
  const nacimiento = new Date(fecha)
  let edad = hoy.getFullYear() - nacimiento.getFullYear()
  const mes = hoy.getMonth() - nacimiento.getMonth()
  if (mes < 0 || (mes === 0 && hoy.getDate() < nacimiento.getDate())) {
    edad--
  }
  return `${edad} año${edad !== 1 ? 's' : ''}`
}

async function onDeptoChange() {
  form.province_id = ''
  form.district_id = ''
  distritos.value = []
  provincias.value = form.department_id
    ? await api(`/app/admision/ubigeo/provincias/${form.department_id}`)
    : []
}

async function onProvChange() {
  form.district_id = ''
  distritos.value = form.province_id
    ? await api(`/app/admision/ubigeo/distritos/${form.province_id}`)
    : []
}

const validateForm = (): boolean => {
  let valid = true
  if (!form.first_name) {
    errors.first_name = 'El primer nombre es requerido'
    valid = false
  }
  if (!form.last_name_paterno) {
    errors.last_name_paterno = 'El apellido paterno es requerido'
    valid = false
  }
  if (!form.last_name_materno) {
    errors.last_name_materno = 'El apellido materno es requerido'
    valid = false
  }
  if (!form.birth_date) {
    errors.birth_date = 'La fecha de nacimiento es requerida'
    valid = false
  }
  if (!form.gender) {
    errors.gender = 'El sexo es requerido'
    valid = false
  }
  return valid
}

async function guardar() {
  if (!validateForm()) return

  error.value = ''
  exito.value = ''
  guardando.value = true
  try {
    const payload = {
      ...form,
      dni: form.is_nn ? null : form.dni,
    }
    await api(`/app/admision/${patientId}`, {
      method: 'PATCH',
      body: payload,
    })
    exito.value = 'Cambios guardados correctamente'
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar cambios'
  } finally {
    guardando.value = false
  }
}

onMounted(async () => {
  try {
    const [paciente, deptos] = await Promise.all([
      api(`/app/admision/${patientId}`),
      api('/app/admision/ubigeo/departamentos'),
    ])
    departamentos.value = deptos

    // Cargar datos del paciente
    Object.keys(form).forEach((key) => {
      if (paciente[key] !== undefined && paciente[key] !== null) {
        form[key] = paciente[key]
      }
    })

    // Cargar cascada de ubigeo
    if (form.department_id) {
      provincias.value = await api(`/app/admision/ubigeo/provincias/${form.department_id}`)
    }
    if (form.province_id) {
      distritos.value = await api(`/app/admision/ubigeo/distritos/${form.province_id}`)
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar el paciente'
  } finally {
    cargando.value = false
  }
})
</script>

<style scoped>
/* Colores y tipografía: heredados de .app-shell (assets/css/hospital-theme.css). */
.paciente-edit-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.paciente-edit-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.paciente-edit-main {
  min-width: 0;
}

.paciente-edit-sidebar {
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

.dni-display {
  font-weight: 500;
}

.separator {
  color: var(--line);
}

.gender-display {
  font-weight: 500;
}

.age-display {
  color: var(--teal);
  font-weight: 500;
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

/* Section Block */
.section-block {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.section-block:first-of-type {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.section-header-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.section-desc {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
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
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
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

/* Checkbox */
.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0;
}

.checkbox-wrapper-small {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-top: 0.25rem;
}

.checkbox-custom {
  accent-color: var(--teal);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.checkbox-custom-small {
  accent-color: var(--teal);
  width: 14px;
  height: 14px;
  cursor: pointer;
}

.checkbox-label {
  font-size: 0.8125rem;
  color: var(--ink);
  cursor: pointer;
}

.checkbox-label-small {
  font-size: 0.75rem;
  color: var(--ink-soft);
  cursor: pointer;
}

/* Preview Section */
.preview-section {
  margin-top: 1.5rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.preview-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
  margin: 0 0 0.75rem 0;
}

.preview-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  background: var(--paper);
  flex-wrap: wrap;
}

.preview-avatar {
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

.preview-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 120px;
}

.preview-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.preview-detail {
  display: flex;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.preview-dni {
  font-family: monospace;
}

.preview-gender {
  font-weight: 500;
}

.preview-age {
  color: var(--teal);
}

.preview-status {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
  flex-shrink: 0;
}

.preview-active {
  background: var(--green-soft);
  color: var(--green);
}

.preview-dot {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  display: inline-block;
}

.dot-active {
  background: var(--green);
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
  .paciente-edit-grid {
    grid-template-columns: 1fr;
  }

  .paciente-edit-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .paciente-edit-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .paciente-edit-sidebar {
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

  .preview-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .preview-info {
    min-width: auto;
    width: 100%;
  }

  .preview-detail {
    flex-wrap: wrap;
  }
}

@media (max-width: 480px) {
  .preview-card {
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

  .checkbox-wrapper {
    flex-wrap: wrap;
  }
}
</style>