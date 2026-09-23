<template>
  <div class="hospital-create-container">
    <!-- Progress Indicator -->
    <div class="onboarding-progress">
      <div class="progress-steps">
        <div 
          v-for="(step, index) in steps" 
          :key="index"
          class="step-item"
          :class="{ 
            active: currentStep >= index, 
            completed: currentStep > index 
          }"
        >
          <div class="step-circle">
            <span v-if="currentStep > index" class="step-check">✓</span>
            <span v-else>{{ index + 1 }}</span>
          </div>
          <span class="step-label">{{ step }}</span>
        </div>
      </div>
    </div>

    <div class="hospital-grid">
      <!-- Main Content -->
      <div class="hospital-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink to="/admin/hospitales" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-building-office-2" class="w-3.5 h-3.5" />
              Hospitales
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Nuevo Hospital</span>
          </div>
          <div class="flex items-center gap-4">
            <div class="header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-plus-circle" class="w-6 h-6" style="color: var(--teal)" />
            </div>
            <div>
              <h1 class="page-title">Configurar Hospital</h1>
              <p class="page-subtitle">Registra un nuevo hospital y configura sus accesos</p>
            </div>
          </div>
        </div>

        <!-- Step 1: Nivel -->
        <section class="hospital-card" v-show="currentStep === 0">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--teal-soft)">
              <UIcon name="i-heroicons-building-library" class="w-4 h-4" style="color: var(--teal)" />
            </div>
            <div>
              <h3 class="card-title">Nivel de Complejidad</h3>
              <p class="card-subtitle">MINSA Perú — Determina los módulos disponibles</p>
            </div>
          </div>

          <div v-if="loadingNiveles" class="loading-state">
            <div class="loading-spinner">
              <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
            </div>
            <p style="color: var(--ink-soft)">Cargando niveles hospitalarios...</p>
          </div>

          <div v-else class="nivel-grid">
            <div
              v-for="nivel in niveles"
              :key="nivel.code"
              class="nivel-card"
              :class="{ 'nivel-card--selected': form.nivel_code === nivel.code }"
              :style="{
                borderColor: form.nivel_code === nivel.code ? (nivel.color || 'var(--teal)') : 'var(--line)',
                background: form.nivel_code === nivel.code ? `${nivel.color}12` : 'var(--paper)',
              }"
              @click="seleccionarNivel(nivel)"
            >
              <div class="nivel-header">
                <span
                  class="nivel-badge"
                  :style="{ background: nivel.color || 'var(--teal)', color: getContrastColor(nivel.color || 'var(--teal)') }"
                >
                  {{ nivel.code }}
                </span>
                <div
                  class="nivel-radio"
                  :style="{
                    borderColor: form.nivel_code === nivel.code ? (nivel.color || 'var(--teal)') : 'var(--line)',
                    background: form.nivel_code === nivel.code ? (nivel.color || 'var(--teal)') : 'transparent',
                  }"
                >
                  <UIcon v-if="form.nivel_code === nivel.code" name="i-heroicons-check" class="w-3 h-3 text-white" />
                </div>
              </div>

              <h4 class="nivel-name">{{ nivel.name }}</h4>
              <p class="nivel-description">{{ nivel.description }}</p>

              <div v-if="form.nivel_code === nivel.code" class="nivel-modules">
                <div v-if="loadingModulos" class="modules-loading">
                  <UIcon name="i-heroicons-arrow-path" class="w-3.5 h-3.5 animate-spin" />
                  <span>Cargando módulos...</span>
                </div>
                <template v-else-if="modulosNivel">
                  <div v-if="modulosNivel.app?.length" class="module-group">
                    <span class="module-group-label">App</span>
                    <div class="module-tags">
                      <span
                        v-for="mod in modulosNivel.app"
                        :key="mod"
                        class="module-tag tag-app"
                      >{{ formatModulo(mod) }}</span>
                    </div>
                  </div>
                  <div v-if="modulosNivel.sigarh?.length" class="module-group">
                    <span class="module-group-label">SIGARH</span>
                    <div class="module-tags">
                      <span
                        v-for="mod in modulosNivel.sigarh"
                        :key="mod"
                        class="module-tag tag-sigarh"
                      >{{ formatModulo(mod) }}</span>
                    </div>
                  </div>
                </template>
              </div>
            </div>
          </div>

          <div v-if="!form.nivel_code && !loadingNiveles" class="selection-hint">
            <UIcon name="i-heroicons-hand-raised" class="w-4 h-4" />
            <span>Selecciona un nivel para continuar</span>
          </div>
        </section>

        <!-- Step 2: Identidad -->
        <section class="hospital-card" v-show="currentStep === 1">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--purple-soft)">
              <UIcon name="i-heroicons-identification" class="w-4 h-4" style="color: var(--purple)" />
            </div>
            <div>
              <h3 class="card-title">Identidad del Hospital</h3>
              <p class="card-subtitle">Datos principales del establecimiento</p>
            </div>
          </div>

          <HospitalLogoInput v-model="form.logo_url" :disabled="creating" @busy="logoLoading = $event" />
          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">Nombre del Hospital <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                <input 
                  v-model="form.name" 
                  class="input-clinical" 
                  placeholder="Ej: Hospital Túmán"
                  :class="{ 'input-error': errors.name }"
                />
              </div>
              <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
            </div>

            <div class="form-group full-width">
              <label class="form-label">Subdominio <span class="required">*</span></label>
              <div class="subdomain-wrapper">
                <div class="input-wrapper" style="flex: 1;">
                  <UIcon name="i-heroicons-globe-alt" class="input-icon" />
                  <input
                    v-model="form.subdomain"
                    class="input-clinical subdomain-input"
                    placeholder="hospital-tuman"
                    :class="{ 'input-error': errors.subdomain }"
                    @input="onSubdomainInput"
                  />
                </div>
                <span class="subdomain-suffix">.{{ tenantBaseDomain }}</span>
              </div>
              <span v-if="errors.subdomain" class="error-message">{{ errors.subdomain }}</span>
              <p class="field-hint">El subdominio será la URL de acceso del hospital y no podrá modificarse después</p>
            </div>

            <div class="form-group">
              <label class="form-label">RUC</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document" class="input-icon" />
                <input 
                  v-model="form.ruc" 
                  class="input-clinical font-mono-data" 
                  placeholder="20123456789"
                  maxlength="11"
                />
              </div>
            </div>

            <div class="form-group">
              <label class="form-label">Nivel Seleccionado</label>
              <div class="selected-level" :style="{ borderColor: nivelSeleccionado?.color || 'var(--line)' }">
                <span
                  class="selected-level-badge"
                  :style="{ background: nivelSeleccionado?.color || 'var(--teal)', color: getContrastColor(nivelSeleccionado?.color || 'var(--teal)') }"
                >
                  {{ nivelSeleccionado?.code || '—' }}
                </span>
                <span>{{ nivelSeleccionado?.name || 'Ninguno seleccionado' }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Step 3: Usuarios -->
        <section class="hospital-card" v-show="currentStep === 2">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--navy-soft)">
              <UIcon name="i-heroicons-users" class="w-4 h-4" style="color: var(--navy)" />
            </div>
            <div>
              <h3 class="card-title">Usuarios de Acceso</h3>
              <p class="card-subtitle">Crea las cuentas para administrar el hospital</p>
            </div>
          </div>

          <!-- Admin User -->
          <div class="user-section">
            <div class="user-section-header">
              <div class="user-section-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-user-circle" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h4 class="user-section-title">Administrador del Hospital</h4>
                <p class="user-section-desc">Acceso al panel de admisiones, caja y operaciones clínicas</p>
              </div>
            </div>

            <div class="user-grid">
              <div class="form-group">
                <label class="form-label">Nombre Completo <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <input 
                    v-model="form.admin_name" 
                    class="input-clinical" 
                    placeholder="Lic. Carmen Flores Medina"
                    :class="{ 'input-error': errors.admin_name }"
                  />
                </div>
                <span v-if="errors.admin_name" class="error-message">{{ errors.admin_name }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Correo Electrónico <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-envelope" class="input-icon" />
                  <input 
                    v-model="form.admin_email" 
                    type="email" 
                    class="input-clinical" 
                    placeholder="admin@hospital.pe"
                    :class="{ 'input-error': errors.admin_email }"
                  />
                </div>
                <span v-if="errors.admin_email" class="error-message">{{ errors.admin_email }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Contraseña <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-key" class="input-icon" />
                  <input
                    v-model="form.admin_password"
                    type="password"
                    class="input-clinical"
                    :class="{ 'input-error': errors.admin_password }"
                  />
                </div>
                <ul class="pwd-checklist">
                  <li :class="{ ok: adminPwdChecks.length }"><UIcon :name="adminPwdChecks.length ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> 8+ caracteres</li>
                  <li :class="{ ok: adminPwdChecks.lower }"><UIcon :name="adminPwdChecks.lower ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Minúscula</li>
                  <li :class="{ ok: adminPwdChecks.upper }"><UIcon :name="adminPwdChecks.upper ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Mayúscula</li>
                  <li :class="{ ok: adminPwdChecks.digit }"><UIcon :name="adminPwdChecks.digit ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Número</li>
                  <li :class="{ ok: adminPwdChecks.special }"><UIcon :name="adminPwdChecks.special ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Carácter especial</li>
                </ul>
                <span v-if="errors.admin_password" class="error-message">{{ errors.admin_password }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Confirmar Contraseña <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-shield-check" class="input-icon" />
                  <input 
                    v-model="form.admin_password_confirm" 
                    type="password" 
                    class="input-clinical" 
                    :class="{ 'input-error': errors.admin_password_confirm }"
                  />
                </div>
                <span v-if="errors.admin_password_confirm" class="error-message">{{ errors.admin_password_confirm }}</span>
              </div>
            </div>
          </div>

          <!-- SIGARH User -->
          <div class="user-section">
            <div class="user-section-header">
              <div class="user-section-icon" style="background: var(--purple-soft)">
                <UIcon name="i-heroicons-folder-open" class="w-4 h-4" style="color: var(--purple)" />
              </div>
              <div>
                <h4 class="user-section-title">Usuario SIGARH</h4>
                <p class="user-section-desc">Acceso a configuración: médicos, turnos, recursos humanos</p>
              </div>
            </div>

            <div class="user-grid">
              <div class="form-group">
                <label class="form-label">Nombre Completo <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <input 
                    v-model="form.sigarh_name" 
                    class="input-clinical" 
                    placeholder="Ing. Marco Quispe Huanca"
                    :class="{ 'input-error': errors.sigarh_name }"
                  />
                </div>
                <span v-if="errors.sigarh_name" class="error-message">{{ errors.sigarh_name }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Correo Electrónico <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-envelope" class="input-icon" />
                  <input 
                    v-model="form.sigarh_email" 
                    type="email" 
                    class="input-clinical" 
                    placeholder="sigarh@hospital.pe"
                    :class="{ 'input-error': errors.sigarh_email }"
                  />
                </div>
                <span v-if="errors.sigarh_email" class="error-message">{{ errors.sigarh_email }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Contraseña <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-key" class="input-icon" />
                  <input
                    v-model="form.sigarh_password"
                    type="password"
                    class="input-clinical"
                    :class="{ 'input-error': errors.sigarh_password }"
                  />
                </div>
                <ul class="pwd-checklist">
                  <li :class="{ ok: sigarhPwdChecks.length }"><UIcon :name="sigarhPwdChecks.length ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> 8+ caracteres</li>
                  <li :class="{ ok: sigarhPwdChecks.lower }"><UIcon :name="sigarhPwdChecks.lower ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Minúscula</li>
                  <li :class="{ ok: sigarhPwdChecks.upper }"><UIcon :name="sigarhPwdChecks.upper ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Mayúscula</li>
                  <li :class="{ ok: sigarhPwdChecks.digit }"><UIcon :name="sigarhPwdChecks.digit ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Número</li>
                  <li :class="{ ok: sigarhPwdChecks.special }"><UIcon :name="sigarhPwdChecks.special ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-3.5 h-3.5" /> Carácter especial</li>
                </ul>
                <span v-if="errors.sigarh_password" class="error-message">{{ errors.sigarh_password }}</span>
              </div>

              <div class="form-group">
                <label class="form-label">Confirmar Contraseña <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-shield-check" class="input-icon" />
                  <input 
                    v-model="form.sigarh_password_confirm" 
                    type="password" 
                    class="input-clinical" 
                    :class="{ 'input-error': errors.sigarh_password_confirm }"
                  />
                </div>
                <span v-if="errors.sigarh_password_confirm" class="error-message">{{ errors.sigarh_password_confirm }}</span>
              </div>
            </div>
          </div>
        </section>

        <!-- Step 4: Módulos -->
        <section class="hospital-card" v-show="currentStep === 3">
          <div class="card-header">
            <div class="card-header-icon" style="background: var(--amber-soft)">
              <UIcon name="i-heroicons-squares-plus" class="w-4 h-4" style="color: var(--amber)" />
            </div>
            <div>
              <h3 class="card-title">Módulos Activos</h3>
              <p class="card-subtitle">
                Basado en el nivel <strong>{{ form.nivel_code }}</strong> — {{ nivelSeleccionado?.name }}
              </p>
            </div>
          </div>

          <div v-if="modulosNivel" class="modules-preview">
            <div class="modules-preview-group">
              <div class="modules-preview-header">
                <span class="modules-preview-icon" style="background: var(--teal-soft); color: var(--teal)">
                  <UIcon name="i-heroicons-squares-2x2" class="w-4 h-4" />
                </span>
                <span class="modules-preview-title">Panel Administrativo</span>
                <span class="modules-preview-count">{{ modulosNivel.app.length }}</span>
              </div>
              <div class="modules-preview-tags">
                <span
                  v-for="mod in modulosNivel.app"
                  :key="mod"
                  class="module-tag tag-app"
                >{{ formatModulo(mod) }}</span>
                <span v-if="!modulosNivel.app.length" class="no-modules">Sin módulos</span>
              </div>
            </div>

            <div class="modules-preview-group">
              <div class="modules-preview-header">
                <span class="modules-preview-icon" style="background: var(--purple-soft); color: var(--purple)">
                  <UIcon name="i-heroicons-rectangle-stack" class="w-4 h-4" />
                </span>
                <span class="modules-preview-title">Panel SIGARH</span>
                <span class="modules-preview-count">{{ modulosNivel.sigarh.length }}</span>
              </div>
              <div class="modules-preview-tags">
                <span
                  v-for="mod in modulosNivel.sigarh"
                  :key="mod"
                  class="module-tag tag-sigarh"
                >{{ formatModulo(mod) }}</span>
                <span v-if="!modulosNivel.sigarh.length" class="no-modules">Sin módulos</span>
              </div>
            </div>

            <div class="modules-summary">
              <span>Total: <strong>{{ totalModulos }}</strong> módulos</span>
              <span class="modules-summary-detail">
                App: {{ modulosNivel.app.length }} · SIGARH: {{ modulosNivel.sigarh.length }}
              </span>
            </div>
          </div>

          <div v-if="createError" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ createError }}
          </div>
        </section>

        <!-- Navigation Actions -->
        <div class="hospital-actions">
          <button 
            v-if="currentStep > 0"
            class="btn-secondary"
            @click="currentStep--"
          >
            <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
            Atrás
          </button>
          
          <div class="action-spacer"></div>

          <button 
            v-if="currentStep < 3"
            class="btn-primary"
            :disabled="!canAdvance"
            @click="nextStep"
          >
            Siguiente
            <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
          </button>

          <div v-else class="action-group">
            <button class="btn-primary" :disabled="creating || logoLoading" @click="handleCreate">
              <UIcon v-if="creating" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
              {{ creating ? 'Creando...' : 'Crear Hospital' }}
            </button>
            <NuxtLink
              to="/admin/hospitales"
              class="btn-cancel"
            >
              Cancelar
            </NuxtLink>
          </div>
        </div>

        <!-- Recent Hospitals -->
        <div v-if="hospitalesRecientes.length" class="recent-hospitals">
          <div class="recent-header">
            <UIcon name="i-heroicons-clock" class="w-4 h-4" style="color: var(--ink-soft)" />
            <span class="recent-title">Creados Recientemente</span>
          </div>
          <div class="recent-grid">
            <div
              v-for="h in hospitalesRecientes"
              :key="h.id"
              class="recent-item"
            >
              <div class="recent-icon" style="background: var(--mist)">
                <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" style="color: var(--navy)" />
              </div>
              <div class="recent-info">
                <p class="recent-name">{{ h.name }}</p>
                <span class="recent-level">{{ h.hospital_level || '—' }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Sidebar Widgets -->
      <div class="hospital-sidebar">
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
              <span class="summary-label">Hospital</span>
              <span class="summary-value">{{ form.name || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Dominio</span>
              <span class="summary-value font-mono-data">{{ form.subdomain ? `${form.subdomain.toLowerCase()}.${tenantBaseDomain}` : '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Nivel</span>
              <span class="summary-value">
                <span
                  v-if="nivelSeleccionado"
                  class="mini-badge"
                  :style="{ background: nivelSeleccionado.color || 'var(--teal)', color: getContrastColor(nivelSeleccionado.color || 'var(--teal)') }"
                >
                  {{ nivelSeleccionado.code }}
                </span>
                <span v-else>—</span>
              </span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Módulos</span>
              <span class="summary-value">{{ totalModulos || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="distribution-summary">
              <div class="distribution-bar">
                <div 
                  class="distribution-fill app" 
                  :style="{ width: appPercentage + '%' }"
                />
                <div 
                  class="distribution-fill sigarh" 
                  :style="{ width: sigarhPercentage + '%' }"
                />
              </div>
              <div class="distribution-labels">
                <span class="distribution-label">
                  <span class="distribution-dot" style="background: var(--teal)"></span>
                  App {{ modulosNivel?.app.length || 0 }}
                </span>
                <span class="distribution-label">
                  <span class="distribution-dot" style="background: var(--purple)"></span>
                  SIGARH {{ modulosNivel?.sigarh.length || 0 }}
                </span>
              </div>
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
              v-for="(step, index) in steps" 
              :key="index"
              class="checklist-item"
              :class="{ 
                'checklist-done': currentStep > index,
                'checklist-active': currentStep === index
              }"
            >
              <div class="checklist-icon">
                <UIcon v-if="currentStep > index" name="i-heroicons-check-circle-solid" class="w-4 h-4" style="color: var(--green)" />
                <span v-else class="checklist-number">{{ index + 1 }}</span>
              </div>
              <span class="checklist-label">{{ step }}</span>
              <span v-if="currentStep === index" class="checklist-current">Actual</span>
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
              <span class="stat-label">Niveles disponibles</span>
              <span class="stat-number">{{ niveles.length }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Hospitales activos</span>
              <span class="stat-number">{{ hospitalesRecientes.length }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Nivel {
  id: string
  code: string
  name: string
  description: string
  color: string | null
  default_modules: { app: string[]; sigarh: string[] } | null
  sort_order: number
}

interface HospitalResumen {
  id: string
  name: string
  hospital_level?: string
}

const { api } = useApi()
const router = useRouter()
const config = useRuntimeConfig()
const tenantBaseDomain = config.public.tenantDomain as string

const steps = ['Nivel', 'Identidad', 'Usuarios', 'Módulos']
const tips = [
  'El nivel MINSA determina qué módulos clínicos y administrativos estarán disponibles automáticamente.',
  'El subdominio será la URL de acceso del hospital. No podrá cambiarse después de creado.',
  'Se crean dos cuentas: una para el panel administrativo y otra para el panel SIGARH.',
  'Revisa los módulos activados antes de confirmar. Puedes ajustarlos posteriormente.'
]

const currentStep = ref(0)
const niveles = ref<Nivel[]>([])
const loadingNiveles = ref(true)
const loadingModulos = ref(false)
const modulosNivel = ref<{ app: string[]; sigarh: string[] } | null>(null)
const creating = ref(false)
const logoLoading = ref(false)
const createError = ref('')
const hospitalesRecientes = ref<HospitalResumen[]>([])

const errors = reactive({
  name: '',
  subdomain: '',
  admin_name: '',
  admin_email: '',
  admin_password: '',
  admin_password_confirm: '',
  sigarh_name: '',
  sigarh_email: '',
  sigarh_password: '',
  sigarh_password_confirm: ''
})

const form = reactive({
  logo_url: null as string | null,
  nivel_code: '',
  name: '',
  subdomain: '',
  ruc: '',
  admin_name: '',
  admin_email: '',
  admin_password: '',
  admin_password_confirm: '',
  sigarh_name: '',
  sigarh_email: '',
  sigarh_password: '',
  sigarh_password_confirm: '',
})

const SUBDOMAIN_MAX = 20
const SUBDOMAIN_STOPWORDS = new Set(['de', 'del', 'la', 'el', 'los', 'las', 'y', 'san', 'santa'])
const subdomainTocadoManualmente = ref(false)

const quitarTildes = (s: string) => {
  const mapa: Record<string, string> = { á: 'a', é: 'e', í: 'i', ó: 'o', ú: 'u', ü: 'u', ñ: 'n' }
  return s.toLowerCase().replace(/[áéíóúüñ]/g, ch => mapa[ch] || ch)
}

const slugify = (s: string) =>
  quitarTildes(s)
    .toLowerCase()
    .replace(/[^a-z0-9\s-]/g, '')
    .trim()
    .replace(/\s+/g, '-')
    .replace(/-+/g, '-')
    .replace(/^-|-$/g, '')

const iniciales = (s: string) =>
  quitarTildes(s)
    .toLowerCase()
    .split(/\s+/)
    .filter(w => w && !SUBDOMAIN_STOPWORDS.has(w))
    .map(w => w[0])
    .join('')

const generarSubdominio = (nombre: string) => {
  const slug = slugify(nombre)
  if (!slug || slug.length <= SUBDOMAIN_MAX) return slug
  return iniciales(nombre) || slug.slice(0, SUBDOMAIN_MAX)
}

watch(() => form.name, (nuevo) => {
  if (subdomainTocadoManualmente.value) return
  form.subdomain = generarSubdominio(nuevo)
})

const onSubdomainInput = () => {
  subdomainTocadoManualmente.value = true
}

const checksDePassword = (pwd: string) => ({
  length: pwd.length >= 8,
  lower: /[a-z]/.test(pwd),
  upper: /[A-Z]/.test(pwd),
  digit: /\d/.test(pwd),
  special: /[^\w\s]/.test(pwd),
})
const adminPwdChecks = computed(() => checksDePassword(form.admin_password))
const sigarhPwdChecks = computed(() => checksDePassword(form.sigarh_password))

// Se avisa "no coinciden" apenas se escribe, sin esperar a que hagan clic
// en Siguiente -- antes solo se revisaba al validar el paso completo.
watch(() => [form.admin_password, form.admin_password_confirm], () => {
  errors.admin_password_confirm = form.admin_password_confirm && form.admin_password !== form.admin_password_confirm
    ? 'Las contraseñas no coinciden'
    : ''
})
watch(() => [form.sigarh_password, form.sigarh_password_confirm], () => {
  errors.sigarh_password_confirm = form.sigarh_password_confirm && form.sigarh_password !== form.sigarh_password_confirm
    ? 'Las contraseñas no coinciden'
    : ''
})

// El backend rechaza correos con formato invalido y que Admin/SIGARH
// compartan el mismo correo (ver tenants/hospitales/schemas.py); antes eso
// solo se descubria al final del wizard, en el ultimo paso, muy lejos de
// donde estan estos dos campos.
const emailValidoLive = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)
watch(() => [form.admin_email, form.sigarh_email], () => {
  const mismo = !!form.admin_email && !!form.sigarh_email &&
    form.admin_email.toLowerCase() === form.sigarh_email.toLowerCase()

  if (!form.admin_email) errors.admin_email = errors.admin_email
  else if (!emailValidoLive(form.admin_email)) errors.admin_email = 'El correo no es válido'
  else errors.admin_email = mismo ? 'Debe ser distinto al correo SIGARH' : ''

  if (!form.sigarh_email) errors.sigarh_email = errors.sigarh_email
  else if (!emailValidoLive(form.sigarh_email)) errors.sigarh_email = 'El correo no es válido'
  else errors.sigarh_email = mismo ? 'Debe ser distinto al correo del Administrador' : ''
})

const nivelSeleccionado = computed(() => niveles.value.find(n => n.code === form.nivel_code) || null)
const totalModulos = computed(() => (modulosNivel.value?.app.length || 0) + (modulosNivel.value?.sigarh.length || 0))
const currentTip = computed(() => tips[currentStep.value])

const progressPercentage = computed(() => {
  let progress = 0
  if (form.nivel_code) progress += 25
  if (form.name && form.subdomain) progress += 25
  if (form.admin_email && form.sigarh_email) progress += 25
  if (modulosNivel.value) progress += 25
  return progress
})

const appPercentage = computed(() => {
  const total = totalModulos.value
  if (total === 0) return 0
  return Math.round(((modulosNivel.value?.app.length || 0) / total) * 100)
})

const sigarhPercentage = computed(() => {
  const total = totalModulos.value
  if (total === 0) return 0
  return Math.round(((modulosNivel.value?.sigarh.length || 0) / total) * 100)
})

const canAdvance = computed(() => {
  if (currentStep.value === 0) return !!form.nivel_code
  if (currentStep.value === 1) return !!form.name && !!form.subdomain
  if (currentStep.value === 2) {
    return !!form.admin_email && !!form.admin_password &&
           form.admin_password === form.admin_password_confirm &&
           !!form.sigarh_email && !!form.sigarh_password &&
           form.sigarh_password === form.sigarh_password_confirm
  }
  return true
})

const getContrastColor = (hex: string) => {
  const r = parseInt(hex.slice(1, 3), 16)
  const g = parseInt(hex.slice(3, 5), 16)
  const b = parseInt(hex.slice(5, 7), 16)
  const luminance = (0.299 * r + 0.587 * g + 0.114 * b) / 255
  return luminance > 0.5 ? '#000000' : '#FFFFFF'
}

const formatModulo = (code: string) => {
  return code
    .replace('sigarh_', '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())
}

const validateStep = (step: number): boolean => {
  let valid = true
  
  if (step === 1) {
    errors.name = !form.name ? 'El nombre es requerido' : ''
    errors.subdomain = !form.subdomain
      ? 'El subdominio es requerido'
      : !/^(?!-)[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?$/.test(form.subdomain.toLowerCase())
        ? 'Usa solo letras, números y guiones'
        : ['www', 'api', 'his-erp', 'admin'].includes(form.subdomain.toLowerCase())
          ? 'Este subdominio está reservado'
          : ''
    if (errors.name || errors.subdomain) valid = false
  }
  
  if (step === 2) {
    const emailValido = (v: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(v)
    const mismoCorreo = !!form.admin_email && !!form.sigarh_email &&
      form.admin_email.toLowerCase() === form.sigarh_email.toLowerCase()

    errors.admin_name = !form.admin_name ? 'El nombre es requerido' : ''
    errors.admin_email = !form.admin_email
      ? 'El correo es requerido'
      : !emailValido(form.admin_email)
        ? 'El correo no es válido'
        : (mismoCorreo ? 'Debe ser distinto al correo SIGARH' : '')
    errors.admin_password = !form.admin_password
      ? 'La contraseña es requerida'
      : (!Object.values(adminPwdChecks.value).every(Boolean) ? 'La contraseña no cumple los requisitos mínimos' : '')
    errors.admin_password_confirm = !form.admin_password_confirm
      ? 'Confirma la contraseña'
      : (form.admin_password !== form.admin_password_confirm ? 'Las contraseñas no coinciden' : '')

    errors.sigarh_name = !form.sigarh_name ? 'El nombre es requerido' : ''
    errors.sigarh_email = !form.sigarh_email
      ? 'El correo es requerido'
      : !emailValido(form.sigarh_email)
        ? 'El correo no es válido'
        : (mismoCorreo ? 'Debe ser distinto al correo del Administrador' : '')
    errors.sigarh_password = !form.sigarh_password
      ? 'La contraseña es requerida'
      : (!Object.values(sigarhPwdChecks.value).every(Boolean) ? 'La contraseña no cumple los requisitos mínimos' : '')
    errors.sigarh_password_confirm = !form.sigarh_password_confirm
      ? 'Confirma la contraseña'
      : (form.sigarh_password !== form.sigarh_password_confirm ? 'Las contraseñas no coinciden' : '')
    
    if (errors.admin_name || errors.admin_email || errors.admin_password || errors.admin_password_confirm ||
        errors.sigarh_name || errors.sigarh_email || errors.sigarh_password || errors.sigarh_password_confirm) {
      valid = false
    }
  }
  
  return valid
}

const nextStep = () => {
  if (!validateStep(currentStep.value)) return
  if (currentStep.value < 3) currentStep.value++
}

const seleccionarNivel = async (nivel: Nivel) => {
  form.nivel_code = nivel.code
  modulosNivel.value = null

  if (nivel.default_modules) {
    modulosNivel.value = nivel.default_modules
    return
  }

  loadingModulos.value = true
  try {
    const data = await api<any>(`/admin/niveles-hospitalarios/${nivel.code}/modulos`)
    modulosNivel.value = data.default_modules
  } catch {
    modulosNivel.value = { app: [], sigarh: [] }
  } finally {
    loadingModulos.value = false
  }
}

const handleCreate = async () => {
  if (creating.value || logoLoading.value) return
  if (!validateStep(2)) {
    currentStep.value = 2
    return
  }

  creating.value = true
  createError.value = ''
  try {
    const domain = `${form.subdomain.toLowerCase()}.${tenantBaseDomain}`
    const activeModules = [
      ...(modulosNivel.value?.app || []),
      ...(modulosNivel.value?.sigarh || []),
    ]

    await api('/admin/hospitales', {
      method: 'POST',
      body: {
        name: form.name,
        logo_url: form.logo_url,
        domain,
        ruc: form.ruc || null,
        hospital_level: form.nivel_code,
        active_modules: activeModules,
        admin_name: form.admin_name,
        admin_email: form.admin_email,
        admin_password: form.admin_password,
        sigarh_name: form.sigarh_name,
        sigarh_email: form.sigarh_email,
        sigarh_password: form.sigarh_password,
      },
    })

    router.push('/admin/hospitales')
  } catch (e: any) {
    createError.value = apiErr(e, 'No se pudo crear el hospital')
    currentStep.value = 3
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  try {
    niveles.value = await api<Nivel[]>('/admin/niveles-hospitalarios')
  } catch {
    // 
  } finally {
    loadingNiveles.value = false
  }

  try {
    const todos = await api<HospitalResumen[]>('/admin/hospitales')
    hospitalesRecientes.value = todos.slice(-3).reverse()
  } catch {
    // 
  }
})
</script>

<style scoped>
.hospital-create-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Grid */
.hospital-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.hospital-main {
  min-width: 0;
}

.hospital-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

/* Header */

/* Cards */
.hospital-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  animation: slideIn 0.3s ease;
}

/* Nivel Grid */
.nivel-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.nivel-card {
  padding: 1.25rem;
  border-radius: var(--radius-lg);
  border: 2px solid var(--line);
  cursor: pointer;
  transition: all 0.3s ease;
}

.nivel-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.nivel-card--selected {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.nivel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.nivel-badge {
  padding: 0.1875rem 0.625rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  font-family: monospace;
}

.nivel-radio {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--line);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  transition: all 0.3s ease;
}

.nivel-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.25rem 0;
}

.nivel-description {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  margin: 0 0 0.75rem 0;
}

.nivel-modules {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--line);
}

.modules-loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.module-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.375rem;
}

.module-group:last-child {
  margin-bottom: 0;
}

.module-group-label {
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--ink-soft);
  background: var(--mist);
  padding: 0.125rem 0.375rem;
  border-radius: 3px;
}

.module-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
}

.module-tag {
  font-size: 0.625rem;
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  font-weight: 500;
}

.tag-app {
  background: var(--teal-soft);
  color: var(--teal);
}

.tag-sigarh {
  background: var(--purple-soft);
  color: var(--purple);
}

.selection-hint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--mist);
  color: var(--ink-soft);
  font-size: 0.875rem;
}

/* Form */

/* Subdomain */
.subdomain-wrapper {
  display: flex;
  align-items: stretch;
}

.subdomain-input {
  border-radius: 8px 0 0 8px;
  border-right: none;
}

.subdomain-suffix {
  display: flex;
  align-items: center;
  padding: 0 0.75rem;
  background: var(--mist);
  border: 1px solid var(--line);
  border-left: none;
  border-radius: 0 8px 8px 0;
  font-size: 0.8125rem;
  color: var(--ink-soft);
  white-space: nowrap;
}

/* Selected Level */
.selected-level {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--paper);
  min-height: 42px;
}

.selected-level-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  font-family: monospace;
}

/* User Sections */
.user-section {
  margin-top: 1.5rem;
  padding: 1.25rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
}

.user-section:first-child {
  margin-top: 0;
}

.user-section-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1.25rem;
}

.user-section-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.user-section-desc {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

.user-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Modules Preview */
.modules-preview {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.modules-preview-group {
  padding: 1rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
}

.modules-preview-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  margin-bottom: 0.75rem;
}

.modules-preview-icon {
  width: 28px;
  height: 28px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modules-preview-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
}

.modules-preview-count {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink-soft);
  background: var(--mist);
  padding: 0.0625rem 0.5rem;
  border-radius: 10px;
  margin-left: auto;
}

.modules-preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.no-modules {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.modules-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: var(--radius);
  background: var(--mist);
  font-size: 0.875rem;
  color: var(--ink);
}

.modules-summary-detail {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

/* Actions */
.hospital-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Recent Hospitals */
.recent-hospitals {
  margin-top: 2rem;
  padding-top: 1.5rem;
  border-top: 1px solid var(--line);
}

.recent-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.recent-title {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  color: var(--ink-soft);
}

.recent-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

.recent-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.75rem;
  border-radius: var(--radius);
  background: var(--paper);
  border: 1px solid var(--line);
}

.recent-icon {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.recent-info {
  min-width: 0;
}

.recent-name {
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  margin: 0;
  truncate: true;
}

.recent-level {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  font-family: monospace;
}

/* Summary Widget */

.mini-badge {
  padding: 0.0625rem 0.5rem;
  border-radius: 3px;
  font-size: 0.6875rem;
  font-weight: 700;
  font-family: monospace;
}

.distribution-fill.app {
  background: var(--teal);
}

.distribution-fill.sigarh {
  background: var(--purple);
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
  background: var(--teal-soft);
  border-color: var(--teal-soft);
}

/* Quick Stats Widget */

.stat-item:first-child {
  border-bottom: 1px solid var(--line);
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
  margin-top: 1rem;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 0.75rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .hospital-grid {
    grid-template-columns: 1fr;
  }
  
  .hospital-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .hospital-create-container {
    padding: 1rem;
  }
  
  .progress-steps {
    flex-wrap: wrap;
  }
  
  .step-item {
    flex: 1;
    min-width: 120px;
  }
  
  .nivel-grid {
    grid-template-columns: 1fr;
  }
  
  .user-grid {
    grid-template-columns: 1fr;
  }
  
  .recent-grid {
    grid-template-columns: 1fr;
  }
  
  .hospital-sidebar {
    grid-template-columns: 1fr;
  }
  
  .hospital-actions {
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
}

@media (max-width: 480px) {
  .subdomain-wrapper {
    flex-wrap: wrap;
  }
  
  .subdomain-input {
    border-radius: 8px;
    border-right: 1px solid var(--line);
  }
  
  .subdomain-suffix {
    border-radius: 0 0 8px 8px;
    border: 1px solid var(--line);
    border-top: none;
    padding: 0.375rem 0.75rem;
    justify-content: center;
    width: 100%;
  }
}
</style>
