<template>
  <div class="paciente-create-container">
    <div class="paciente-create-grid">
      <!-- Main Content -->
      <div class="paciente-create-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="link('/app/gestion-pacientes/pacientes')" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-user-group" class="w-3.5 h-3.5" />
              Pacientes
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nuevo Paciente</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--teal)" />
            </div>
            <div>
              <h1 class="page-title">Registrar Paciente</h1>
              <p class="page-subtitle">Ingresa los datos del nuevo paciente</p>
            </div>
          </div>
        </div>

        <!-- Error Message -->
        <div v-if="error" class="error-banner">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
          {{ error }}
        </div>

        <div v-if="exito" class="error-banner" style="background: var(--green-soft, #d1fae5); color: var(--green, #059669);">
  <UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />
  {{ exito }}
</div>  

        <!-- Form Card -->
        <section class="form-card">
          <!-- Historia Clínica -->
          <div class="section-block">
            <div class="section-header">
              <div class="section-header-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h4 class="section-title">Datos de la Historia Clínica</h4>
                <p class="section-desc">Documento de identidad y número de historia</p>
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

              <div class="form-group" style="display: flex; align-items: flex-end; gap: 0.5rem;">
                <button
                  class="btn-search-dni"
                  :disabled="form.is_nn || !form.dni || buscandoDni"
                  @click="buscarPorDni"
                >
                  <UIcon v-if="buscandoDni" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-magnifying-glass" class="w-4 h-4" />
                  {{ buscandoDni ? 'Buscando...' : 'Buscar por DNI' }}
                </button>
              </div>

              <div class="form-group">
                <div class="checkbox-wrapper">
                  <input type="checkbox" v-model="form.is_nn" id="isNn" class="checkbox-custom" />
                  <label for="isNn" class="checkbox-label">No Identificado (NN)</label>
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Nro Historia</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-numbered-list" class="input-icon" />
                  <select v-model="modoHistoria" class="input-clinical">
                    <option value="automatica">Automática</option>
                    <option value="manual">Manual</option>
                  </select>
                </div>
              </div>

              <div v-if="modoHistoria === 'manual'" class="form-group">
                <label class="form-label">N° Historia Manual</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-pencil" class="input-icon" />
                  <input
                    type="text"
                    class="input-clinical"
                    placeholder="Número..."
                    disabled
                    title="Registro manual de historia aun no soportado por el backend"
                  />
                </div>
                <p class="field-hint-warning">
                  <UIcon name="i-heroicons-exclamation-triangle" class="w-3.5 h-3.5" />
                  El registro manual no está implementado — se generará automáticamente
                </p>
              </div>
            </div>
          </div>

          <!-- Datos del Paciente -->
          <div class="section-block">
            <div class="section-header">
              <div class="section-header-icon" style="background: var(--purple-soft)">
                <UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--purple)" />
              </div>
              <div>
                <h4 class="section-title">Datos del Paciente</h4>
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

          <!-- Ubicación Tabs -->
          <div class="section-block">
            <div class="tabs-container">
              <button
                type="button"
                class="tab-btn"
                :class="{ 'tab-active': tab === 'domicilio' }"
                @click="tab = 'domicilio'"
              >
                <UIcon name="i-heroicons-home" class="w-4 h-4" />
                Datos de Domicilio
              </button>
              <button
                type="button"
                class="tab-btn"
                :class="{ 'tab-active': tab === 'nacimiento' }"
                @click="tab = 'nacimiento'"
              >
                <UIcon name="i-heroicons-baby" class="w-4 h-4" />
                Datos de Nacimiento
              </button>
            </div>

            <!-- Domicilio -->
            <div v-show="tab === 'domicilio'" class="tab-content">
              <div class="form-grid">
                <div class="form-group">
                  <label class="form-label">Departamento</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-map-pin" class="input-icon" />
                    <select v-model="form.department_id" class="input-clinical" @change="onDeptoDomicilioChange">
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
                      :disabled="!provinciasDomicilio.length"
                      @change="onProvDomicilioChange"
                    >
                      <option value="">Seleccionar...</option>
                      <option v-for="p in provinciasDomicilio" :key="p.id" :value="p.id">{{ p.nombre }}</option>
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
                      :disabled="!distritosDomicilio.length"
                    >
                      <option value="">Seleccionar...</option>
                      <option v-for="d in distritosDomicilio" :key="d.id" :value="d.id">{{ d.nombre }}</option>
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

            <!-- Nacimiento -->
            <div v-show="tab === 'nacimiento'" class="tab-content">
              <div class="checkbox-wrapper">
                <input type="checkbox" v-model="form.birth_same_as_address" id="sameAddress" class="checkbox-custom" />
                <label for="sameAddress" class="checkbox-label">Igual que Domicilio</label>
              </div>

              <div v-if="!form.birth_same_as_address" class="form-grid mt-3">
                <div class="form-group">
                  <label class="form-label">Departamento</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-map-pin" class="input-icon" />
                    <select v-model="form.birth_department_id" class="input-clinical" @change="onDeptoNacimientoChange">
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
                      v-model="form.birth_province_id"
                      class="input-clinical"
                      :disabled="!provinciasNacimiento.length"
                      @change="onProvNacimientoChange"
                    >
                      <option value="">Seleccionar...</option>
                      <option v-for="p in provinciasNacimiento" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Distrito</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-map-pin" class="input-icon" />
                    <select
                      v-model="form.birth_district_id"
                      class="input-clinical"
                      :disabled="!distritosNacimiento.length"
                    >
                      <option value="">Seleccionar...</option>
                      <option v-for="d in distritosNacimiento" :key="d.id" :value="d.id">{{ d.nombre }}</option>
                    </select>
                  </div>
                </div>

                <div class="form-group">
                  <label class="form-label">Centro Poblado</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                    <input
                      v-model="form.birth_populated_center"
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
                      v-model="form.birth_country"
                      type="text"
                      class="input-clinical"
                      placeholder="Perú"
                    />
                  </div>
                </div>
              </div>
              <p v-else class="text-sm" style="color: var(--ink-soft)">
                <UIcon name="i-heroicons-check-circle" class="w-4 h-4" style="color: var(--teal)" />
                Se usarán los mismos datos del domicilio.
              </p>
            </div>
          </div>

          <!-- Preview Section -->
          <div v-if="form.first_name || form.last_name_paterno" class="preview-section">
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
                Nuevo paciente
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
                {{ guardando ? 'Guardando...' : 'Registrar Paciente' }}
              </button>
              <NuxtLink
                :to="link('/app/gestion-pacientes/pacientes')"
                class="btn-cancel"
              >
                Cancelar
              </NuxtLink>
            </div>
          </div>
        </section>
      </div>

      <!-- Sidebar Widgets -->
      <div class="paciente-create-sidebar">
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
                <span>El DNI se puede buscar para autocompletar</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>El número de historia se genera automáticamente</span>
              </li>
              <li class="info-item">
                <UIcon name="i-heroicons-check-circle" class="info-item-icon" style="color: var(--teal)" />
                <span>Para pacientes NN, dejar el DNI vacío</span>
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
              <span class="summary-label">Teléfono</span>
              <span class="summary-value">{{ form.phone || '—' }}</span>
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
                  Usa la búsqueda por DNI para autocompletar los datos del paciente
                  y evitar errores de digitación.
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
              <span class="stat-label">Estado</span>
              <span class="stat-number" :style="{ color: form.is_nn ? 'var(--amber)' : 'var(--green)' }">
                {{ form.is_nn ? 'NN' : 'Identificado' }}
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

const tab = ref<'domicilio' | 'nacimiento'>('domicilio')
const modoHistoria = ref<'automatica' | 'manual'>('automatica')
const error = ref('')
const guardando = ref(false)
const buscandoDni = ref(false)

const errors = reactive({
  first_name: '',
  last_name_paterno: '',
  last_name_materno: '',
  birth_date: '',
  gender: '',
})

const form = reactive({
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
  birth_same_as_address: true,
  birth_department_id: '',
  birth_province_id: '',
  birth_district_id: '',
  birth_populated_center: '',
  birth_country: 'Perú',
  insurance_type: '',
  insurance_number: '',
})

const departamentos = ref<any[]>([])
const provinciasDomicilio = ref<any[]>([])
const distritosDomicilio = ref<any[]>([])
const provinciasNacimiento = ref<any[]>([])
const distritosNacimiento = ref<any[]>([])

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

watch(() => form.is_nn, (isNn) => {
  if (isNn) { form.dni = '' }
})

onMounted(async () => {
  try {
    departamentos.value = await api('/app/gestion-pacientes/ubigeo/departamentos')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar departamentos'
  }
})

async function onDeptoDomicilioChange() {
  form.province_id = ''
  form.district_id = ''
  distritosDomicilio.value = []
  provinciasDomicilio.value = form.department_id
    ? await api(`/app/gestion-pacientes/ubigeo/provincias/${form.department_id}`)
    : []
}

async function onProvDomicilioChange() {
  form.district_id = ''
  distritosDomicilio.value = form.province_id
    ? await api(`/app/gestion-pacientes/ubigeo/distritos/${form.province_id}`)
    : []
}

async function onDeptoNacimientoChange() {
  form.birth_province_id = ''
  form.birth_district_id = ''
  distritosNacimiento.value = []
  provinciasNacimiento.value = form.birth_department_id
    ? await api(`/app/gestion-pacientes/ubigeo/provincias/${form.birth_department_id}`)
    : []
}

async function onProvNacimientoChange() {
  form.birth_district_id = ''
  distritosNacimiento.value = form.birth_province_id
    ? await api(`/app/gestion-pacientes/ubigeo/distritos/${form.birth_province_id}`)
    : []
}

async function buscarPorDni() {
  if (!form.dni || form.dni.length < 8) {
    error.value = 'Ingresa un DNI válido (8 dígitos)'
    return
  }
  buscandoDni.value = true
  error.value = ''
  try {
    // Verificar si ya existe en la BD
    const existente = await api(`/app/gestion-pacientes/dni/${form.dni}`)
    error.value = `Ya existe un paciente registrado con este documento: ${existente.full_name}`
    return
  } catch (e: any) {
    if (e?.status !== 404) {
      error.value = e?.data?.detail || 'Error al buscar'
      return
    }
  }
  try {
    const datos = await api(`/app/gestion-pacientes/dni-lookup/${form.dni}`)
    if (datos) {
      form.first_name = datos.first_name || form.first_name
      form.last_name_paterno = datos.last_name_paterno || form.last_name_paterno
      form.last_name_materno = datos.last_name_materno || form.last_name_materno
      if (datos.birth_date) form.birth_date = datos.birth_date
      if (datos.gender) form.gender = datos.gender
    }
  } catch (e: any) {
    // 404 es normal: no se encontró en el servicio externo
  } finally {
    buscandoDni.value = false
  }
}

function validar(): string | null {
  if (!form.is_nn && !form.dni) return 'El documento es obligatorio'
  if (!form.first_name) return 'El primer nombre es obligatorio'
  if (!form.last_name_paterno) return 'El apellido paterno es obligatorio'
  if (!form.last_name_materno) return 'El apellido materno es obligatorio'
  if (!form.birth_date) return 'La fecha de nacimiento es obligatoria'
  if (!form.gender) return 'El sexo es obligatorio'
  return null
}

const exito = ref('')

async function guardar() {
  const err = validar()
  if (err) {
    error.value = err
    return
  }
  error.value = ''
  exito.value = ''
  guardando.value = true
  try {
    const payload = {
      ...form,
      dni: form.is_nn ? null : form.dni,
      document_type: form.is_nn ? null : form.document_type,
    }
    const nuevo = await api('/app/gestion-pacientes/', {
      method: 'POST',
      body: payload,
    })
    exito.value = `Paciente registrado correctamente: ${nuevo.full_name} (HC: ${nuevo.record_number})`
    setTimeout(() => {
      navigateTo(link('/app/gestion-pacientes/pacientes'))
    }, 1800)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al registrar el paciente'
  } finally {
    guardando.value = false
  }

}
</script>

<style scoped>
.paciente-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.paciente-create-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.paciente-create-main {
  min-width: 0;
}

.paciente-create-sidebar {
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

.field-hint-warning {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--amber);
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

/* Search DNI Button */
.btn-search-dni {
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
  white-space: nowrap;
  height: 42px;
}

.btn-search-dni:hover:not(:disabled) {
  background: var(--teal-dark);
}

.btn-search-dni:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Tabs */
.tabs-container {
  display: flex;
  gap: 0.25rem;
  margin-bottom: 1.25rem;
  border-bottom: 1px solid var(--line);
}

.tab-btn {
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

.tab-btn:hover {
  color: var(--ink);
}

.tab-active {
  color: var(--teal);
  border-bottom-color: var(--teal);
}

.tab-content {
  padding-top: 0.5rem;
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
  .paciente-create-grid {
    grid-template-columns: 1fr;
  }

  .paciente-create-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .paciente-create-container {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .paciente-create-sidebar {
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

  .btn-search-dni {
    width: 100%;
    justify-content: center;
  }

  .tabs-container {
    flex-direction: column;
    gap: 0.25rem;
    border-bottom: none;
  }

  .tab-btn {
    border-bottom: 1px solid var(--line);
    border-radius: 0;
  }

  .tab-active {
    border-bottom-color: var(--teal);
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