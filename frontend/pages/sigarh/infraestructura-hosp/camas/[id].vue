<template>
  <div class="cama-edit-container">
    <!-- Progress Indicator (solo 1 paso) -->
    <div class="onboarding-progress">
      <div class="progress-steps">
        <div 
          class="step-item active completed"
        >
          <div class="step-circle">
            <span class="step-check">✓</span>
          </div>
          <span class="step-label">Editar Cama</span>
        </div>
      </div>
    </div>

    <div class="cama-edit-grid">
      <!-- Main Content -->
      <div class="cama-edit-main">
        <!-- Breadcrumb + Title -->
        <div class="mb-8">
          <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
            <NuxtLink :to="`/sigarh/infraestructura-hosp/camas?tenant=${tenant}`" class="hover:underline flex items-center gap-1" style="color: var(--ink-soft)">
              <UIcon name="i-heroicons-bed" class="w-3.5 h-3.5" />
              Camas
            </NuxtLink>
            <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
            <span style="color: var(--ink)">Editar</span>
          </div>
          <div class="flex items-center justify-between gap-4">
            <div class="flex items-center gap-4">
              <div class="header-icon" :style="{ background: form.is_active ? 'var(--teal-soft)' : 'var(--mist)' }">
                <UIcon 
                  name="i-heroicons-bed" 
                  class="w-6 h-6" 
                  :style="{ color: form.is_active ? 'var(--teal)' : 'var(--ink-soft)' }" 
                />
              </div>
              <div>
                <h1 class="page-title">{{ form.nombre || 'Editar Cama' }}</h1>
                <p class="page-subtitle">
                  <span class="dni-display font-mono-data">Código: {{ form.codigo || '—' }}</span>
                  <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
                  <span class="status-text-mini" :class="form.is_active ? 'text-active' : 'text-inactive'">
                    {{ form.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </p>
              </div>
            </div>
            <button
              class="btn-danger"
              @click="confirmarEliminar"
            >
              <UIcon name="i-heroicons-trash" class="w-4 h-4" />
              Eliminar
            </button>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="loading-spinner">
            <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
          </div>
          <p style="color: var(--ink-soft)">Cargando información de la cama...</p>
        </div>

        <template v-else>
          <!-- Form Card -->
          <section class="cama-edit-card">
            <div class="card-header">
              <div class="card-header-icon" style="background: var(--teal-soft)">
                <UIcon name="i-heroicons-bed" class="w-4 h-4" style="color: var(--teal)" />
              </div>
              <div>
                <h3 class="card-title">Datos de la Cama</h3>
                <p class="card-subtitle">Edita la información de la cama</p>
              </div>
            </div>

            <!-- Código Section (No modificable) -->
            <div class="codigo-section">
              <div class="codigo-header">
                <div class="codigo-header-left">
                  <UIcon name="i-heroicons-identification" class="w-4 h-4" style="color: var(--navy)" />
                  <span class="codigo-title">Código de la Cama</span>
                </div>
                <div class="codigo-display-field">
                  <span class="codigo-value font-mono-data">{{ form.codigo || '—' }}</span>
                  <span class="codigo-hint">No modificable</span>
                </div>
              </div>
            </div>

            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Código <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-identification" class="input-icon" />
                  <input 
                    v-model="form.codigo" 
                    type="text" 
                    class="input-clinical font-mono-data input-readonly"
                    disabled
                  />
                </div>
                <p class="field-hint">El código no puede modificarse</p>
              </div>

              <div class="form-group">
                <label class="form-label">Nombre <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-document-text" class="input-icon" />
                  <input 
                    v-model="form.nombre" 
                    type="text" 
                    class="input-clinical"
                    :class="{ 'input-error': errors.nombre }"
                    placeholder="Ej: Cama 101"
                    @input="errors.nombre = ''"
                  />
                </div>
                <span v-if="errors.nombre" class="error-message">{{ errors.nombre }}</span>
                <p class="field-hint">Nombre descriptivo de la cama</p>
              </div>

              <div class="form-group">
                <label class="form-label">Piso</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-arrow-up" class="input-icon" />
                  <select v-model="form.piso_id" class="input-clinical">
                    <option value="">Sin piso</option>
                    <option v-for="p in pisos" :key="p.id" :value="p.id">{{ p.nombre }}</option>
                  </select>
                </div>
                <p class="field-hint">Ubicación de la cama</p>
              </div>

              <div class="form-group">
                <label class="form-label">Sala</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                  <select v-model="form.sala_id" class="input-clinical">
                    <option value="">Sin sala</option>
                    <option v-for="s in salas" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                  </select>
                </div>
                <p class="field-hint">Sala donde se encuentra la cama</p>
              </div>

              <div class="form-group">
                <label class="form-label">Servicio</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-folder" class="input-icon" />
                  <select v-model="form.servicio_id" class="input-clinical">
                    <option value="">Sin servicio</option>
                    <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
                  </select>
                </div>
                <p class="field-hint">Servicio al que pertenece</p>
              </div>

              <div class="form-group">
                <label class="form-label">Tipo de Cama</label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-list-bullet" class="input-icon" />
                  <select v-model="form.tipo_cama" class="input-clinical">
                    <option value="">Sin tipo</option>
                    <option value="ADULTO">Adulto</option>
                    <option value="PEDIÁTRICO">Pediátrico</option>
                    <option value="UCI">UCI</option>
                    <option value="NEONATAL">Neonatal</option>
                    <option value="MATERNIDAD">Maternidad</option>
                    <option value="OBSERVACIÓN">Observación</option>
                  </select>
                </div>
                <p class="field-hint">Tipo de cama según especialidad</p>
              </div>

              <div class="form-group full-width">
                <label class="form-label">Estado <span class="required">*</span></label>
                <div class="input-wrapper">
                  <UIcon name="i-heroicons-flag" class="input-icon" />
                  <select v-model="form.estado" class="input-clinical">
                    <option value="DISPONIBLE">Disponible</option>
                    <option value="OCUPADA">Ocupada</option>
                    <option value="MANTENIMIENTO">Mantenimiento</option>
                    <option value="RESERVADA">Reservada</option>
                  </select>
                </div>
                <p class="field-hint">Estado actual de la cama</p>
              </div>

              <div class="form-group full-width">
                <div class="status-toggle">
                  <span class="toggle-label">Cama Activa</span>
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
                <p class="field-hint" style="margin-top: 0.5rem;">Las camas inactivas no se muestran en los listados</p>
              </div>
            </div>

            <!-- Preview Section -->
            <div v-if="form.codigo || form.nombre" class="preview-section">
              <h4 class="preview-title">Vista Previa</h4>
              <div class="preview-card">
                <div class="preview-icon" :style="{ background: getEstadoColor(form.estado) + '22' }">
                  <UIcon name="i-heroicons-bed" class="w-5 h-5" :style="{ color: getEstadoColor(form.estado) }" />
                </div>
                <div class="preview-info">
                  <span class="preview-name">{{ form.nombre || 'Nombre no definido' }}</span>
                  <span class="preview-dates">
                    <span class="preview-codigo font-mono-data">{{ form.codigo || 'Sin código' }}</span>
                    <span v-if="form.tipo_cama" class="preview-tipo">• {{ formatearTipo(form.tipo_cama) }}</span>
                  </span>
                </div>
                <span class="preview-status" :class="getEstadoClass(form.estado)">
                  <span class="estado-dot" :class="getEstadoDot(form.estado)" />
                  {{ formatearEstado(form.estado) }}
                </span>
              </div>

              <!-- Ubicación Preview -->
              <div v-if="form.piso_id || form.sala_id || form.servicio_id" class="preview-ubicacion">
                <span v-if="form.piso_texto" class="ubicacion-item">
                  <UIcon name="i-heroicons-arrow-up" class="w-3 h-3" />
                  {{ form.piso_texto }}
                </span>
                <span v-if="form.sala_texto" class="ubicacion-item">
                  <UIcon name="i-heroicons-building-office-2" class="w-3 h-3" />
                  {{ form.sala_texto }}
                </span>
                <span v-if="form.servicio_texto" class="ubicacion-item">
                  <UIcon name="i-heroicons-folder" class="w-3 h-3" />
                  {{ form.servicio_texto }}
                </span>
              </div>
            </div>

            <!-- Error Message -->
            <div v-if="error" class="error-banner">
              <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
              {{ error }}
            </div>

            <!-- Actions -->
            <div class="cama-edit-actions">
              <div class="action-spacer"></div>
              <div class="action-group">
                <button 
                  class="btn-primary" 
                  :disabled="saving" 
                  @click="guardar"
                >
                  <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                  <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
                  {{ saving ? 'Guardando...' : 'Guardar Cambios' }}
                </button>
                <NuxtLink
                  :to="`/sigarh/infraestructura-hosp/camas?tenant=${tenant}`"
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
      <div class="cama-edit-sidebar">
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
              <span class="summary-label">Código</span>
              <span class="summary-value font-mono-data">{{ form.codigo || '—' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Nombre</span>
              <span class="summary-value">{{ form.nombre || '—' }}</span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Tipo</span>
              <span class="summary-value">{{ formatearTipo(form.tipo_cama) || 'Sin tipo' }}</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Estado</span>
              <span class="summary-value">
                <span class="status-badge-mini" :class="getEstadoClass(form.estado)">
                  <span class="estado-dot" :class="getEstadoDot(form.estado)" />
                  {{ formatearEstado(form.estado) }}
                </span>
              </span>
            </div>
            <div class="summary-divider"></div>
            <div class="summary-item">
              <span class="summary-label">Ubicación</span>
              <span class="summary-value">{{ ubicacionResumen || 'Sin ubicación' }}</span>
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
                <p class="tip-text">
                  Mantén actualizada la información de la cama y su estado 
                  para una correcta asignación de pacientes.
                </p>
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
              <span class="stat-label">Campos Completos</span>
              <span class="stat-number">{{ filledFields }}/{{ totalFields }}</span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Estado</span>
              <span class="stat-number" :style="{ color: getEstadoColor(form.estado) }">
                {{ formatearEstado(form.estado) }}
              </span>
            </div>
            <div class="stat-item">
              <span class="stat-label">Ubicación</span>
              <span class="stat-number" :style="{ color: form.piso_id || form.sala_id ? 'var(--teal)' : 'var(--ink-soft)' }">
                {{ form.piso_id || form.sala_id ? '✓' : '—' }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-content" style="background: var(--paper); border-radius: var(--radius-lg)">
        <div class="modal-header">
          <div class="modal-icon" style="background: var(--alert-soft)">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" style="color: var(--alert)" />
          </div>
          <h3 class="modal-title">Confirmar Eliminación</h3>
        </div>
        <p class="modal-body">
          ¿Estás seguro de que deseas eliminar la cama <strong>{{ form.nombre }}</strong>?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta acción no se puede deshacer y eliminará todos los datos asociados.
          </span>
        </p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-danger" @click="deleteItem">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar Permanentemente
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Editar Cama' })

const { $api } = useNuxtApp()
const route = useRoute()
const router = useRouter()

const tenant = route.query.tenant as string
const id = route.params.id as string

const form = reactive({
  codigo: '',
  nombre: '',
  sala_id: '',
  piso_id: '',
  servicio_id: '',
  sala_texto: '',
  piso_texto: '',
  servicio_texto: '',
  tipo_cama: '',
  estado: 'DISPONIBLE',
  is_active: true,
})

const pisos = ref<any[]>([])
const salas = ref<any[]>([])
const servicios = ref<any[]>([])
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const showDeleteModal = ref(false)

const errors = reactive({
  nombre: '',
})

const filledFields = computed(() => {
  let count = 0
  if (form.codigo) count++
  if (form.nombre) count++
  if (form.piso_id) count++
  if (form.sala_id) count++
  if (form.servicio_id) count++
  if (form.tipo_cama) count++
  if (form.estado) count++
  return count
})

const totalFields = 7

const progressPercentage = computed(() => {
  let progress = 0
  if (form.codigo) progress += 15
  if (form.nombre) progress += 15
  if (form.piso_id) progress += 15
  if (form.sala_id) progress += 15
  if (form.servicio_id) progress += 15
  if (form.tipo_cama) progress += 15
  if (form.estado) progress += 10
  return progress
})

const ubicacionResumen = computed(() => {
  const partes = []
  if (form.piso_texto) partes.push(form.piso_texto)
  if (form.sala_texto) partes.push(form.sala_texto)
  if (form.servicio_texto) partes.push(form.servicio_texto)
  return partes.join(' › ') || 'Sin ubicación'
})

const formatearEstado = (estado: string) => {
  const map: Record<string, string> = {
    DISPONIBLE: 'Disponible',
    OCUPADA: 'Ocupada',
    MANTENIMIENTO: 'Mantenimiento',
    RESERVADA: 'Reservada'
  }
  return map[estado] || estado
}

const formatearTipo = (tipo: string) => {
  const map: Record<string, string> = {
    ADULTO: 'Adulto',
    PEDIÁTRICO: 'Pediátrico',
    UCI: 'UCI',
    NEONATAL: 'Neonatal',
    MATERNIDAD: 'Maternidad',
    OBSERVACIÓN: 'Observación'
  }
  return map[tipo] || tipo
}

const getEstadoColor = (estado: string) => {
  const map: Record<string, string> = {
    DISPONIBLE: 'var(--green)',
    OCUPADA: 'var(--alert)',
    MANTENIMIENTO: 'var(--amber)',
    RESERVADA: 'var(--purple)'
  }
  return map[estado] || 'var(--ink-soft)'
}

const getEstadoClass = (estado: string) => {
  const map: Record<string, string> = {
    DISPONIBLE: 'estado-disponible',
    OCUPADA: 'estado-ocupada',
    MANTENIMIENTO: 'estado-mantenimiento',
    RESERVADA: 'estado-reservada'
  }
  return map[estado] || 'estado-default'
}

const getEstadoDot = (estado: string) => {
  const map: Record<string, string> = {
    DISPONIBLE: 'dot-disponible',
    OCUPADA: 'dot-ocupada',
    MANTENIMIENTO: 'dot-mantenimiento',
    RESERVADA: 'dot-reservada'
  }
  return map[estado] || 'dot-default'
}

watch(() => form.piso_id, (val) => {
  form.piso_texto = pisos.value.find(p => p.id === val)?.nombre || ''
})

watch(() => form.sala_id, (val) => {
  form.sala_texto = salas.value.find(s => s.id === val)?.nombre || ''
})

watch(() => form.servicio_id, (val) => {
  form.servicio_texto = servicios.value.find(s => s.id === val)?.nombre || ''
})

const validateForm = (): boolean => {
  let valid = true
  if (!form.nombre.trim()) {
    errors.nombre = 'El nombre es requerido'
    valid = false
  }
  return valid
}

const confirmarEliminar = () => {
  showDeleteModal.value = true
}

const deleteItem = async () => {
  try {
    await $api(`/sigarh/infraestructura-hosp/camas/${id}`, {
      method: 'DELETE',
      tenant
    })
    router.push(`/sigarh/infraestructura-hosp/camas?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar la cama'
  } finally {
    showDeleteModal.value = false
  }
}

async function guardar() {
  if (!validateForm()) return

  saving.value = true
  error.value = ''
  try {
    await $api(`/sigarh/infraestructura-hosp/camas/${id}`, {
      method: 'PATCH',
      tenant,
      body: {
        nombre: form.nombre,
        sala_id: form.sala_id || null,
        piso_id: form.piso_id || null,
        servicio_id: form.servicio_id || null,
        sala_texto: form.sala_texto || null,
        piso_texto: form.piso_texto || null,
        servicio_texto: form.servicio_texto || null,
        tipo_cama: form.tipo_cama || null,
        estado: form.estado,
        is_active: form.is_active,
      }
    })
    router.push(`/sigarh/infraestructura-hosp/camas?tenant=${tenant}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al guardar los cambios'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [data, pss, sls, svs] = await Promise.all([
      $api(`/sigarh/infraestructura-hosp/camas/${id}`, { tenant }),
      $api('/sigarh/infraestructura-hosp/pisos', { tenant }),
      $api('/sigarh/infraestructura-hosp/salas', { tenant }),
      $api('/sigarh/mantenimiento/servicios', { tenant }),
    ])
    Object.assign(form, data)
    pisos.value = pss
    salas.value = sls
    servicios.value = svs
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error al cargar la cama'
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.cama-edit-container {
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
.cama-edit-grid {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 2rem;
}

.cama-edit-main {
  min-width: 0;
}

.cama-edit-sidebar {
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
}

.dni-display {
  font-size: 0.8125rem;
}

.status-dot-mini {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-active-mini {
  background: var(--green);
}

.dot-inactive-mini {
  background: var(--ink-soft);
}

.status-text-mini {
  font-size: 0.75rem;
  font-weight: 500;
}

.text-active {
  color: var(--green);
}

.text-inactive {
  color: var(--ink-soft);
}

.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
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
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

/* Cards */
.cama-edit-card {
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

/* Código Section */
.codigo-section {
  background: var(--mist);
  border-radius: var(--radius);
  padding: 1.25rem;
  margin-bottom: 1.5rem;
}

.codigo-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.codigo-header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.codigo-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.codigo-display-field {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.codigo-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.codigo-hint {
  font-size: 0.6875rem;
  color: var(--ink-soft);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
  background: var(--line);
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

.input-clinical.input-readonly {
  background: var(--mist);
  color: var(--ink-soft);
  cursor: not-allowed;
}

.input-clinical.input-readonly:focus {
  box-shadow: none;
  border-color: var(--line);
}

.input-clinical::placeholder {
  color: var(--ink-soft);
  opacity: 0.6;
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

.preview-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
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

.preview-dates {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

.preview-codigo {
  font-weight: 500;
}

.preview-tipo {
  font-weight: 400;
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

.preview-ubicacion {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: var(--radius);
  background: var(--mist);
  flex-wrap: wrap;
}

.ubicacion-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  color: var(--ink-soft);
}

/* Estado Badges */
.estado-disponible {
  background: var(--green-soft);
  color: var(--green);
}

.estado-ocupada {
  background: var(--alert-soft);
  color: var(--alert);
}

.estado-mantenimiento {
  background: var(--amber-soft);
  color: var(--amber);
}

.estado-reservada {
  background: var(--purple-soft);
  color: var(--purple);
}

.estado-default {
  background: var(--mist);
  color: var(--ink-soft);
}

.estado-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-disponible {
  background: var(--green);
}

.dot-ocupada {
  background: var(--alert);
}

.dot-mantenimiento {
  background: var(--amber);
}

.dot-reservada {
  background: var(--purple);
}

.dot-default {
  background: var(--ink-soft);
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
  margin-top: 1.5rem;
}

/* Actions */
.cama-edit-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding-top: 1.5rem;
  margin-top: 1.5rem;
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
  max-width: 60%;
  text-align: right;
  word-break: break-word;
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

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.modal-content {
  max-width: 420px;
  width: 100%;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.modal-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.modal-body {
  color: var(--ink);
  margin-bottom: 1.5rem;
  line-height: 1.6;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

/* Responsive */
@media (max-width: 1024px) {
  .cama-edit-grid {
    grid-template-columns: 1fr;
  }

  .cama-edit-sidebar {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1.25rem;
  }
}

@media (max-width: 768px) {
  .cama-edit-container {
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

  .cama-edit-sidebar {
    grid-template-columns: 1fr;
  }

  .cama-edit-actions {
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

  .page-subtitle {
    flex-wrap: wrap;
  }

  .codigo-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .preview-card {
    flex-direction: column;
    align-items: flex-start;
  }

  .preview-info {
    min-width: auto;
    width: 100%;
  }

  .preview-status {
    align-self: flex-start;
  }
}

@media (max-width: 480px) {
  .codigo-display-field {
    flex-wrap: wrap;
  }

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

  .status-toggle {
    flex-direction: column;
    align-items: stretch;
    gap: 0.5rem;
  }

  .preview-ubicacion {
    flex-direction: column;
    gap: 0.25rem;
  }

  .modal-content {
    margin: 1rem;
  }
}
</style>