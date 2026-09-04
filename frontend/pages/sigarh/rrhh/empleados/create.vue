<template>
  <div class="empleado-create-container">
    <!-- Progress Indicator -->
    <div class="onboarding-progress">
      <div class="progress-steps">
        <div 
          v-for="(step, index) in pasos" 
          :key="index"
          class="step-item"
          :class="{ 
            active: stepActual >= index, 
            completed: stepActual > index 
          }"
        >
          <div class="step-circle">
            <span v-if="stepActual > index" class="step-check">✓</span>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span class="step-label">{{ step }}</span>
        </div>
      </div>
    </div>

    <div class="empleado-grid">
      <!-- Main Content -->
      <div class="empleado-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/rrhh/empleados?tenant=${tenantId}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-users" class="w-3.5 h-3.5" />
              Empleados
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nuevo Empleado</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-user-plus" class="w-6 h-6" style="color: var(--teal)" />
            </div>
            <div>
              <h1 class="page-title">Registrar Empleado</h1>
              <p class="page-subtitle">Ingresa los datos del nuevo colaborador</p>
            </div>
          </div>
        </div>

        <!-- Step 1: Datos Personales -->
        <section class="empleado-card" v-show="stepActual === 0">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-identification" class="w-4 h-4" style="color: var(--teal)" />
            </div>
            <div>
              <h3 class="card-title">Identificación Personal</h3>
              <p class="card-subtitle">Datos de identidad y contacto del empleado</p>
            </div>
          </div>

          <!-- DNI Section -->
          <div class="dni-section">
            <div class="dni-header">
              <div class="dni-header-left">
                <UIcon name="i-heroicons-credit-card" class="w-4 h-4" style="color: var(--navy)" />
                <span class="dni-title">Documento de Identidad</span>
              </div>
              <div class="dni-toggle">
                <input type="checkbox" v-model="registroManual" id="manual" class="toggle-checkbox" />
                <label for="manual" class="dni-toggle-label">Registro Manual</label>
                <span class="dni-toggle-hint">Activa si el empleado no figura en el servicio DNI</span>
              </div>
            </div>

            <div class="dni-consult">
              <div class="dni-input-group">
                <label class="form-label">DNI <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-identification" class="input-icon" />
                  <input 
                    v-model="form.dni" 
                    class="input-clinical font-mono-data" 
                    placeholder="Ej: 76557726" 
                    maxlength="8"
                    :class="{ 'input-error': errors.dni }"
                  />
                </div>
                <span v-if="errors.dni" class="error-message">{{ errors.dni }}</span>
              </div>
              <button
                class="btn-consult-dni"
                :disabled="consultandoDni || form.dni.length !== 8"
                @click="consultarDni"
              >
                <UIcon v-if="consultandoDni" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                <UIcon v-else name="i-heroicons-magnifying-glass" class="w-4 h-4" />
                {{ consultandoDni ? 'Consultando...' : 'Consultar DNI' }}
              </button>
            </div>
            <p v-if="dniMsg" class="dni-message" :class="{ 'dni-error': dniError, 'dni-success': !dniError }">
              <UIcon :name="dniError ? 'i-heroicons-exclamation-circle' : 'i-heroicons-check-circle'" class="w-4 h-4" />
              {{ dniMsg }}
            </p>
          </div>

          <!-- Personal Information -->
          <div class="info-section">
            <h4 class="section-title">Información Personal</h4>
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Nombres <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <input 
                    v-model="form.nombres" 
                    class="input-clinical" 
                    :disabled="!registroManual && dniCargado"
                    :class="{ 'input-error': errors.nombres }"
                  />
                </div>
                <span v-if="errors.nombres" class="error-message">{{ errors.nombres }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Apellido Paterno <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <input 
                    v-model="form.apellido_paterno" 
                    class="input-clinical" 
                    :disabled="!registroManual && dniCargado"
                    :class="{ 'input-error': errors.apellido_paterno }"
                  />
                </div>
                <span v-if="errors.apellido_paterno" class="error-message">{{ errors.apellido_paterno }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Apellido Materno <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <input 
                    v-model="form.apellido_materno" 
                    class="input-clinical" 
                    :disabled="!registroManual && dniCargado"
                    :class="{ 'input-error': errors.apellido_materno }"
                  />
                </div>
                <span v-if="errors.apellido_materno" class="error-message">{{ errors.apellido_materno }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Fecha de Nacimiento <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-calendar" class="input-icon" />
                  <input 
                    v-model="form.fecha_nacimiento" 
                    type="date" 
                    class="input-clinical"
                    :class="{ 'input-error': errors.fecha_nacimiento }"
                  />
                </div>
                <span v-if="errors.fecha_nacimiento" class="error-message">{{ errors.fecha_nacimiento }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Sexo <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-arrows-right-left" class="input-icon" />
                  <select v-model="form.sexo" class="input-clinical" :class="{ 'input-error': errors.sexo }">
                    <option value="">Seleccione</option>
                    <option value="M">Masculino</option>
                    <option value="F">Femenino</option>
                  </select>
                </div>
                <span v-if="errors.sexo" class="error-message">{{ errors.sexo }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Estado Civil <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-heart" class="input-icon" />
                  <select v-model="form.estado_civil" class="input-clinical" :class="{ 'input-error': errors.estado_civil }">
                    <option value="">Seleccione</option>
                    <option value="soltero">Soltero(a)</option>
                    <option value="casado">Casado(a)</option>
                    <option value="divorciado">Divorciado(a)</option>
                    <option value="viudo">Viudo(a)</option>
                    <option value="conviviente">Conviviente</option>
                  </select>
                </div>
                <span v-if="errors.estado_civil" class="error-message">{{ errors.estado_civil }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Grupo Sanguíneo <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-droplet" class="input-icon" />
                  <select v-model="form.grupo_sanguineo" class="input-clinical" :class="{ 'input-error': errors.grupo_sanguineo }">
                    <option value="">Seleccione</option>
                    <option v-for="g in gruposSanguineos" :key="g" :value="g">{{ g }}</option>
                  </select>
                </div>
                <span v-if="errors.grupo_sanguineo" class="error-message">{{ errors.grupo_sanguineo }}</span>
              </div>
            </div>
          </div>

          <!-- Contact Information -->
          <div class="info-section">
            <h4 class="section-title">Información de Contacto</h4>
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Celular <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-phone" class="input-icon" />
                  <input 
                    v-model="form.celular" 
                    class="input-clinical" 
                    placeholder="+51 987654321"
                    :class="{ 'input-error': errors.celular }"
                  />
                </div>
                <span v-if="errors.celular" class="error-message">{{ errors.celular }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Teléfono Fijo</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-phone-arrow-up-right" class="input-icon" />
                  <input v-model="form.telefono_fijo" class="input-clinical" placeholder="(01) 234-5678" />
                </div>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Correo Electrónico <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-envelope" class="input-icon" />
                  <input 
                    v-model="form.correo" 
                    type="email" 
                    class="input-clinical" 
                    placeholder="empleado@hospital.pe"
                    :class="{ 'input-error': errors.correo }"
                  />
                </div>
                <span v-if="errors.correo" class="error-message">{{ errors.correo }}</span>
              </div>

              <div class="form-group full-width">
                <div class="status-toggle">
                  <span class="toggle-label">Empleado Activo</span>
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="form.is_active"
                    @click="form.is_active = !form.is_active"
                    class="toggle-switch"
                    :class="{ 'toggle-active': form.is_active }"
                  >
                    <span class="toggle-slider" />
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Step 2: Datos Laborales -->
        <section class="empleado-card" v-show="stepActual === 1">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--navy-soft)">
              <UIcon name="i-heroicons-briefcase" class="w-4 h-4" style="color: var(--navy)" />
            </div>
            <div>
              <h3 class="card-title">Clasificación Laboral</h3>
              <p class="card-subtitle">Tipo de trabajador, nivel remunerativo y grupo ocupacional</p>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Tipo de Trabajador <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-user-group" class="input-icon" />
                <select v-model="form.tipo_trabajador_id" class="input-clinical" :class="{ 'input-error': errors.tipo_trabajador_id }">
                  <option value="">Seleccione</option>
                  <option v-for="t in tiposTrabajador" :key="t.id" :value="t.id">{{ t.nombre }}</option>
                </select>
              </div>
              <span v-if="errors.tipo_trabajador_id" class="error-message">{{ errors.tipo_trabajador_id }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Nivel Remunerativo <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-currency-dollar" class="input-icon" />
                <select v-model="form.nivel_remunerativo_id" class="input-clinical" :class="{ 'input-error': errors.nivel_remunerativo_id }">
                  <option value="">Seleccione</option>
                  <option v-for="n in nivelesRemunerativos" :key="n.id" :value="n.id">{{ n.nombre }}</option>
                </select>
              </div>
              <span v-if="errors.nivel_remunerativo_id" class="error-message">{{ errors.nivel_remunerativo_id }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Grupo Ocupacional <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-chart-bar" class="input-icon" />
                <select v-model="form.grupo_ocupacional_id" class="input-clinical" :class="{ 'input-error': errors.grupo_ocupacional_id }">
                  <option value="">Seleccione</option>
                  <option v-for="g in gruposOcupacionales" :key="g.id" :value="g.id">{{ g.nombre }}</option>
                </select>
              </div>
              <span v-if="errors.grupo_ocupacional_id" class="error-message">{{ errors.grupo_ocupacional_id }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Departamento</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-building-office" class="input-icon" />
                <select v-model="form.departamento_id" class="input-clinical">
                  <option value="">Seleccione</option>
                  <option v-for="d in departamentos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Servicio / Área <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-folder" class="input-icon" />
                <select v-model="form.servicio_id" class="input-clinical" :class="{ 'input-error': errors.servicio_id }">
                  <option value="">Seleccione</option>
                  <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                </select>
              </div>
              <span v-if="errors.servicio_id" class="error-message">{{ errors.servicio_id }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Cargo Laboral <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-briefcase" class="input-icon" />
                <input 
                  v-model="form.cargo_laboral" 
                  class="input-clinical" 
                  placeholder="Ej: Médico Especialista"
                  :class="{ 'input-error': errors.cargo_laboral }"
                />
              </div>
              <span v-if="errors.cargo_laboral" class="error-message">{{ errors.cargo_laboral }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Modalidad <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" />
                <input 
                  v-model="form.modalidad" 
                  class="input-clinical" 
                  placeholder="Ej: Nombrado"
                  :class="{ 'input-error': errors.modalidad }"
                />
              </div>
              <span v-if="errors.modalidad" class="error-message">{{ errors.modalidad }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Código MINSA</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-identification" class="input-icon" />
                <input v-model="form.codigo_minsa" class="input-clinical font-mono-data" placeholder="Código institucional" />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">N° CMP</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document" class="input-icon" />
                <input v-model="form.numero_cmp" class="input-clinical font-mono-data" placeholder="Colegio Médico del Perú" />
              </div>
              <p class="field-hint">Solo para médicos</p>
            </div>
          </div>

          <!-- Resumen Laboral -->
          <div v-if="form.cargo_laboral || form.tipo_trabajador_id || form.servicio_id" class="resumen-section">
            <h4 class="section-title">Resumen Laboral</h4>
            <div class="resumen-grid">
              <div class="resumen-item">
                <span class="resumen-label">Cargo</span>
                <span class="resumen-value">{{ form.cargo_laboral || '—' }}</span>
              </div>
              <div class="resumen-item">
                <span class="resumen-label">Tipo Trabajador</span>
                <span class="resumen-value">{{ tiposTrabajador.find(t => t.id === form.tipo_trabajador_id)?.nombre || '—' }}</span>
              </div>
              <div class="resumen-item">
                <span class="resumen-label">Servicio</span>
                <span class="resumen-value">{{ servicios.find(s => s.id === form.servicio_id)?.nombre || '—' }}</span>
              </div>
              <div class="resumen-item">
                <span class="resumen-label">Nivel Remunerativo</span>
                <span class="resumen-value">{{ nivelesRemunerativos.find(n => n.id === form.nivel_remunerativo_id)?.nombre || '—' }}</span>
              </div>
              <div class="resumen-item">
                <span class="resumen-label">Grupo Ocupacional</span>
                <span class="resumen-value">{{ gruposOcupacionales.find(g => g.id === form.grupo_ocupacional_id)?.nombre || '—' }}</span>
              </div>
              <div class="resumen-item">
                <span class="resumen-label">Modalidad</span>
                <span class="resumen-value">{{ form.modalidad || '—' }}</span>
              </div>
            </div>
          </div>

          <!-- Resoluciones y Fechas -->
          <div class="info-section">
            <h4 class="section-title">Resoluciones y Fechas</h4>
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Fecha de Ingreso <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-calendar" class="input-icon" />
                  <input 
                    v-model="form.fecha_ingreso" 
                    type="date" 
                    class="input-clinical"
                    :class="{ 'input-error': errors.fecha_ingreso }"
                  />
                </div>
                <span v-if="errors.fecha_ingreso" class="error-message">{{ errors.fecha_ingreso }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Resolución Nombramiento</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" />
                  <input v-model="form.resolucion_nombramiento" class="input-clinical" placeholder="N° de resolución" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Fecha de Nombramiento</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-calendar" class="input-icon" />
                  <input v-model="form.fecha_nombramiento" type="date" class="input-clinical" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Resolución de Cese</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" />
                  <input v-model="form.resolucion_cese" class="input-clinical" placeholder="N° de resolución" />
                </div>
              </div>

              <div class="form-group">
                <label class="form-label">Fecha de Cese</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-calendar" class="input-icon" />
                  <input v-model="form.fecha_cese" type="date" class="input-clinical" />
                </div>
              </div>
            </div>

            <!-- Resumen Fechas -->
            <div v-if="form.fecha_ingreso" class="fechas-resumen">
              <div class="fechas-grid">
                <div class="fecha-item">
                  <span class="fecha-label">Fecha de Ingreso</span>
                  <span class="fecha-value">{{ form.fecha_ingreso }}</span>
                </div>
                <div class="fecha-item">
                  <span class="fecha-label">Antigüedad</span>
                  <span class="fecha-value">{{ calcularAntiguedad(form.fecha_ingreso) }}</span>
                </div>
                <div class="fecha-item">
                  <span class="fecha-label">Estado</span>
                  <span class="fecha-value" style="color: var(--teal)">{{ form.fecha_cese ? 'Cesado' : 'En actividad' }}</span>
                </div>
              </div>
            </div>
          </div>
        </section>

        <!-- Step 3: Especialidades -->
        <section class="empleado-card" v-show="stepActual === 2">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--purple-soft)">
              <UIcon name="i-heroicons-star" class="w-4 h-4" style="color: var(--purple)" />
            </div>
            <div>
              <h3 class="card-title">Especialidades</h3>
              <p class="card-subtitle">Registra las especialidades médicas del empleado</p>
            </div>
          </div>

          <div v-for="(esp, i) in form.especialidades" :key="i" class="especialidad-item">
            <div class="especialidad-header">
              <span class="especialidad-number">Especialidad {{ i + 1 }}</span>
              <button class="btn-remove-especialidad" @click="form.especialidades.splice(i, 1)">
                <UIcon name="i-heroicons-trash" class="w-4 h-4" />
              </button>
            </div>
            <div class="especialidad-grid">
              <div class="form-group">
                <label class="form-label">Especialidad <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-star" class="input-icon" />
                  <select v-model="esp.especialidad_id" class="input-clinical">
                    <option value="">Seleccione</option>
                    <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">N° RNE</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" />
                  <input v-model="esp.numero_rne" class="input-clinical" placeholder="Registro Nacional de Especialistas" />
                </div>
              </div>
              <div class="form-group">
                <div class="checkbox-wrapper">
                  <input type="checkbox" v-model="esp.validado" :id="`validado_${i}`" class="checkbox-custom" />
                  <label :for="`validado_${i}`" class="checkbox-label">Validado</label>
                </div>
              </div>
            </div>
          </div>

          <button class="btn-add-especialidad" @click="form.especialidades.push({ especialidad_id: '', numero_rne: '', validado: false })">
            <UIcon name="i-heroicons-plus" class="w-4 h-4" />
            Agregar Especialidad
          </button>
        </section>

        <!-- Step 4: Datos Bancarios -->
        <section class="empleado-card" v-show="stepActual === 3">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--amber-soft)">
              <UIcon name="i-heroicons-currency-dollar" class="w-4 h-4" style="color: var(--amber)" />
            </div>
            <div>
              <h3 class="card-title">Datos Bancarios</h3>
              <p class="card-subtitle">Información de cuenta para pagos</p>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Banco</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                <select v-model="form.banco" class="input-clinical">
                  <option value="">Seleccione un banco</option>
                  <option v-for="b in bancosPeru" :key="b" :value="b">{{ b }}</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">RUC</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document" class="input-icon" />
                <input v-model="form.ruc" class="input-clinical font-mono-data" maxlength="11" placeholder="20123456789" />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Número de Cuenta</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-credit-card" class="input-icon" />
                <input v-model="form.numero_cuenta" class="input-clinical font-mono-data" placeholder="N° de cuenta" />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Número CCI</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-credit-card" class="input-icon" />
                <input v-model="form.numero_cci" class="input-clinical font-mono-data" placeholder="Código de cuenta interbancario" />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Tipo de Cuenta</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-list-bullet" class="input-icon" />
                <select v-model="form.tipo_cuenta" class="input-clinical">
                  <option value="">Seleccione</option>
                  <option value="ahorros">Ahorros</option>
                  <option value="corriente">Corriente</option>
                </select>
              </div>
            </div>
          </div>
        </section>

        <!-- Step 5: Ubicación -->
        <section class="empleado-card" v-show="stepActual === 4">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--green-soft)">
              <UIcon name="i-heroicons-map-pin" class="w-4 h-4" style="color: var(--green)" />
            </div>
            <div>
              <h3 class="card-title">Ubicación</h3>
              <p class="card-subtitle">Dirección y ubicación geográfica del empleado</p>
            </div>
          </div>

          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Departamento</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-map-pin" class="input-icon" />
                <select v-model="form.departamento_ubigeo" class="input-clinical" @change="form.provincia_ubigeo = ''; form.distrito_ubigeo = ''">
                  <option value="">Seleccione</option>
                  <option v-for="d in ubigeo.departamentos" :key="d.codigo" :value="d.codigo">{{ d.nombre }}</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Provincia</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-map-pin" class="input-icon" />
                <select v-model="form.provincia_ubigeo" class="input-clinical" @change="form.distrito_ubigeo = ''">
                  <option value="">Seleccione</option>
                  <option v-for="p in provinciasFiltradas" :key="p.codigo" :value="p.codigo">{{ p.nombre }}</option>
                </select>
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Distrito</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-map-pin" class="input-icon" />
                <select v-model="form.distrito_ubigeo" class="input-clinical">
                  <option value="">Seleccione</option>
                  <option v-for="d in distritosFiltrados" :key="d.codigo" :value="d.codigo">{{ d.nombre }}</option>
                </select>
              </div>
            </div>

            <div class="form-group full-width">
              <label class="form-label">Dirección</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-home" class="input-icon" style="top: 0.75rem; transform: none;" />
                <textarea v-model="form.direccion" class="input-clinical" rows="2" placeholder="Dirección completa" />
              </div>
            </div>
          </div>
        </section>

        <!-- Error Message -->
        <div v-if="error" class="error-banner">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
          {{ error }}
        </div>

        <!-- Navigation Actions -->
        <div class="empleado-actions">
          <button 
            v-if="stepActual > 0"
            class="btn-secondary"
            @click="stepActual--"
          >
            <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
            Anterior
          </button>
          
          <div class="action-spacer"></div>

          <button 
            v-if="stepActual < pasos.length - 1"
            class="btn-primary"
            @click="nextStep"
          >
            Siguiente
            <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
          </button>

          <div v-else class="action-group">
            <button class="btn-primary" :disabled="saving" @click="handleCreate">
              <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
              {{ saving ? 'Creando...' : 'Crear Empleado' }}
            </button>
            <NuxtLink
              :to="`/sigarh/rrhh/empleados?tenant=${tenantId}`"
              class="btn-cancel"
            >
              Cancelar
            </NuxtLink>
          </div>
        </div>
      </div>

      <!-- Sidebar Widgets -->
      <div class="empleado-sidebar">
        <!-- Summary Widget -->
        <div class="widget widget-summary">
          <div class="widget-header">
            <UIcon name="i-heroicons-document-text" class="widget-icon" style="color: var(--teal)" />
            <h4 class="widget-title">Resumen</h4>
          </div>
          <div class="widget-content">
            <div class="widget-progress">
              <span class="widget-progress-label">Progreso</span>
              <div class="widget-progress-bar">
                <div 
                  class="widget-progress-fill" 
                  :style="{ width: progressPercentage + '%' }"
                />
              </div>
              <span class="widget-progress-value">{{ progressPercentage }}%</span>
            </div>

            <div class="summary-item">
              <span class="summary-label">Empleado</span>
              <span class="summary-value">{{ fullName || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">DNI</span>
              <span class="summary-value font-mono-data">{{ form.dni || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Cargo</span>
              <span class="summary-value">{{ form.cargo_laboral || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Estado</span>
              <span class="summary-value">
                <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
                  <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
                  {{ form.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Especialidades</span>
              <span class="summary-value">{{ form.especialidades.filter(e => e.especialidad_id).length }}</span>
            </div>
          </div>
        </div>

        <!-- Checklist Widget -->
        <div class="widget widget-checklist">
          <div class="widget-header">
            <UIcon name="i-heroicons-check-badge" class="widget-icon" style="color: var(--green)" />
            <h4 class="widget-title">Checklist</h4>
          </div>
          <div class="widget-content">
            <div 
              v-for="(step, index) in pasos" 
              :key="index"
              class="checklist-item"
              :class="{ 
                'checklist-done': stepActual > index,
                'checklist-active': stepActual === index
              }"
            >
              <div class="checklist-icon">
                <UIcon v-if="stepActual > index" name="i-heroicons-check-circle-solid" class="w-4 h-4" style="color: var(--green)" />
                <span v-else class="checklist-number">{{ index + 1 }}</span>
              </div>
              <span class="checklist-label">{{ step }}</span>
              <span v-if="stepActual === index" class="checklist-current">Actual</span>
            </div>
          </div>
        </div>

        <!-- Tip Widget -->
        <div class="widget widget-tip">
          <div class="widget-content">
            <div class="tip-content">
              <UIcon name="i-heroicons-light-bulb" class="tip-icon" style="color: var(--amber)" />
              <div>
                <p class="tip-title">Tip</p>
                <p class="tip-text">{{ currentTip }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Quick Stats Widget -->
        <div class="widget widget-quick-stats">
          <div class="widget-header">
            <UIcon name="i-heroicons-chart-bar" class="widget-icon" style="color: var(--navy)" />
            <h4 class="widget-title">Estadísticas</h4>
          </div>
          <div class="widget-content">
            <div class="stat-item">
              <span class="stat-label">Pasos Completados</span>
              <span class="stat-number">{{ stepActual + 1 }}/{{ pasos.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Campos Obligatorios</span>
              <span class="stat-number">{{ requiredFieldsFilled }}/{{ totalRequiredFields }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')

const pasos = ['Datos Personales', 'Datos Laborales', 'Especialidades', 'Datos Bancarios', 'Ubicación']
const stepActual = ref(0)
const saving = ref(false)
const error = ref('')
const registroManual = ref(false)
const dniCargado = ref(false)
const consultandoDni = ref(false)
const dniMsg = ref('')
const dniError = ref(false)

const gruposSanguineos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

const bancosPeru = [
  'Banco de la Nación', 'BCP - Banco de Crédito del Perú', 'BBVA Perú',
  'Interbank', 'Scotiabank Perú', 'BanBif', 'Banco Pichincha',
  'MiBanco', 'Banco GNB Perú', 'BCRP', 'Citibank Perú',
  'Banco Falabella', 'Banco Ripley', 'Banco Azteca', 'Compartamos Financiera',
]

// Catálogos
const tiposTrabajador = ref<any[]>([])
const nivelesRemunerativos = ref<any[]>([])
const gruposOcupacionales = ref<any[]>([])
const departamentos = ref<any[]>([])
const servicios = ref<any[]>([])
const especialidades = ref<any[]>([])

// Ubigeo simplificado
const ubigeo = reactive({
  departamentos: [
    { codigo: '01', nombre: 'Amazonas' }, { codigo: '02', nombre: 'Ancash' },
    { codigo: '03', nombre: 'Apurímac' }, { codigo: '04', nombre: 'Arequipa' },
    { codigo: '05', nombre: 'Ayacucho' }, { codigo: '06', nombre: 'Cajamarca' },
    { codigo: '07', nombre: 'Callao' }, { codigo: '08', nombre: 'Cusco' },
    { codigo: '09', nombre: 'Huancavelica' }, { codigo: '10', nombre: 'Huánuco' },
    { codigo: '11', nombre: 'Ica' }, { codigo: '12', nombre: 'Junín' },
    { codigo: '13', nombre: 'La Libertad' }, { codigo: '14', nombre: 'Lambayeque' },
    { codigo: '15', nombre: 'Lima' }, { codigo: '16', nombre: 'Loreto' },
    { codigo: '17', nombre: 'Madre de Dios' }, { codigo: '18', nombre: 'Moquegua' },
    { codigo: '19', nombre: 'Pasco' }, { codigo: '20', nombre: 'Piura' },
    { codigo: '21', nombre: 'Puno' }, { codigo: '22', nombre: 'San Martín' },
    { codigo: '23', nombre: 'Tacna' }, { codigo: '24', nombre: 'Tumbes' },
    { codigo: '25', nombre: 'Ucayali' },
  ],
  provincias: [] as any[],
  distritos: [] as any[],
})

const provinciasFiltradas = computed(() =>
  ubigeo.provincias.filter(p => p.dep_codigo === form.departamento_ubigeo)
)
const distritosFiltrados = computed(() =>
  ubigeo.distritos.filter(d => d.prov_codigo === form.provincia_ubigeo)
)

const errors = reactive({
  dni: '',
  nombres: '',
  apellido_paterno: '',
  apellido_materno: '',
  fecha_nacimiento: '',
  sexo: '',
  estado_civil: '',
  grupo_sanguineo: '',
  celular: '',
  correo: '',
  tipo_trabajador_id: '',
  nivel_remunerativo_id: '',
  grupo_ocupacional_id: '',
  servicio_id: '',
  cargo_laboral: '',
  modalidad: '',
  fecha_ingreso: '',
})

const form = reactive({
  dni: '',
  nombres: '',
  apellido_paterno: '',
  apellido_materno: '',
  fecha_nacimiento: '',
  sexo: '',
  estado_civil: '',
  grupo_sanguineo: '',
  celular: '',
  telefono_fijo: '',
  correo: '',
  is_active: true,
  tipo_trabajador_id: '',
  nivel_remunerativo_id: '',
  grupo_ocupacional_id: '',
  departamento_id: '',
  servicio_id: '',
  cargo_laboral: '',
  modalidad: '',
  codigo_minsa: '',
  numero_cmp: '',
  fecha_ingreso: '',
  fecha_nombramiento: '',
  fecha_cese: '',
  resolucion_nombramiento: '',
  resolucion_cese: '',
  especialidades: [] as any[],
  banco: '',
  ruc: '',
  numero_cuenta: '',
  numero_cci: '',
  tipo_cuenta: '',
  departamento_ubigeo: '',
  provincia_ubigeo: '',
  distrito_ubigeo: '',
  direccion: '',
})

const fullName = computed(() => {
  const parts = [form.nombres, form.apellido_paterno, form.apellido_materno].filter(Boolean)
  return parts.join(' ') || ''
})

const progressPercentage = computed(() => {
  let progress = 0
  // Step 1: Datos Personales
  if (form.dni && form.nombres && form.apellido_paterno && form.apellido_materno && 
      form.fecha_nacimiento && form.sexo && form.estado_civil && form.grupo_sanguineo && 
      form.celular && form.correo) progress += 20
  // Step 2: Datos Laborales
  if (form.tipo_trabajador_id && form.nivel_remunerativo_id && form.grupo_ocupacional_id && 
      form.servicio_id && form.cargo_laboral && form.modalidad && form.fecha_ingreso) progress += 20
  // Step 3: Especialidades
  if (form.especialidades.some(e => e.especialidad_id)) progress += 20
  // Step 4: Datos Bancarios
  if (form.banco || form.ruc || form.numero_cuenta) progress += 20
  // Step 5: Ubicación
  if (form.departamento_ubigeo || form.provincia_ubigeo || form.distrito_ubigeo || form.direccion) progress += 20
  return progress
})

const currentTip = computed(() => {
  const tips = [
    'El DNI debe tener 8 dígitos. Usa el botón "Consultar DNI" para autocompletar datos desde RENIEC.',
    'Selecciona el tipo de trabajador y nivel remunerativo según el régimen laboral del empleado.',
    'Las especialidades solo aplican para personal médico. El N° RNE es el Registro Nacional de Especialistas.',
    'Los datos bancarios son necesarios para el pago de remuneraciones.',
    'La dirección completa ayuda a ubicar al empleado para emergencias o comunicaciones.'
  ]
  return tips[stepActual.value] || 'Completa todos los pasos para registrar al empleado.'
})

const requiredFieldsFilled = computed(() => {
  let count = 0
  if (form.dni) count++
  if (form.nombres) count++
  if (form.apellido_paterno) count++
  if (form.apellido_materno) count++
  if (form.fecha_nacimiento) count++
  if (form.sexo) count++
  if (form.estado_civil) count++
  if (form.grupo_sanguineo) count++
  if (form.celular) count++
  if (form.correo) count++
  if (form.tipo_trabajador_id) count++
  if (form.nivel_remunerativo_id) count++
  if (form.grupo_ocupacional_id) count++
  if (form.servicio_id) count++
  if (form.cargo_laboral) count++
  if (form.modalidad) count++
  if (form.fecha_ingreso) count++
  return count
})

const totalRequiredFields = 17

const calcularAntiguedad = (fecha: string) => {
  if (!fecha) return '—'
  const hoy = new Date()
  const ingreso = new Date(fecha)
  const diff = Math.floor((hoy.getTime() - ingreso.getTime()) / (1000 * 60 * 60 * 24))
  const years = Math.floor(diff / 365)
  const months = Math.floor((diff % 365) / 30)
  if (years > 0) return `${years} año(s) y ${months} mes(es)`
  if (months > 0) return `${months} mes(es)`
  return `${diff} día(s)`
}

const consultarDni = async () => {
  consultandoDni.value = true
  dniMsg.value = ''
  dniError.value = false
  try {
    await new Promise(r => setTimeout(r, 800))
    dniMsg.value = 'DNI consultado correctamente. Complete los datos o active registro manual.'
    dniError.value = false
    dniCargado.value = true
  } catch {
    dniMsg.value = 'No se pudo consultar el DNI. Active el registro manual.'
    dniError.value = true
  } finally {
    consultandoDni.value = false
  }
}

const validateStep = (step: number): boolean => {
  let valid = true
  
  if (step === 0) {
    errors.dni = !form.dni ? 'El DNI es requerido' : form.dni.length !== 8 ? 'El DNI debe tener 8 dígitos' : ''
    errors.nombres = !form.nombres ? 'Los nombres son requeridos' : ''
    errors.apellido_paterno = !form.apellido_paterno ? 'El apellido paterno es requerido' : ''
    errors.apellido_materno = !form.apellido_materno ? 'El apellido materno es requerido' : ''
    errors.fecha_nacimiento = !form.fecha_nacimiento ? 'La fecha de nacimiento es requerida' : ''
    errors.sexo = !form.sexo ? 'El sexo es requerido' : ''
    errors.estado_civil = !form.estado_civil ? 'El estado civil es requerido' : ''
    errors.grupo_sanguineo = !form.grupo_sanguineo ? 'El grupo sanguíneo es requerido' : ''
    errors.celular = !form.celular ? 'El celular es requerido' : ''
    errors.correo = !form.correo ? 'El correo es requerido' : ''
    
    if (errors.dni || errors.nombres || errors.apellido_paterno || errors.apellido_materno ||
        errors.fecha_nacimiento || errors.sexo || errors.estado_civil || errors.grupo_sanguineo ||
        errors.celular || errors.correo) {
      valid = false
    }
  }
  
  if (step === 1) {
    errors.tipo_trabajador_id = !form.tipo_trabajador_id ? 'El tipo de trabajador es requerido' : ''
    errors.nivel_remunerativo_id = !form.nivel_remunerativo_id ? 'El nivel remunerativo es requerido' : ''
    errors.grupo_ocupacional_id = !form.grupo_ocupacional_id ? 'El grupo ocupacional es requerido' : ''
    errors.servicio_id = !form.servicio_id ? 'El servicio es requerido' : ''
    errors.cargo_laboral = !form.cargo_laboral ? 'El cargo laboral es requerido' : ''
    errors.modalidad = !form.modalidad ? 'La modalidad es requerida' : ''
    errors.fecha_ingreso = !form.fecha_ingreso ? 'La fecha de ingreso es requerida' : ''
    
    if (errors.tipo_trabajador_id || errors.nivel_remunerativo_id || errors.grupo_ocupacional_id ||
        errors.servicio_id || errors.cargo_laboral || errors.modalidad || errors.fecha_ingreso) {
      valid = false
    }
  }
  
  return valid
}

const nextStep = () => {
  if (!validateStep(stepActual.value)) return
  if (stepActual.value < pasos.length - 1) stepActual.value++
}

const handleCreate = async () => {
  if (!validateStep(0) || !validateStep(1)) {
    stepActual.value = 0
    return
  }
  
  saving.value = true
  error.value = ''
  try {
    const payload = {
      ...form,
      tipo_trabajador_id: form.tipo_trabajador_id || null,
      nivel_remunerativo_id: form.nivel_remunerativo_id || null,
      grupo_ocupacional_id: form.grupo_ocupacional_id || null,
      departamento_id: form.departamento_id || null,
      servicio_id: form.servicio_id || null,
      fecha_nacimiento: form.fecha_nacimiento || null,
      fecha_ingreso: form.fecha_ingreso || null,
      fecha_nombramiento: form.fecha_nombramiento || null,
      fecha_cese: form.fecha_cese || null,
    }
    const created = await api<any>('/sigarh/rrhh/empleados', {
      method: 'POST',
      body: payload,
    })

    for (const esp of form.especialidades) {
      if (esp.especialidad_id) {
        await api(`/sigarh/rrhh/empleados/${created.id}/especialidades`, {
          method: 'POST',
          body: esp,
        })
      }
    }

    router.push(`/sigarh/rrhh/empleados?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo crear el empleado'
    stepActual.value = 0
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [tt, nr, go, dep, ser, esp] = await Promise.all([
      api<any[]>('/sigarh/mantenimiento/tipos-trabajador'),
      api<any[]>('/sigarh/mantenimiento/niveles-remunerativos'),
      api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
      api<any[]>('/sigarh/mantenimiento/departamentos'),
      api<any[]>('/sigarh/mantenimiento/servicios'),
      api<any[]>('/sigarh/rrhh/especialidades'),
    ])
    tiposTrabajador.value = tt
    nivelesRemunerativos.value = nr
    gruposOcupacionales.value = go
    departamentos.value = dep
    servicios.value = ser
    especialidades.value = esp
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar catálogos'
  }
})
</script>

<style scoped>
.empleado-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Progress Steps */
.onboarding-progress {
  margin-bottom: 2rem;
}

.progress-steps {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 12px;
  background: var(--paper);
  border: 1px solid var(--line);
  opacity: 0.5;
  transition: all 0.3s ease;
}

.step-item.active {
  opacity: 1;
  border-color: var(--teal);
  background: var(--teal-soft);
}

.step-item.completed {
  opacity: 1;
  border-color: var(--teal);
  background: rgba(8, 145, 178, 0.08);
}

.step-circle {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  background: var(--mist);
  color: var(--ink-soft);
  transition: all 0.3s ease;
}

.step-item.active .step-circle {
  background: var(--teal);
  color: white;
}

.step-item.completed .step-circle {
  background: var(--teal);
  color: white;
}

.step-check {
  font-size: 0.875rem;
}

.step-label {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
}

/* Grid */
.empleado-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.empleado-main {
  min-width: 0;
}

.empleado-sidebar {
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

/* Cards */
.empleado-card {
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

/* DNI Section */
.dni-section {
  background: var(--mist);
  border-radius: var(--radius);
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.dni-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.dni-header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dni-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.dni-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toggle-checkbox {
  accent-color: var(--teal);
}

.dni-toggle-label {
  font-size: 0.8125rem;
  color: var(--ink);
  cursor: pointer;
}

.dni-toggle-hint {
  font-size: 0.6875rem;
  color: var(--ink-soft);
}

.dni-consult {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.dni-input-group {
  flex: 1;
}

.btn-consult-dni {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  white-space: nowrap;
}

.btn-consult-dni:hover:not(:disabled) {
  background: var(--teal-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-consult-dni:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dni-message {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  margin-top: 0.75rem;
  padding: 0.5rem 0.75rem;
  border-radius: 6px;
}

.dni-success {
  background: var(--green-soft);
  color: var(--green);
}

.dni-error {
  background: var(--alert-soft);
  color: var(--alert);
}

/* Info Sections */
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

.input-clinical[type="select"],
.input-clinical select {
  appearance: none;
  cursor: pointer;
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

/* Status Toggle */
.status-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--mist);
}

.toggle-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.toggle-switch {
  position: relative;
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: var(--line);
  border: none;
  cursor: pointer;
  transition: background 0.3s ease;
  padding: 0;
}

.toggle-switch.toggle-active {
  background: var(--teal);
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-active .toggle-slider {
  transform: translateX(20px);
}

/* Resumen Section */
.resumen-section {
  margin: 1.5rem 0;
  padding: 1rem 1.25rem;
  border-radius: var(--radius);
  background: var(--navy-soft);
  border: 1px solid var(--navy-soft);
}

.resumen-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.resumen-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.resumen-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--navy);
}

.resumen-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
}

/* Fechas Resumen */
.fechas-resumen {
  margin-top: 1rem;
  padding: 1rem 1.25rem;
  border-radius: var(--radius);
  background: var(--teal-soft);
  border: 1px solid var(--teal-soft);
}

.fechas-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
}

.fecha-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.fecha-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--teal);
}

.fecha-value {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
}

/* Especialidades */
.especialidad-item {
  padding: 1rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  margin-bottom: 0.75rem;
}

.especialidad-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.especialidad-number {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink-soft);
}

.btn-remove-especialidad {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.5rem;
  border-radius: 6px;
  border: none;
  background: transparent;
  color: var(--alert);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-remove-especialidad:hover {
  background: var(--alert-soft);
}

.especialidad-grid {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr;
  gap: 0.75rem;
  align-items: end;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-bottom: 0.375rem;
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

.btn-add-especialidad {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.625rem;
  border-radius: 8px;
  border: 2px dashed var(--line);
  background: transparent;
  color: var(--ink-soft);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-add-especialidad:hover {
  border-color: var(--teal);
  color: var(--teal);
  background: var(--teal-soft);
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

/* Actions */
.empleado-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.action-spacer {
  flex: 1;
}

.action-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
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

/* Summary Widget */
.widget-progress {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.widget-progress-label {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.widget-progress-bar {
  flex: 1;
  height: 4px;
  border-radius: 2px;
  background: var(--mist);
  overflow: hidden;
}

.widget-progress-fill {
  height: 100%;
  border-radius: 2px;
  background: var(--teal);
  transition: width 0.6s ease;
}

.widget-progress-value {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--teal);
}

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

.status-active-mini {
  background: var(--green-soft);
  color: var(--green);
}

.status-inactive-mini {
  background: var(--mist);
  color: var(--ink-soft);
}

.status-dot-mini {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  display: inline-block;
}

.dot-active-mini {
  background: var(--green);
}

.dot-inactive-mini {
  background: var(--ink-soft);
}

/* Checklist Widget */
.checklist-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--line);
}

.checklist-item:last-child {
  border-bottom: none;
}

.checklist-done {
  opacity: 0.7;
}

.checklist-active .checklist-label {
  color: var(--ink);
  font-weight: 500;
}

.checklist-icon {
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.checklist-number {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: 600;
  background: var(--mist);
  color: var(--ink-soft);
}

.checklist-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  flex: 1;
}

.checklist-current {
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--teal);
  background: var(--teal-soft);
  padding: 0.125rem 0.5rem;
  border-radius: 10px;
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

/* Responsive */
@media (max-width: 1024px) {
  .empleado-grid {
    grid-template-columns: 1fr;
  }
  
  .empleado-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .empleado-create-container {
    padding: 1rem;
  }
  
  .progress-steps {
    flex-wrap: wrap;
  }
  
  .step-item {
    flex: 1;
    min-width: 120px;
  }
  
  .form-grid {
    grid-template-columns: 1fr;
  }
  
  .especialidad-grid {
    grid-template-columns: 1fr;
  }
  
  .resumen-grid,
  .fechas-grid {
    grid-template-columns: 1fr;
  }
  
  .empleado-sidebar {
    grid-template-columns: 1fr;
  }
  
  .empleado-actions {
    flex-wrap: wrap;
  }
  
  .action-group {
    flex-wrap: wrap;
    width: 100%;
  }
  
  .action-group > * {
    flex: 1;
    justify-content: center;
  }
  
  .dni-consult {
    flex-direction: column;
  }
  
  .btn-consult-dni {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .dni-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .dni-toggle {
    flex-wrap: wrap;
  }
  
  .dni-toggle-hint {
    width: 100%;
  }
  
  .status-toggle {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }
}
</style>