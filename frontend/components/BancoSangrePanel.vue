<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-beaker" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">BANCO DE SANGRE · PRONAHEBAS · LEY N.° 26454</span>
          <h1 class="page-title">{{ mode === 'movimientos' ? 'Movimientos' : 'Solicitud Transfusional' }}</h1>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <!-- ═══════════ MOVIMIENTOS ═══════════ -->
    <template v-if="mode === 'movimientos'">
      <section class="panel search-panel">
        <div class="search-actions" style="justify-content:flex-start">
          <button v-for="t in tabsMov" :key="t.key" class="btn-secondary btn-sm" :class="{ 'btn-active': subTab === t.key }" @click="subTab = t.key; cargarSub()">{{ t.label }}</button>
        </div>
      </section>

      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>

      <!-- Donantes -->
      <template v-else-if="subTab === 'donantes'">
        <section class="panel">
          <div class="card-header-row"><h2 class="results-title">Nuevo donante</h2></div>
          <form class="editor-form" @submit.prevent="crearDonante">
            <div class="form-grid">
              <div class="form-group"><label class="form-label">DNI</label><input v-model="nuevoDonante.dni" class="input-clinical" required /></div>
              <div class="form-group"><label class="form-label">Nombres</label><input v-model="nuevoDonante.nombres" class="input-clinical" required /></div>
              <div class="form-group"><label class="form-label">Apellido paterno</label><input v-model="nuevoDonante.apellido_paterno" class="input-clinical" required /></div>
              <div class="form-group"><label class="form-label">Apellido materno</label><input v-model="nuevoDonante.apellido_materno" class="input-clinical" required /></div>
              <div class="form-group"><label class="form-label">Fecha de nacimiento</label><input v-model="nuevoDonante.fecha_nacimiento" type="date" class="input-clinical" required /></div>
              <div class="form-group"><label class="form-label">Sexo</label><select v-model="nuevoDonante.sexo" class="input-clinical"><option value="M">M</option><option value="F">F</option></select></div>
              <div class="form-group"><label class="form-label">Celular</label><input v-model="nuevoDonante.celular" class="input-clinical" /></div>
              <div class="form-group"><label class="form-label">Correo</label><input v-model="nuevoDonante.correo" class="input-clinical" /></div>
            </div>
            <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Registrar donante</button></div>
          </form>
        </section>
        <section class="panel results-panel">
          <div class="results-header"><h2 class="results-title">{{ donantes.length }} donantes</h2></div>
          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th>Nombre</th><th>DNI</th><th>Grupo/Rh</th><th>Última donación</th><th>Estado</th></tr></thead>
              <tbody>
                <tr v-for="d in donantes" :key="d.id">
                  <td>{{ d.nombre_completo }}</td><td>{{ d.dni }}</td>
                  <td>{{ d.grupo_sanguineo ? d.grupo_sanguineo + d.factor_rh : '—' }}</td>
                  <td>{{ d.fecha_ultima_donacion || '—' }}</td>
                  <td><span class="badge" :class="d.is_active ? 'badge-ok' : 'badge-off'">{{ d.is_active ? 'Activo' : 'Diferido' }}</span></td>
                </tr>
                <tr v-if="!donantes.length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Sin donantes registrados.</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

      <!-- Unidades -->
      <template v-else-if="subTab === 'unidades'">
        <section class="panel">
          <div class="card-header-row"><h2 class="results-title">Nueva extracción</h2></div>
          <form class="editor-form" @submit.prevent="crearUnidad">
            <div class="form-grid">
              <div class="form-group full-width"><label class="form-label">Donante</label>
                <select v-model="nuevaUnidad.donante_id" class="input-clinical" required>
                  <option value="" disabled>Seleccione un donante</option>
                  <option v-for="d in donantes" :key="d.id" :value="d.id">{{ d.nombre_completo }} ({{ d.dni }})</option>
                </select>
              </div>
              <div class="form-group"><label class="form-label">Grupo sanguíneo</label>
                <select v-model="nuevaUnidad.grupo_sanguineo" class="input-clinical"><option v-for="g in ['A','B','AB','O']" :key="g" :value="g">{{ g }}</option></select>
              </div>
              <div class="form-group"><label class="form-label">Factor Rh</label>
                <select v-model="nuevaUnidad.factor_rh" class="input-clinical"><option value="+">+</option><option value="-">-</option></select>
              </div>
              <div class="form-group"><label class="form-label">Peso (kg)</label><input v-model.number="nuevaUnidad.peso_kg" type="number" step="0.1" class="input-clinical" /></div>
              <div class="form-group"><label class="form-label">Hemoglobina (g/dL)</label><input v-model.number="nuevaUnidad.hemoglobina_g_dl" type="number" step="0.1" class="input-clinical" /></div>
              <div class="form-group"><label class="form-label">PA sistólica</label><input v-model.number="nuevaUnidad.presion_sistolica" type="number" class="input-clinical" /></div>
              <div class="form-group"><label class="form-label">PA diastólica</label><input v-model.number="nuevaUnidad.presion_diastolica" type="number" class="input-clinical" /></div>
            </div>
            <div class="form-actions"><button class="btn-primary" :disabled="busy || !donantes.length"><UIcon name="i-heroicons-check" class="w-4 h-4" />Registrar extracción</button></div>
            <p v-if="!donantes.length" class="field-hint">Registre primero un donante en la pestaña Donantes.</p>
          </form>
        </section>
        <section class="panel results-panel">
          <div class="results-header"><h2 class="results-title">{{ unidades.length }} unidades</h2></div>
          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th>N.° unidad</th><th>Donante</th><th>Grupo/Rh</th><th>Tamizaje</th><th>Apto</th><th>Estado</th><th></th></tr></thead>
              <tbody>
                <tr v-for="u in unidades" :key="u.id">
                  <td>{{ u.numero_unidad }}</td><td>{{ u.donante_nombre }}</td><td>{{ u.grupo_sanguineo }}{{ u.factor_rh }}</td>
                  <td>{{ u.tamizaje_registrado ? 'Registrado' : 'Pendiente' }}</td>
                  <td><span v-if="u.apto !== null" class="badge" :class="u.apto ? 'badge-ok' : 'badge-off'">{{ u.apto ? 'Apto' : 'No apto' }}</span><span v-else>—</span></td>
                  <td><span class="badge badge-pendiente">{{ u.estado }}</span></td>
                  <td>
                    <button v-if="!u.tamizaje_registrado" class="btn-secondary btn-sm" :disabled="busy" @click="abrirTamizaje(u)"><UIcon name="i-heroicons-beaker" class="w-4 h-4" />Tamizaje</button>
                    <button v-else-if="u.estado === 'extraida' && u.apto" class="btn-secondary btn-sm" :disabled="busy" @click="abrirFraccionar(u)"><UIcon name="i-heroicons-squares-2x2" class="w-4 h-4" />Fraccionar</button>
                  </td>
                </tr>
                <tr v-if="!unidades.length"><td colspan="7" style="text-align:center;color:var(--ink-soft)">Sin unidades extraídas.</td></tr>
              </tbody>
            </table>
          </div>
        </section>

        <section v-if="unidadTamizaje" class="panel">
          <div class="card-header-row"><h2 class="results-title">Tamizaje serológico — {{ unidadTamizaje.numero_unidad }}</h2><button class="btn-secondary" @click="unidadTamizaje = null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
          <form class="editor-form" @submit.prevent="confirmarTamizaje">
            <div class="form-grid">
              <label v-for="k in tamizajeCampos" :key="k.key" class="check-field"><input type="checkbox" v-model="tamizaje[k.key]" /> {{ k.label }} reactivo</label>
              <div class="form-group full-width"><label class="form-label">Motivo de diferimiento (opcional, aun sin reactivos)</label><input v-model="tamizaje.motivo_diferido" class="input-clinical" /></div>
            </div>
            <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Registrar tamizaje</button></div>
          </form>
        </section>

        <section v-if="unidadFraccionar" class="panel">
          <div class="card-header-row"><h2 class="results-title">Fraccionar — {{ unidadFraccionar.numero_unidad }}</h2><button class="btn-secondary" @click="unidadFraccionar = null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button></div>
          <div class="check-list">
            <label v-for="t in tiposComponente" :key="t" class="check-field"><input type="checkbox" :value="t" v-model="tiposAFraccionar" /> {{ t.replaceAll('_', ' ') }}</label>
          </div>
          <div class="form-actions" style="margin-top:1rem"><button class="btn-primary" :disabled="busy || !tiposAFraccionar.length" @click="confirmarFraccionar"><UIcon name="i-heroicons-check" class="w-4 h-4" />Producir componentes</button></div>
        </section>
      </template>

      <!-- Inventario -->
      <template v-else-if="subTab === 'inventario'">
        <section class="stats-row">
          <div v-for="i in inventario" :key="i.tipo + i.grupo_sanguineo + i.factor_rh" class="stat-card">
            <div class="stat-icon" style="background:var(--teal-soft)"><UIcon name="i-heroicons-beaker" class="w-5 h-5" style="color:var(--teal)" /></div>
            <div class="stat-body"><span class="stat-num">{{ i.unidades_disponibles }}</span><span class="stat-label">{{ i.tipo.replaceAll('_',' ') }} {{ i.grupo_sanguineo }}{{ i.factor_rh }}</span></div>
          </div>
          <p v-if="!inventario.length" class="field-hint">Sin componentes disponibles en inventario.</p>
        </section>
        <section class="panel results-panel">
          <div class="results-header"><h2 class="results-title">{{ componentes.length }} componentes</h2></div>
          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th>Código</th><th>Tipo</th><th>Grupo/Rh</th><th>Vencimiento</th><th>Días</th><th>Estado</th></tr></thead>
              <tbody>
                <tr v-for="c in componentes" :key="c.id">
                  <td>{{ c.codigo }}</td><td>{{ c.tipo.replaceAll('_',' ') }}</td><td>{{ c.grupo_sanguineo }}{{ c.factor_rh }}</td>
                  <td>{{ c.fecha_vencimiento }}</td>
                  <td :style="{ color: c.dias_para_vencer <= 5 ? 'var(--alert)' : 'inherit' }">{{ c.dias_para_vencer }}</td>
                  <td><span class="badge" :class="c.estado === 'disponible' ? 'badge-ok' : c.estado === 'vencido' || c.estado === 'descartado' ? 'badge-off' : 'badge-pendiente'">{{ c.estado }}</span></td>
                </tr>
                <tr v-if="!componentes.length"><td colspan="6" style="text-align:center;color:var(--ink-soft)">Sin componentes registrados.</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>

      <!-- Kardex -->
      <template v-else-if="subTab === 'kardex'">
        <section class="panel results-panel">
          <div class="results-header"><h2 class="results-title">{{ kardex.total }} movimientos</h2></div>
          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th>Fecha</th><th>Tipo</th><th>Componente</th><th>Observaciones</th><th>Registrado por</th></tr></thead>
              <tbody>
                <tr v-for="m in kardex.items" :key="m.id">
                  <td>{{ formatFechaHora(m.created_at) }}</td><td>{{ m.tipo.replaceAll('_',' ') }}</td>
                  <td>{{ m.componente_codigo }} ({{ m.componente_tipo.replaceAll('_',' ') }})</td>
                  <td>{{ m.observaciones || '—' }}</td><td>{{ m.registrado_por }}</td>
                </tr>
                <tr v-if="!kardex.items.length"><td colspan="5" style="text-align:center;color:var(--ink-soft)">Sin movimientos registrados.</td></tr>
              </tbody>
            </table>
          </div>
        </section>
      </template>
    </template>

    <!-- ═══════════ SOLICITUD TRANSFUSIONAL ═══════════ -->
    <template v-else>
      <section class="panel">
        <div class="card-header-row"><h2 class="results-title">Nueva solicitud</h2></div>
        <form class="editor-form" @submit.prevent="crearSolicitud">
          <div class="form-grid">
            <div class="form-group"><label class="form-label">Origen</label>
              <select v-model="nuevaSolicitud.origenTipo" class="input-clinical">
                <option value="atencion_medica_id">Consulta Externa (Atención Médica)</option>
                <option value="atencion_emergencia_id">Emergencia</option>
                <option value="hospitalizacion_id">Hospitalización</option>
              </select>
            </div>
            <div class="form-group"><label class="form-label">ID del origen</label><input v-model="nuevaSolicitud.origenId" class="input-clinical" placeholder="UUID de la atención/hospitalización" required /></div>
            <div class="form-group"><label class="form-label">Tipo de componente</label>
              <select v-model="nuevaSolicitud.tipo_componente" class="input-clinical"><option v-for="t in tiposComponente" :key="t" :value="t">{{ t.replaceAll('_',' ') }}</option></select>
            </div>
            <div class="form-group"><label class="form-label">Cantidad de unidades</label><input v-model.number="nuevaSolicitud.cantidad_unidades" type="number" min="1" class="input-clinical" /></div>
            <div class="form-group"><label class="form-label">Grupo sanguíneo del paciente</label>
              <select v-model="nuevaSolicitud.grupo_sanguineo_paciente" class="input-clinical"><option v-for="g in ['A','B','AB','O']" :key="g" :value="g">{{ g }}</option></select>
            </div>
            <div class="form-group"><label class="form-label">Factor Rh del paciente</label>
              <select v-model="nuevaSolicitud.factor_rh_paciente" class="input-clinical"><option value="+">+</option><option value="-">-</option></select>
            </div>
            <div class="form-group"><label class="form-label">Urgencia</label>
              <select v-model="nuevaSolicitud.urgencia" class="input-clinical"><option value="RUTINA">Rutina</option><option value="URGENTE">Urgente</option><option value="EMERGENCIA">Emergencia</option></select>
            </div>
            <div class="form-group full-width"><label class="form-label">Motivo clínico</label><textarea v-model="nuevaSolicitud.motivo_clinico" class="input-clinical" rows="2" required></textarea></div>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Registrar solicitud</button></div>
        </form>
      </section>

      <section class="panel search-panel">
        <div class="search-actions" style="justify-content:flex-start">
          <button v-for="e in ['', 'pendiente', 'en_pruebas_cruzadas', 'lista_para_dispensar', 'dispensada', 'anulada']" :key="e" class="btn-secondary btn-sm" :class="{ 'btn-active': filtroEstado === e }" @click="filtroEstado = e; cargarSolicitudes()">{{ e || 'Todas' }}</button>
        </div>
      </section>

      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <section v-else class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ solicitudes.length }} solicitudes</h2></div>
        <div class="solicitud-list">
          <div v-for="s in solicitudes" :key="s.id" class="solicitud-card">
            <div class="solicitud-head">
              <div>
                <strong>{{ s.numero_solicitud }}</strong> — {{ s.paciente_nombre }} ({{ s.paciente_dni }})
                <span class="field-hint">{{ s.tipo_componente.replaceAll('_',' ') }} × {{ s.cantidad_unidades }} · {{ s.grupo_sanguineo_paciente }}{{ s.factor_rh_paciente }} · {{ s.urgencia }}</span>
              </div>
              <span class="badge" :class="s.estado === 'dispensada' ? 'badge-ok' : s.estado === 'anulada' ? 'badge-off' : 'badge-pendiente'">{{ s.estado }}</span>
            </div>
            <p class="field-hint">{{ s.motivo_clinico }}</p>
            <table v-if="s.asignaciones.length" class="lab-table">
              <thead><tr><th>Componente</th><th>Grupo/Rh</th><th>Prueba cruzada</th><th>Dispensado</th><th></th></tr></thead>
              <tbody>
                <tr v-for="a in s.asignaciones" :key="a.id">
                  <td>{{ a.componente_codigo }} ({{ a.componente_tipo.replaceAll('_',' ') }})</td><td>{{ a.grupo_sanguineo }}{{ a.factor_rh }}</td>
                  <td>
                    <span class="badge" :class="a.resultado_prueba_cruzada === 'compatible' ? 'badge-ok' : a.resultado_prueba_cruzada === 'incompatible' ? 'badge-off' : 'badge-pendiente'">{{ a.resultado_prueba_cruzada }}</span>
                    <button v-if="a.resultado_prueba_cruzada === 'pendiente'" class="btn-secondary btn-sm" :disabled="busy" @click="pruebaCruzada(a, 'compatible')">Compatible</button>
                    <button v-if="a.resultado_prueba_cruzada === 'pendiente'" class="btn-secondary btn-sm" :disabled="busy" @click="pruebaCruzada(a, 'incompatible')">Incompatible</button>
                  </td>
                  <td>{{ a.dispensado ? 'Sí' : 'No' }}</td>
                  <td><button v-if="a.resultado_prueba_cruzada === 'compatible' && !a.dispensado" class="btn-secondary btn-sm" :disabled="busy" @click="dispensar(a)"><UIcon name="i-heroicons-arrow-up-tray" class="w-4 h-4" />Dispensar</button></td>
                </tr>
              </tbody>
            </table>
            <div v-if="['pendiente','en_pruebas_cruzadas'].includes(s.estado)" class="row-actions" style="margin-top:0.5rem">
              <select v-model="componentePorSolicitud[s.id]" class="input-clinical input-sm">
                <option value="">Seleccione un componente compatible</option>
                <option v-for="c in componentesPara(s)" :key="c.id" :value="c.id">
                  {{ c.codigo }} · {{ c.tipo.replaceAll('_',' ') }} · {{ c.grupo_sanguineo }}{{ c.factor_rh }} · vence {{ c.fecha_vencimiento }}
                </option>
              </select>
              <button class="btn-secondary btn-sm" :disabled="busy || !componentePorSolicitud[s.id]" @click="asignarComponente(s)"><UIcon name="i-heroicons-link" class="w-4 h-4" />Asignar componente</button>
              <button class="btn-secondary btn-sm" :disabled="busy" @click="anularSolicitud(s)"><UIcon name="i-heroicons-x-circle" class="w-4 h-4" />Anular</button>
            </div>
            <p v-if="['pendiente','en_pruebas_cruzadas'].includes(s.estado) && !componentesPara(s).length" class="field-hint">No hay componentes disponibles del tipo solicitado. Revise el inventario.</p>
          </div>
          <p v-if="!solicitudes.length" class="field-hint">No hay solicitudes registradas todavía.</p>
        </div>
        <p class="field-hint" style="margin-top:0.75rem">Seleccione una unidad del inventario; el sistema valida tipo y compatibilidad ABO/Rh antes de reservarla.</p>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'movimientos' | 'solicitud-transfusional'
const props = defineProps<{ mode: Mode }>()
const { api } = useApi()
const endpoint = '/app/banco-sangre'

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}
function formatFechaHora(f: string) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

const tiposComponente = ['PAQUETE_GLOBULAR', 'PLASMA_FRESCO_CONGELADO', 'PLAQUETAS', 'CRIOPRECIPITADO', 'SANGRE_TOTAL']
const tamizajeCampos = [
  { key: 'vih_reactivo', label: 'VIH' }, { key: 'hbsag_reactivo', label: 'Hepatitis B (HBsAg)' },
  { key: 'hcv_reactivo', label: 'Hepatitis C (Anti-HCV)' }, { key: 'sifilis_reactivo', label: 'Sífilis' },
  { key: 'chagas_reactivo', label: 'Chagas' },
]

// Movimientos
const tabsMov = [
  { key: 'donantes', label: 'Donantes' }, { key: 'unidades', label: 'Unidades' },
  { key: 'inventario', label: 'Inventario' }, { key: 'kardex', label: 'Kardex' },
]
const subTab = ref('donantes')
const donantes = ref<any[]>([])
const unidades = ref<any[]>([])
const componentes = ref<any[]>([])
const inventario = ref<any[]>([])
const kardex = ref<{ items: any[]; total: number }>({ items: [], total: 0 })

const nuevoDonante = reactive({ dni: '', nombres: '', apellido_paterno: '', apellido_materno: '', fecha_nacimiento: '', sexo: 'M', celular: '', correo: '' })
const nuevaUnidad = reactive({ donante_id: '', grupo_sanguineo: 'O', factor_rh: '+', peso_kg: null, hemoglobina_g_dl: null, presion_sistolica: null, presion_diastolica: null })
const unidadTamizaje = ref<any>(null)
const tamizaje = reactive<any>({ vih_reactivo: false, hbsag_reactivo: false, hcv_reactivo: false, sifilis_reactivo: false, chagas_reactivo: false, motivo_diferido: '' })
const unidadFraccionar = ref<any>(null)
const tiposAFraccionar = ref<string[]>([])

async function cargarSub() {
  loading.value = true; error.value = ''
  try {
    if (subTab.value === 'donantes') donantes.value = await api(endpoint + '/donantes')
    else if (subTab.value === 'unidades') {
      if (!donantes.value.length) donantes.value = await api(endpoint + '/donantes')
      unidades.value = await api(endpoint + '/unidades')
    } else if (subTab.value === 'inventario') {
      inventario.value = await api(endpoint + '/inventario')
      componentes.value = await api(endpoint + '/componentes')
    } else if (subTab.value === 'kardex') {
      kardex.value = await api(endpoint + '/movimientos')
    }
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function crearDonante() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/donantes', { method: 'POST', body: { ...nuevoDonante, celular: nuevoDonante.celular || undefined, correo: nuevoDonante.correo || undefined } })
    notice.value = 'Donante registrado.'
    Object.assign(nuevoDonante, { dni: '', nombres: '', apellido_paterno: '', apellido_materno: '', fecha_nacimiento: '', sexo: 'M', celular: '', correo: '' })
    await cargarSub()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function crearUnidad() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/unidades', { method: 'POST', body: nuevaUnidad })
    notice.value = 'Extracción registrada. Ahora registre el tamizaje serológico.'
    Object.assign(nuevaUnidad, { donante_id: '', grupo_sanguineo: 'O', factor_rh: '+', peso_kg: null, hemoglobina_g_dl: null, presion_sistolica: null, presion_diastolica: null })
    await cargarSub()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

function abrirTamizaje(u: any) {
  unidadTamizaje.value = u
  Object.assign(tamizaje, { vih_reactivo: false, hbsag_reactivo: false, hcv_reactivo: false, sifilis_reactivo: false, chagas_reactivo: false, motivo_diferido: '' })
}
async function confirmarTamizaje() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/unidades/' + unidadTamizaje.value.id + '/tamizaje', { method: 'POST', body: { ...tamizaje, motivo_diferido: tamizaje.motivo_diferido || undefined } })
    notice.value = 'Tamizaje registrado.'
    unidadTamizaje.value = null
    await cargarSub()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

function abrirFraccionar(u: any) {
  unidadFraccionar.value = u
  tiposAFraccionar.value = []
}
async function confirmarFraccionar() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/unidades/' + unidadFraccionar.value.id + '/fraccionar', { method: 'POST', body: { tipos: tiposAFraccionar.value } })
    notice.value = 'Componentes producidos.'
    unidadFraccionar.value = null
    await cargarSub()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

// Solicitud Transfusional
const solicitudes = ref<any[]>([])
const filtroEstado = ref('')
const nuevaSolicitud = reactive({
  origenTipo: 'atencion_medica_id', origenId: '', tipo_componente: 'PAQUETE_GLOBULAR', cantidad_unidades: 1,
  grupo_sanguineo_paciente: 'O', factor_rh_paciente: '+', urgencia: 'RUTINA', motivo_clinico: '',
})
const componentePorSolicitud = reactive<Record<string, string>>({})

async function cargarSolicitudes() {
  loading.value = true; error.value = ''
  try {
    const [lista, stock] = await Promise.all([
      api<any[]>(endpoint + '/solicitud-transfusional', { query: filtroEstado.value ? { estado: filtroEstado.value } : {} }),
      api<any[]>(endpoint + '/componentes', { query: { estado: 'disponible' } }),
    ])
    solicitudes.value = lista
    componentes.value = stock
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

function componentesPara(s: any) {
  return componentes.value.filter(c => c.estado === 'disponible' && c.tipo === s.tipo_componente)
}

async function crearSolicitud() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    const body: any = {
      tipo_componente: nuevaSolicitud.tipo_componente, cantidad_unidades: nuevaSolicitud.cantidad_unidades,
      grupo_sanguineo_paciente: nuevaSolicitud.grupo_sanguineo_paciente, factor_rh_paciente: nuevaSolicitud.factor_rh_paciente,
      urgencia: nuevaSolicitud.urgencia, motivo_clinico: nuevaSolicitud.motivo_clinico,
      [nuevaSolicitud.origenTipo]: nuevaSolicitud.origenId,
    }
    await api(endpoint + '/solicitud-transfusional', { method: 'POST', body })
    notice.value = 'Solicitud registrada.'
    Object.assign(nuevaSolicitud, { origenId: '', motivo_clinico: '' })
    await cargarSolicitudes()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function asignarComponente(s: any) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/solicitud-transfusional/' + s.id + '/asignar-componente', { method: 'POST', body: { componente_id: componentePorSolicitud[s.id] } })
    notice.value = 'Componente asignado.'
    componentePorSolicitud[s.id] = ''
    await cargarSolicitudes()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function pruebaCruzada(a: any, resultado: string) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/solicitud-transfusional/asignaciones/' + a.id + '/prueba-cruzada', { method: 'POST', body: { resultado } })
    notice.value = 'Resultado de prueba cruzada registrado.'
    await cargarSolicitudes()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function dispensar(a: any) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/solicitud-transfusional/asignaciones/' + a.id + '/dispensar', { method: 'POST' })
    notice.value = 'Componente dispensado.'
    await cargarSolicitudes()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function anularSolicitud(s: any) {
  const motivo = prompt('Motivo de anulación:')
  if (!motivo) return
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/solicitud-transfusional/' + s.id + '/anular', { method: 'POST', body: { motivo } })
    notice.value = 'Solicitud anulada.'
    await cargarSolicitudes()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

onMounted(async () => {
  if (props.mode === 'movimientos') await cargarSub()
  else await cargarSolicitudes()
})
</script>

<style scoped>
.lab-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.375rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { padding: 0.375rem 0.625rem; font-size: 0.75rem; margin-left: 0.375rem; }
.btn-active { background: var(--teal-soft); border-color: var(--teal); color: var(--teal); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); }
.field-hint.full-width { grid-column: 1 / -1; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.search-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.input-sm { width: 220px; padding: 0.375rem 0.5rem; font-size: 0.75rem; display: inline-block; }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; margin-top: 0.5rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); white-space: nowrap; }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.row-actions { display: flex; align-items: center; gap: 0.375rem; flex-wrap: wrap; }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; white-space: nowrap; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-off { color: var(--ink-soft); background: var(--mist); }
.badge-pendiente { color: var(--amber); background: var(--amber-soft); }
.editor-form { display: flex; flex-direction: column; gap: 1rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.check-field { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8125rem; color: var(--ink); }
.check-list { display: flex; flex-wrap: wrap; gap: 1rem; }

.stats-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card { display: flex; align-items: center; gap: 1rem; padding: 1.125rem 1.25rem; border-radius: var(--radius-lg); border: 1px solid var(--line); background: var(--paper); box-shadow: var(--shadow-sm); }
.stat-icon { width: 44px; height: 44px; border-radius: 12px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.stat-body { display: flex; flex-direction: column; min-width: 0; }
.stat-num { font-size: 1.375rem; font-weight: 700; color: var(--ink); line-height: 1.2; }
.stat-label { font-size: 0.8125rem; color: var(--ink-soft); }

.solicitud-list { display: flex; flex-direction: column; gap: 1rem; }
.solicitud-card { border: 1px solid var(--line); border-radius: 10px; padding: 1rem; }
.solicitud-head { display: flex; justify-content: space-between; align-items: flex-start; gap: 1rem; flex-wrap: wrap; margin-bottom: 0.375rem; }

@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
