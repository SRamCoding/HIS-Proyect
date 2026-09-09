<template>
  <div class="lab-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-beaker" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ATENCIÓN HOSPITALARIA</span>
            <h1 class="page-title">Laboratorio · {{ titles[mode] }}</h1>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary btn-sm" @click="load">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
          Actualizar
        </button>
        <button v-if="mode!=='cupos'" class="btn-secondary btn-sm" @click="download('/reportes/'+mode+'.csv', mode+'.csv')">
          <UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />
          Exportar CSV
        </button>
        <button class="btn-primary" @click="newRecord">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Agregar
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="lab-tabs">
      <NuxtLink
        v-for="(title, key) in titles"
        :key="key"
        :to="'/app/laboratorio/'+key"
        class="tab-link"
        :class="{ 'tab-link--active': key === mode }"
      >
        {{ title }}
      </NuxtLink>
    </div>

    <!-- Messages -->
    <div v-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>
    <div v-if="notice" class="success-banner">
      <UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />
      {{ notice }}
    </div>

    <!-- Search Panel -->
    <section class="panel search-panel">
      <form class="search-form" @submit.prevent="search">
        <div class="search-grid">
          <div class="search-field" v-for="f in searchFields" :key="f.key">
            <label class="form-label">{{ f.label }}</label>
            <input
              v-model="filter[f.key]"
              :type="f.key === 'fecha' ? 'date' : 'text'"
              class="input-clinical"
              maxlength="100"
            />
          </div>
          <div class="search-field" v-if="mode!=='cupos'">
            <label class="form-label">Estado</label>
            <select v-model="filter.estado" class="input-clinical">
              <option value="">Todos</option>
              <option v-for="s in states" :key="s">{{ s }}</option>
            </select>
          </div>
          <div v-if="mode==='ordenes'||mode==='movimientos'" class="search-field search-types">
            <label class="form-label">Tipo de servicio</label>
            <div class="types-group">
              <label v-for="t in serviceTypes" :key="t.value" class="type-label">
                <input v-model="filter.tipos" type="checkbox" :value="t.value" />
                {{ t.label }}
              </label>
            </div>
          </div>
        </div>
        <div class="search-actions">
          <button type="button" class="btn-secondary" @click="clearFilter">
            <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            Limpiar
          </button>
          <button class="btn-primary" :disabled="loading" @click="search">
            <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
            Buscar
          </button>
        </div>
      </form>
    </section>

    <!-- Results Panel -->
    <section class="panel results-panel">
      <div class="results-header">
        <h2 class="results-title">{{ titles[mode] }} · {{ total }} registros</h2>
        <div class="results-controls">
          <label class="form-label">Mostrar</label>
          <select v-model.number="pageSize" class="input-clinical input-sm" @change="search">
            <option :value="10">10</option>
            <option :value="20">20</option>
            <option :value="50">50</option>
          </select>
        </div>
      </div>

      <div v-if="loading" class="loading-state">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando...</p>
      </div>

      <div v-else class="table-responsive">
        <table class="lab-table">
          <thead>
            <tr>
              <th v-for="c in tableColumns" :key="c.key">{{ c.label }}</th>
              <th>Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in rows" :key="row.id">
              <td v-for="c in tableColumns" :key="c.key">{{ row[c.key] ?? '—' }}</td>
              <td>
                <div class="action-buttons">
                  <button class="action-btn action-view" @click="view(row)">
                    <UIcon :name="mode==='cupos' ? 'i-heroicons-pencil-square' : 'i-heroicons-eye'" class="w-4 h-4" />
                  </button>
                  <button v-if="mode==='ficha-covid'" class="action-btn action-pdf" @click="download('/ficha-covid/'+row.id+'/reporte.pdf', 'ficha-covid.pdf')">
                    <UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
            <tr v-if="!rows.length">
              <td :colspan="tableColumns.length + 1" style="text-align: center; color: var(--ink-soft);">
                No se encontraron registros.
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <nav v-if="mode!=='cupos'" class="pagination">
        <button class="btn-secondary btn-sm" :disabled="page<=1 || loading" @click="loadPage(page-1)">
          <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
          Anterior
        </button>
        <span class="page-info">{{ page }} / {{ pages }}</span>
        <button class="btn-secondary btn-sm" :disabled="page>=pages || loading" @click="loadPage(page+1)">
          Siguiente
          <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
        </button>
      </nav>
    </section>

    <!-- Editor Panel -->
    <section v-if="formKind" class="panel editor-panel">
      <div class="editor-header">
        <h2 class="editor-title">{{ formTitles[formKind] }}</h2>
        <button class="btn-secondary" :disabled="busy" @click="closeEditor">
          <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
          Cerrar
        </button>
      </div>

      <!-- Cupo Form -->
      <form v-if="formKind==='cupo'" class="editor-form" @submit.prevent="saveCupo">
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Fecha</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-calendar" class="input-icon" />
              <input v-model="cupo.fecha" type="date" class="input-clinical" required :disabled="!!editingId" />
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Cupos</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-numbered-list" class="input-icon" />
              <input v-model.number="cupo.cupos" type="number" class="input-clinical" min="0" max="10000" required />
            </div>
          </div>
        </div>
        <div class="form-actions">
          <button class="btn-primary" :disabled="busy">
            <UIcon name="i-heroicons-check" class="w-4 h-4" />
            Guardar
          </button>
        </div>
      </form>

      <!-- Orden / Covid Patient Search -->
      <template v-if="formKind==='orden' || formKind==='covid'">
        <form class="editor-form" @submit.prevent="findPatients">
          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">Buscar paciente por DNI, HC o apellidos</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-magnifying-glass" class="input-icon" />
                <input v-model="patientQuery" class="input-clinical" minlength="2" maxlength="200" required />
              </div>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn-primary" :disabled="busy">
              <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
              Buscar paciente
            </button>
          </div>
        </form>

        <div class="choices">
          <button v-for="p in foundPatients" :key="p.id" class="choice-btn" @click="choosePatient(p)">
            {{ p.nombre }} · {{ p.dni }} · HC {{ p.historia }}
          </button>
        </div>

        <div v-if="patient" class="patient-info-card">
          <div class="patient-info-header">
            <div class="patient-avatar" :style="{ background: getColorPaciente(patient.nombre) }">
              <span>{{ getInitials(patient.nombre) }}</span>
            </div>
            <div class="patient-info">
              <span class="patient-name">{{ patient.nombre }}</span>
              <div class="patient-details">
                <span class="patient-dni">HC {{ patient.historia }}</span>
                <span class="patient-separator">•</span>
                <span>{{ patient.sexo }}</span>
                <span class="patient-separator">•</span>
                <span>Nacimiento {{ patient.fecha_nacimiento }}</span>
                <span class="patient-separator">•</span>
                <span>Tel. {{ patient.telefono || '—' }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- Covid Form -->
        <form v-if="formKind==='covid'" class="editor-form" @submit.prevent="saveCovid">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Fecha</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-calendar" class="input-icon" />
                <input v-model="covid.fecha" type="date" class="input-clinical" required />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Tipo de prueba</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-beaker" class="input-icon" />
                <input v-model="covid.tipo_prueba" class="input-clinical" maxlength="100" required />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Muestra</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" />
                <input v-model="covid.muestra" class="input-clinical" maxlength="100" required />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Resultado</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-flag" class="input-icon" />
                <select v-model="covid.resultado" class="input-clinical">
                  <option v-for="s in covidStates" :key="s" :value="s">{{ s }}</option>
                </select>
              </div>
            </div>
            <div class="form-group full-width">
              <label class="form-label">Observaciones</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                <textarea v-model="covid.observaciones" class="input-clinical" maxlength="4000" rows="2"></textarea>
              </div>
            </div>
          </div>
          <div class="form-actions">
            <button class="btn-primary" :disabled="busy || !patient">
              <UIcon name="i-heroicons-check" class="w-4 h-4" />
              Guardar ficha
            </button>
          </div>
        </form>

        <!-- Orden Form -->
        <form v-if="formKind==='orden'" class="editor-form" @submit.prevent="saveOrder">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Tipo de servicio</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-list-bullet" class="input-icon" />
                <select v-model="orderForm.tipo_servicio" class="input-clinical">
                  <option v-for="t in serviceTypes" :key="t.value" :value="t.value">{{ t.label }}</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">N.° cuenta</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-identification" class="input-icon" />
                <input v-model="orderForm.numero_cuenta" class="input-clinical" maxlength="50" />
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Fuente financiamiento</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-currency-dollar" class="input-icon" />
                <input v-model="orderForm.fuente_financiamiento" class="input-clinical" maxlength="100" list="lab-seguros" required />
                <datalist id="lab-seguros">
                  <option v-for="s in catalogs.seguros" :key="s.id" :value="s.nombre" />
                </datalist>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Servicio</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                <select v-model="orderForm.servicio_id" class="input-clinical" required>
                  <option value="">Seleccionar</option>
                  <option v-for="s in catalogs.servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Especialidad</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-star" class="input-icon" />
                <select v-model="orderForm.especialidad_id" class="input-clinical">
                  <option value="">Sin especialidad</option>
                  <option v-for="s in catalogs.especialidades" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Médico orden</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-user" class="input-icon" />
                <select v-model="orderForm.medico_id" class="input-clinical" required>
                  <option value="">Seleccionar</option>
                  <option v-for="s in catalogs.empleados" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                </select>
              </div>
            </div>
            <div class="form-group full-width">
              <label class="form-label">Indicación clínica</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                <textarea v-model="orderForm.indicacion_clinica" class="input-clinical" maxlength="4000" rows="2"></textarea>
              </div>
            </div>
          </div>

          <!-- Exámenes -->
          <div class="exam-section">
            <div class="exam-search">
              <div class="form-group" style="flex: 2;">
                <label class="form-label">Buscar exámenes</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-magnifying-glass" class="input-icon" />
                  <input v-model="examQuery" class="input-clinical" />
                </div>
              </div>
              <button type="button" class="btn-secondary" @click="findExams" style="margin-top: 1.5rem;">
                <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
                Buscar
              </button>
            </div>
            <div class="exam-add">
              <div class="form-group" style="flex: 2;">
                <label class="form-label">Examen</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-list-bullet" class="input-icon" />
                  <select v-model="examId" class="input-clinical">
                    <option value="">Seleccionar</option>
                    <option v-for="e in catalogs.examenes" :key="e.id" :value="e.id">{{ e.codigo }} · {{ e.nombre }}</option>
                  </select>
                </div>
              </div>
              <button type="button" class="btn-primary" @click="addExam" style="margin-top: 1.5rem;">
                <UIcon name="i-heroicons-plus" class="w-4 h-4" />
                Agregar
              </button>
            </div>
          </div>

          <div v-if="chosenExams.length" class="exam-list">
            <div v-for="(e, i) in chosenExams" :key="e.id" class="exam-item">
              <span class="exam-code">{{ e.codigo }}</span>
              <span class="exam-name">{{ e.nombre }}</span>
              <button type="button" class="btn-remove" @click="chosenExams.splice(i, 1)">
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
              </button>
            </div>
          </div>

          <div class="form-actions">
            <button class="btn-primary" :disabled="busy || !patient || !chosenExams.length">
              <UIcon name="i-heroicons-check" class="w-4 h-4" />
              Guardar orden
            </button>
          </div>
        </form>
      </template>

      <!-- Movimiento Form -->
      <template v-if="formKind==='movimiento'">
        <form v-if="!editingId" class="editor-form" @submit.prevent="findOrders">
          <div class="form-grid">
            <div class="form-group">
              <label class="form-label">Registrar por</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-list-bullet" class="input-icon" />
                <select v-model="movementForm.registrar_por" class="input-clinical">
                  <option value="ORDEN">N.° orden</option>
                  <option value="CUENTA">N.° cuenta</option>
                  <option value="HISTORIA">Historia clínica</option>
                </select>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">Número</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-identification" class="input-icon" />
                <input v-model="orderQuery" class="input-clinical" required maxlength="50" />
              </div>
            </div>
          </div>
          <div class="form-actions" style="gap: 0.75rem;">
            <button class="btn-primary" :disabled="busy">
              <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
              Buscar
            </button>
            <button type="button" class="btn-secondary" @click="startOrder">
              <UIcon name="i-heroicons-plus" class="w-4 h-4" />
              Crear orden
            </button>
          </div>
        </form>

        <div class="choices">
          <button v-for="o in foundOrders" :key="o.id" class="choice-btn" @click="chooseOrder(o.id)">
            {{ o.numero_orden }} · {{ o.paciente }}
          </button>
        </div>

        <template v-if="selectedOrder">
          <div class="patient-info-card">
            <div class="patient-info-header">
              <div class="patient-avatar" :style="{ background: getColorPaciente(selectedOrder.paciente) }">
                <span>{{ getInitials(selectedOrder.paciente) }}</span>
              </div>
              <div class="patient-info">
                <span class="patient-name"><strong>{{ selectedOrder.paciente }}</strong></span>
                <div class="patient-details">
                  <span>HC {{ selectedOrder.historia }}</span>
                  <span class="patient-separator">•</span>
                  <span>Sexo {{ selectedOrder.sexo }}</span>
                  <span class="patient-separator">•</span>
                  <span>Nacimiento {{ selectedOrder.fecha_nacimiento }}</span>
                  <span class="patient-separator">•</span>
                  <span>Tel. {{ selectedOrder.telefono || '—' }}</span>
                </div>
                <div class="patient-details" style="font-size: 0.75rem; color: var(--ink-soft);">
                  <span>Cuenta {{ selectedOrder.numero_cuenta || '—' }}</span>
                  <span class="patient-separator">•</span>
                  <span>Orden {{ selectedOrder.numero_orden }}</span>
                  <span class="patient-separator">•</span>
                  <span>{{ selectedOrder.especialidad }}</span>
                  <span class="patient-separator">•</span>
                  <span>{{ selectedOrder.tipo_servicio }}</span>
                  <span class="patient-separator">•</span>
                  <span>{{ selectedOrder.servicio }}</span>
                  <span class="patient-separator">•</span>
                  <span>{{ selectedOrder.fuente_financiamiento }}</span>
                </div>
                <div class="patient-details" style="font-size: 0.75rem; color: var(--ink-soft);">
                  <span>Médico orden: {{ selectedOrder.medico }}</span>
                </div>
              </div>
            </div>
          </div>

          <form class="editor-form" @submit.prevent="saveMovement">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Fecha realiza</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-calendar" class="input-icon" />
                  <input v-model="movementForm.fecha" type="date" class="input-clinical" required />
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Agendamiento por</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-list-bullet" class="input-icon" />
                  <select v-model="movementForm.agendamiento_por" class="input-clinical">
                    <option value="PACIENTE">Paciente (N.° cuenta - orden)</option>
                    <option value="ORDEN">Orden</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Cuenta nueva</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-list-bullet" class="input-icon" />
                  <select v-model="movementForm.cuenta_nueva" class="input-clinical">
                    <option :value="false">No</option>
                    <option :value="true">Sí</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Médico orden</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <select v-model="movementForm.medico_id" class="input-clinical" required>
                    <option value="">Seleccionar médico</option>
                    <option v-for="s in catalogs.empleados" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Toma examen</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-user" class="input-icon" />
                  <select v-model="movementForm.toma_examen_id" class="input-clinical" required>
                    <option value="">Seleccionar responsable</option>
                    <option v-for="s in catalogs.empleados" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                  </select>
                </div>
              </div>
              <div class="form-group">
                <label class="form-label">Comprobante</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" />
                  <input v-model="movementForm.comprobante" class="input-clinical" maxlength="100" />
                </div>
              </div>
            </div>
            <p class="field-hint">La cuenta nueva es una referencia de laboratorio; no genera un cobro en Caja.</p>

            <!-- Exámenes -->
            <div class="exam-section">
              <div class="exam-search">
                <div class="form-group" style="flex: 2;">
                  <label class="form-label">Buscar exámenes</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-magnifying-glass" class="input-icon" />
                    <input v-model="examQuery" class="input-clinical" />
                  </div>
                </div>
                <button type="button" class="btn-secondary" @click="findExams" style="margin-top: 1.5rem;">
                  <UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />
                  Buscar
                </button>
              </div>
              <div class="exam-add">
                <div class="form-group" style="flex: 2;">
                  <label class="form-label">Examen</label>
                  <div class="input-wrapper">
                    <UIcon name="i-heroicons-list-bullet" class="input-icon" />
                    <select v-model="examId" class="input-clinical">
                      <option value="">Seleccionar</option>
                      <option v-for="e in catalogs.examenes" :key="e.id" :value="e.id">{{ e.codigo }} · {{ e.nombre }}</option>
                    </select>
                  </div>
                </div>
                <button type="button" class="btn-primary" @click="addMovementExam" style="margin-top: 1.5rem;">
                  <UIcon name="i-heroicons-plus" class="w-4 h-4" />
                  Agregar
                </button>
              </div>
            </div>

            <div v-if="movementItems.length" class="table-responsive">
              <table class="lab-table">
                <thead>
                  <tr>
                    <th>Código</th>
                    <th>Descripción</th>
                    <th>Cantidad</th>
                    <th>Precio unitario S/</th>
                    <th>Subtotal S/</th>
                    <th>Acción</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(i, index) in movementItems" :key="i.examen_id">
                    <td>{{ i.codigo }}</td>
                    <td>{{ i.nombre }}</td>
                    <td>
                      <input v-model.number="i.cantidad" type="number" class="input-clinical input-sm" min="1" max="1000" required />
                    </td>
                    <td>
                      <input v-model="i.precio" type="number" class="input-clinical input-sm" min="0" max="999999" step="0.0001" required />
                    </td>
                    <td>{{ money(Number(i.precio) * i.cantidad) }}</td>
                    <td>
                      <button type="button" class="btn-remove" :disabled="requestedIds.includes(i.examen_id)" @click="movementItems.splice(index, 1)">
                        <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <p class="total">Total S/ {{ money(movementTotal) }}</p>

            <div class="form-group full-width">
              <label class="form-label">Observaciones</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
                <textarea v-model="movementForm.observaciones" class="input-clinical" maxlength="4000" rows="2"></textarea>
              </div>
            </div>

            <div class="form-actions">
              <button class="btn-primary" :disabled="busy || !movementItems.length">
                <UIcon name="i-heroicons-check" class="w-4 h-4" />
                {{ editingId ? 'Actualizar' : 'Guardar movimiento' }}
              </button>
            </div>
          </form>

          <!-- Historial -->
          <div v-if="history.length" class="history-section">
            <h4 class="section-title">Exámenes históricos del paciente</h4>
            <div class="table-responsive">
              <table class="lab-table">
                <thead>
                  <tr>
                    <th>Fecha</th>
                    <th>Movimiento</th>
                    <th>Examen</th>
                    <th>Cuenta</th>
                    <th>Comprobante</th>
                    <th>Orden</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(h, i) in history" :key="i">
                    <td>{{ h.fecha }}</td>
                    <td>{{ h.movimiento }}</td>
                    <td>{{ h.codigo }} · {{ h.examen }}</td>
                    <td>{{ h.cuenta }}</td>
                    <td>{{ h.comprobante }}</td>
                    <td>{{ h.orden }}</td>
                  </tr>
                  <tr v-if="!history.length">
                    <td colspan="6" style="text-align: center; color: var(--ink-soft);">Sin exámenes históricos.</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </template>
      </template>
    </section>

    <!-- Detail Panel -->
    <section v-if="detail && !formKind" class="panel detail-panel">
      <div class="detail-header">
        <div>
          <h2 class="detail-title">{{ detail.numero || detail.numero_orden }}</h2>
          <p class="detail-subtitle">{{ detail.orden?.paciente || detail.paciente }} · {{ detail.estado }}</p>
        </div>
        <button class="btn-secondary" @click="detail = null">
          <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
          Cerrar
        </button>
      </div>

      <!-- Órdenes Detail -->
      <template v-if="mode==='ordenes'">
        <div class="detail-info">
          <p>HC {{ detail.historia }} · Cuenta {{ detail.numero_cuenta }} · {{ detail.servicio }} · Médico {{ detail.medico }}</p>
          <p>{{ detail.indicacion_clinica }}</p>
        </div>
        <div class="exam-list">
          <div v-for="e in detail.items" :key="e.id" class="exam-item">
            <span class="exam-code">{{ e.codigo }}</span>
            <span class="exam-name">{{ e.nombre }}</span>
            <span class="exam-muestra">{{ e.tipo_muestra }}</span>
          </div>
        </div>
        <div class="form-actions">
          <button v-if="!detail.movimiento_id && detail.estado==='pendiente'" class="btn-primary" @click="scheduleDetail">
            <UIcon name="i-heroicons-calendar" class="w-4 h-4" />
            Agendar laboratorio
          </button>
          <NuxtLink v-if="detail.movimiento_id" :to="'/app/laboratorio/movimientos/'+detail.movimiento_id" class="btn-secondary">
            <UIcon name="i-heroicons-eye" class="w-4 h-4" />
            Ver movimiento
          </NuxtLink>
        </div>
      </template>

      <!-- Movimientos Detail -->
      <template v-else>
        <div class="detail-info">
          <p>HC {{ detail.orden.historia }} · Cuenta {{ detail.orden.numero_cuenta }} · {{ detail.orden.servicio }} · Médico {{ detail.orden.medico }} · Toma examen {{ detail.toma_examen }}</p>
        </div>

        <div class="form-actions">
          <button v-if="detail.estado==='agendado'" class="btn-secondary" @click="editMovement">
            <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
            Editar
          </button>
          <button class="btn-secondary" @click="download('/movimientos/'+detail.id+'/ticket.pdf', 'ticket-laboratorio.pdf')">
            <UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />
            Ticket PDF
          </button>
          <button class="btn-secondary" @click="loadAudit">
            <UIcon name="i-heroicons-document-text" class="w-4 h-4" />
            Auditoría
          </button>
          <button v-if="detail.estado==='agendado'" class="btn-primary" :disabled="busy" @click="action('tomar-muestra')">
            <UIcon name="i-heroicons-check" class="w-4 h-4" />
            Registrar toma de muestra
          </button>
          <button v-if="detail.estado==='atendido'" class="btn-primary" @click="download('/movimientos/'+detail.id+'/resultados.pdf', 'resultados-laboratorio.pdf')">
            <UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />
            Resultados PDF
          </button>
        </div>

        <!-- Resultados -->
        <div v-for="i in detail.items" :key="i.id" class="result-section">
          <h4 class="result-title">{{ i.codigo }} · {{ i.nombre }}</h4>
          <p class="field-hint">Muestra {{ i.tipo_muestra || 'No especificada' }} · Cantidad {{ i.cantidad }} · Subtotal S/ {{ money(i.subtotal) }}</p>
          <div v-for="(r, index) in resultForms[i.id]" :key="index" class="result-row">
            <div class="form-grid">
              <div class="form-group" v-for="f in resultFields" :key="f.key">
                <label class="form-label">{{ f.label }}</label>
                <input
                  v-model="r[f.key]"
                  class="input-clinical"
                  :disabled="detail.estado!=='en_proceso'"
                  :maxlength="f.max"
                />
              </div>
              <button v-if="detail.estado==='en_proceso'" class="btn-remove" @click="resultForms[i.id].splice(index, 1)">
                <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
              </button>
            </div>
          </div>
          <button v-if="detail.estado==='en_proceso'" class="btn-secondary" @click="resultForms[i.id].push(emptyResult(i))">
            <UIcon name="i-heroicons-plus" class="w-4 h-4" />
            Agregar parámetro
          </button>
        </div>

        <div v-if="detail.estado==='en_proceso'" class="form-actions">
          <button class="btn-secondary" :disabled="busy" @click="saveResults">
            <UIcon name="i-heroicons-check" class="w-4 h-4" />
            Guardar resultados
          </button>
          <button class="btn-primary" :disabled="busy" @click="validateResults">
            <UIcon name="i-heroicons-check-badge" class="w-4 h-4" />
            Guardar y validar informe
          </button>
        </div>

        <!-- Anulación -->
        <form v-if="['agendado','en_proceso'].includes(detail.estado)" class="cancel-form" @submit.prevent="action('anular')">
          <div class="form-group">
            <label class="form-label">Motivo de anulación</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
              <textarea v-model="cancelReason" class="input-clinical" maxlength="2000" required rows="2"></textarea>
            </div>
          </div>
          <button class="btn-danger" :disabled="busy">
            <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            Anular movimiento
          </button>
        </form>

        <p v-if="detail.motivo_anulacion" class="field-hint">Motivo: {{ detail.motivo_anulacion }}</p>
        <p v-if="detail.validado_por" class="field-hint">Validado por {{ detail.validado_por }} · {{ detail.validado_at }} UTC</p>

        <!-- Auditoría -->
        <div v-if="auditRows" class="audit-section">
          <h4 class="section-title">Auditoría</h4>
          <div class="table-responsive">
            <table class="lab-table">
              <thead>
                <tr>
                  <th>Fecha UTC</th>
                  <th>Acción</th>
                  <th>Usuario</th>
                  <th>Detalle</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="a in auditRows" :key="a.id">
                  <td>{{ a.created_at }}</td>
                  <td>{{ a.action }}</td>
                  <td>{{ a.user_name }}</td>
                  <td>
                    <details>
                      <summary>Ver cambios</summary>
                      <pre>{{ JSON.stringify({ antes: a.old_values, despues: a.new_values }, null, 2) }}</pre>
                    </details>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </section>
  </div>
</template>

<script setup lang="ts">
type Mode = 'ordenes' | 'movimientos' | 'cupos' | 'ficha-covid'

const props = defineProps<{
  mode: Mode
  initialId?: string
  create?: boolean
}>()

const { api } = useApi()
const endpoint = '/app/laboratorio'

// Configuración
const titles = {
  ordenes: 'Órdenes',
  movimientos: 'Movimientos',
  cupos: 'Cupos',
  'ficha-covid': 'Ficha Covid'
}

const formTitles: Record<string, string> = {
  cupo: 'Registrar / editar cupos',
  orden: 'Registrar orden',
  covid: 'Ficha Covid',
  movimiento: 'Agendar / editar laboratorio'
}

const serviceTypes = [
  { value: 'CONSULTA_EXTERNA', label: 'Consulta externa' },
  { value: 'APOYO_DIAGNOSTICO', label: 'Apoyo al diagnóstico' },
  { value: 'HOSPITALIZACION', label: 'Hospitalización' },
  { value: 'EMERGENCIA', label: 'Emergencia' }
]

const covidStates = ['pendiente', 'positivo', 'negativo', 'indeterminado', 'invalido']

const resultFields = [
  { key: 'parametro', label: 'Parámetro', max: 150 },
  { key: 'valor', label: 'Resultado', max: 2000 },
  { key: 'unidad', label: 'Unidad', max: 50 },
  { key: 'referencia', label: 'Referencia', max: 1000 },
  { key: 'observacion', label: 'Observación', max: 1000 }
]

// Computed
const states = computed(() => {
  if (props.mode === 'ficha-covid') return covidStates
  if (props.mode === 'ordenes') return ['pendiente', 'en_proceso', 'completada', 'anulada']
  return ['agendado', 'en_proceso', 'atendido', 'anulado']
})

const searchFields = computed(() => {
  if (props.mode === 'cupos') return [{ key: 'fecha', label: 'Fecha' }]
  if (props.mode === 'ficha-covid') {
    return [
      { key: 'dni', label: 'DNI' },
      { key: 'historia', label: 'N.° historia' },
      { key: 'apellido', label: 'Apellido paterno' },
      { key: 'materno', label: 'Apellido materno' },
      { key: 'fecha', label: 'Fecha' }
    ]
  }
  return [
    { key: 'numero', label: props.mode === 'ordenes' ? 'N.° orden' : 'N.° movimiento' },
    { key: 'historia', label: 'N.° historia clínica' },
    { key: 'cuenta', label: 'N.° cuenta' },
    { key: 'apellido', label: 'Apellido paterno' },
    { key: 'fecha', label: 'Fecha' }
  ]
})

const tableColumns = computed(() => {
  let cols: Record<string, string> = {}
  if (props.mode === 'cupos') {
    cols = {
      fecha: 'Fecha',
      cupos: 'Cupos',
      usados: 'Reservados',
      disponibles: 'Disponibles',
      registrado_por: 'Registrado por'
    }
  } else if (props.mode === 'ficha-covid') {
    cols = {
      fecha: 'Fecha',
      dni: 'DNI',
      historia: 'HC',
      paciente: 'Paciente',
      tipo_prueba: 'Prueba',
      muestra: 'Muestra',
      resultado: 'Resultado'
    }
  } else {
    const prefix = props.mode === 'ordenes' ? 'numero_orden' : 'numero'
    cols = {
      [prefix]: 'Número',
      numero_cuenta: 'N.° cuenta',
      historia: 'HC',
      paciente: 'Paciente',
      estado: 'Estado',
      [props.mode === 'ordenes' ? 'created_at' : 'fecha']: 'Fecha',
      medico: 'Ordena prueba',
      servicio: 'Servicio',
      fuente_financiamiento: 'Fuente financ.',
      registrado_por: 'Registrado por'
    }
  }
  return Object.entries(cols).map(([key, label]) => ({ key, label }))
})

// State
const today = () => {
  return new Intl.DateTimeFormat('en-CA', {
    timeZone: 'America/Lima',
    year: 'numeric',
    month: '2-digit',
    day: '2-digit'
  }).format(new Date())
}

const blankFilter = () => ({
  numero: '',
  historia: '',
  cuenta: '',
  apellido: '',
  materno: '',
  dni: '',
  fecha: '',
  estado: '',
  tipos: [] as string[]
})

const filter = reactive<Record<string, any>>(blankFilter())
let applied: Record<string, any> = {}

const rows = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)
const formKind = ref('')
const editingId = ref('')
const detail = ref<any>(null)

const catalogs = reactive<Record<string, any[]>>({
  examenes: [],
  empleados: [],
  servicios: [],
  especialidades: [],
  seguros: []
})

const patient = ref<any>(null)
const foundPatients = ref<any[]>([])
const patientQuery = ref('')

const orderForm = reactive({
  tipo_servicio: 'APOYO_DIAGNOSTICO',
  numero_cuenta: '',
  fuente_financiamiento: '',
  servicio_id: '',
  especialidad_id: '',
  medico_id: '',
  indicacion_clinica: ''
})

const chosenExams = ref<any[]>([])
const examQuery = ref('')
const examId = ref('')

const cupo = reactive({ fecha: today(), cupos: 0 })
const covid = reactive({
  fecha: today(),
  tipo_prueba: '',
  muestra: '',
  resultado: 'pendiente',
  observaciones: '',
  version: 1
})

const movementForm = reactive({
  fecha: today(),
  toma_examen_id: '',
  medico_id: '',
  agendamiento_por: 'PACIENTE',
  registrar_por: 'ORDEN',
  cuenta_nueva: false,
  comprobante: '',
  observaciones: ''
})

const orderQuery = ref('')
const foundOrders = ref<any[]>([])
const selectedOrder = ref<any>(null)
const movementItems = ref<any[]>([])
const requestedIds = computed(() => selectedOrder.value?.items?.map((i: any) => i.examen_id) || [])
const movementTotal = computed(() => movementItems.value.reduce((sum, i) => sum + Number(i.precio) * i.cantidad, 0))
const movementVersion = ref(1)
const history = ref<any[]>([])
const auditRows = ref<any[] | null>(null)
const cancelReason = ref('')
const resultForms = reactive<Record<string, any[]>>({})
let loadId = 0

// Utils
const money = (n: any) => Number(n || 0).toFixed(4)

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}

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

// API Methods
async function run(fn: () => Promise<void>) {
  if (busy.value) return
  busy.value = true
  error.value = ''
  notice.value = ''
  try {
    await fn()
  } catch (e) {
    error.value = err(e)
  } finally {
    busy.value = false
  }
}

async function loadPage(p: number) {
  page.value = p
  await load()
}

async function load() {
  const request = ++loadId
  loading.value = true
  error.value = ''
  try {
    const data = await api<any>(endpoint + '/' + props.mode, {
      query: { ...applied, page: page.value, page_size: pageSize.value }
    })
    if (request !== loadId) return
    rows.value = Array.isArray(data) ? data : data.items
    total.value = Array.isArray(data) ? data.length : data.total
    if (page.value > pages.value) {
      page.value = pages.value
      await load()
    }
  } catch (e) {
    if (request === loadId) {
      error.value = err(e)
      rows.value = []
      total.value = 0
    }
  } finally {
    if (request === loadId) loading.value = false
  }
}

function search() {
  applied = Object.fromEntries(
    Object.entries(filter).filter(([, v]) => Array.isArray(v) ? v.length : v !== '')
  )
  page.value = 1
  void load()
}

function clearFilter() {
  Object.assign(filter, blankFilter())
  search()
}

async function getCatalogs() {
  const keys = ['examenes', 'empleados', 'servicios', 'especialidades', 'seguros']
  await Promise.all(keys.map(async k => {
    catalogs[k] = await api<any[]>(endpoint + '/catalogos/' + k)
  }))
}

function closeEditor() {
  formKind.value = ''
  editingId.value = ''
  selectedOrder.value = null
  foundOrders.value = []
  foundPatients.value = []
  patient.value = null
}

async function newRecord() {
  await run(async () => {
    closeEditor()
    detail.value = null
    if (props.mode !== 'cupos') await getCatalogs()
    formKind.value = props.mode === 'cupos' ? 'cupo' : props.mode === 'ficha-covid' ? 'covid' : props.mode === 'ordenes' ? 'orden' : 'movimiento'
    chosenExams.value = []
    movementItems.value = []
    Object.assign(cupo, { fecha: today(), cupos: 0 })
    Object.assign(covid, { fecha: today(), tipo_prueba: '', muestra: '', resultado: 'pendiente', observaciones: '', version: 1 })
    Object.assign(orderForm, { tipo_servicio: 'APOYO_DIAGNOSTICO', numero_cuenta: '', fuente_financiamiento: '', servicio_id: '', especialidad_id: '', medico_id: '', indicacion_clinica: '' })
    Object.assign(movementForm, { fecha: today(), toma_examen_id: '', medico_id: '', agendamiento_por: 'PACIENTE', registrar_por: 'ORDEN', cuenta_nueva: false, comprobante: '', observaciones: '' })
  })
}

function startOrder() {
  formKind.value = 'orden'
  selectedOrder.value = null
  patient.value = null
  chosenExams.value = []
}

async function findPatients() {
  await run(async () => {
    foundPatients.value = await api<any[]>(endpoint + '/pacientes', { query: { q: patientQuery.value } })
    if (!foundPatients.value.length) notice.value = 'No se encontraron pacientes. Regístrelo primero en Gestión de Pacientes.'
  })
}

function choosePatient(p: any) {
  patient.value = p
  foundPatients.value = []
}

async function findExams() {
  await run(async () => {
    catalogs.examenes = await api<any[]>(endpoint + '/catalogos/examenes', { query: { q: examQuery.value } })
  })
}

function addExam() {
  const e = catalogs.examenes.find(x => x.id === examId.value)
  if (e && !chosenExams.value.some(x => x.id === e.id)) {
    chosenExams.value.push(e)
  }
}

function addMovementExam() {
  const e = catalogs.examenes.find(x => x.id === examId.value)
  if (e && !movementItems.value.some(x => x.examen_id === e.id)) {
    movementItems.value.push({
      examen_id: e.id,
      codigo: e.codigo,
      nombre: e.nombre,
      cantidad: 1,
      precio: money(e.precio)
    })
  }
}

async function saveOrder() {
  await run(async () => {
    const o = await api<any>(endpoint + '/ordenes', {
      method: 'POST',
      body: {
        ...orderForm,
        patient_id: patient.value.id,
        examen_ids: chosenExams.value.map(e => e.id)
      }
    })
    notice.value = 'Orden registrada.'
    closeEditor()
    await load()
    await getCatalogs()
    formKind.value = 'movimiento'
    await chooseOrderInternal(o.id)
  })
}

async function findOrders() {
  await run(async () => {
    const key = movementForm.registrar_por === 'CUENTA' ? 'cuenta' : movementForm.registrar_por === 'HISTORIA' ? 'historia' : 'numero'
    const data = await api<any>(endpoint + '/ordenes', {
      query: { [key]: orderQuery.value, estado: 'pendiente' }
    })
    foundOrders.value = data.items
    if (!data.items.length) notice.value = 'No se encontraron órdenes pendientes.'
  })
}

async function chooseOrderInternal(id: string) {
  selectedOrder.value = await api<any>(endpoint + '/ordenes/' + id)
  movementForm.medico_id = selectedOrder.value.medico_id || ''
  movementItems.value = selectedOrder.value.items.map((e: any) => ({
    examen_id: e.examen_id,
    codigo: e.codigo,
    nombre: e.nombre,
    cantidad: 1,
    precio: money(e.precio)
  }))
  foundOrders.value = []
  history.value = await api<any[]>(endpoint + '/pacientes/' + selectedOrder.value.patient_id + '/historial')
}

async function chooseOrder(id: string) {
  await run(() => chooseOrderInternal(id))
}

async function saveMovement() {
  await run(async () => {
    const data = await api<any>(endpoint + '/movimientos' + (editingId.value ? '/' + editingId.value : ''), {
      method: editingId.value ? 'PATCH' : 'POST',
      body: {
        ...movementForm,
        orden_id: selectedOrder.value.id,
        ...(editingId.value ? { version: movementVersion.value } : {}),
        items: movementItems.value.map(i => ({
          examen_id: i.examen_id,
          cantidad: i.cantidad,
          precio: i.precio
        }))
      }
    })
    notice.value = 'Movimiento guardado.'
    closeEditor()
    await load()
    if (props.mode === 'movimientos') setDetail(data)
    else await navigateTo('/app/laboratorio/movimientos/' + data.id)
  })
}

function editCupo(row: any) {
  editingId.value = row.id
  Object.assign(cupo, { fecha: row.fecha, cupos: row.cupos })
  formKind.value = 'cupo'
  detail.value = null
}

async function saveCupo() {
  await run(async () => {
    await api(endpoint + '/cupos', {
      method: editingId.value ? 'PUT' : 'POST',
      body: { ...cupo }
    })
    closeEditor()
    notice.value = 'Cupos guardados.'
    await load()
  })
}

function editCovid(row: any) {
  editingId.value = row.id
  patient.value = { id: row.patient_id, nombre: row.paciente, historia: row.historia }
  Object.assign(covid, {
    fecha: row.fecha,
    tipo_prueba: row.tipo_prueba,
    muestra: row.muestra,
    resultado: row.resultado,
    observaciones: row.observaciones || '',
    version: row.version
  })
  formKind.value = 'covid'
}

async function saveCovid() {
  await run(async () => {
    const { version, ...values } = covid
    await api(endpoint + '/ficha-covid' + (editingId.value ? '/' + editingId.value : ''), {
      method: editingId.value ? 'PATCH' : 'POST',
      body: {
        ...values,
        patient_id: patient.value.id,
        ...(editingId.value ? { version } : {})
      }
    })
    closeEditor()
    notice.value = 'Ficha guardada.'
    await load()
  })
}

function emptyResult(i: any) {
  return {
    parametro: i.nombre,
    valor: '',
    unidad: i.unidad || '',
    referencia: i.referencia || '',
    observacion: ''
  }
}

function setDetail(d: any) {
  detail.value = d
  auditRows.value = null
  cancelReason.value = ''
  if (d.orden) {
    for (const i of d.items) {
      resultForms[i.id] = i.resultados.length ? i.resultados.map((r: any) => ({ ...r })) : [emptyResult(i)]
    }
  }
}

async function view(row: any) {
  if (props.mode === 'cupos') { editCupo(row); return }
  if (props.mode === 'ficha-covid') { editCovid(row); return }
  await run(async () => {
    closeEditor()
    setDetail(await api(endpoint + '/' + props.mode + '/' + row.id))
  })
}

async function scheduleDetail() {
  await run(async () => {
    const id = detail.value.id
    await getCatalogs()
    formKind.value = 'movimiento'
    editingId.value = ''
    await chooseOrderInternal(id)
  })
}

async function editMovement() {
  await run(async () => {
    const d = detail.value
    await getCatalogs()
    await chooseOrderInternal(d.orden_id)
    editingId.value = d.id
    movementVersion.value = d.version
    for (const k of Object.keys(movementForm)) {
      (movementForm as any)[k] = k === 'medico_id' ? d.orden.medico_id : d[k] ?? ''
    }
    movementItems.value = d.items.map((i: any) => ({ ...i }))
    formKind.value = 'movimiento'
  })
}

async function action(kind: string) {
  await run(async () => {
    const d = await api(endpoint + '/movimientos/' + detail.value.id + '/' + kind, {
      method: 'POST',
      body: {
        version: detail.value.version,
        motivo: kind === 'anular' ? cancelReason.value : null
      }
    })
    setDetail(d)
    notice.value = 'Operación registrada.'
    await load()
  })
}

async function resultsInternal() {
  const items = detail.value.items.map((i: any) => ({
    item_id: i.id,
    valores: resultForms[i.id] || []
  }))
  if (items.some((i: any) => !i.valores.length || i.valores.some((r: any) => !r.parametro?.trim() || !r.valor?.trim()))) {
    throw { data: { detail: 'Complete al menos un resultado por examen.' } }
  }
  const d = await api(endpoint + '/movimientos/' + detail.value.id + '/resultados', {
    method: 'PUT',
    body: { version: detail.value.version, items }
  })
  setDetail(d)
}

async function saveResults() {
  await run(async () => {
    await resultsInternal()
    notice.value = 'Resultados guardados como borrador.'
  })
}

async function validateResults() {
  await run(async () => {
    await resultsInternal()
    const d = await api(endpoint + '/movimientos/' + detail.value.id + '/validar', {
      method: 'POST',
      body: { version: detail.value.version }
    })
    setDetail(d)
    notice.value = 'Informe validado. Los resultados quedan cerrados.'
    await load()
  })
}

async function loadAudit() {
  await run(async () => {
    auditRows.value = await api<any[]>(endpoint + '/movimientos/' + detail.value.id + '/auditoria')
  })
}

async function download(path: string, name: string) {
  await run(async () => {
    const blob = await api<Blob>(endpoint + path, {
      responseType: 'blob',
      query: path.endsWith('.csv') ? applied : undefined
    })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = name
    a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  })
}

onMounted(async () => {
  await load()
  if (props.initialId) await view({ id: props.initialId })
  else if (props.create) await newRecord()
})

onBeforeUnmount(() => {
  ++loadId
})
</script>

<style scoped>
.lab-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
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

.breadcrumb {
  display: flex;
  flex-direction: column;
}

.header-actions {
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
  background: var(--teal);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
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
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
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

.btn-danger {
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
}

.btn-danger:hover {
  background: var(--alert-dark);
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

.btn-remove {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: none;
  background: transparent;
  color: var(--alert);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-remove:hover {
  background: var(--alert-soft);
}

/* Tabs */
.lab-tabs {
  display: flex;
  gap: 0.25rem;
  border-bottom: 2px solid var(--line);
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.tab-link {
  padding: 0.625rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink-soft);
  text-decoration: none;
  border-bottom: 2px solid transparent;
  transition: all 0.2s ease;
  margin-bottom: -2px;
}

.tab-link:hover {
  color: var(--ink);
}

.tab-link--active {
  color: var(--teal);
  border-bottom-color: var(--teal);
}

/* Messages */
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

/* Panels */
.panel {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  padding: 1.25rem;
  margin-bottom: 1.5rem;
  box-shadow: var(--shadow-sm);
}

/* Search */
.search-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.search-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

.search-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.search-types {
  grid-column: 1 / -1;
}

.types-group {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
}

.type-label {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: var(--ink);
  cursor: pointer;
}

.type-label input {
  width: auto;
}

.search-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

/* Results */
.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1rem;
}

.results-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.results-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.input-sm {
  padding: 0.375rem 0.625rem;
  font-size: 0.8125rem;
  width: auto;
  min-width: 60px;
}

/* Loading */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  gap: 0.5rem;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* Table */
.table-responsive {
  overflow-x: auto;
}

.lab-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.lab-table thead {
  background: var(--mist);
}

.lab-table th {
  padding: 0.625rem 0.75rem;
  text-align: left;
  font-weight: 600;
  color: var(--ink-soft);
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--line);
}

.lab-table td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
}

.lab-table tr:hover {
  background: var(--mist);
}

/* Action Buttons in Table */
.action-buttons {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 4px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--mist);
}

.action-view:hover {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
}

.action-pdf:hover {
  color: var(--alert);
  border-color: var(--alert-soft);
  background: var(--alert-soft);
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  justify-content: center;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

.page-info {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Editor */
.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
}

.editor-title {
  font-size: 1rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.editor-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  margin-bottom: 0.25rem;
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
  padding: 0.5rem 0.75rem;
  padding-left: 2.25rem;
  border-radius: 6px;
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
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin-top: 0.25rem;
}

.form-actions {
  display: flex;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}

/* Choices */
.choices {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin: 0.75rem 0;
}

.choice-btn {
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s ease;
}

.choice-btn:hover {
  background: var(--teal-soft);
  border-color: var(--teal);
}

/* Patient Info Card */
.patient-info-card {
  background: var(--paper);
  border-radius: var(--radius);
  border: 1px solid var(--line);
  padding: 0.75rem 1rem;
  margin: 0.75rem 0;
}

.patient-info-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.patient-avatar {
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

.patient-info {
  display: flex;
  flex-direction: column;
}

.patient-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.patient-details {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.patient-separator {
  color: var(--line);
}

/* Exam Section */
.exam-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  padding: 0.75rem;
  background: var(--mist);
  border-radius: var(--radius);
  margin: 0.5rem 0;
}

.exam-search,
.exam-add {
  display: flex;
  gap: 0.75rem;
  align-items: flex-end;
}

.exam-search .form-group,
.exam-add .form-group {
  flex: 2;
}

.exam-list {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  margin: 0.5rem 0;
}

.exam-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.375rem 0.75rem;
  background: var(--teal-soft);
  border-radius: 6px;
  font-size: 0.8125rem;
}

.exam-code {
  font-weight: 600;
  color: var(--teal);
  font-family: monospace;
}

.exam-name {
  flex: 1;
  color: var(--ink);
}

.exam-muestra {
  font-size: 0.6875rem;
  color: var(--ink-soft);
}

/* Total */
.total {
  text-align: right;
  font-weight: 600;
  font-size: 1rem;
  color: var(--ink);
  margin: 0.5rem 0;
}

/* Detail */
.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.detail-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.detail-subtitle {
  font-size: 0.875rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

.detail-info {
  font-size: 0.875rem;
  color: var(--ink);
  padding: 0.5rem 0;
}

/* Result Section */
.result-section {
  border-top: 1px solid var(--line);
  padding: 0.75rem 0;
}

.result-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.25rem 0;
}

.result-row {
  padding: 0.375rem 0;
}

/* Cancel Form */
.cancel-form {
  border-top: 1px solid var(--alert-soft);
  padding-top: 1rem;
  margin-top: 0.5rem;
}

/* Audit */
.audit-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0 0 0.5rem 0;
}

details summary {
  cursor: pointer;
  color: var(--teal);
}

details pre {
  white-space: pre-wrap;
  max-width: 600px;
  overflow-wrap: anywhere;
  font-size: 0.75rem;
  background: var(--mist);
  padding: 0.5rem;
  border-radius: 4px;
}

/* History */
.history-section {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

/* Responsive */
@media (max-width: 1024px) {
  .lab-container {
    padding: 1rem 1.5rem;
  }

  .search-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 768px) {
  .lab-container {
    padding: 0.75rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .search-grid {
    grid-template-columns: 1fr;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .exam-search,
  .exam-add {
    flex-direction: column;
    align-items: stretch;
  }

  .results-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .lab-tabs {
    gap: 0;
  }

  .tab-link {
    padding: 0.5rem 0.75rem;
    font-size: 0.75rem;
  }

  .types-group {
    flex-direction: column;
    gap: 0.25rem;
  }
}

@media (max-width: 480px) {
  .panel {
    padding: 0.75rem;
  }

  .lab-table th,
  .lab-table td {
    padding: 0.375rem 0.5rem;
    font-size: 0.75rem;
  }

  .detail-header {
    flex-direction: column;
    gap: 0.5rem;
  }

  .form-actions {
    flex-direction: column;
  }

  .form-actions > * {
    width: 100%;
    justify-content: center;
  }

  .pagination {
    flex-wrap: wrap;
  }

  .patient-info-header {
    flex-direction: column;
    align-items: flex-start;
  }
}
</style>