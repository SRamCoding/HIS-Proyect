<template>
  <div class="lab-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ATENCIÓN HOSPITALARIA</span>
            <h1 class="page-title">Hospitalización · {{ titles[mode] }}</h1>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary btn-sm" @click="init"><UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />Actualizar</button>
        <button v-if="mode==='hospitalizaciones'" class="btn-primary" @click="abrirAdmision"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Admitir desde Emergencia</button>
        <button v-if="mode==='interconsultas'" class="btn-primary" @click="abrirAdmisionInterc"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Admitir Interconsulta desde Emergencia</button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="lab-tabs">
      <NuxtLink v-for="(title, key) in titles" :key="key" :to="'/app/hospitalizacion/'+key" class="tab-link" :class="{ 'tab-link--active': key === mode }">{{ title }}</NuxtLink>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <!-- ═══════════ ADMITIR DESDE EMERGENCIA ═══════════ -->
    <section v-if="formAdmision" class="panel">
      <div class="card-header-row"><h2 class="results-title">Admitir paciente derivado de Emergencia</h2>
        <button class="btn-secondary" @click="formAdmision=false"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
      <div class="choices">
        <button v-for="d in pendientesEmergencia" :key="d.destino_id" class="choice-btn" :class="{'choice-btn--active': admisionForm.destino_id===d.destino_id}" @click="admisionForm.destino_id=d.destino_id">
          {{ d.numero_cuenta }} · {{ d.paciente_nombre }} · {{ d.paciente_dni }}
        </button>
        <p v-if="!pendientesEmergencia.length" class="field-hint">No hay pacientes de Emergencia esperando cama.</p>
      </div>
      <form v-if="admisionForm.destino_id" class="editor-form" @submit.prevent="admitirEmergencia">
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">Cama disponible</label>
            <select v-model="admisionForm.cama_id" class="input-clinical" required>
              <option value="">Seleccionar</option>
              <option v-for="c in catalogs.camas" :key="c.id" :value="c.id">{{ c.codigo }} · {{ c.servicio_nombre }}</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">Especialidad de ingreso</label>
            <select v-model="admisionForm.especialidad_ingreso_id" class="input-clinical">
              <option value="">Sin especificar</option>
              <option v-for="e in catalogs.especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Admitir</button></div>
      </form>
    </section>

    <!-- ═══════════ ADMITIR INTERCONSULTA DESDE EMERGENCIA ═══════════ -->
    <section v-if="formAdmisionInterc" class="panel">
      <div class="card-header-row"><h2 class="results-title">Solicitar interconsulta para paciente de Emergencia</h2>
        <button class="btn-secondary" @click="formAdmisionInterc=false"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
      <div class="choices">
        <button v-for="d in pendientesEmergenciaInterc" :key="d.destino_id" class="choice-btn" :class="{'choice-btn--active': admisionIntercForm.destino_id===d.destino_id}" @click="admisionIntercForm.destino_id=d.destino_id">
          {{ d.numero_cuenta }} · {{ d.paciente_nombre }} · {{ d.paciente_dni }}
        </button>
        <p v-if="!pendientesEmergenciaInterc.length" class="field-hint">No hay pacientes de Emergencia esperando interconsulta.</p>
      </div>
      <form v-if="admisionIntercForm.destino_id" class="editor-form" @submit.prevent="admitirInterconsultaEmergencia">
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Especialidad</label>
            <select v-model="admisionIntercForm.especialidad_destino_id" class="input-clinical" required>
              <option value="">Seleccionar</option><option v-for="e in catalogs.especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
            </select>
          </div>
          <div class="form-group"><label class="form-label">Urgente</label>
            <select v-model="admisionIntercForm.urgente" class="input-clinical"><option :value="false">No</option><option :value="true">Sí</option></select>
          </div>
          <div class="form-group full-width"><label class="form-label">Motivo</label><textarea v-model="admisionIntercForm.motivo" class="input-clinical" rows="2" required maxlength="4000"></textarea></div>
        </div>
        <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Solicitar interconsulta</button></div>
      </form>
    </section>

    <!-- ═══════════ HOSPITALIZACIONES / SEGUIMIENTO PACIENTE ═══════════ -->
    <template v-if="mode==='hospitalizaciones' || mode==='seguimiento-paciente'">
      <section class="panel search-panel">
        <form class="search-form" @submit.prevent="buscarHospitalizaciones">
          <div class="search-grid">
            <div class="search-field"><label class="form-label">Buscar paciente / N.° hospitalización</label><input v-model="filtro.q" class="input-clinical" /></div>
            <div class="search-field" v-if="mode==='hospitalizaciones'">
              <label class="form-label">Estado</label>
              <select v-model="filtro.estado" class="input-clinical"><option value="">Todos</option><option value="internado">Internado</option><option value="alta">Alta</option></select>
            </div>
          </div>
          <div class="search-actions"><button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button></div>
        </form>
      </section>

      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ total }} registros</h2></div>
        <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
        <div v-else class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>N.° hospitalización</th><th>Paciente</th><th>Cama</th><th>Origen</th><th>Ingreso</th><th>Estado</th><th>Acciones</th></tr></thead>
            <tbody>
              <tr v-for="h in hospitalizaciones" :key="h.id">
                <td>{{ h.numero_hospitalizacion }}</td><td>{{ h.paciente }}</td><td>{{ h.cama_codigo }}</td>
                <td>{{ h.origen }}</td><td>{{ h.fecha_ingreso }}</td><td>{{ h.estado }}</td>
                <td><button class="action-btn action-view" @click="verHospitalizacion(h.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button></td>
              </tr>
              <tr v-if="!hospitalizaciones.length"><td colspan="7" style="text-align:center;color:var(--ink-soft)">Sin registros.</td></tr>
            </tbody>
          </table>
        </div>
        <nav class="pagination">
          <button class="btn-secondary btn-sm" :disabled="page<=1" @click="cambiarPagina(page-1)"><UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />Anterior</button>
          <span class="page-info">{{ page }} / {{ pages }}</span>
          <button class="btn-secondary btn-sm" :disabled="page>=pages" @click="cambiarPagina(page+1)">Siguiente<UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></button>
        </nav>
      </section>

      <!-- Detalle -->
      <section v-if="detalle" class="panel detail-panel">
        <div class="detail-header">
          <div><h2 class="detail-title">{{ detalle.numero_hospitalizacion }}</h2><p class="detail-subtitle">{{ detalle.paciente }} · HC {{ detalle.historia }} · Cama {{ detalle.cama_codigo }} · {{ detalle.estado }}</p></div>
          <button class="btn-secondary" @click="detalle=null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button>
        </div>
        <div class="detail-info">
          <p>Origen {{ detalle.origen }} · Especialidad {{ detalle.especialidad_ingreso_nombre || '—' }} · Diagnóstico {{ detalle.diagnostico_ingreso_descripcion || '—' }}</p>
          <p>Ingreso {{ detalle.fecha_ingreso }} <span v-if="detalle.fecha_alta">· Alta {{ detalle.fecha_alta }}</span></p>
          <p v-if="detalle.resumen_alta" class="field-hint">Resumen de alta: {{ detalle.resumen_alta }}</p>
        </div>

        <!-- Notas de evolución -->
        <h3 class="section-title">Notas de evolución</h3>
        <div v-for="n in detalle.notas_evolucion" :key="n.id" class="result-section">
          <p class="field-hint">{{ n.tipo }} · {{ n.autor_nombre }} · {{ n.created_at }}</p>
          <p>{{ n.contenido }}</p>
          <p v-if="n.plan_indicaciones" class="field-hint">Plan: {{ n.plan_indicaciones }}</p>
          <p v-if="n.pulso || n.temperatura" class="field-hint">
            Pulso {{ n.pulso ?? '—' }} · T° {{ n.temperatura ?? '—' }} · PA {{ n.presion_sistolica ?? '—' }}/{{ n.presion_diastolica ?? '—' }} · Sat.O2 {{ n.saturacion_o2 ?? '—' }}%
          </p>
        </div>
        <form v-if="detalle.estado==='internado'" class="editor-form" @submit.prevent="agregarNota">
          <div class="form-grid">
            <div class="form-group"><label class="form-label">Tipo</label>
              <select v-model="notaForm.tipo" class="input-clinical"><option value="MEDICA">Médica</option><option value="ENFERMERIA">Enfermería</option></select>
            </div>
            <div class="form-group"><label class="form-label">Pulso</label><input v-model.number="notaForm.pulso" type="number" class="input-clinical" /></div>
            <div class="form-group"><label class="form-label">Temperatura °C</label><input v-model.number="notaForm.temperatura" type="number" step="0.1" class="input-clinical" /></div>
            <div class="form-group"><label class="form-label">Sat. O2 %</label><input v-model.number="notaForm.saturacion_o2" type="number" class="input-clinical" /></div>
            <div class="form-group full-width"><label class="form-label">Evolución</label><textarea v-model="notaForm.contenido" class="input-clinical" rows="2" required maxlength="8000"></textarea></div>
            <div class="form-group full-width"><label class="form-label">Plan / indicaciones</label><textarea v-model="notaForm.plan_indicaciones" class="input-clinical" rows="2" maxlength="4000"></textarea></div>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Agregar nota</button></div>
        </form>

        <!-- Interconsultas -->
        <h3 class="section-title">Interconsultas</h3>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Especialidad</th><th>Motivo</th><th>Urgente</th><th>Estado</th></tr></thead>
            <tbody>
              <tr v-for="i in detalle.interconsultas" :key="i.id"><td>{{ i.especialidad_nombre }}</td><td>{{ i.motivo }}</td><td>{{ i.urgente?'Sí':'No' }}</td><td>{{ i.estado }}</td></tr>
              <tr v-if="!detalle.interconsultas.length"><td colspan="4" style="text-align:center;color:var(--ink-soft)">Sin interconsultas.</td></tr>
            </tbody>
          </table>
        </div>
        <form v-if="detalle.estado==='internado' && !detalle.interconsultas.length" class="editor-form" @submit.prevent="solicitarInterconsulta">
          <div class="form-grid">
            <div class="form-group"><label class="form-label">Especialidad</label>
              <select v-model="intercForm.especialidad_destino_id" class="input-clinical" required>
                <option value="">Seleccionar</option><option v-for="e in catalogs.especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
              </select>
            </div>
            <div class="form-group"><label class="form-label">Urgente</label>
              <select v-model="intercForm.urgente" class="input-clinical"><option :value="false">No</option><option :value="true">Sí</option></select>
            </div>
            <div class="form-group full-width"><label class="form-label">Motivo</label><textarea v-model="intercForm.motivo" class="input-clinical" rows="2" required maxlength="4000"></textarea></div>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Solicitar interconsulta</button></div>
        </form>

        <!-- Consentimientos -->
        <h3 class="section-title">Consentimientos informados</h3>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>N.°</th><th>Procedimiento</th><th>Fecha</th><th>Estado</th><th>Acciones</th></tr></thead>
            <tbody>
              <tr v-for="c in detalle.consentimientos" :key="c.id">
                <td>{{ c.numero }}</td><td>{{ c.procedimiento }}</td><td>{{ c.fecha }}</td><td>{{ c.estado }}</td>
                <td>
                  <div class="action-buttons">
                    <button class="action-btn action-pdf" @click="download('/consentimientos/'+c.id+'/comprobante.pdf', 'consentimiento.pdf')"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" /></button>
                    <button v-if="c.estado==='registrado'" class="action-btn" style="color:var(--alert)" @click="revocarConsentimientoId=c.id"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" /></button>
                  </div>
                </td>
              </tr>
              <tr v-if="!detalle.consentimientos.length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Sin consentimientos.</td></tr>
            </tbody>
          </table>
        </div>
        <form v-if="revocarConsentimientoId" class="cancel-form" @submit.prevent="revocarConsentimiento">
          <div class="form-group"><label class="form-label">Motivo de revocación</label><textarea v-model="motivoRevocacion" class="input-clinical" required rows="2"></textarea></div>
          <div class="form-actions"><button class="btn-danger" :disabled="busy">Revocar</button><button type="button" class="btn-secondary" @click="revocarConsentimientoId=null">Cancelar</button></div>
        </form>
        <form v-if="detalle.estado==='internado'" class="editor-form" @submit.prevent="agregarConsentimiento">
          <div class="form-grid">
            <div class="form-group"><label class="form-label">Procedimiento</label><input v-model="consentForm.procedimiento" class="input-clinical" required maxlength="255" /></div>
            <div class="form-group"><label class="form-label">Fecha</label><input v-model="consentForm.fecha" type="date" class="input-clinical" required /></div>
            <div class="form-group full-width"><label class="form-label">Riesgos y beneficios explicados</label><textarea v-model="consentForm.riesgos_beneficios" class="input-clinical" rows="2" required maxlength="4000"></textarea></div>
            <div class="form-group"><label class="form-label">Firmante</label><input v-model="consentForm.firmante_nombre" class="input-clinical" required maxlength="255" /></div>
            <div class="form-group"><label class="form-label">Documento firmante</label><input v-model="consentForm.firmante_documento" class="input-clinical" required maxlength="20" /></div>
            <div class="form-group"><label class="form-label">Relación</label>
              <select v-model="consentForm.relacion_firmante" class="input-clinical"><option value="PACIENTE">Paciente</option><option value="REPRESENTANTE">Representante</option></select>
            </div>
            <div class="form-group"><label class="form-label">Testigo (opcional)</label><input v-model="consentForm.testigo_nombre" class="input-clinical" maxlength="255" /></div>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-plus" class="w-4 h-4" />Registrar consentimiento</button></div>
        </form>

        <!-- Alta -->
        <form v-if="detalle.estado==='internado'" class="cancel-form" @submit.prevent="darAlta">
          <div class="form-group"><label class="form-label">Resumen de alta</label><textarea v-model="altaForm.resumen_alta" class="input-clinical" rows="2" maxlength="4000"></textarea></div>
          <button class="btn-danger" :disabled="busy"><UIcon name="i-heroicons-arrow-right-end-on-rectangle" class="w-4 h-4" />Dar de alta</button>
        </form>
      </section>
    </template>

    <!-- ═══════════ CENSO DIARIO ═══════════ -->
    <template v-else-if="mode==='censo-diario'">
      <section class="panel">
        <div class="form-grid">
          <div class="form-group"><label class="form-label">Fecha</label><input v-model="censoFecha" type="date" class="input-clinical" @change="cargarCenso" /></div>
        </div>
        <div v-if="censo" class="table-responsive" style="margin-top:1rem">
          <table class="lab-table">
            <thead><tr><th>Camas totales</th><th>Internados</th><th>Ingresos del día</th><th>Altas del día</th></tr></thead>
            <tbody><tr><td>{{ censo.total_camas }}</td><td>{{ censo.total_internados }}</td><td>{{ censo.ingresos_del_dia }}</td><td>{{ censo.altas_del_dia }}</td></tr></tbody>
          </table>
        </div>
        <div class="form-actions" style="margin-top:1rem">
          <button class="btn-secondary" @click="download('/censo-diario/reporte.pdf?fecha='+censoFecha, 'censo-diario.pdf')"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />PDF</button>
          <button class="btn-secondary" @click="download('/censo-diario/reporte.csv?fecha='+censoFecha, 'censo-diario.csv')"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />CSV</button>
        </div>
      </section>
      <section v-if="censo" class="panel results-panel">
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>N.° hospitalización</th><th>Paciente</th><th>Cama</th><th>Diagnóstico</th><th>Días internado</th></tr></thead>
            <tbody>
              <tr v-for="i in censo.items" :key="i.id"><td>{{ i.numero_hospitalizacion }}</td><td>{{ i.paciente }}</td><td>{{ i.cama_codigo }}</td><td>{{ i.diagnostico_ingreso_descripcion || '—' }}</td><td>{{ i.dias_internado }}</td></tr>
              <tr v-if="!censo.items.length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Sin internados en esta fecha.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <!-- ═══════════ INTERCONSULTAS (global) ═══════════ -->
    <template v-else-if="mode==='interconsultas'">
      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">Interconsultas intrahospitalarias</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Origen</th><th>N.°</th><th>Paciente</th><th>Especialidad</th><th>Motivo</th><th>Urgente</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              <tr v-for="i in interconsultasGlobal" :key="i.id">
                <td>{{ i.origen === 'HOSPITALIZACION' ? 'Hospitalización' : 'Emergencia' }}</td>
                <td>{{ i.hospitalizacion_numero || i.numero_cuenta_emergencia }}</td><td>{{ i.paciente_nombre }}</td><td>{{ i.especialidad_nombre }}</td>
                <td>{{ i.motivo }}</td><td>{{ i.urgente?'Sí':'No' }}</td><td>{{ i.estado }}</td>
                <td><button v-if="i.hospitalizacion_id" class="action-btn action-view" @click="verHospitalizacion(i.hospitalizacion_id, 'hospitalizaciones')"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button></td>
              </tr>
              <tr v-if="!interconsultasGlobal.length"><td colspan="8" style="text-align:center;color:var(--ink-soft)">Sin interconsultas.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <!-- ═══════════ CONSENTIMIENTOS (global) ═══════════ -->
    <template v-else-if="mode==='consentimientos'">
      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">Consentimientos informados</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>N.°</th><th>Hospitalización</th><th>Paciente</th><th>Procedimiento</th><th>Fecha</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              <tr v-for="c in consentimientosGlobal" :key="c.id">
                <td>{{ c.numero }}</td><td>{{ c.hospitalizacion_numero }}</td><td>{{ c.paciente_nombre }}</td>
                <td>{{ c.procedimiento }}</td><td>{{ c.fecha }}</td><td>{{ c.estado }}</td>
                <td><button class="action-btn action-pdf" @click="download('/consentimientos/'+c.id+'/comprobante.pdf', 'consentimiento.pdf')"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" /></button></td>
              </tr>
              <tr v-if="!consentimientosGlobal.length"><td colspan="7" style="text-align:center;color:var(--ink-soft)">Sin consentimientos.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'hospitalizaciones' | 'seguimiento-paciente' | 'censo-diario' | 'interconsultas' | 'consentimientos'
const props = defineProps<{ mode: Mode; initialId?: string; admitir?: boolean }>()
const { api } = useApi()
const endpoint = '/app/hospitalizacion'

const titles = {
  'hospitalizaciones': 'Hospitalizaciones',
  'seguimiento-paciente': 'Seguimiento Paciente',
  'censo-diario': 'Censo Diario',
  'interconsultas': 'Interconsultas',
  'consentimientos': 'Consentimientos'
}

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)

const filtro = reactive({ q: '', estado: '' })
const hospitalizaciones = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const detalle = ref<any>(null)

const catalogs = reactive<Record<string, any[]>>({ camas: [], especialidades: [] })
const pendientesEmergencia = ref<any[]>([])
const formAdmision = ref(false)
const admisionForm = reactive({ destino_id: '', cama_id: '', especialidad_ingreso_id: '' })

const pendientesEmergenciaInterc = ref<any[]>([])
const formAdmisionInterc = ref(false)
const admisionIntercForm = reactive({ destino_id: '', especialidad_destino_id: '', motivo: '', urgente: false })

const notaForm = reactive({ tipo: 'MEDICA', pulso: null, temperatura: null, saturacion_o2: null, contenido: '', plan_indicaciones: '' })
const intercForm = reactive({ especialidad_destino_id: '', motivo: '', urgente: false })
const consentForm = reactive({ procedimiento: '', riesgos_beneficios: '', firmante_nombre: '', firmante_documento: '', relacion_firmante: 'PACIENTE', testigo_nombre: '', fecha: today() })
const altaForm = reactive({ resumen_alta: '' })
const revocarConsentimientoId = ref('')
const motivoRevocacion = ref('')

const censoFecha = ref(today())
const censo = ref<any>(null)
const interconsultasGlobal = ref<any[]>([])
const consentimientosGlobal = ref<any[]>([])

function today() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date())
}

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}

async function run(fn: () => Promise<void>) {
  if (busy.value) return
  busy.value = true; error.value = ''; notice.value = ''
  try { await fn() } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function getCatalogs() {
  catalogs.especialidades = await api<any[]>(endpoint + '/catalogos/especialidades')
  catalogs.camas = await api<any[]>(endpoint + '/camas-disponibles')
}

async function abrirAdmision() {
  await run(async () => {
    formAdmision.value = true
    await getCatalogs()
    pendientesEmergencia.value = await api<any[]>(endpoint + '/emergencia-pendientes')
    Object.assign(admisionForm, { destino_id: '', cama_id: '', especialidad_ingreso_id: '' })
  })
}

async function admitirEmergencia() {
  await run(async () => {
    await api(endpoint + '/hospitalizaciones/admitir-emergencia', { method: 'POST', body: { ...admisionForm, especialidad_ingreso_id: admisionForm.especialidad_ingreso_id || null } })
    notice.value = 'Paciente admitido.'
    formAdmision.value = false
    await buscarHospitalizaciones()
  })
}

async function abrirAdmisionInterc() {
  await run(async () => {
    formAdmisionInterc.value = true
    if (!catalogs.especialidades.length) await getCatalogs()
    pendientesEmergenciaInterc.value = await api<any[]>(endpoint + '/emergencia-pendientes', { query: { destino: 'INTERCONSULTA' } })
    Object.assign(admisionIntercForm, { destino_id: '', especialidad_destino_id: '', motivo: '', urgente: false })
  })
}

async function admitirInterconsultaEmergencia() {
  await run(async () => {
    await api(endpoint + '/interconsultas/admitir-emergencia', { method: 'POST', body: { ...admisionIntercForm } })
    notice.value = 'Interconsulta solicitada.'
    formAdmisionInterc.value = false
    await cargarInterconsultasGlobal()
  })
}

async function buscarHospitalizaciones() {
  page.value = 1
  await cargarHospitalizaciones()
}

async function cargarHospitalizaciones() {
  loading.value = true; error.value = ''
  try {
    const q: Record<string, any> = { page: page.value, page_size: pageSize.value }
    if (filtro.q) q.q = filtro.q
    if (mode_estado()) q.estado = mode_estado()
    const data = await api<any>(endpoint + '/hospitalizaciones', { query: q })
    hospitalizaciones.value = data.items
    total.value = data.total
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

function mode_estado() {
  if (props.mode === 'seguimiento-paciente') return 'internado'
  return filtro.estado
}

async function cambiarPagina(p: number) { page.value = p; await cargarHospitalizaciones() }

async function verHospitalizacion(id: string, target?: string) {
  if (target && target !== props.mode) { await navigateTo('/app/hospitalizacion/' + target + '/' + id); return }
  await run(async () => {
    detalle.value = await api(endpoint + '/hospitalizaciones/' + id)
    Object.assign(notaForm, { tipo: 'MEDICA', pulso: null, temperatura: null, saturacion_o2: null, contenido: '', plan_indicaciones: '' })
    Object.assign(intercForm, { especialidad_destino_id: '', motivo: '', urgente: false })
    Object.assign(consentForm, { procedimiento: '', riesgos_beneficios: '', firmante_nombre: '', firmante_documento: '', relacion_firmante: 'PACIENTE', testigo_nombre: '', fecha: today() })
    altaForm.resumen_alta = ''
    revocarConsentimientoId.value = ''
    if (!catalogs.especialidades.length) await getCatalogs()
  })
}

async function agregarNota() {
  await run(async () => {
    await api(endpoint + '/hospitalizaciones/' + detalle.value.id + '/notas', { method: 'POST', body: notaForm })
    notice.value = 'Nota agregada.'
    await verHospitalizacion(detalle.value.id)
  })
}

async function solicitarInterconsulta() {
  await run(async () => {
    await api(endpoint + '/hospitalizaciones/' + detalle.value.id + '/interconsultas', { method: 'POST', body: intercForm })
    notice.value = 'Interconsulta solicitada.'
    await verHospitalizacion(detalle.value.id)
  })
}

async function agregarConsentimiento() {
  await run(async () => {
    await api(endpoint + '/hospitalizaciones/' + detalle.value.id + '/consentimientos', { method: 'POST', body: consentForm })
    notice.value = 'Consentimiento registrado.'
    await verHospitalizacion(detalle.value.id)
  })
}

async function revocarConsentimiento() {
  await run(async () => {
    await api(endpoint + '/consentimientos/' + revocarConsentimientoId.value + '/revocar', { method: 'POST', body: { motivo_revocacion: motivoRevocacion.value } })
    notice.value = 'Consentimiento revocado.'
    revocarConsentimientoId.value = ''; motivoRevocacion.value = ''
    await verHospitalizacion(detalle.value.id)
  })
}

async function darAlta() {
  await run(async () => {
    await api(endpoint + '/hospitalizaciones/' + detalle.value.id + '/alta', { method: 'POST', body: altaForm })
    notice.value = 'Alta registrada.'
    await verHospitalizacion(detalle.value.id)
    await cargarHospitalizaciones()
  })
}

async function cargarCenso() {
  await run(async () => { censo.value = await api(endpoint + '/censo-diario', { query: { fecha: censoFecha.value } }) })
}

async function cargarInterconsultasGlobal() {
  await run(async () => { interconsultasGlobal.value = await api<any[]>(endpoint + '/interconsultas') })
}

async function cargarConsentimientosGlobal() {
  await run(async () => { consentimientosGlobal.value = await api<any[]>(endpoint + '/consentimientos') })
}

async function download(path: string, name: string) {
  await run(async () => {
    const blob = await api<Blob>(endpoint + path, { responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a'); a.href = url; a.download = name; a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  })
}

async function init() {
  if (props.mode === 'hospitalizaciones' || props.mode === 'seguimiento-paciente') {
    await cargarHospitalizaciones()
    if (props.initialId) await verHospitalizacion(props.initialId)
    if (props.admitir) await abrirAdmision()
  } else if (props.mode === 'censo-diario') { await cargarCenso() }
  else if (props.mode === 'interconsultas') { await cargarInterconsultasGlobal() }
  else if (props.mode === 'consentimientos') { await cargarConsentimientosGlobal() }
}

onMounted(init)
</script>

<style scoped>
.lab-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.header-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-danger { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--alert); color: white; border: none; cursor: pointer; }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.lab-tabs { display: flex; gap: 0.25rem; border-bottom: 2px solid var(--line); margin-bottom: 1.5rem; flex-wrap: wrap; }
.tab-link { padding: 0.625rem 1.25rem; font-size: 0.875rem; font-weight: 500; color: var(--ink-soft); text-decoration: none; border-bottom: 2px solid transparent; margin-bottom: -2px; }
.tab-link--active { color: var(--teal); border-bottom-color: var(--teal); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.search-form { display: flex; flex-direction: column; gap: 1rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.search-field { display: flex; flex-direction: column; gap: 0.25rem; }
.search-actions { display: flex; gap: 0.75rem; justify-content: flex-end; }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.action-buttons { display: flex; gap: 0.25rem; }
.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; color: var(--ink-soft); cursor: pointer; }
.action-btn:hover { background: var(--mist); }
.action-view:hover { color: var(--teal); border-color: var(--teal-soft); background: var(--teal-soft); }
.action-pdf:hover { color: var(--alert); border-color: var(--alert-soft); background: var(--alert-soft); }
.pagination { display: flex; align-items: center; gap: 0.75rem; justify-content: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--line); }
.page-info { font-size: 0.8125rem; color: var(--ink-soft); }
.editor-form { display: flex; flex-direction: column; gap: 1rem; margin-top: 0.75rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.5rem; }
.choices { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.75rem 0; }
.choice-btn { padding: 0.375rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.8125rem; cursor: pointer; }
.choice-btn:hover, .choice-btn--active { background: var(--teal-soft); border-color: var(--teal); }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.detail-title { font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0; }
.detail-subtitle { font-size: 0.875rem; color: var(--ink-soft); margin: 0.125rem 0 0 0; }
.detail-info { font-size: 0.875rem; color: var(--ink); padding: 0.5rem 0; }
.section-title { font-size: 0.875rem; font-weight: 600; color: var(--ink); margin: 1.25rem 0 0.5rem 0; padding-top: 0.75rem; border-top: 1px solid var(--line); }
.result-section { padding: 0.5rem 0; border-bottom: 1px solid var(--line); }
.cancel-form { border-top: 1px solid var(--alert-soft); padding-top: 1rem; margin-top: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid, .form-grid { grid-template-columns: 1fr; }
}
</style>
