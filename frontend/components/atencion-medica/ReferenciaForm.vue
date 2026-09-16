<template>
  <section class="form-card">
    <div class="card-header">
      <div class="card-header-icon" style="background: #fee2e2">
        <UIcon name="i-heroicons-arrow-right-circle" class="w-4 h-4" style="color: #dc2626" />
      </div>
      <div>
        <h3 class="card-title">Referencia</h3>
        <p class="card-subtitle">Envío del paciente a otro establecimiento</p>
      </div>
      <span v-if="referenciaExistente" class="receta-status-badge" :class="getEstadoBadgeClass(referenciaExistente.estado)">
        <UIcon :name="getEstadoIcon(referenciaExistente.estado)" class="w-3.5 h-3.5" />
        {{ formatEstado(referenciaExistente.estado) }}
      </span>
    </div>

    <div v-if="referenciaExistente" class="receta-generada">
      <div class="receta-header">
        <div class="receta-number">
          <UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: #dc2626" />
          <span>Referencia N° <strong>{{ referenciaExistente.numero_referencia }}</strong></span>
        </div>
        <span class="receta-estado" :class="getEstadoClass(referenciaExistente.estado)">
          {{ formatEstado(referenciaExistente.estado) }}
        </span>
      </div>
      <div class="receta-items">
        <div class="receta-item">
          <div class="receta-item-header">
            <span class="receta-item-name">Hospital Destino</span>
            <span class="receta-item-value">{{ referenciaExistente.tenant_destino_nombre || referenciaExistente.nombre_ipress_destino || '—' }}</span>
          </div>
        </div>
        <div v-if="referenciaExistente.codigo_renipress_destino" class="receta-item">
          <div class="receta-item-header">
            <span class="receta-item-name">RENIPRESS</span>
            <span class="receta-item-value">{{ referenciaExistente.codigo_renipress_destino }}</span>
          </div>
        </div>
        <div v-if="referenciaExistente.especialidad_destino" class="receta-item">
          <div class="receta-item-header">
            <span class="receta-item-name">Especialidad</span>
            <span class="receta-item-value">{{ referenciaExistente.especialidad_destino }}</span>
          </div>
        </div>
        <div v-if="referenciaExistente.diagnostico_codigo" class="receta-item">
          <div class="receta-item-header">
            <span class="receta-item-name">Diagnóstico</span>
            <span class="receta-item-value">[{{ referenciaExistente.diagnostico_codigo }}] {{ referenciaExistente.diagnostico_descripcion }}</span>
          </div>
        </div>
        <div class="receta-item">
          <div class="receta-item-header">
            <span class="receta-item-name">Motivo</span>
            <span class="receta-item-value">{{ referenciaExistente.motivo }}</span>
          </div>
        </div>
      </div>
      <div v-if="referenciaExistente.estado === 'pendiente'" class="receta-item-indicaciones" style="padding: 0.75rem 1rem; background: var(--amber-soft);">
        <UIcon name="i-heroicons-clock" class="w-4 h-4" style="color: var(--amber)" />
        <span>Referencia pendiente de aprobación.</span>
      </div>
      <div v-if="referenciaExistente.estado === 'confirmada'" class="receta-item-indicaciones" style="padding: 0.75rem 1rem; background: var(--green-soft);">
        <UIcon name="i-heroicons-check-circle" class="w-4 h-4" style="color: var(--green)" />
        <span>Referencia confirmada y en proceso.</span>
      </div>
    </div>

    <p v-else-if="soloLectura" role="status">No hay un documento disponible. Guarda los cambios de la atención antes de generar órdenes; una atención cerrada permite solo consulta.</p>
    <template v-else>
      <div class="flex gap-3 mb-3">
        <button class="px-3 py-1 rounded text-sm" :class="tipoDestino === 'interno' ? 'bg-red-600 text-white' : 'border'" @click="tipoDestino = 'interno'">
          Hospital de nuestro sistema
        </button>
        <button class="px-3 py-1 rounded text-sm" :class="tipoDestino === 'externo' ? 'bg-red-600 text-white' : 'border'" @click="tipoDestino = 'externo'">
          IPRESS externo
        </button>
      </div>

      <div v-if="tipoDestino === 'interno'" class="form-group full-width" style="margin-bottom: 0.75rem;">
        <label class="form-label">Hospital Destino *</label>
        <select v-model="tenantDestino" class="input-clinical" style="padding-left: 0.875rem;">
          <option value="">Seleccionar...</option>
          <option v-for="t in tenantsDisponibles" :key="t.id" :value="t.id">{{ t.name }}</option>
        </select>
      </div>

      <template v-else>
        <div class="form-group" style="margin-bottom: 0.75rem;">
          <label class="form-label">Código RENIPRESS</label>
          <input v-model="codigoRenipress" class="input-clinical" style="padding-left: 0.875rem;" placeholder="Ej: 00004319" />
        </div>
        <div class="form-group full-width" style="margin-bottom: 0.75rem;">
          <label class="form-label">Nombre del IPRESS *</label>
          <input v-model="nombreIpress" class="input-clinical" style="padding-left: 0.875rem;" placeholder="Nombre del establecimiento de salud..." />
        </div>
      </template>

      <div class="form-group full-width" style="margin-bottom: 0.75rem;">
        <label class="form-label">Especialidad Destino</label>
        <input v-model="especialidadDestino" class="input-clinical" style="padding-left: 0.875rem;" placeholder="Ej: Cardiología" />
      </div>

      <div class="form-group full-width" style="margin-bottom: 0.75rem;">
        <label class="form-label">Motivo *</label>
        <textarea v-model="motivo" rows="3" class="input-clinical" style="padding-left: 0.875rem;" placeholder="Motivo de la referencia..."></textarea>
      </div>

      <button class="btn-generar-receta" style="background: #dc2626;" :disabled="!puedeGenerar || generando" @click="generarReferencia">
        {{ generando ? 'Generando...' : 'Generar Referencia' }}
      </button>

    </template>
    <p v-if="errorLocal" class="text-sm text-red-600 mt-2" role="alert">{{ errorLocal }}</p>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{ citaId: string; soloLectura?: boolean }>()
const emit = defineEmits<{ generada: [] }>()

const { api } = useApi()

const referenciaExistente = ref<any>(null)
const tenantsDisponibles = ref<any[]>([])
const tipoDestino = ref<'interno' | 'externo'>('externo')
const tenantDestino = ref('')
const codigoRenipress = ref('')
const nombreIpress = ref('')
const especialidadDestino = ref('')
const motivo = ref('')
const generando = ref(false)
const errorLocal = ref('')

// Mapas de estado para referencia
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

const getEstadoBadgeClass = (estado: string) => {
  const map: Record<string, string> = {
    pendiente: 'status-pendiente',
    confirmada: 'status-confirmada',
    en_proceso: 'status-en-proceso',
    completada: 'status-completada',
    cancelada: 'status-cancelada',
    rechazada: 'status-rechazada',
  }
  return map[estado] || 'status-pendiente'
}

const puedeGenerar = computed(() => {
  if (!motivo.value) return false
  return tipoDestino.value === 'interno' ? !!tenantDestino.value : !!nombreIpress.value
})

async function generarReferencia() {
  if (props.soloLectura) return
  generando.value = true
  errorLocal.value = ''
  try {
    const payload = tipoDestino.value === 'interno'
      ? { tenant_destino_id: tenantDestino.value, especialidad_destino: especialidadDestino.value, motivo: motivo.value }
      : { codigo_renipress_destino: codigoRenipress.value, nombre_ipress_destino: nombreIpress.value, especialidad_destino: especialidadDestino.value, motivo: motivo.value }
    referenciaExistente.value = await api(`/app/consulta-externa/referencias/${props.citaId}`, { method: 'POST', body: payload })
    emit('generada')
  } catch (e: any) {
    errorLocal.value = e?.data?.detail || 'Error al generar la referencia'
  } finally {
    generando.value = false
  }
}

onMounted(async () => {
  try {
    referenciaExistente.value = await api(`/app/consulta-externa/referencias/${props.citaId}`)
  } catch (e: any) { if ((e?.statusCode || e?.status || e?.response?.status) !== 404) errorLocal.value = 'No se pudo cargar el documento. Recarga la página para reintentar.' }
  if (!referenciaExistente.value) {
    try {
      tenantsDisponibles.value = await api('/app/consulta-externa/referencias/tenants-disponibles')
    } catch { /* silencioso */ }
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

.status-en-proceso {
  background: var(--teal-soft);
  color: var(--teal);
}

.status-completada {
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

/* Estado badges para referencia */
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

/* Botones de tipo */
.flex.gap-3 .border {
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.flex.gap-3 .border:hover {
  background: var(--mist);
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

  .flex.gap-3 {
    flex-direction: column;
  }
}
</style>
