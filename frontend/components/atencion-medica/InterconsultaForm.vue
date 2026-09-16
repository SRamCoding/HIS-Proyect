<template>
  <section class="form-card">
    <div class="card-header">
      <div class="card-header-icon" style="background: #f3e8ff">
        <UIcon name="i-heroicons-arrow-path-rounded-square" class="w-4 h-4" style="color: #9333ea" />
      </div>
      <div>
        <h3 class="card-title">Interconsulta</h3>
        <p class="card-subtitle">Solicitud a otra especialidad</p>
      </div>
      <span v-if="interconsultaExistente" class="receta-status-badge" :class="getEstadoBadgeClass(interconsultaExistente.estado)">
        <UIcon :name="getEstadoIcon(interconsultaExistente.estado)" class="w-3.5 h-3.5" />
        {{ formatEstado(interconsultaExistente.estado) }}
      </span>
    </div>

    <div v-if="interconsultaExistente" class="receta-generada">
      <div class="receta-header">
        <div class="receta-number">
          <UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: #9333ea" />
          <span>Interconsulta N° <strong>{{ interconsultaExistente.numero || '—' }}</strong></span>
        </div>
        <span class="receta-estado" :class="getEstadoClass(interconsultaExistente.estado)">
          {{ formatEstado(interconsultaExistente.estado) }}
        </span>
      </div>
      <div class="receta-items">
        <div class="receta-item">
          <div class="receta-item-header">
            <span class="receta-item-name">Especialidad Destino</span>
            <span class="receta-item-value">{{ interconsultaExistente.especialidad_destino_nombre }}</span>
          </div>
        </div>
        <div class="receta-item">
          <div class="receta-item-header">
            <span class="receta-item-name">Motivo</span>
            <span class="receta-item-value">{{ interconsultaExistente.motivo }}</span>
          </div>
        </div>
        <div v-if="interconsultaExistente.urgente" class="receta-item" style="background: var(--alert-soft); border-left: 3px solid var(--alert);">
          <div class="receta-item-header">
            <span class="receta-item-name" style="color: var(--alert); font-weight: 600;">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" />
              Urgente
            </span>
          </div>
        </div>
      </div>
      <div v-if="interconsultaExistente.estado === 'pendiente'" class="receta-item-indicaciones" style="padding: 0.75rem 1rem; background: var(--blue-soft);">
        <UIcon name="i-heroicons-information-circle" class="w-4 h-4" style="color: var(--blue)" />
        <span>Quedó registrada en Admisión para ser programada.</span>
      </div>
      <div v-if="interconsultaExistente.estado === 'confirmada'" class="receta-item-indicaciones" style="padding: 0.75rem 1rem; background: var(--green-soft);">
        <UIcon name="i-heroicons-check-circle" class="w-4 h-4" style="color: var(--green)" />
        <span>Interconsulta confirmada y en proceso de atención.</span>
      </div>
    </div>

    <p v-else-if="soloLectura" role="status">No hay un documento disponible. Guarda los cambios de la atención antes de generar órdenes; una atención cerrada permite solo consulta.</p>
    <template v-else>
      <div class="form-group full-width" style="margin-bottom: 0.75rem;">
        <label class="form-label">Especialidad Destino *</label>
        <select v-model="especialidadDestino" class="input-clinical" style="padding-left: 0.875rem;">
          <option value="">Seleccionar...</option>
          <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
        </select>
      </div>
      <div class="form-group full-width" style="margin-bottom: 0.75rem;">
        <label class="form-label">Motivo *</label>
        <textarea v-model="motivo" rows="3" class="input-clinical" style="padding-left: 0.875rem;" placeholder="Motivo de la interconsulta..."></textarea>
      </div>
      <div class="form-group" style="margin-bottom: 0.75rem;">
        <label class="flex items-center gap-2 text-sm">
          <input type="checkbox" v-model="urgente" />
          Urgente
        </label>
      </div>
      <button class="btn-generar-receta" style="background: #9333ea;" :disabled="!especialidadDestino || !motivo || generando" @click="generarInterconsulta">
        {{ generando ? 'Generando...' : 'Generar Interconsulta' }}
      </button>

    </template>
    <p v-if="errorLocal" class="text-sm text-red-600 mt-2" role="alert">{{ errorLocal }}</p>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{ citaId: string; soloLectura?: boolean }>()
const emit = defineEmits<{ generada: [] }>()

const { api } = useApi()

const interconsultaExistente = ref<any>(null)
const especialidades = ref<any[]>([])
const especialidadDestino = ref('')
const motivo = ref('')
const urgente = ref(false)
const generando = ref(false)
const errorLocal = ref('')

// Mapas de estado para interconsulta
const getEstadoColor = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'var(--amber)',
    confirmada: 'var(--blue)',
    programada: 'var(--teal)',
    atendida: 'var(--green)',
    cancelada: 'var(--alert)',
    rechazada: 'var(--alert)',
  }
  return map[estado] || 'var(--ink-soft)'
}

const getEstadoClass = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'estado-pendiente',
    confirmada: 'estado-confirmada',
    programada: 'estado-programada',
    atendida: 'estado-atendida',
    cancelada: 'estado-cancelada',
    rechazada: 'estado-rechazada',
  }
  return map[estado] || ''
}

const getEstadoIcon = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'i-heroicons-clock',
    confirmada: 'i-heroicons-check-badge',
    programada: 'i-heroicons-calendar',
    atendida: 'i-heroicons-check-circle',
    cancelada: 'i-heroicons-x-circle',
    rechazada: 'i-heroicons-x-mark',
  }
  return map[estado] || 'i-heroicons-circle'
}

const formatEstado = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'Pendiente',
    confirmada: 'Confirmada',
    programada: 'Programada',
    atendida: 'Atendida',
    cancelada: 'Cancelada',
    rechazada: 'Rechazada',
  }
  return map[estado] || estado
}

const getEstadoBadgeClass = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'status-pendiente',
    confirmada: 'status-confirmada',
    programada: 'status-programada',
    atendida: 'status-atendida',
    cancelada: 'status-cancelada',
    rechazada: 'status-rechazada',
  }
  return map[estado] || 'status-pendiente'
}

async function generarInterconsulta() {
  if (props.soloLectura) return
  generando.value = true
  errorLocal.value = ''
  try {
    interconsultaExistente.value = await api(`/app/consulta-externa/interconsultas/${props.citaId}`, {
      method: 'POST',
      body: { especialidad_destino_id: especialidadDestino.value, motivo: motivo.value, urgente: urgente.value },
    })
    emit('generada')
  } catch (e: any) {
    errorLocal.value = e?.data?.detail || 'Error al generar la interconsulta'
  } finally {
    generando.value = false
  }
}

onMounted(async () => {
  try {
    interconsultaExistente.value = await api(`/app/consulta-externa/interconsultas/${props.citaId}`)
  } catch (e: any) { if ((e?.statusCode || e?.status || e?.response?.status) !== 404) errorLocal.value = 'No se pudo cargar el documento. Recarga la página para reintentar.' }
  if (!interconsultaExistente.value) {
    try { especialidades.value = await api('/app/consulta-externa/programacion-medica/especialidades') }
    catch { errorLocal.value = 'No se pudieron cargar las especialidades disponibles.' }
  }
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

.status-pendiente {
  background: var(--amber-soft);
  color: var(--amber);
}

.status-confirmada {
  background: var(--blue-soft);
  color: var(--blue);
}

.status-programada {
  background: var(--teal-soft);
  color: var(--teal);
}

.status-atendida {
  background: var(--green-soft);
  color: var(--green);
}

.status-cancelada {
  background: var(--alert-soft);
  color: var(--alert);
}

.status-rechazada {
  background: var(--alert-soft);
  color: var(--alert);
}

/* Estado badges para interconsulta */
.estado-pendiente {
  background: var(--amber-soft);
  color: var(--amber);
}

.estado-confirmada {
  background: var(--blue-soft);
  color: var(--blue);
}

.estado-programada {
  background: var(--teal-soft);
  color: var(--teal);
}

.estado-atendida {
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

.input-clinical {
  width: 100%;
  padding: 0.625rem 0.875rem;
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

.input-clinical[type="checkbox"] {
  width: auto;
  padding: 0;
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

.receta-item-value {
  font-size: 0.875rem;
  color: var(--ink-soft);
  text-align: right;
  max-width: 60%;
  word-break: break-word;
}

.receta-item-indicaciones {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: var(--ink);
  border-top: 1px solid var(--line);
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

  .receta-item-value {
    text-align: left;
    max-width: 100%;
  }
}
</style>
