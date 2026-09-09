<template>
  <section class="form-card">
    <div class="card-header">
      <div class="card-header-icon" style="background: #fef3c7">
        <UIcon name="i-heroicons-beaker" class="w-4 h-4" style="color: #d97706" />
      </div>
      <div>
        <h3 class="card-title">Orden de Laboratorio</h3>
        <p class="card-subtitle">Exámenes solicitados para el paciente</p>
      </div>
      <span v-if="ordenExistente" class="receta-status-badge status-generada">
        <UIcon name="i-heroicons-check-circle" class="w-3.5 h-3.5" />
        Orden Generada
      </span>
      <span v-else class="receta-status-badge status-pendiente">
        <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
        Pendiente
      </span>
    </div>

    <!-- Orden ya generada -->
    <div v-if="ordenExistente" class="receta-generada">
      <div class="receta-header">
        <div class="receta-number">
          <UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: #d97706" />
          <span>Orden N° <strong>{{ ordenExistente.numero_orden }}</strong></span>
        </div>
        <span class="receta-estado estado-pendiente-farmacia">{{ ordenExistente.estado }}</span>
      </div>
      <div class="receta-items">
        <div v-for="item in ordenExistente.items" :key="item.id" class="receta-item">
          <div class="receta-item-header">
            <span class="receta-item-name">[{{ item.codigo }}] {{ item.nombre }}</span>
          </div>
          <div class="receta-item-details">
            <span v-if="item.categoria"><UIcon name="i-heroicons-tag" class="w-3 h-3" /> {{ item.categoria }}</span>
            <span v-if="item.tipo_muestra"><UIcon name="i-heroicons-beaker" class="w-3 h-3" /> {{ item.tipo_muestra }}</span>
          </div>
        </div>
      </div>
      <div v-if="ordenExistente.indicacion_clinica" class="receta-item-indicaciones" style="padding: 0.75rem 1rem;">
        <strong>Indicación clínica:</strong> {{ ordenExistente.indicacion_clinica }}
      </div>
    </div>

    <!-- Formulario para generar orden -->
    <template v-else>
      <div class="form-group full-width" style="margin-bottom: 0.75rem;">
        <label class="form-label">Buscar Examen</label>
        <div class="input-wrapper">
          <UIcon name="i-heroicons-magnifying-glass" class="input-icon" />
          <input v-model="buscaExamen" type="text" class="input-clinical" placeholder="Buscar por código o nombre..." @input="buscarExamenDebounced" />
        </div>
      </div>

      <ul v-if="resultadosExamen.length" class="medicamento-results">
        <li v-for="e in resultadosExamen" :key="e.id" class="medicamento-result-item" @click="agregarExamen(e)">
          <div class="medicamento-result-info">
            <span class="medicamento-result-code">[{{ e.codigo }}]</span>
            <span class="medicamento-result-name">{{ e.nombre }}</span>
            <span v-if="e.categoria" class="medicamento-result-concentracion">{{ e.categoria }}</span>
            <span v-if="e.requiere_ayuno" class="medicamento-result-dci">(requiere ayuno)</span>
          </div>
          <UIcon name="i-heroicons-plus-circle" class="w-5 h-5" style="color: #d97706" />
        </li>
      </ul>

      <div v-if="examenesSeleccionados.length" class="receta-items-form">
        <div class="receta-items-header">
          <span class="receta-items-title">Exámenes seleccionados</span>
          <span class="receta-items-count">{{ examenesSeleccionados.length }} exámenes</span>
        </div>
        <div v-for="(ex, idx) in examenesSeleccionados" :key="idx" class="diagnostico-item" style="margin-bottom: 0.5rem;">
          <div class="diagnostico-info">
            <span class="diagnostico-code">[{{ ex.codigo }}]</span>
            <span class="diagnostico-desc">{{ ex.nombre }}</span>
          </div>
          <button class="diagnostico-remove" @click="examenesSeleccionados.splice(idx, 1)">
            <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
          </button>
        </div>

        <div class="form-group full-width" style="margin-top: 0.75rem;">
          <label class="form-label">Indicación Clínica</label>
          <textarea v-model="indicacionClinica" rows="2" class="input-clinical" style="padding-left: 0.875rem;" placeholder="Motivo del estudio, sospecha diagnóstica..."></textarea>
        </div>

        <button class="btn-generar-receta" style="background: #d97706;" :disabled="generando" @click="generarOrden">
          {{ generando ? 'Generando...' : 'Generar Orden' }}
        </button>
      </div>
      <div v-else class="receta-empty">
        <div class="receta-empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-beaker" class="w-8 h-8" style="color: var(--ink-soft)" />
        </div>
        <p class="receta-empty-text">Busca y agrega exámenes a la orden</p>
      </div>

      <div v-if="errorLocal" class="text-sm text-red-600 mt-2">{{ errorLocal }}</div>
    </template>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{ citaId: string }>()
const emit = defineEmits<{ generada: [] }>()

const { api } = useApi()

const cargandoInicial = ref(true)
const ordenExistente = ref<any>(null)
const buscaExamen = ref('')
const resultadosExamen = ref<any[]>([])
const examenesSeleccionados = ref<any[]>([])
const indicacionClinica = ref('')
const generando = ref(false)
const errorLocal = ref('')
let debounceTimer: any = null

// Mapas de estado para exámenes de laboratorio
const getEstadoColor = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'var(--amber)',
    confirmada: 'var(--blue)',
    en_proceso: 'var(--teal)',
    completada: 'var(--green)',
    cancelada: 'var(--alert)',
    rechazada: 'var(--alert)',
  }
  return map[estado] || 'var(--ink-soft)'
}

const getEstadoClass = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'estado-pendiente',
    confirmada: 'estado-confirmada',
    en_proceso: 'estado-en-proceso',
    completada: 'estado-completada',
    cancelada: 'estado-cancelada',
    rechazada: 'estado-rechazada',
  }
  return map[estado] || ''
}

const getEstadoIcon = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'i-heroicons-clock',
    confirmada: 'i-heroicons-check-badge',
    en_proceso: 'i-heroicons-arrow-path',
    completada: 'i-heroicons-check-circle',
    cancelada: 'i-heroicons-x-circle',
    rechazada: 'i-heroicons-x-mark',
  }
  return map[estado] || 'i-heroicons-circle'
}

const formatEstado = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'Pendiente',
    confirmada: 'Confirmada',
    en_proceso: 'En Proceso',
    completada: 'Completada',
    cancelada: 'Cancelada',
    rechazada: 'Rechazada',
  }
  return map[estado] || estado
}

function buscarExamenDebounced() {
  clearTimeout(debounceTimer)
  debounceTimer = setTimeout(async () => {
    if (buscaExamen.value.length < 2) { resultadosExamen.value = []; return }
    try {
      resultadosExamen.value = await api(`/app/consulta-externa/laboratorio/examenes/buscar?q=${encodeURIComponent(buscaExamen.value)}`)
    } catch { /* silencioso */ }
  }, 300)
}

function agregarExamen(e: any) {
  if (examenesSeleccionados.value.some((x) => x.id === e.id)) return
  examenesSeleccionados.value.push(e)
  buscaExamen.value = ''
  resultadosExamen.value = []
}

async function generarOrden() {
  generando.value = true
  errorLocal.value = ''
  try {
    ordenExistente.value = await api(`/app/consulta-externa/laboratorio/ordenes/${props.citaId}`, {
      method: 'POST',
      body: { examen_ids: examenesSeleccionados.value.map((e) => e.id), indicacion_clinica: indicacionClinica.value || null },
    })
    emit('generada')
  } catch (e: any) {
    errorLocal.value = e?.data?.detail || 'Error al generar la orden'
  } finally {
    generando.value = false
  }
}

onMounted(async () => {
  try {
    ordenExistente.value = await api(`/app/consulta-externa/laboratorio/ordenes/${props.citaId}`)
  } catch { /* aun no tiene orden */ }
  cargandoInicial.value = false
})
</script>

<style scoped>
/* Estilos base */
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

/* Status Badges */
.receta-status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  margin-left: auto;
}

.status-generada {
  background: var(--green-soft);
  color: var(--green);
}

.status-pendiente {
  background: var(--amber-soft);
  color: var(--amber);
}

/* Estado badges para laboratorio */
.estado-pendiente {
  background: var(--amber-soft);
  color: var(--amber);
}

.estado-confirmada {
  background: var(--blue-soft);
  color: var(--blue);
}

.estado-en-proceso {
  background: var(--teal-soft);
  color: var(--teal);
}

.estado-completada {
  background: var(--green-soft);
  color: var(--green);
}

.estado-cancelada {
  background: var(--alert-soft);
  color: var(--alert);
}

.estado-rechazada {
  background: var(--alert-soft);
  color: var(--alert);
}

/* Inputs */
.form-group {
  margin-bottom: 1rem;
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

/* Resultados de búsqueda */
.medicamento-results {
  list-style: none;
  padding: 0;
  margin: 0.5rem 0 0 0;
  max-height: 200px;
  overflow-y: auto;
  border: 1px solid var(--line);
  border-radius: 8px;
  background: var(--paper);
}

.medicamento-result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  transition: background 0.15s ease;
  border-bottom: 1px solid var(--line);
}

.medicamento-result-item:last-child {
  border-bottom: none;
}

.medicamento-result-item:hover {
  background: var(--mist);
}

.medicamento-result-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.medicamento-result-code {
  font-family: monospace;
  font-size: 0.75rem;
  color: var(--ink-soft);
  font-weight: 500;
}

.medicamento-result-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.medicamento-result-concentracion {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.medicamento-result-dci {
  font-size: 0.75rem;
  color: var(--ink-soft);
  font-style: italic;
}

/* Orden generada */
.receta-generada {
  border: 1px solid var(--line);
  border-radius: var(--radius);
  overflow: hidden;
}

.receta-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background: var(--mist);
  border-bottom: 1px solid var(--line);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.receta-number {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--ink);
}

.receta-number strong {
  font-weight: 600;
}

.receta-estado {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.125rem 0.625rem;
  border-radius: 12px;
}

.estado-pendiente-farmacia {
  background: var(--amber-soft);
  color: var(--amber);
}

.receta-items {
  padding: 0.5rem 0;
}

.receta-item {
  padding: 0.5rem 1rem;
  border-bottom: 1px solid var(--line);
}

.receta-item:last-child {
  border-bottom: none;
}

.receta-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.receta-item-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.receta-item-details {
  display: flex;
  gap: 1rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin-top: 0.125rem;
}

.receta-item-details span {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.receta-item-indicaciones {
  font-size: 0.875rem;
  color: var(--ink);
  border-top: 1px solid var(--line);
  background: var(--mist);
}

/* Formulario de selección */
.receta-items-form {
  margin-top: 1rem;
}

.receta-items-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.receta-items-title {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.receta-items-count {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.diagnostico-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.375rem 0.75rem;
  background: var(--mist);
  border-radius: 6px;
  gap: 0.5rem;
}

.diagnostico-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.diagnostico-code {
  font-family: monospace;
  font-size: 0.75rem;
  color: var(--ink-soft);
  font-weight: 500;
  flex-shrink: 0;
}

.diagnostico-desc {
  font-size: 0.875rem;
  color: var(--ink);
  word-break: break-word;
}

.diagnostico-remove {
  background: none;
  border: none;
  color: var(--alert);
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 4px;
  transition: background 0.15s ease;
  flex-shrink: 0;
}

.diagnostico-remove:hover {
  background: var(--alert-soft);
}

/* Botón generar */
.btn-generar-receta {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  border: none;
  color: white;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
  margin-top: 0.75rem;
}

.btn-generar-receta:hover:not(:disabled) {
  filter: brightness(0.9);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-generar-receta:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* Empty state */
.receta-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  gap: 0.75rem;
}

.receta-empty-icon {
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.receta-empty-text {
  font-size: 0.875rem;
  color: var(--ink-soft);
  margin: 0;
}

/* Responsive */
@media (max-width: 768px) {
  .form-card {
    padding: 1rem;
  }

  .card-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .receta-status-badge {
    margin-left: 0;
  }

  .receta-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .receta-item-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .receta-item-details {
    flex-wrap: wrap;
  }
}
</style>