<template>
  <section class="form-card">
    <div class="card-header">
      <div class="card-header-icon" style="background: var(--purple-soft)">
        <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" style="color: var(--purple)" />
      </div>
      <div>
        <h3 class="card-title">Hospitalización</h3>
        <p class="card-subtitle">Asignación de cama e ingreso del paciente</p>
      </div>
      <span v-if="hospitalizacionExistente" class="receta-status-badge status-generada">
        <UIcon name="i-heroicons-check-circle" class="w-3.5 h-3.5" />
        {{ hospitalizacionExistente.estado === 'internado' ? 'Internado' : hospitalizacionExistente.estado === 'alta' ? 'Alta' : 'Pendiente' }}
      </span>
      <span v-else class="receta-status-badge status-pendiente">
        <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
        Pendiente
      </span>
    </div>

    <!-- Hospitalización ya registrada -->
    <div v-if="hospitalizacionExistente" class="hospitalizacion-generada">
      <div class="hospitalizacion-header">
        <div class="hospitalizacion-number">
          <UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: var(--purple)" />
          <span>N° <strong>{{ hospitalizacionExistente.numero_hospitalizacion }}</strong></span>
        </div>
        <span class="hospitalizacion-estado" :class="hospitalizacionExistente.estado === 'internado' ? 'estado-internado' : hospitalizacionExistente.estado === 'alta' ? 'estado-alta' : 'estado-pendiente-hosp'">
          {{ hospitalizacionExistente.estado === 'internado' ? '🛏️ Internado' : hospitalizacionExistente.estado === 'alta' ? '✅ Alta' : '⏳ Pendiente' }}
        </span>
      </div>

      <div class="hospitalizacion-info-grid">
        <div class="hosp-info-item">
          <span class="hosp-info-label">Cama</span>
          <span class="hosp-info-value">
            <UIcon name="i-heroicons-building-office-2" class="w-3.5 h-3.5" style="color: var(--purple)" />
            {{ hospitalizacionExistente.cama_codigo }} - {{ hospitalizacionExistente.cama_nombre }}
          </span>
        </div>
        <div class="hosp-info-item">
          <span class="hosp-info-label">Ingreso</span>
          <span class="hosp-info-value">
            <UIcon name="i-heroicons-calendar" class="w-3.5 h-3.5" style="color: var(--ink-soft)" />
            {{ formatFechaHora(hospitalizacionExistente.fecha_ingreso) }}
          </span>
        </div>
        <div v-if="hospitalizacionExistente.especialidad_ingreso_nombre" class="hosp-info-item">
          <span class="hosp-info-label">Especialidad</span>
          <span class="hosp-info-value">
            <UIcon name="i-heroicons-star" class="w-3.5 h-3.5" style="color: var(--purple)" />
            {{ hospitalizacionExistente.especialidad_ingreso_nombre }}
          </span>
        </div>
        <div v-if="hospitalizacionExistente.diagnostico_ingreso_codigo" class="hosp-info-item hosp-info-full">
          <span class="hosp-info-label">Diagnóstico de Ingreso</span>
          <span class="hosp-info-value">
            <span class="diagnostico-badge">[{{ hospitalizacionExistente.diagnostico_ingreso_codigo }}]</span>
            {{ hospitalizacionExistente.diagnostico_ingreso_descripcion }}
          </span>
        </div>
      </div>

      <div v-if="hospitalizacionExistente.estado === 'internado'" class="hospitalizacion-actions">
        <button class="btn-alta" :disabled="dandoAlta" @click="darAlta">
          <UIcon v-if="dandoAlta" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
          <UIcon v-else name="i-heroicons-check-badge" class="w-4 h-4" />
          {{ dandoAlta ? 'Procesando...' : 'Dar de Alta' }}
        </button>
      </div>
    </div>

    <!-- Formulario para registrar hospitalización -->
    <template v-else>
      <div class="hosp-form-grid">
        <!-- Cama Disponible -->
        <div class="form-group full-width">
          <label class="form-label">Cama Disponible <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-building-office-2" class="input-icon" />
            <select v-model="camaSeleccionada" class="input-clinical" :class="{ 'input-error': errorCama }">
              <option value="">Seleccionar cama...</option>
              <option v-for="c in camasDisponibles" :key="c.id" :value="c.id">
                [{{ c.codigo }}] {{ c.nombre }} {{ c.tipo_cama ? '- ' + c.tipo_cama : '' }}
              </option>
            </select>
          </div>
          <div v-if="!camasDisponibles.length" class="field-hint-warning">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-3.5 h-3.5" />
            No hay camas disponibles en este momento.
          </div>
          <span v-if="errorCama" class="error-message">{{ errorCama }}</span>
        </div>

        <!-- Especialidad de Ingreso -->
        <div class="form-group full-width">
          <label class="form-label">Especialidad de Ingreso</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-star" class="input-icon" />
            <select v-model="especialidadIngreso" class="input-clinical">
              <option value="">Sin especificar</option>
              <option v-for="e in especialidadesIngreso" :key="e.id" :value="e.id">{{ e.nombre }}</option>
            </select>
          </div>
          <p class="field-hint">Especialidad que solicita la hospitalización</p>
        </div>

        <!-- Diagnóstico de Ingreso (CIE-10) -->
        <div class="form-group full-width">
          <label class="form-label">Diagnóstico de Ingreso (CIE-10)</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-document-magnifying-glass" class="input-icon" />
            <input
              v-model="buscaCie10Ingreso"
              type="text"
              class="input-clinical"
              placeholder="Buscar código o descripción..."
              @input="buscarCie10IngresoDebounced"
            />
          </div>
          <ul v-if="resultadosCie10Ingreso.length" class="cie10-results">
            <li v-for="r in resultadosCie10Ingreso" :key="r.id" class="cie10-result-item" @click="seleccionarDiagnosticoIngreso(r)">
              <span class="cie10-result-code">[{{ r.codigo_cie10 }}]</span>
              <span class="cie10-result-desc">{{ r.descripcion }}</span>
              <span class="cie10-result-add">
                <UIcon name="i-heroicons-plus-circle" class="w-4 h-4" style="color: var(--purple)" />
              </span>
            </li>
          </ul>
          <div v-if="diagnosticoIngresoSeleccionado" class="diagnostico-seleccionado">
            <div class="diagnostico-seleccionado-info">
              <span class="diagnostico-code">[{{ diagnosticoIngresoSeleccionado.codigo_cie10 }}]</span>
              <span class="diagnostico-desc">{{ diagnosticoIngresoSeleccionado.descripcion }}</span>
            </div>
            <button class="diagnostico-remove-btn" @click="diagnosticoIngresoSeleccionado = null">
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            </button>
          </div>
        </div>
      </div>

      <!-- Acciones -->
      <div class="hosp-actions">
        <button class="btn-hosp-registrar" :disabled="!camaSeleccionada || generandoHosp" @click="registrarIngreso">
          <UIcon v-if="generandoHosp" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
          <UIcon v-else name="i-heroicons-check-badge" class="w-4 h-4" />
          {{ generandoHosp ? 'Generando...' : 'Registrar Ingreso' }}
        </button>
        <span v-if="!camaSeleccionada && camasDisponibles.length" class="hosp-warning">
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" />
          Selecciona una cama para continuar
        </span>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  citaId: string
  hospitalizacionExistente: any | null
  camasDisponibles: any[]
  especialidadesIngreso: any[]
}>()

const emit = defineEmits<{
  (e: 'hospitalizacion-registrada', data: any): void
  (e: 'alta-registrada', data: any): void
  (e: 'error', msg: string): void
}>()

const { api } = useApi()

// Estado
const camaSeleccionada = ref('')
const especialidadIngreso = ref('')
const buscaCie10Ingreso = ref('')
const resultadosCie10Ingreso = ref<any[]>([])
const diagnosticoIngresoSeleccionado = ref<any>(null)
const generandoHosp = ref(false)
const dandoAlta = ref(false)
const errorCama = ref('')
let debounceCie10IngresoTimer: any = null

// Helpers
const formatFechaHora = (fecha: string) => {
  if (!fecha) return '—'
  return new Date(fecha).toLocaleString('es-PE')
}

// CIE-10
function buscarCie10IngresoDebounced() {
  clearTimeout(debounceCie10IngresoTimer)
  debounceCie10IngresoTimer = setTimeout(async () => {
    if (buscaCie10Ingreso.value.length < 2) {
      resultadosCie10Ingreso.value = []
      return
    }
    try {
      resultadosCie10Ingreso.value = await api(
        `/app/consulta-externa/atenciones-medicas/cie10/buscar?q=${encodeURIComponent(buscaCie10Ingreso.value)}`
      )
    } catch (e) {
      /* silencioso */
    }
  }, 300)
}

function seleccionarDiagnosticoIngreso(r: any) {
  diagnosticoIngresoSeleccionado.value = r
  buscaCie10Ingreso.value = ''
  resultadosCie10Ingreso.value = []
}

// Acciones
async function registrarIngreso() {
  if (!camaSeleccionada.value) {
    errorCama.value = 'Debes seleccionar una cama'
    return
  }
  errorCama.value = ''
  generandoHosp.value = true

  try {
    const result = await api(`/app/consulta-externa/hospitalizacion/${props.citaId}`, {
      method: 'POST',
      body: {
        cama_id: camaSeleccionada.value,
        especialidad_ingreso_id: especialidadIngreso.value || null,
        diagnostico_ingreso_id: diagnosticoIngresoSeleccionado.value?.id || null,
      },
    })
    // Limpiar formulario
    camaSeleccionada.value = ''
    especialidadIngreso.value = ''
    diagnosticoIngresoSeleccionado.value = null
    emit('hospitalizacion-registrada', result)
  } catch (e: any) {
    emit('error', e?.data?.detail || 'Error al registrar la hospitalización')
  } finally {
    generandoHosp.value = false
  }
}

async function darAlta() {
  dandoAlta.value = true
  try {
    const result = await api(`/app/consulta-externa/hospitalizacion/${props.citaId}/alta`, {
      method: 'POST'
    })
    emit('alta-registrada', result)
  } catch (e: any) {
    emit('error', e?.data?.detail || 'Error al dar de alta')
  } finally {
    dandoAlta.value = false
  }
}
</script>

<style scoped>
/* ============================================
   Estilos para Hospitalización - Mejorados
   ============================================ */

/* Reutilizar estilos base del padre */
.form-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  padding: 1.5rem;
  border: 1px solid var(--line);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
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

/* Badge de estado */
.receta-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
  margin-left: auto;
  flex-shrink: 0;
}

.receta-status-badge.status-generada {
  background: var(--green-soft);
  color: var(--green);
}

.receta-status-badge.status-pendiente {
  background: var(--amber-soft);
  color: var(--amber);
}

/* Hospitalización Generada */
.hospitalizacion-generada {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}

.hospitalizacion-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: var(--mist);
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.hospitalizacion-number {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--ink);
}

.hospitalizacion-number strong {
  color: var(--purple);
}

.hospitalizacion-estado {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.125rem 0.625rem;
  border-radius: 12px;
}

.estado-internado {
  background: var(--blue-soft);
  color: var(--blue);
}

.estado-alta {
  background: var(--green-soft);
  color: var(--green);
}

.estado-pendiente-hosp {
  background: var(--amber-soft);
  color: var(--amber);
}

/* Info Grid */
.hospitalizacion-info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
}

.hosp-info-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  padding: 0.375rem;
  border-radius: var(--radius);
  background: var(--mist);
}

.hosp-info-full {
  grid-column: 1 / -1;
}

.hosp-info-label {
  font-size: 0.625rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
}

.hosp-info-value {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
}

.hosp-info-value .diagnostico-badge {
  font-weight: 600;
  color: var(--purple);
  font-size: 0.75rem;
  background: var(--purple-soft);
  padding: 0.0625rem 0.375rem;
  border-radius: 4px;
}

/* Acciones de Hospitalización */
.hospitalizacion-actions {
  padding: 0.75rem 1rem;
  border-top: 1px solid var(--line);
}

.btn-alta {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1.25rem;
  border-radius: 8px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: none;
  background: var(--amber);
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-alta:hover:not(:disabled) {
  background: var(--amber-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-alta:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Formulario */
.hosp-form-grid {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.form-group.full-width {
  width: 100%;
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
  border-color: var(--purple);
  box-shadow: 0 0 0 3px var(--purple-soft);
}

.input-clinical.input-error {
  border-color: var(--alert);
}

.input-clinical.input-error:focus {
  box-shadow: 0 0 0 3px var(--alert-soft);
}

.field-hint {
  font-size: 0.6875rem;
  color: var(--ink-soft);
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

.error-message {
  display: block;
  font-size: 0.75rem;
  color: var(--alert);
  margin-top: 0.25rem;
}

/* CIE-10 Results */
.cie10-results {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0 0;
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
  color: var(--purple);
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

/* Diagnóstico Seleccionado */
.diagnostico-seleccionado {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  margin-top: 0.5rem;
  border-radius: 6px;
  border: 1px solid var(--purple-soft);
  background: var(--purple-soft);
}

.diagnostico-seleccionado-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  font-size: 0.8125rem;
}

.diagnostico-code {
  font-weight: 600;
  color: var(--purple);
  font-size: 0.75rem;
  flex-shrink: 0;
}

.diagnostico-desc {
  color: var(--ink);
}

.diagnostico-remove-btn {
  background: transparent;
  border: none;
  color: var(--alert);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background 0.15s ease;
}

.diagnostico-remove-btn:hover {
  background: var(--alert-soft);
}

/* Acciones */
.hosp-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 1.25rem;
  flex-wrap: wrap;
}

.btn-hosp-registrar {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  background: var(--purple);
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-hosp-registrar:hover:not(:disabled) {
  background: var(--purple-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-hosp-registrar:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.hosp-warning {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.75rem;
  color: var(--alert);
}

/* Responsive */
@media (max-width: 768px) {
  .hospitalizacion-info-grid {
    grid-template-columns: 1fr;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .receta-status-badge {
    margin-left: 0;
  }

  .hospitalizacion-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .hosp-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-hosp-registrar {
    justify-content: center;
  }

  .btn-alta {
    width: 100%;
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .diagnostico-seleccionado {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .diagnostico-seleccionado-info {
    flex-wrap: wrap;
  }

  .cie10-result-item {
    flex-wrap: wrap;
  }
}
</style>