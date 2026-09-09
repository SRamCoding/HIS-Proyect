<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const tiposProducto = ref<{ id: string; nombre: string }[]>([])

const pasos = ['Identificación', 'Registro y procedencia', 'Clasificación y control', 'Cadena de frío']
const stepActual = ref(0)

const FF = { tableta: 'Tableta', capsula: 'Cápsula', ampolla: 'Ampolla', frasco_ampolla: 'Frasco ampolla', jarabe: 'Jarabe', suspension: 'Suspensión', solucion: 'Solución', crema: 'Crema', pomada: 'Pomada', gel: 'Gel', parche: 'Parche', supositorio: 'Supositorio', colirio: 'Colirio', inhalador: 'Inhalador', polvo_reconstituir: 'Polvo para reconstituir', otro: 'Otro' }
const VIAS = { oral: 'Oral', intravenosa: 'Intravenosa', intramuscular: 'Intramuscular', subcutanea: 'Subcutánea', topica: 'Tópica', oftalmica: 'Oftálmica', inhalada: 'Inhalada', rectal: 'Rectal', sublingual: 'Sublingual', nasal: 'Nasal', otro: 'Otro' }
const CV = { sin_receta: 'Sin receta', receta_simple: 'Con receta médica simple', receta_retenida: 'Con receta retenida en farmacia', control_medico: 'Bajo estricto control médico' }

const form = reactive({
  codigo_interno: '', nombre_comercial: '', dci: '', nombre_generico: '',
  presentacion: '', unidad: 'unidad', concentracion: '', forma_farmaceutica: '', via_administracion: '', codigo_atc: '',
  numero_registro_sanitario: '', laboratorio_fabricante: '', pais_origen: '', condicion_venta: 'sin_receta',
  tipo_producto_id: '', precio_referencia: 0, precio_referencia_sismed: 0,
  requiere_receta: false, controlado: false, fiscalizado_digemid: false, reporte_sismed: false,
  stock_minimo_alerta: 10, is_active: true,
  requiere_cadena_frio: false, temperatura_min: null as number | null, temperatura_max: null as number | null,
})
let cargado = false
watch(() => form.condicion_venta, (v) => { if (cargado) form.requiere_receta = v !== 'sin_receta' })

const validateStep = (step: number): boolean => {
  if (step === 0) {
    if (!form.codigo_interno.trim()) { error.value = 'El código interno es requerido'; return false }
    if (!form.nombre_comercial.trim() || !form.nombre_generico.trim()) { error.value = 'Nombre comercial y genérico son requeridos'; return false }
  }
  if (step === 2) {
    if (form.stock_minimo_alerta < 1) { error.value = 'El stock mínimo debe ser 1 o mayor'; return false }
  }
  if (step === 3) {
    if (form.requiere_cadena_frio && form.temperatura_min != null && form.temperatura_max != null && form.temperatura_min > form.temperatura_max) {
      error.value = 'La temperatura mínima no puede ser mayor que la máxima'; return false
    }
  }
  return true
}
const prevStep = () => { if (stepActual.value > 0) stepActual.value--; error.value = '' }
const nextStep = () => {
  if (!validateStep(stepActual.value)) return
  error.value = ''
  if (stepActual.value < pasos.length - 1) stepActual.value++
}

const handleSave = async () => {
  for (const s of [0, 2, 3]) {
    if (!validateStep(s)) { stepActual.value = s; return }
  }
  saving.value = true; error.value = ''
  try {
    await api(`/sigarh/config-farmacia/medicamentos/${id.value}`, { method: 'PATCH', body: {
      codigo_interno: form.codigo_interno, nombre_comercial: form.nombre_comercial,
      dci: form.dci || null, nombre_generico: form.nombre_generico,
      presentacion: form.presentacion || null, unidad: form.unidad || 'unidad', concentracion: form.concentracion || null,
      forma_farmaceutica: form.forma_farmaceutica || null, via_administracion: form.via_administracion || null,
      codigo_atc: form.codigo_atc || null, numero_registro_sanitario: form.numero_registro_sanitario || null,
      laboratorio_fabricante: form.laboratorio_fabricante || null, pais_origen: form.pais_origen || null,
      condicion_venta: form.condicion_venta, tipo_producto_id: form.tipo_producto_id || null,
      precio_referencia: form.precio_referencia || 0,
      precio_referencia_sismed: form.reporte_sismed ? (form.precio_referencia_sismed || 0) : null,
      requiere_receta: form.requiere_receta, controlado: form.controlado,
      fiscalizado_digemid: form.fiscalizado_digemid, reporte_sismed: form.reporte_sismed,
      stock_minimo_alerta: form.stock_minimo_alerta, is_active: form.is_active,
      requiere_cadena_frio: form.requiere_cadena_frio,
      temperatura_min: form.requiere_cadena_frio ? form.temperatura_min : null,
      temperatura_max: form.requiere_cadena_frio ? form.temperatura_max : null,
    } })
    router.push(`/sigarh/config-farmacia/medicamentos?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const [tp, d] = await Promise.all([
      api<any[]>('/sigarh/config-farmacia/tipos-producto'),
      api<any>(`/sigarh/config-farmacia/medicamentos/${id.value}`),
    ])
    tiposProducto.value = tp
    Object.assign(form, {
      codigo_interno: d.codigo_interno, nombre_comercial: d.nombre_comercial, dci: d.dci || '',
      nombre_generico: d.nombre_generico || '', presentacion: d.presentacion || '', unidad: d.unidad || 'unidad',
      concentracion: d.concentracion || '', forma_farmaceutica: d.forma_farmaceutica || '', via_administracion: d.via_administracion || '',
      codigo_atc: d.codigo_atc || '', numero_registro_sanitario: d.numero_registro_sanitario || '',
      laboratorio_fabricante: d.laboratorio_fabricante || '', pais_origen: d.pais_origen || '',
      condicion_venta: d.condicion_venta || 'sin_receta', tipo_producto_id: d.tipo_producto_id || '',
      precio_referencia: d.precio_referencia ?? 0, precio_referencia_sismed: d.precio_referencia_sismed ?? 0,
      requiere_receta: d.requiere_receta, controlado: d.controlado, fiscalizado_digemid: d.fiscalizado_digemid,
      reporte_sismed: d.reporte_sismed, stock_minimo_alerta: d.stock_minimo_alerta, is_active: d.is_active,
      requiere_cadena_frio: d.requiere_cadena_frio, temperatura_min: d.temperatura_min, temperatura_max: d.temperatura_max,
    })
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false; nextTick(() => { cargado = true }) }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-6">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/config-farmacia/medicamentos?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Medicamentos</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Editar</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-beaker" class="w-6 h-6" style="color: var(--teal)" /></div>
          <div><h1 class="page-title">{{ form.nombre_comercial || 'Editar Producto' }}</h1><p class="page-subtitle">Paso {{ stepActual + 1 }} de {{ pasos.length }} — {{ pasos[stepActual] }}</p></div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" /></div>
      <template v-else>
        <!-- Stepper -->
        <div class="wiz-steps">
          <button v-for="(s, i) in pasos" :key="i" type="button" class="wiz-step"
            :class="{ done: stepActual > i, active: stepActual === i }"
            @click="stepActual = i">
            <span class="wiz-dot"><span>{{ i + 1 }}</span></span>
            <span class="wiz-label">{{ s }}</span>
          </button>
        </div>

        <!-- Paso 1: Identificación -->
        <SFormCard v-show="stepActual === 0" title="Identificación del producto" subtitle="Nombres, presentación y forma"
          icon="i-heroicons-identification" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="stepActual === 0 ? error : ''">
          <div class="form-group">
            <label class="form-label">Código interno / DIGEMID <span class="required">*</span></label>
            <div class="input-wrapper"><UIcon name="i-heroicons-hashtag" class="input-icon" /><input v-model="form.codigo_interno" class="input-clinical font-mono-data" maxlength="50" @focus="error = ''" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Nombre comercial <span class="required">*</span></label>
            <div class="input-wrapper"><UIcon name="i-heroicons-beaker" class="input-icon" /><input v-model="form.nombre_comercial" class="input-clinical" maxlength="255" @focus="error = ''" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Nombre genérico <span class="required">*</span></label>
            <div class="input-wrapper"><UIcon name="i-heroicons-beaker" class="input-icon" /><input v-model="form.nombre_generico" class="input-clinical" maxlength="255" @focus="error = ''" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">DCI (principio activo)</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-sparkles" class="input-icon" /><input v-model="form.dci" class="input-clinical" maxlength="150" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Presentación</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-cube" class="input-icon" /><input v-model="form.presentacion" class="input-clinical" maxlength="100" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Unidad</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-scale" class="input-icon" /><input v-model="form.unidad" class="input-clinical" maxlength="20" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Concentración</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-adjustments-horizontal" class="input-icon" /><input v-model="form.concentracion" class="input-clinical" maxlength="100" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Forma farmacéutica</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-cube-transparent" class="input-icon" />
              <select v-model="form.forma_farmaceutica" class="input-clinical"><option value="">Seleccione</option><option v-for="(v, k) in FF" :key="k" :value="k">{{ v }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Vía de administración</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-arrow-right-circle" class="input-icon" />
              <select v-model="form.via_administracion" class="input-clinical"><option value="">Seleccione</option><option v-for="(v, k) in VIAS" :key="k" :value="k">{{ v }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Código ATC</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-tag" class="input-icon" /><input v-model="form.codigo_atc" class="input-clinical font-mono-data" maxlength="10" /></div>
          </div>
          <template #actions>
            <div class="wiz-nav">
              <div style="flex: 1" />
              <button type="button" class="btn-primary" @click="nextStep">Siguiente <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" /></button>
            </div>
          </template>
        </SFormCard>

        <!-- Paso 2: Registro y procedencia -->
        <SFormCard v-show="stepActual === 1" title="Registro y procedencia" subtitle="Datos sanitarios y de fabricación"
          icon="i-heroicons-document-check" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="stepActual === 1 ? error : ''">
          <div class="form-group">
            <label class="form-label">N° de registro sanitario</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-shield-check" class="input-icon" /><input v-model="form.numero_registro_sanitario" class="input-clinical font-mono-data" maxlength="50" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Laboratorio / Fabricante</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-building-office-2" class="input-icon" /><input v-model="form.laboratorio_fabricante" class="input-clinical" maxlength="150" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">País de origen</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-globe-americas" class="input-icon" /><input v-model="form.pais_origen" class="input-clinical" maxlength="100" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Condición de venta <span class="required">*</span></label>
            <div class="input-wrapper"><UIcon name="i-heroicons-clipboard-document-check" class="input-icon" />
              <select v-model="form.condicion_venta" class="input-clinical"><option v-for="(v, k) in CV" :key="k" :value="k">{{ v }}</option></select>
            </div>
            <p class="field-hint">Si exige receta, "Requiere receta" se marca automáticamente.</p>
          </div>
          <template #actions>
            <div class="wiz-nav">
              <button type="button" class="btn-outline" @click="prevStep"><UIcon name="i-heroicons-arrow-left" class="w-4 h-4" /> Anterior</button>
              <div style="flex: 1" />
              <button type="button" class="btn-primary" @click="nextStep">Siguiente <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" /></button>
            </div>
          </template>
        </SFormCard>

        <!-- Paso 3: Clasificación, precios y control -->
        <SFormCard v-show="stepActual === 2" title="Clasificación, precios y control" subtitle="Tipo, precios de referencia y marcas de control"
          icon="i-heroicons-currency-dollar" icon-bg="var(--amber-soft)" icon-color="var(--amber)" :error="stepActual === 2 ? error : ''">
          <div class="form-group">
            <label class="form-label">Tipo de producto</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-tag" class="input-icon" />
              <select v-model="form.tipo_producto_id" class="input-clinical"><option value="">Seleccione</option><option v-for="t in tiposProducto" :key="t.id" :value="t.id">{{ t.nombre }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Precio de referencia</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-banknotes" class="input-icon" /><input v-model.number="form.precio_referencia" type="number" min="0" step="0.01" class="input-clinical font-mono-data" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Stock mínimo de alerta</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-bell-alert" class="input-icon" /><input v-model.number="form.stock_minimo_alerta" type="number" min="1" class="input-clinical font-mono-data" /></div>
          </div>
          <div class="form-group full-width">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 0.5rem">
              <label class="status-toggle"><span class="toggle-label">Requiere receta</span><button type="button" @click="form.requiere_receta = !form.requiere_receta" class="toggle-switch" :class="{ 'toggle-active': form.requiere_receta }"><span class="toggle-slider" /></button></label>
              <label class="status-toggle"><span class="toggle-label">Controlado</span><button type="button" @click="form.controlado = !form.controlado" class="toggle-switch" :class="{ 'toggle-active': form.controlado }"><span class="toggle-slider" /></button></label>
              <label class="status-toggle"><span class="toggle-label">Fiscalizado DIGEMID</span><button type="button" @click="form.fiscalizado_digemid = !form.fiscalizado_digemid" class="toggle-switch" :class="{ 'toggle-active': form.fiscalizado_digemid }"><span class="toggle-slider" /></button></label>
              <label class="status-toggle"><span class="toggle-label">Reportar SISMED</span><button type="button" @click="form.reporte_sismed = !form.reporte_sismed" class="toggle-switch" :class="{ 'toggle-active': form.reporte_sismed }"><span class="toggle-slider" /></button></label>
            </div>
          </div>
          <div v-if="form.reporte_sismed" class="form-group">
            <label class="form-label">Precio de referencia SISMED</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-banknotes" class="input-icon" /><input v-model.number="form.precio_referencia_sismed" type="number" min="0" step="0.01" class="input-clinical font-mono-data" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle"><span class="toggle-label">Producto Activo</span><button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }"><span class="toggle-slider" /></button></div>
          </div>
          <template #actions>
            <div class="wiz-nav">
              <button type="button" class="btn-outline" @click="prevStep"><UIcon name="i-heroicons-arrow-left" class="w-4 h-4" /> Anterior</button>
              <div style="flex: 1" />
              <button type="button" class="btn-primary" @click="nextStep">Siguiente <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" /></button>
            </div>
          </template>
        </SFormCard>

        <!-- Paso 4: Cadena de frío -->
        <SFormCard v-show="stepActual === 3" title="Cadena de frío" subtitle="Condiciones de temperatura del producto"
          icon="i-heroicons-snowflake" icon-bg="var(--purple-soft)" icon-color="var(--purple)" :error="stepActual === 3 ? error : ''">
          <div class="form-group full-width">
            <div class="status-toggle"><span class="toggle-label">Requiere cadena de frío</span><button type="button" @click="form.requiere_cadena_frio = !form.requiere_cadena_frio" class="toggle-switch" :class="{ 'toggle-active': form.requiere_cadena_frio }"><span class="toggle-slider" /></button></div>
          </div>
          <template v-if="form.requiere_cadena_frio">
            <div class="form-group">
              <label class="form-label">Temperatura mínima (°C)</label>
              <div class="input-wrapper"><UIcon name="i-heroicons-arrow-trending-down" class="input-icon" /><input v-model.number="form.temperatura_min" type="number" class="input-clinical font-mono-data" /></div>
            </div>
            <div class="form-group">
              <label class="form-label">Temperatura máxima (°C)</label>
              <div class="input-wrapper"><UIcon name="i-heroicons-arrow-trending-up" class="input-icon" /><input v-model.number="form.temperatura_max" type="number" class="input-clinical font-mono-data" /></div>
            </div>
          </template>
          <template #actions>
            <div class="wiz-nav">
              <button type="button" class="btn-outline" @click="prevStep"><UIcon name="i-heroicons-arrow-left" class="w-4 h-4" /> Anterior</button>
              <div style="flex: 1" />
              <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
                :cancel-to="`/sigarh/config-farmacia/medicamentos?tenant=${tenantId}`" @save="handleSave" />
            </div>
          </template>
        </SFormCard>
      </template>
    </template>
    <template #sidebar>
      <SWidgetSummary :items="[
        { label: 'Código', value: form.codigo_interno, mono: true },
        { label: 'Producto', value: form.nombre_comercial },
        { label: 'Condición', value: CV[form.condicion_venta] },
        { divider: true },
        { label: 'Precio ref.', value: String(form.precio_referencia) },
        { label: 'Stock mínimo', value: String(form.stock_minimo_alerta) },
        { label: 'Estado', value: form.is_active ? 'Activo' : 'Inactivo' },
      ]" />
      <SWidgetInfo :items="['El stock por lote y vencimiento se maneja en el inventario del hospital', 'Cambiar la condición de venta ajusta el marcador Requiere receta automáticamente', 'No se puede eliminar un producto con stock mayor que cero']" />
    </template>
  </SFormLayout>
</template>

<style scoped>
.wiz-steps {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}
.wiz-step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: var(--paper);
  font-size: 0.8125rem;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}
.wiz-step.done { border-color: var(--teal); color: var(--ink); }
.wiz-step.active { border-color: var(--teal); background: var(--teal-soft); color: var(--teal); font-weight: 600; }
.wiz-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6875rem;
  font-weight: 600;
  background: var(--mist);
  color: var(--ink-soft);
}
.wiz-step.done .wiz-dot,
.wiz-step.active .wiz-dot { background: var(--teal); color: #fff; }
.wiz-nav {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
}
@media (max-width: 640px) {
  .wiz-label { display: none; }
}
</style>
