<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-user-group" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">HEMODIÁLISIS · TERAPIA DE REEMPLAZO RENAL</span>
          <h1 class="page-title">{{ mode === 'hemodialis' ? 'Programa de Hemodiálisis' : 'Sesiones' }}</h1>
        </div>
      </div>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <div v-if="notice" class="success-banner"><UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />{{ notice }}</div>

    <!-- ═══════════ HEMODIALIS: programa de pacientes ═══════════ -->
    <template v-if="mode === 'hemodialis'">
      <section class="panel">
        <div class="card-header-row"><h2 class="results-title">Inscribir paciente en el programa</h2></div>
        <form class="editor-form" @submit.prevent="crearPaciente">
          <div class="form-grid">
            <div class="form-group"><label class="form-label">ID del paciente</label><input v-model="nuevoPaciente.patient_id" class="input-clinical" placeholder="UUID del paciente" required /></div>
            <div class="form-group"><label class="form-label">ID de diagnóstico CIE-10 (opcional, ej. N18.x)</label><input v-model="nuevoPaciente.diagnostico_id" class="input-clinical" placeholder="UUID del diagnóstico" /></div>
            <div class="form-group"><label class="form-label">ID del médico nefrólogo (opcional)</label><input v-model="nuevoPaciente.medico_nefrologo_id" class="input-clinical" placeholder="UUID del empleado" /></div>
            <div class="form-group"><label class="form-label">Acceso vascular</label>
              <select v-model="nuevoPaciente.acceso_vascular_tipo" class="input-clinical">
                <option value="FAV">Fístula arteriovenosa (FAV)</option><option value="CATETER_VENOSO_CENTRAL">Catéter venoso central</option><option value="INJERTO">Injerto</option>
              </select>
            </div>
            <div class="form-group"><label class="form-label">Fecha de creación del acceso</label><input v-model="nuevoPaciente.fecha_creacion_acceso" type="date" class="input-clinical" /></div>
            <div class="form-group"><label class="form-label">Peso seco (kg)</label><input v-model.number="nuevoPaciente.peso_seco_kg" type="number" step="0.1" class="input-clinical" required /></div>
            <div class="form-group"><label class="form-label">Turno habitual</label>
              <select v-model="nuevoPaciente.turno_habitual" class="input-clinical"><option value="MAÑANA">Mañana</option><option value="TARDE">Tarde</option><option value="NOCHE">Noche</option></select>
            </div>
            <div class="form-group"><label class="form-label">Frecuencia semanal</label><input v-model.number="nuevoPaciente.frecuencia_semanal" type="number" min="1" max="7" class="input-clinical" /></div>
            <div class="form-group full-width"><label class="form-label">Observaciones</label><textarea v-model="nuevoPaciente.observaciones" class="input-clinical" rows="2"></textarea></div>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-check" class="w-4 h-4" />Inscribir</button></div>
        </form>
      </section>

      <section class="panel search-panel">
        <div class="search-actions" style="justify-content:flex-start">
          <button v-for="e in ['', 'activo', 'transferido', 'trasplantado', 'fallecido', 'alta']" :key="e" class="btn-secondary btn-sm" :class="{ 'btn-active': filtroEstado === e }" @click="filtroEstado = e; cargarPacientes()">{{ e || 'Todos' }}</button>
        </div>
      </section>

      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <section v-else class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ pacientes.length }} pacientes</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Paciente</th><th>Diagnóstico</th><th>Acceso</th><th>Peso seco</th><th>Turno</th><th>Últ. sesión</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              <tr v-for="p in pacientes" :key="p.id">
                <td>{{ p.paciente_nombre }} <span class="field-hint">({{ p.paciente_dni }})</span></td>
                <td>{{ p.diagnostico || '—' }}</td>
                <td>{{ p.acceso_vascular_tipo.replaceAll('_',' ') }}</td>
                <td>{{ p.peso_seco_kg }} kg</td>
                <td>{{ p.turno_habitual }} · {{ p.frecuencia_semanal }}x/sem</td>
                <td>{{ p.ultima_sesion_completada || '—' }}</td>
                <td><span class="badge" :class="p.estado === 'activo' ? 'badge-ok' : 'badge-off'">{{ p.estado }}</span></td>
                <td><button v-if="p.estado === 'activo'" class="btn-secondary btn-sm" :disabled="busy" @click="cambiarEstadoPaciente(p)"><UIcon name="i-heroicons-arrow-path-rounded-square" class="w-4 h-4" />Cambiar estado</button></td>
              </tr>
              <tr v-if="!pacientes.length"><td colspan="8" style="text-align:center;color:var(--ink-soft)">Sin pacientes en el programa.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>

    <!-- ═══════════ SESIONES ═══════════ -->
    <template v-else>
      <section class="panel">
        <div class="card-header-row"><h2 class="results-title">Programar sesión</h2></div>
        <form class="editor-form" @submit.prevent="crearSesion">
          <div class="form-grid">
            <div class="form-group full-width"><label class="form-label">Paciente del programa</label>
              <select v-model="nuevaSesion.paciente_hemodialisis_id" class="input-clinical" required>
                <option value="" disabled>Seleccione un paciente activo</option>
                <option v-for="p in pacientesActivos" :key="p.id" :value="p.id">{{ p.paciente_nombre }} ({{ p.paciente_dni }})</option>
              </select>
            </div>
            <div class="form-group"><label class="form-label">Turno</label>
              <select v-model="nuevaSesion.turno" class="input-clinical"><option value="MAÑANA">Mañana</option><option value="TARDE">Tarde</option><option value="NOCHE">Noche</option></select>
            </div>
            <div class="form-group"><label class="form-label">N.° de máquina</label><input v-model="nuevaSesion.numero_maquina" class="input-clinical" /></div>
            <div class="form-group"><label class="form-label">Hora de inicio</label><input v-model="nuevaSesion.hora_inicio" type="time" class="input-clinical" /></div>
            <div class="form-group"><label class="form-label">Peso pre-sesión (kg)</label><input v-model.number="nuevaSesion.peso_pre_kg" type="number" step="0.1" class="input-clinical" /></div>
            <div class="form-group"><label class="form-label">PA sistólica pre</label><input v-model.number="nuevaSesion.presion_pre_sistolica" type="number" class="input-clinical" /></div>
            <div class="form-group"><label class="form-label">PA diastólica pre</label><input v-model.number="nuevaSesion.presion_pre_diastolica" type="number" class="input-clinical" /></div>
            <label class="check-field" style="align-self:end"><input type="checkbox" v-model="nuevaSesion.heparinizacion" /> Con heparinización</label>
          </div>
          <div class="form-actions"><button class="btn-primary" :disabled="busy || !pacientesActivos.length"><UIcon name="i-heroicons-check" class="w-4 h-4" />Programar</button></div>
          <p v-if="!pacientesActivos.length" class="field-hint">Inscriba primero pacientes activos en Hemodialis.</p>
        </form>
      </section>

      <section class="panel search-panel">
        <div class="search-grid">
          <div class="search-field"><label class="form-label">Fecha</label><input v-model="filtroFecha" type="date" class="input-clinical" /></div>
          <div class="search-field"><label class="form-label">Estado</label>
            <select v-model="filtroEstadoSesion" class="input-clinical">
              <option value="">Todos</option>
              <option v-for="e in ['programada','en_curso','completada','suspendida','no_asistio']" :key="e" :value="e">{{ e }}</option>
            </select>
          </div>
        </div>
        <div class="search-actions"><button class="btn-primary" @click="cargarSesiones"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button></div>
      </section>

      <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
      <section v-else class="panel results-panel">
        <div class="results-header"><h2 class="results-title">{{ sesiones.length }} sesiones</h2></div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Fecha</th><th>Paciente</th><th>Turno</th><th>Peso pre/post</th><th>UF (L)</th><th>Complicaciones</th><th>Estado</th><th></th></tr></thead>
            <tbody>
              <tr v-for="s in sesiones" :key="s.id">
                <td>{{ s.fecha }}</td><td>{{ s.paciente_nombre }} <span class="field-hint">({{ s.paciente_dni }})</span></td><td>{{ s.turno }}</td>
                <td>{{ s.peso_pre_kg ?? '—' }} / {{ s.peso_post_kg ?? '—' }}</td>
                <td>{{ s.ultrafiltracion_litros ?? '—' }}</td>
                <td>{{ s.complicaciones || '—' }}</td>
                <td><span class="badge" :class="s.estado === 'completada' ? 'badge-ok' : s.estado === 'suspendida' || s.estado === 'no_asistio' ? 'badge-off' : 'badge-pendiente'">{{ s.estado }}</span></td>
                <td>
                  <button v-if="s.estado === 'programada'" class="btn-secondary btn-sm" :disabled="busy" @click="cambiarEstadoSesion(s, 'en_curso')">Iniciar</button>
                  <button v-if="s.estado === 'programada'" class="btn-secondary btn-sm" :disabled="busy" @click="cambiarEstadoSesion(s, 'no_asistio')">No asistió</button>
                  <button v-if="s.estado === 'en_curso'" class="btn-secondary btn-sm" :disabled="busy" @click="completarSesion(s)">Completar</button>
                  <button v-if="s.estado === 'programada' || s.estado === 'en_curso'" class="btn-secondary btn-sm" :disabled="busy" @click="cambiarEstadoSesion(s, 'suspendida')">Suspender</button>
                </td>
              </tr>
              <tr v-if="!sesiones.length"><td colspan="8" style="text-align:center;color:var(--ink-soft)">Sin sesiones registradas.</td></tr>
            </tbody>
          </table>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'hemodialis' | 'sesiones'
const props = defineProps<{ mode: Mode }>()
const { api } = useApi()
const endpoint = '/app/hemodialisis'

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

// Hemodialis
const pacientes = ref<any[]>([])
const filtroEstado = ref('')
const nuevoPaciente = reactive({
  patient_id: '', diagnostico_id: '', medico_nefrologo_id: '', acceso_vascular_tipo: 'FAV',
  fecha_creacion_acceso: '', peso_seco_kg: null, turno_habitual: 'MAÑANA', frecuencia_semanal: 3, observaciones: '',
})
const pacientesActivos = computed(() => pacientes.value.filter(p => p.estado === 'activo'))

async function cargarPacientes() {
  loading.value = true; error.value = ''
  try {
    pacientes.value = await api(endpoint + '/hemodialis', { query: filtroEstado.value ? { estado: filtroEstado.value } : {} })
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function crearPaciente() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/hemodialis', { method: 'POST', body: {
      ...nuevoPaciente,
      diagnostico_id: nuevoPaciente.diagnostico_id || undefined,
      medico_nefrologo_id: nuevoPaciente.medico_nefrologo_id || undefined,
      fecha_creacion_acceso: nuevoPaciente.fecha_creacion_acceso || undefined,
      observaciones: nuevoPaciente.observaciones || undefined,
    } })
    notice.value = 'Paciente inscrito en el programa.'
    Object.assign(nuevoPaciente, { patient_id: '', diagnostico_id: '', medico_nefrologo_id: '', acceso_vascular_tipo: 'FAV',
      fecha_creacion_acceso: '', peso_seco_kg: null, turno_habitual: 'MAÑANA', frecuencia_semanal: 3, observaciones: '' })
    await cargarPacientes()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function cambiarEstadoPaciente(p: any) {
  const estado = prompt('Nuevo estado (transferido, trasplantado, fallecido, alta):')
  if (!estado) return
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/hemodialis/' + p.id + '/estado', { method: 'POST', body: { estado } })
    notice.value = 'Estado actualizado.'
    await cargarPacientes()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

// Sesiones
const sesiones = ref<any[]>([])
const filtroFecha = ref('')
const filtroEstadoSesion = ref('')
const nuevaSesion = reactive({
  paciente_hemodialisis_id: '', turno: 'MAÑANA', numero_maquina: '', hora_inicio: '',
  peso_pre_kg: null, presion_pre_sistolica: null, presion_pre_diastolica: null, heparinizacion: true,
})

async function cargarSesiones() {
  loading.value = true; error.value = ''
  try {
    const query: any = {}
    if (filtroFecha.value) query.fecha = filtroFecha.value
    if (filtroEstadoSesion.value) query.estado = filtroEstadoSesion.value
    sesiones.value = await api(endpoint + '/sesiones', { query })
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function crearSesion() {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/sesiones', { method: 'POST', body: {
      ...nuevaSesion,
      numero_maquina: nuevaSesion.numero_maquina || undefined,
      hora_inicio: nuevaSesion.hora_inicio || undefined,
    } })
    notice.value = 'Sesión programada.'
    Object.assign(nuevaSesion, { paciente_hemodialisis_id: '', turno: 'MAÑANA', numero_maquina: '', hora_inicio: '',
      peso_pre_kg: null, presion_pre_sistolica: null, presion_pre_diastolica: null, heparinizacion: true })
    await cargarSesiones()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function cambiarEstadoSesion(s: any, estado: string) {
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/sesiones/' + s.id + '/estado', { method: 'POST', body: { estado } })
    notice.value = 'Sesión actualizada.'
    await cargarSesiones()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function completarSesion(s: any) {
  const pesoStr = prompt('Peso post-sesión (kg):')
  if (pesoStr === null) return
  const peso_post_kg = parseFloat(pesoStr)
  const complicaciones = prompt('Complicaciones (dejar vacío si ninguna):') || undefined
  busy.value = true; error.value = ''; notice.value = ''
  try {
    await api(endpoint + '/sesiones/' + s.id + '/estado', { method: 'POST', body: {
      estado: 'completada', peso_post_kg: isNaN(peso_post_kg) ? undefined : peso_post_kg, complicaciones,
    } })
    notice.value = 'Sesión completada.'
    await cargarSesiones()
  } catch (e) { error.value = err(e) } finally { busy.value = false }
}

onMounted(async () => {
  if (props.mode === 'hemodialis') await cargarPacientes()
  else {
    await Promise.all([cargarPacientes(), cargarSesiones()])
  }
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
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: 1rem; margin-bottom: 1rem; }
.search-field { display: flex; flex-direction: column; gap: 0.25rem; }
.search-actions { display: flex; gap: 0.5rem; flex-wrap: wrap; justify-content: flex-end; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); white-space: nowrap; }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; white-space: nowrap; }
.badge-ok { color: var(--green); background: var(--green-soft); }
.badge-off { color: var(--ink-soft); background: var(--mist); }
.badge-pendiente { color: var(--amber); background: var(--amber-soft); }
.editor-form { display: flex; flex-direction: column; gap: 1rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; }
.check-field { display: flex; align-items: center; gap: 0.5rem; font-size: 0.8125rem; color: var(--ink); }

@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .form-grid, .search-grid { grid-template-columns: 1fr; }
}
</style>
