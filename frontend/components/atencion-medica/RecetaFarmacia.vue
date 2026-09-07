<template>
  <section class="form-card">
    <div class="card-header">
      <div class="card-header-icon" style="background: var(--blue-soft)">
        <UIcon name="i-heroicons-pills" class="w-4 h-4" style="color: var(--blue)" />
      </div>
      <div>
        <h3 class="card-title">Receta de Farmacia</h3>
        <p class="card-subtitle">Medicamentos prescritos para el paciente</p>
      </div>
      <span v-if="recetaYaGenerada" class="receta-status-badge status-generada">
        <UIcon name="i-heroicons-check-circle" class="w-3.5 h-3.5" />
        Receta Generada
      </span>
      <span v-else class="receta-status-badge status-pendiente">
        <UIcon name="i-heroicons-clock" class="w-3.5 h-3.5" />
        Pendiente
      </span>
    </div>

    <!-- Receta ya generada -->
    <div v-if="recetaYaGenerada" class="receta-generada">
      <div class="receta-header">
        <div class="receta-number">
          <UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: var(--teal)" />
          <span>Receta N° <strong>{{ recetaExistente.numero_receta }}</strong></span>
        </div>
        <span class="receta-estado" :class="recetaExistente.estado === 'entregado' ? 'estado-entregado' : 'estado-pendiente-farmacia'">
          {{ recetaExistente.estado === 'entregado' ? '✓ Entregado' : 'Pendiente de entrega' }}
        </span>
      </div>
      <div class="receta-items">
        <div v-for="item in recetaExistente.items" :key="item.id" class="receta-item">
          <div class="receta-item-header">
            <span class="receta-item-name">{{ item.nombre_comercial }}</span>
            <span class="receta-item-cantidad">Cant: {{ item.cantidad }}</span>
          </div>
          <div class="receta-item-details">
            <span v-if="item.dosis"><UIcon name="i-heroicons-document-text" class="w-3 h-3" /> {{ item.dosis }}</span>
            <span v-if="item.frecuencia"><UIcon name="i-heroicons-clock" class="w-3 h-3" /> {{ item.frecuencia }}</span>
            <span v-if="item.duracion_dias"><UIcon name="i-heroicons-calendar" class="w-3 h-3" /> {{ item.duracion_dias }} días</span>
          </div>
          <div v-if="item.indicaciones" class="receta-item-indicaciones">
            <UIcon name="i-heroicons-document-text" class="w-3 h-3" style="color: var(--ink-soft)" />
            {{ item.indicaciones }}
          </div>
        </div>
      </div>
    </div>

    <!-- Formulario para generar receta -->
    <template v-else>
      <div class="receta-search">
        <div class="form-group full-width" style="margin-bottom: 0.75rem;">
          <label class="form-label">Buscar Medicamento</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="input-icon" />
            <input v-model="buscaMedicamento" type="text" class="input-clinical" placeholder="Buscar por código, nombre o DCI..." @input="buscarMedicamentoDebounced" />
          </div>
          <p class="field-hint">Escribe al menos 2 caracteres para buscar</p>
        </div>
      </div>

      <ul v-if="resultadosMedicamento.length" class="medicamento-results">
        <li v-for="m in resultadosMedicamento" :key="m.id" class="medicamento-result-item" @click="agregarMedicamento(m)">
          <div class="medicamento-result-info">
            <span class="medicamento-result-code">[{{ m.codigo_interno }}]</span>
            <span class="medicamento-result-name">{{ m.nombre_comercial }}</span>
            <span v-if="m.concentracion" class="medicamento-result-concentracion">{{ m.concentracion }}</span>
            <span v-if="m.dci" class="medicamento-result-dci">({{ m.dci }})</span>
          </div>
          <span class="medicamento-result-add"><UIcon name="i-heroicons-plus-circle" class="w-5 h-5" style="color: var(--teal)" /></span>
        </li>
      </ul>

      <div v-if="itemsReceta.length" class="receta-items-form">
        <div class="receta-items-header">
          <span class="receta-items-title">Medicamentos prescritos</span>
          <span class="receta-items-count">{{ itemsReceta.length }} medicamentos</span>
        </div>

        <div v-for="(item, idx) in itemsReceta" :key="idx" class="receta-item-form">
          <div class="receta-item-form-header">
            <div class="receta-item-form-name">
              <span class="medicamento-code">[{{ item.codigo_interno }}]</span>
              <span class="medicamento-name">{{ item.nombre_comercial }}</span>
            </div>
            <button class="receta-item-remove" @click="itemsReceta.splice(idx, 1)">
              <UIcon name="i-heroicons-x-mark" class="w-4 h-4" />
            </button>
          </div>

          <div class="receta-item-form-fields">
            <div class="receta-field">
              <label class="receta-field-label">Cantidad <span class="required">*</span></label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-numbered-list" class="input-icon-small" style="left: 0.5rem;" />
                <input v-model.number="item.cantidad" type="number" min="1" class="input-clinical-small" style="padding-left: 1.75rem;" placeholder="1" />
              </div>
            </div>
            <div class="receta-field">
              <label class="receta-field-label">Dosis</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-document-text" class="input-icon-small" style="left: 0.5rem;" />
                <input v-model="item.dosis" type="text" class="input-clinical-small" style="padding-left: 1.75rem;" placeholder="1 tableta" />
              </div>
            </div>
            <div class="receta-field">
              <label class="receta-field-label">Frecuencia</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-clock" class="input-icon-small" style="left: 0.5rem;" />
                <input v-model="item.frecuencia" type="text" class="input-clinical-small" style="padding-left: 1.75rem;" placeholder="cada 8 horas" />
              </div>
            </div>
            <div class="receta-field">
              <label class="receta-field-label">Duración (días)</label>
              <div class="input-wrapper-small">
                <UIcon name="i-heroicons-calendar" class="input-icon-small" style="left: 0.5rem;" />
                <input v-model.number="item.duracion_dias" type="number" min="1" class="input-clinical-small" style="padding-left: 1.75rem;" placeholder="5" />
              </div>
            </div>
          </div>

          <div class="receta-item-form-indicaciones">
            <label class="receta-field-label">Indicaciones</label>
            <div class="input-wrapper">
              <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.5rem; transform: none;" />
              <input v-model="item.indicaciones" type="text" class="input-clinical" style="padding-left: 2rem; padding-top: 0.375rem; padding-bottom: 0.375rem;" placeholder="Instrucciones adicionales..." />
            </div>
          </div>
        </div>

        <div class="receta-actions">
          <button class="btn-generar-receta" :disabled="generandoReceta || !itemsReceta.length" @click="generarReceta">
            <UIcon v-if="generandoReceta" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            <UIcon v-else name="i-heroicons-check-badge" class="w-4 h-4" />
            {{ generandoReceta ? 'Generando...' : 'Generar Receta' }}
          </button>
          <span v-if="itemsReceta.some(i => !i.cantidad || i.cantidad < 1)" class="receta-warning">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4" />
            Todos los medicamentos deben tener cantidad
          </span>
        </div>
      </div>

      <div v-else class="receta-empty">
        <div class="receta-empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-pills" class="w-8 h-8" style="color: var(--ink-soft)" />
        </div>
        <p class="receta-empty-text">Busca y agrega medicamentos a la receta</p>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
const props = defineProps<{
  citaId: string
  recetaExistente: any | null
  generandoReceta: boolean
  error: string
}>()

const emit = defineEmits<{
  (e: 'receta-generada', data: any): void
  (e: 'error', msg: string): void
}>()

const { api } = useApi()

const buscaMedicamento = ref('')
const resultadosMedicamento = ref<any[]>([])
const itemsReceta = ref<any[]>([])
const generandoReceta = ref(false)
const errorLocal = ref('')
let debounceMedTimer: any = null

const recetaYaGenerada = computed(() => !!props.recetaExistente)

function buscarMedicamentoDebounced() {
  clearTimeout(debounceMedTimer)
  debounceMedTimer = setTimeout(async () => {
    if (buscaMedicamento.value.length < 2) { resultadosMedicamento.value = []; return }
    try {
      resultadosMedicamento.value = await api(`/app/consulta-externa/farmacia/medicamentos/buscar?q=${encodeURIComponent(buscaMedicamento.value)}`)
    } catch (e) { /* silencioso */ }
  }, 300)
}

function agregarMedicamento(m: any) {
  if (itemsReceta.value.some((i) => i.medicamento_id === m.id)) return
  itemsReceta.value.push({
    medicamento_id: m.id,
    codigo_interno: m.codigo_interno,
    nombre_comercial: m.nombre_comercial,
    cantidad: 1,
    dosis: '',
    frecuencia: '',
    duracion_dias: null,
    indicaciones: '',
  })
  buscaMedicamento.value = ''
  resultadosMedicamento.value = []
}

async function generarReceta() {
  if (itemsReceta.value.some((i) => !i.cantidad || i.cantidad < 1)) {
    emit('error', 'Todos los medicamentos deben tener una cantidad válida')
    return
  }
  generandoReceta.value = true
  try {
    const payload = { items: itemsReceta.value.map(({ codigo_interno, nombre_comercial, ...rest }) => rest) }
    const result = await api(`/app/consulta-externa/farmacia/recetas/${props.citaId}`, { method: 'POST', body: payload })
    itemsReceta.value = []
    emit('receta-generada', result)
  } catch (e: any) {
    emit('error', e?.data?.detail || 'Error al generar la receta')
  } finally {
    generandoReceta.value = false
  }
}
</script>

<style scoped>
/* Clases compartidas que este componente usa (copiadas del padre) */
.form-card { background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1.5rem; margin-bottom: 1.5rem; }
.card-header { display: flex; align-items: center; gap: 1rem; margin-bottom: 1.5rem; }
.card-header-icon { width: 40px; height: 40px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.card-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.card-subtitle { font-size: 0.8125rem; color: var(--ink-soft); margin: 0; }
.form-group.full-width { grid-column: 1 / -1; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.5rem; }
.required { color: var(--alert); }
.input-wrapper { position: relative; }
.input-icon { position: absolute; left: 0.75rem; top: 50%; transform: translateY(-50%); width: 1rem; height: 1rem; color: var(--ink-soft); }
.input-clinical { width: 100%; padding: 0.625rem 0.875rem; padding-left: 2.5rem; border-radius: 8px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.field-hint { font-size: 0.6875rem; color: var(--ink-soft); margin-top: 0.25rem; }
.input-wrapper-small { position: relative; }
.input-icon-small { position: absolute; top: 50%; transform: translateY(-50%); width: 0.875rem; height: 0.875rem; color: var(--ink-soft); }
.input-clinical-small { width: 100%; padding: 0.375rem 0.625rem 0.375rem 2rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.8125rem; }

/* Receta específico */
.receta-status-badge { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.1875rem 0.625rem; border-radius: 12px; font-size: 0.6875rem; font-weight: 500; margin-left: auto; flex-shrink: 0; }
.receta-status-badge.status-generada { background: var(--green-soft); color: var(--green); }
.receta-status-badge.status-pendiente { background: var(--amber-soft); color: var(--amber); }
.receta-generada { border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }
.receta-header { display: flex; align-items: center; justify-content: space-between; padding: 0.75rem 1rem; background: var(--mist); border-bottom: 1px solid var(--line); flex-wrap: wrap; gap: 0.5rem; }
.receta-number { display: flex; align-items: center; gap: 0.5rem; font-size: 0.875rem; color: var(--ink); }
.receta-number strong { color: var(--teal); }
.receta-estado { font-size: 0.75rem; font-weight: 500; padding: 0.125rem 0.625rem; border-radius: 12px; }
.receta-estado.estado-entregado { background: var(--green-soft); color: var(--green); }
.receta-estado.estado-pendiente-farmacia { background: var(--amber-soft); color: var(--amber); }
.receta-items { padding: 0.75rem 1rem; }
.receta-item { padding: 0.625rem 0; border-bottom: 1px solid var(--line); }
.receta-item:last-child { border-bottom: none; }
.receta-item-header { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.receta-item-name { font-weight: 500; color: var(--ink); font-size: 0.875rem; }
.receta-item-cantidad { font-size: 0.75rem; color: var(--ink-soft); background: var(--mist); padding: 0.125rem 0.5rem; border-radius: 10px; }
.receta-item-details { display: flex; gap: 0.75rem; font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.125rem; flex-wrap: wrap; }
.receta-item-details span { display: flex; align-items: center; gap: 0.25rem; }
.receta-item-indicaciones { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; padding-top: 0.25rem; border-top: 1px dashed var(--line); display: flex; gap: 0.25rem; }
.medicamento-results { list-style: none; padding: 0; margin: 0 0 0.75rem 0; border: 1px solid var(--line); border-radius: 6px; max-height: 200px; overflow-y: auto; }
.medicamento-result-item { display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0.75rem; cursor: pointer; border-bottom: 1px solid var(--line); }
.medicamento-result-item:last-child { border-bottom: none; }
.medicamento-result-item:hover { background: var(--mist); }
.medicamento-result-info { display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap; flex: 1; }
.medicamento-result-code { font-weight: 600; color: var(--teal); font-size: 0.75rem; }
.medicamento-result-name { font-weight: 500; color: var(--ink); font-size: 0.8125rem; }
.medicamento-result-concentracion { font-size: 0.75rem; color: var(--ink-soft); }
.medicamento-result-dci { font-size: 0.6875rem; color: var(--ink-soft); font-style: italic; }
.receta-items-form { margin-top: 0.75rem; }
.receta-items-header { display: flex; align-items: center; justify-content: space-between; padding: 0.5rem 0; border-bottom: 2px solid var(--line); margin-bottom: 0.75rem; }
.receta-items-title { font-size: 0.8125rem; font-weight: 600; color: var(--ink); }
.receta-items-count { font-size: 0.75rem; color: var(--ink-soft); background: var(--mist); padding: 0.125rem 0.5rem; border-radius: 10px; }
.receta-item-form { border: 1px solid var(--line); border-radius: var(--radius); padding: 0.75rem; margin-bottom: 0.75rem; background: var(--paper); }
.receta-item-form-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.625rem; }
.receta-item-form-name { display: flex; align-items: center; gap: 0.5rem; }
.medicamento-code { font-weight: 600; color: var(--teal); font-size: 0.75rem; }
.medicamento-name { font-weight: 500; color: var(--ink); font-size: 0.875rem; }
.receta-item-remove { background: transparent; border: none; color: var(--alert); cursor: pointer; padding: 0.25rem; border-radius: 4px; }
.receta-item-remove:hover { background: var(--alert-soft); }
.receta-item-form-fields { display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 0.5rem; }
.receta-field { display: flex; flex-direction: column; gap: 0.25rem; }
.receta-field-label { font-size: 0.6875rem; font-weight: 500; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.05em; }
.receta-item-form-indicaciones { margin-top: 0.625rem; }
.receta-actions { display: flex; align-items: center; gap: 0.75rem; margin-top: 0.75rem; flex-wrap: wrap; }
.btn-generar-receta { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; border: none; background: #2563eb; color: white; cursor: pointer; }
.btn-generar-receta:hover:not(:disabled) { background: #1d4ed8; }
.btn-generar-receta:disabled { opacity: 0.5; cursor: not-allowed; }
.receta-warning { display: flex; align-items: center; gap: 0.375rem; font-size: 0.75rem; color: var(--alert); }
.receta-empty { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 2rem 1rem; gap: 0.5rem; }
.receta-empty-icon { width: 56px; height: 56px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }
.receta-empty-text { font-size: 0.875rem; color: var(--ink-soft); margin: 0; }

@media (max-width: 768px) {
  .receta-item-form-fields { grid-template-columns: 1fr 1fr; }
  .receta-header { flex-direction: column; align-items: flex-start; }
  .receta-status-badge { margin-left: 0; }
}
</style>