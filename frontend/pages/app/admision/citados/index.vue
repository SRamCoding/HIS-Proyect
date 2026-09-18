<template>
  <div class="citados-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-calendar-days" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Pacientes Citados</h1>
          <p class="page-subtitle">Admisión · Agenda autorizada desde SIGARH</p>
        </div>
      </div>
      <button class="btn-primary" :disabled="!seleccionados.length" @click="abrirBloque">
        <UIcon name="i-heroicons-arrows-right-left" class="w-4 h-4" />
        Reprogramar bloque<template v-if="seleccionados.length"> ({{ seleccionados.length }})</template>
      </button>
    </div>

    <!-- Search Section -->
    <div class="search-section">
      <div class="search-card">
        <div class="search-header">
          <UIcon name="i-heroicons-magnifying-glass" class="search-header-icon" />
          <span class="search-header-title">Búsqueda</span>
        </div>
        <div class="search-body">
          <div class="filter-grid">
            <input v-model="filtros.dni" class="filter-input" placeholder="DNI" />
            <input v-model="filtros.cuenta" class="filter-input" placeholder="Cuenta" />
            <input v-model="filtros.historia" class="filter-input" placeholder="N.° historia" />
            <input v-model="filtros.apellido" class="filter-input" placeholder="Apellido" />
            <input v-model="filtros.desde" type="date" class="filter-input" />
            <input v-model="filtros.hasta" type="date" class="filter-input" />
            <select v-model="filtros.medico" class="filter-input">
              <option value="">Todos los médicos</option>
              <option v-for="m in medicos" :key="m.nombre" :value="m.id">{{ m.nombre }}</option>
            </select>
            <select v-model="filtros.estado" class="filter-input">
              <option value="">Todos los estados</option>
              <option value="separada">Separada</option>
              <option value="confirmada">Confirmada</option>
              <option value="atendida">Atendida</option>
              <option value="cancelada">Cancelada</option>
              <option value="no_asistio">No asistió</option>
            </select>
          </div>
          <div class="search-actions">
            <button class="btn-clear" @click="limpiar">
              <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />
              Limpiar
            </button>
            <button class="btn-search" :disabled="cargando" @click="cargar">
              <UIcon v-if="cargando" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
              <UIcon v-else name="i-heroicons-magnifying-glass" class="w-4 h-4" />
              {{ cargando ? 'Buscando...' : 'Buscar' }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Loading State -->
    <div v-if="cargando && !citas.length" class="loading-state">
      <div class="loading-spinner">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
      </div>
      <p style="color: var(--ink-soft)">Cargando citas...</p>
    </div>

    <!-- Results Table -->
    <div v-if="!cargando && citas.length" class="table-card">
      <div class="table-header">
        <div class="table-header-left">
          <span class="table-title">Listado de citados</span>
          <span class="table-count">{{ citas.length }} resultado{{ citas.length === 1 ? '' : 's' }}</span>
        </div>
      </div>
      <div class="table-responsive">
        <table class="citados-table">
          <thead>
            <tr>
              <th class="col-check"><input type="checkbox" :checked="todos" @change="marcarTodos" /></th>
              <th><span class="th-content">Ticket</span></th>
              <th><span class="th-content">HC</span></th>
              <th><span class="th-content">Cuenta</span></th>
              <th><span class="th-content">Paciente</span></th>
              <th><span class="th-content">Teléfono</span></th>
              <th><span class="th-content">Fecha</span></th>
              <th><span class="th-content">Hora</span></th>
              <th><span class="th-content">Seguro</span></th>
              <th><span class="th-content">Especialidad</span></th>
              <th><span class="th-content">Servicio</span></th>
              <th><span class="th-content">Modalidad</span></th>
              <th><span class="th-content">Médico</span></th>
              <th><span class="th-content">Estado</span></th>
              <th class="col-actions"><span class="th-content">Acción</span></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="c in citas" :key="c.id" class="table-row" :class="{ selected: seleccionados.includes(c.id) }">
              <td class="col-check">
                <input v-model="seleccionados" type="checkbox" :value="c.id" :disabled="['atendida','cancelada'].includes(c.estado)" />
              </td>
              <td class="font-mono-data muted">{{ ticket(c.id) }}</td>
              <td class="font-mono-data muted">{{ c.paciente_record || '—' }}</td>
              <td class="font-mono-data muted">{{ c.numero_cuenta || '—' }}</td>
              <td><span class="name-text">{{ c.paciente_nombre }}</span></td>
              <td class="muted">{{ c.paciente_telefono || '—' }}</td>
              <td class="muted">{{ fecha(c.fecha) }}</td>
              <td class="font-mono-data muted">{{ c.hora_inicio }}</td>
              <td class="muted">{{ c.paciente_insurance || c.fuente_financiamiento || '—' }}</td>
              <td class="muted">{{ c.especialidad_nombre || '—' }}</td>
              <td class="muted">{{ c.servicio_nombre || '—' }}</td>
              <td class="muted">{{ c.tipo_consulta || 'PRESENCIAL' }}</td>
              <td class="muted">{{ c.medico_nombre || '—' }}</td>
              <td><span class="badge" :class="badgeClase(c.estado)">{{ estado(c.estado) }}</span></td>
              <td class="col-actions">
                <div class="action-buttons">
                  <button class="action-btn action-view" title="Detalle" @click="ver(c)">
                    <UIcon name="i-heroicons-eye" class="w-4 h-4" />
                  </button>
                  <button class="action-btn action-print" title="Imprimir cita" @click="imprimir(c.id)">
                    <UIcon name="i-heroicons-printer" class="w-4 h-4" />
                  </button>
                  <button
                    v-if="!['atendida','cancelada'].includes(c.estado)"
                    class="action-btn action-edit"
                    title="Reprogramar"
                    @click="abrirReprogramar(c)"
                  >
                    <UIcon name="i-heroicons-calendar-days" class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="!cargando" class="empty-state">
      <div class="empty-icon" style="background: var(--mist)">
        <UIcon name="i-heroicons-calendar-days" class="w-12 h-12" style="color: var(--ink-soft)" />
      </div>
      <h3 style="color: var(--ink)">No se encontraron citas</h3>
      <p style="color: var(--ink-soft)">No hay citas que coincidan con los filtros indicados.</p>
    </div>

    <!-- Modal: Detalle -->
    <div v-if="modalDetalle" class="overlay" @click.self="modalDetalle = false">
      <section class="modal detail-modal">
        <header>
          <h2>Detalle de la cita</h2>
          <button class="modal-close" @click="modalDetalle = false">×</button>
        </header>
        <div class="detail-grid">
          <div><b>Paciente</b><span>{{ actual.paciente_nombre }}</span></div>
          <div><b>N.° cuenta</b><span>{{ actual.numero_cuenta || '—' }}</span></div>
          <div><b>DNI</b><span>{{ actual.paciente_dni || '—' }}</span></div>
          <div><b>Historia clínica</b><span>{{ actual.paciente_record || '—' }}</span></div>
          <div><b>Especialidad</b><span>{{ actual.especialidad_nombre || '—' }}</span></div>
          <div><b>Servicio</b><span>{{ actual.servicio_nombre || '—' }}</span></div>
          <div><b>Médico</b><span>{{ actual.medico_nombre || '—' }}</span></div>
          <div><b>Fecha y hora</b><span>{{ fecha(actual.fecha) }} {{ actual.hora_inicio }}</span></div>
          <div><b>Seguro</b><span>{{ actual.paciente_insurance || actual.fuente_financiamiento || '—' }}</span></div>
          <div><b>Estado</b><span>{{ estado(actual.estado) }}</span></div>
        </div>
        <footer>
          <button class="btn-secondary" @click="modalDetalle = false">Cerrar</button>
          <button class="btn-primary" @click="imprimir(actual.id)">
            <UIcon name="i-heroicons-printer" class="w-4 h-4" /> Imprimir cita
          </button>
        </footer>
      </section>
    </div>

    <!-- Modal: Reprogramar -->
    <div v-if="modalReprogramar" class="overlay" @click.self="cerrarReprogramar">
      <section class="modal">
        <header>
          <div>
            <h2>{{ modoBloque ? 'Reprogramación en bloque' : 'Reprogramación de cita' }}</h2>
            <p v-if="modoBloque">{{ seleccionados.length }} pacientes seleccionados</p>
          </div>
          <button class="modal-close" @click="cerrarReprogramar">×</button>
        </header>

        <div v-if="!modoBloque" class="current-card">
          <b>{{ actual.paciente_nombre }}</b>
          <span>{{ fecha(actual.fecha) }} · {{ actual.hora_inicio }} · {{ actual.medico_nombre }}</span>
        </div>

        <label class="field-label">Fecha destino *</label>
        <input v-model="reprog.fecha" type="date" class="filter-input full" @change="cargarProgramaciones" />

        <label class="field-label">Programación autorizada en SIGARH *</label>
        <select v-model="reprog.programacion" class="filter-input full" @change="cargarCupos">
          <option value="">Seleccione médico, especialidad y turno</option>
          <option v-for="p in programaciones" :key="p.id" :value="p.id">
            {{ p.medico_nombre }} · {{ p.especialidad_nombre || p.servicio_nombre }} · {{ p.turno }} {{ p.hora_inicio }}-{{ p.hora_fin }}
          </option>
        </select>

        <template v-if="!modoBloque">
          <label class="field-label">Cupo libre *</label>
          <select v-model="reprog.cupo" class="filter-input full">
            <option value="">Seleccione hora</option>
            <option v-for="c in cupos" :key="c.hora_inicio" :value="`${c.hora_inicio}|${c.hora_fin}`">
              {{ c.hora_inicio }} - {{ c.hora_fin }}
            </option>
          </select>
        </template>
        <p v-else class="hint">Se asignarán consecutivamente los primeros {{ seleccionados.length }} cupos libres de la programación.</p>

        <label class="field-label">Mensaje para el paciente</label>
        <textarea v-model="reprog.mensaje" class="filter-input full textarea" maxlength="500" rows="3" />

        <div v-if="modalError" class="error-banner compact">{{ modalError }}</div>

        <footer>
          <button class="btn-secondary" @click="cerrarReprogramar">Cancelar</button>
          <button class="btn-primary" :disabled="guardando" @click="guardarReprogramacion">
            {{ guardando ? 'Reprogramando...' : 'Reprogramar' }}
          </button>
        </footer>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: ['auth'] })
const { api } = useApi(); const { abrirComprobante } = useCitaPdf(); const hoy = new Date().toISOString().slice(0, 10)
const filtros = reactive({ dni:'', cuenta:'', historia:'', apellido:'', desde:hoy, hasta:hoy, medico:'', estado:'' })
const citas=ref<any[]>([]), seleccionados=ref<string[]>([]), cargando=ref(false), error=ref(''), medicos=ref<any[]>([])
const modalDetalle=ref(false), modalReprogramar=ref(false), modoBloque=ref(false), actual=ref<any>({}), programaciones=ref<any[]>([]), cupos=ref<any[]>([]), guardando=ref(false), modalError=ref('')
const reprog=reactive({ fecha:hoy, programacion:'', cupo:'', mensaje:'' })
const elegibles=computed(()=>citas.value.filter(c=>!['atendida','cancelada'].includes(c.estado))); const todos=computed(()=>elegibles.value.length>0&&elegibles.value.every(c=>seleccionados.value.includes(c.id)))
const ticket=(id:string)=>id?.split('-')[0].toUpperCase(); const fecha=(v:string)=>v?new Date(`${v}T12:00:00`).toLocaleDateString('es-PE'):'—'; const estado=(v:string)=>({separada:'Separada',confirmada:'Confirmada',atendida:'Atendida',cancelada:'Cancelada',no_asistio:'No asistió'} as any)[v]||v
const badgeClase=(v:string)=>({separada:'badge--warn',confirmada:'badge--info',atendida:'badge--ok',cancelada:'badge--alert',no_asistio:'badge--neutral'} as any)[v]||'badge--neutral'
function marcarTodos(e:any){seleccionados.value=e.target.checked?elegibles.value.map(c=>c.id):[]} function ver(c:any){actual.value=c;modalDetalle.value=true} async function imprimir(id:string){try{await abrirComprobante(id)}catch(e:any){error.value=e?.data?.detail||'No se pudo generar el PDF'}}
async function cargar(){cargando.value=true;error.value='';try{const q=new URLSearchParams();Object.entries({fecha_desde:filtros.desde,fecha_hasta:filtros.hasta,dni:filtros.dni,cuenta:filtros.cuenta,historia:filtros.historia,apellido:filtros.apellido,medico_id:filtros.medico,estado:filtros.estado}).forEach(([k,v])=>v&&q.set(k,v));citas.value=await api(`/app/consulta-externa/citas?${q}`);const map=new Map();citas.value.forEach(c=>c.medico_nombre&&map.set(c.medico_nombre,{id:c.medico_id,nombre:c.medico_nombre}));medicos.value=[...map.values()];seleccionados.value=[]}catch(e:any){error.value=e?.data?.detail||'No se pudieron cargar los citados'}finally{cargando.value=false}}
function limpiar(){Object.assign(filtros,{dni:'',cuenta:'',historia:'',apellido:'',desde:hoy,hasta:hoy,medico:'',estado:''});cargar()} function preparar(){Object.assign(reprog,{fecha:hoy,programacion:'',cupo:'',mensaje:''});programaciones.value=[];cupos.value=[];modalError.value='';modalReprogramar.value=true}
function abrirReprogramar(c:any){actual.value=c;modoBloque.value=false;preparar();reprog.fecha=c.fecha||hoy;cargarProgramaciones()} function abrirBloque(){modoBloque.value=true;preparar();cargarProgramaciones()} function cerrarReprogramar(){modalReprogramar.value=false}
async function cargarProgramaciones(){reprog.programacion='';reprog.cupo='';cupos.value=[];if(!reprog.fecha)return;try{programaciones.value=await api(`/app/consulta-externa/programacion-medica?fecha=${reprog.fecha}`)}catch{modalError.value='No se pudo cargar la programación SIGARH'}} async function cargarCupos(){reprog.cupo='';if(!reprog.programacion)return;try{cupos.value=(await api(`/app/consulta-externa/citas/cupos/${reprog.programacion}`)).filter((c:any)=>c.disponible)}catch{modalError.value='No se pudieron cargar los cupos'}}
async function guardarReprogramacion(){modalError.value='';if(!reprog.programacion||(!modoBloque.value&&!reprog.cupo)){modalError.value='Selecciona una programación y un cupo libre';return}guardando.value=true;try{if(modoBloque.value){await api('/app/consulta-externa/citas/acciones/reprogramar-bloque',{method:'POST',body:{cita_ids:seleccionados.value,programacion_medica_id:reprog.programacion,mensaje:reprog.mensaje||null}})}else{const [inicio,fin]=reprog.cupo.split('|');await api(`/app/consulta-externa/citas/${actual.value.id}/reprogramar`,{method:'POST',body:{programacion_medica_id:reprog.programacion,hora_inicio:inicio,hora_fin:fin,mensaje:reprog.mensaje||null}})}modalReprogramar.value=false;await cargar()}catch(e:any){modalError.value=e?.data?.detail||'No se pudo reprogramar'}finally{guardando.value=false}} onMounted(cargar)
</script>

<style scoped>
.citados-container {
  max-width: 1900px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

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
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover:not(:disabled) {
  background: var(--teal-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
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

/* Search Section */
.search-section {
  margin-bottom: 1.5rem;
}

.search-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  overflow: hidden;
}

.search-header {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.75rem 1.25rem;
  background: var(--teal);
}

.search-header-icon {
  width: 1.25rem;
  height: 1.25rem;
  color: white;
}

.search-header-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
}

.search-body {
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 0.75rem;
}

.filter-input {
  width: 100%;
  height: 2.5rem;
  padding: 0 0.875rem;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.filter-input.full {
  margin-bottom: 0;
}

.filter-input.textarea {
  height: auto;
  padding: 0.625rem 0.875rem;
  resize: vertical;
  font-family: inherit;
}

.filter-input:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.search-actions {
  display: flex;
  gap: 0.625rem;
  justify-content: flex-end;
}

.btn-clear {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-clear:hover {
  background: var(--mist);
}

.btn-search {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1.25rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-search:hover:not(:disabled) {
  background: var(--teal-dark);
}

.btn-search:disabled {
  opacity: 0.6;
  cursor: not-allowed;
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
  margin-bottom: 1.5rem;
}

.error-banner.compact {
  margin: 0.75rem 0 0;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* Table Card */
.table-card {
  background: var(--paper);
  border-radius: var(--radius-lg);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-card);
  overflow: hidden;
}

.table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid var(--line);
}

.table-header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.table-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--ink);
}

.table-count {
  font-size: 0.75rem;
  color: var(--ink-soft);
  background: var(--mist);
  padding: 0.125rem 0.5rem;
  border-radius: 12px;
}

.table-responsive {
  overflow-x: auto;
}

.citados-table {
  width: 100%;
  min-width: 1500px;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.citados-table thead {
  background: var(--mist);
}

.citados-table th {
  padding: 0.75rem 0.875rem;
  text-align: left;
  font-weight: 600;
  color: var(--ink-soft);
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--line);
  white-space: nowrap;
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.citados-table td {
  padding: 0.75rem 0.875rem;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
}

.col-check {
  width: 2.5rem;
}

.col-actions {
  width: 8%;
  text-align: right;
}

.table-row {
  transition: background 0.15s ease;
}

.table-row:hover {
  background: var(--mist);
}

.table-row.selected {
  background: var(--teal-soft);
}

.name-text {
  font-weight: 500;
  color: var(--ink);
}

.muted {
  color: var(--ink-soft);
}

/* Badges */
.badge--info {
  background: var(--navy-soft);
  color: var(--navy);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.25rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
  text-decoration: none;
}

.action-btn:hover {
  background: var(--mist);
}

.action-view:hover {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
}

.action-print:hover {
  color: var(--navy);
  border-color: var(--navy-soft);
  background: var(--navy-soft);
}

.action-edit:hover {
  color: var(--amber);
  border-color: var(--amber-soft);
  background: var(--amber-soft);
}

/* Empty State */
.empty-state {
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

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-state h3 {
  font-size: 1.125rem;
  margin: 0;
}

.empty-state p {
  margin: 0;
}

/* Modals */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(16, 28, 36, 0.55);
  z-index: 1000;
  display: grid;
  place-items: center;
  padding: 20px;
}

.modal {
  background: var(--paper);
  border-radius: var(--radius-lg);
  width: min(720px, 96vw);
  max-height: 90vh;
  overflow: auto;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.modal header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  border-bottom: 1px solid var(--line);
  padding-bottom: 1rem;
  margin-bottom: 1.25rem;
}

.modal h2 {
  font-size: 1.125rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
}

.modal header p {
  color: var(--ink-soft);
  font-size: 0.8125rem;
  margin: 0.25rem 0 0;
}

.modal-close {
  font-size: 1.5rem;
  line-height: 1;
  color: var(--ink-soft);
  background: none;
  border: none;
  cursor: pointer;
}

.field-label {
  display: block;
  font-weight: 600;
  font-size: 0.8125rem;
  color: var(--ink);
  margin: 0.875rem 0 0.375rem;
}

.modal footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.625rem;
  margin-top: 1.5rem;
}

.detail-modal {
  width: min(900px, 96vw);
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1px;
  background: var(--line);
  border: 1px solid var(--line);
  border-radius: 8px;
  overflow: hidden;
}

.detail-grid div {
  background: var(--paper);
  padding: 0.875rem;
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 0.625rem;
}

.detail-grid b {
  font-size: 0.6875rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--ink-soft);
}

.current-card {
  display: flex;
  flex-direction: column;
  background: var(--teal-soft);
  border-radius: 8px;
  padding: 0.875rem;
}

.current-card span,
.hint {
  color: var(--ink-soft);
  font-size: 0.8125rem;
  margin-top: 0.25rem;
}

/* Responsive */
@media (max-width: 1100px) {
  .filter-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .citados-container {
    padding: 1rem 1.5rem;
  }
}

@media (max-width: 768px) {
  .citados-container {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-header .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .search-actions {
    flex-direction: column;
  }

  .btn-clear,
  .btn-search {
    justify-content: center;
  }

  .filter-grid,
  .detail-grid {
    grid-template-columns: 1fr;
  }

  .detail-grid div {
    grid-template-columns: 1fr;
  }
}
</style>
