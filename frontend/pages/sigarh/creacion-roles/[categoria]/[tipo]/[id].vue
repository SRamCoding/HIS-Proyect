<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const { modalidadLabel, periodoLabel, estadoRol, DIAS_SEMANA } = useRolesTurno()
const tenantId = computed(() => route.query.tenant as string || '')
const categoria = computed(() => route.params.categoria as string)
const tipo = computed(() => route.params.tipo as string)
const id = computed(() => route.params.id as string)

const rol = ref<any>(null)
const diag = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const busy = ref(false)

const diagErrores = computed(() => diag.value.filter((d: any) => d.nivel === 'error'))
const diagAdvertencias = computed(() => diag.value.filter((d: any) => d.nivel === 'advertencia'))
const cargarDiag = async () => {
  diag.value = await api<any[]>(`/sigarh/creacion-roles/roles/${id.value}/diagnostico`).catch(() => [])
}

const personalDisp = ref<any[]>([])
const actividades = ref<any[]>([])
const horarios = ref<any[]>([])

const editable = computed(() => rol.value && ['draft', 'rejected'].includes(rol.value.status))
const completo = computed(() =>
  rol.value?.empleados?.length &&
  rol.value.empleados.every((e: any) => e.actividades?.length && e.actividades.every((a: any) => a.turnos?.length)))

const pasos = computed(() => {
  if (!rol.value) return [] as { label: string; done: boolean }[]
  const e = rol.value.empleados || []
  const conAct = e.length > 0 && e.every((x: any) => x.actividades?.length)
  const conTur = conAct && e.every((x: any) => x.actividades.every((a: any) => a.turnos?.length))
  const enviado = !['draft', 'rejected'].includes(rol.value.status)
  return [
    { label: 'Ámbito y período definidos', done: true },
    { label: 'Personal agregado', done: e.length > 0 },
    { label: 'Actividades asignadas', done: !!conAct },
    { label: 'Turnos definidos', done: !!conTur },
    { label: 'Enviado a revisión', done: enviado },
  ]
})
const progreso = computed(() => {
  const p = pasos.value
  return p.length ? Math.round(p.filter(x => x.done).length / p.length * 100) : 0
})
const empleadosIncompletos = computed(() =>
  (rol.value?.empleados || []).filter((e: any) => !e.actividades?.length || e.actividades.some((a: any) => !a.turnos?.length)).length)

// ── Modales ──
const showPersonal = ref(false)
const actModal = reactive<{ open: boolean; empId: string; empNombre: string }>({ open: false, empId: '', empNombre: '' })
const turnoModal = reactive<{ open: boolean; raId: string; actNombre: string; requiereConsultorio: boolean; horario_guardia_id: string; dias: number[] }>(
  { open: false, raId: '', actNombre: '', requiereConsultorio: false, horario_guardia_id: '', dias: [] })

const personalOpciones = computed(() => {
  const ya = new Set((rol.value?.empleados || []).map((e: any) => e.empleado_id))
  return personalDisp.value.filter(p => !ya.has(p.id)).map(p => ({ id: p.id, label: p.nombre_completo, sublabel: `DNI ${p.dni}${p.cargo_laboral ? ' · ' + p.cargo_laboral : ''}` }))
})
const actividadOpciones = (emp: any) => {
  const ya = new Set((emp?.actividades || []).map((a: any) => a.actividad_id))
  return actividades.value.filter(a => !ya.has(a.id)).map(a => ({
    id: a.id, label: a.nombre, sublabel: a.codigo || '', badge: a.requiere_consultorio ? 'Consultorio' : undefined,
  }))
}
const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    const data = await api<any>(`/sigarh/creacion-roles/roles/${id.value}`)
    rol.value = data
    const [pd, acts, hors] = await Promise.all([
      api<any[]>(`/sigarh/creacion-roles/personal-disponible?servicio_id=${data.servicio_id || ''}`).catch(() => []),
      api<any[]>('/sigarh/mantenimiento/actividades').catch(() => []),
      api<any[]>('/sigarh/mantenimiento/horarios-guardia').catch(() => []),
    ])
    personalDisp.value = pd
    actividades.value = acts.filter((a: any) => a.is_active)
    horarios.value = hors.filter((h: any) => h.is_active)
    await cargarDiag()
  } catch (e: any) { error.value = apiErr(e, 'No se pudo cargar el rol') }
  finally { loading.value = false }
}

const run = async (fn: () => Promise<any>) => {
  busy.value = true; error.value = ''
  try { rol.value = await fn(); await cargarDiag() }
  catch (e: any) { error.value = apiErr(e, 'Operación no permitida') }
  finally { busy.value = false }
}

const onPersonal = (ids: string[]) =>
  run(() => api(`/sigarh/creacion-roles/roles/${id.value}/personal`, { method: 'POST', body: { empleado_ids: ids } }))
const quitarPersonal = (rid: string) => {
  if (!confirm('¿Quitar a este empleado del rol?')) return
  run(() => api(`/sigarh/creacion-roles/roles/personal/${rid}`, { method: 'DELETE' }))
}

const abrirActividades = (emp: any) => { actModal.open = true; actModal.empId = emp.id; actModal.empNombre = emp.empleado_nombre }
const onActividades = (ids: string[]) =>
  run(() => api(`/sigarh/creacion-roles/roles/personal/${actModal.empId}/actividades`, { method: 'POST', body: { actividad_ids: ids } }))
const quitarActividad = (raId: string) => run(() => api(`/sigarh/creacion-roles/roles/actividades/${raId}`, { method: 'DELETE' }))

const abrirTurno = (act: any) => {
  Object.assign(turnoModal, {
    open: true, raId: act.id, actNombre: act.actividad_nombre,
    requiereConsultorio: !!act.requiere_consultorio, horario_guardia_id: '', dias: [],
  })
}
const toggleDiaTurno = (d: number) => {
  turnoModal.dias = turnoModal.dias.includes(d) ? turnoModal.dias.filter(x => x !== d) : [...turnoModal.dias, d]
}
const guardarTurno = () =>
  run(() => api(`/sigarh/creacion-roles/roles/actividades/${turnoModal.raId}/turnos`, {
    method: 'POST', body: { horario_guardia_id: turnoModal.horario_guardia_id || null, dias_semana: turnoModal.dias },
  })).then(() => { turnoModal.open = false })
const quitarTurno = (tId: string) => run(() => api(`/sigarh/creacion-roles/roles/turnos/${tId}`, { method: 'DELETE' }))

const enviar = async () => {
  if (diagErrores.value.length) { error.value = 'Corrige los errores del diagnóstico antes de enviar.'; return }
  if (!confirm('¿Enviar el rol a revisión? Ya no podrás editarlo salvo que sea rechazado.')) return
  busy.value = true; error.value = ''
  try {
    await api(`/sigarh/creacion-roles/roles/${id.value}/enviar`, { method: 'POST' })
    router.push(`/sigarh/creacion-roles/${categoria.value}/${tipo.value}?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo enviar') }
  finally { busy.value = false }
}

const iniciales = (n: string) => (n || '?').replace(',', '').split(/\s+/).filter(Boolean).slice(0, 2).map(w => w[0]).join('').toUpperCase()
const diasChip = (dias: number[]) => (dias || []).map(d => DIAS_SEMANA[d]?.label).filter(Boolean).join(' · ') || 'Sin días'
const horarioNombre = (hid: string) => horarios.value.find(h => h.id === hid)?.nombre || ''

onMounted(cargar)
</script>

<template>
  <div class="cr">
    <!-- Header -->
    <div class="cr-top">
      <div>
        <div class="cr-crumb">
          <NuxtLink :to="`/sigarh/creacion-roles/${categoria}/${tipo}?tenant=${tenantId}`">Roles</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span>Programación</span>
        </div>
        <div class="cr-title-row">
          <div class="cr-badge-icon"><UIcon name="i-heroicons-calendar-days" class="w-6 h-6" style="color: var(--navy)" /></div>
          <div>
            <h1>{{ rol ? (rol.servicio_nombre || 'Rol') : 'Rol' }}</h1>
            <p>{{ modalidadLabel(categoria, tipo) }}</p>
          </div>
        </div>
      </div>
      <div v-if="rol" class="cr-actions">
        <span class="badge" :class="estadoRol(rol.status).badge">{{ estadoRol(rol.status).label }}</span>
        <button v-if="editable" class="btn-primary" :disabled="busy || !completo || diagErrores.length > 0"
          :title="diagErrores.length ? 'Hay errores en el diagnóstico que impiden generar cupos' : (!completo ? 'Cada empleado necesita al menos una actividad y cada actividad al menos un turno' : '')"
          @click="enviar">
          <UIcon name="i-heroicons-paper-airplane" class="w-4 h-4" /> Enviar a revisión
        </button>
      </div>
    </div>

    <div v-if="loading" class="cr-card cr-center"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" /></div>

    <template v-else-if="rol">
      <div v-if="error" class="error-banner cr-mb">{{ error }}</div>

      <div v-if="editable && diagErrores.length" class="cr-diag cr-diag--error cr-mb">
        <div class="cr-diag-head"><UIcon name="i-heroicons-x-circle" class="w-4 h-4 shrink-0" /> {{ diagErrores.length }} problema(s) que impiden generar cupos en App Hospitalario</div>
        <ul><li v-for="(d, i) in diagErrores" :key="i">{{ d.mensaje }}</li></ul>
      </div>
      <div v-if="editable && diagAdvertencias.length" class="cr-diag cr-diag--warn cr-mb">
        <div class="cr-diag-head"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" /> {{ diagAdvertencias.length }} advertencia(s)</div>
        <ul><li v-for="(d, i) in diagAdvertencias" :key="i">{{ d.mensaje }}</li></ul>
      </div>

      <div v-if="rol.status === 'rejected' && rol.rejection_reason" class="cr-reject">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
        <div><strong>Rol rechazado.</strong> {{ rol.rejection_reason }}</div>
      </div>

      <div class="cr-grid">
        <!-- ─── Columna principal ─── -->
        <div class="cr-main">
          <!-- Ámbito -->
          <div class="cr-ambito">
            <div class="cr-amb-cell" style="--c: var(--navy); --cs: var(--navy-soft)">
              <div class="cr-amb-ic"><UIcon name="i-heroicons-building-office-2" class="w-4 h-4" /></div>
              <div><span>Departamento</span><b>{{ rol.departamento_nombre || '—' }}</b></div>
            </div>
            <div class="cr-amb-cell" style="--c: var(--teal); --cs: var(--teal-soft)">
              <div class="cr-amb-ic"><UIcon name="i-heroicons-squares-2x2" class="w-4 h-4" /></div>
              <div><span>Servicio</span><b>{{ rol.servicio_nombre || '—' }}</b></div>
            </div>
            <div class="cr-amb-cell" style="--c: var(--purple); --cs: var(--purple-soft)">
              <div class="cr-amb-ic"><UIcon name="i-heroicons-calendar" class="w-4 h-4" /></div>
              <div><span>Período de cobertura</span><b>{{ periodoLabel(rol.mes, rol.anio) }}</b></div>
            </div>
          </div>

          <!-- Progreso -->
          <div class="cr-progress">
            <div class="cr-prog-tiles">
              <div class="cr-tile" style="--c: var(--navy); --cs: var(--navy-soft)">
                <UIcon name="i-heroicons-users" class="w-5 h-5" />
                <div><b>{{ rol.total_empleados }}</b><span>Personal</span></div>
              </div>
              <div class="cr-tile" style="--c: var(--orange); --cs: var(--orange-soft)">
                <UIcon name="i-heroicons-bolt" class="w-5 h-5" />
                <div><b>{{ rol.total_actividades }}</b><span>Actividades</span></div>
              </div>
              <div class="cr-tile" style="--c: var(--purple); --cs: var(--purple-soft)">
                <UIcon name="i-heroicons-clock" class="w-5 h-5" />
                <div><b>{{ rol.total_turnos }}</b><span>Turnos</span></div>
              </div>
            </div>
            <div class="cr-prog-bar">
              <div class="cr-prog-fill" :style="{ width: progreso + '%', background: completo ? 'var(--green)' : 'var(--amber)' }" />
            </div>
            <div class="cr-prog-legend">
              <span :style="{ color: completo ? 'var(--green)' : 'var(--amber)', fontWeight: 600 }">{{ progreso }}% completado</span>
              <span v-if="!completo && rol.empleados.length" style="color: var(--ink-soft)">{{ empleadosIncompletos }} empleado(s) sin programación completa</span>
            </div>
          </div>

          <!-- Personal -->
          <div class="cr-section-head">
            <h2>Personal del rol</h2>
            <button v-if="editable" class="btn-primary btn-sm" @click="showPersonal = true">
              <UIcon name="i-heroicons-user-plus" class="w-4 h-4" /> Agregar personal
            </button>
          </div>

          <div v-if="!rol.empleados.length" class="cr-empty">
            <div class="cr-empty-ic"><UIcon name="i-heroicons-user-group" class="w-7 h-7" style="color: var(--navy)" /></div>
            <p><strong>Sin personal todavía</strong></p>
            <span>Agrega los empleados del servicio y luego asígnales actividades y turnos.</span>
            <button v-if="editable" class="btn-primary btn-sm" @click="showPersonal = true">
              <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Agregar personal
            </button>
          </div>

          <div v-for="emp in rol.empleados" :key="emp.id" class="cr-emp"
            :class="{ incompleto: editable && (!emp.actividades.length || emp.actividades.some((a:any) => !a.turnos.length)) }">
            <div class="cr-emp-head">
              <div class="cr-emp-id">
                <div class="cr-avatar">{{ iniciales(emp.empleado_nombre) }}</div>
                <div>
                  <div class="cr-emp-name">{{ emp.empleado_nombre || 'Empleado' }}</div>
                  <div class="cr-emp-dni">DNI {{ emp.dni || '—' }} · {{ emp.actividades.length }} actividad(es)</div>
                </div>
              </div>
              <div v-if="editable" class="cr-emp-btns">
                <button class="btn-outline btn-sm" @click="abrirActividades(emp)"><UIcon name="i-heroicons-plus" class="w-3.5 h-3.5" /> Actividades</button>
                <button class="cr-icon-btn danger" title="Quitar" @click="quitarPersonal(emp.id)"><UIcon name="i-heroicons-trash" class="w-4 h-4" /></button>
              </div>
            </div>

            <div v-if="!emp.actividades.length" class="cr-emp-empty">
              <UIcon name="i-heroicons-exclamation-circle" class="w-4 h-4 shrink-0" style="color: var(--amber)" />
              Sin actividades asignadas
            </div>

            <div v-for="act in emp.actividades" :key="act.id" class="cr-act">
              <div class="cr-act-head">
                <div class="cr-act-name">
                  <UIcon name="i-heroicons-bolt" class="w-4 h-4" style="color: var(--orange)" />
                  {{ act.actividad_nombre || 'Actividad' }}
                  <span v-if="act.requiere_consultorio" class="badge badge--neutral">Requiere consultorio</span>
                </div>
                <div v-if="editable" class="cr-act-btns">
                  <button class="btn-outline btn-xs" @click="abrirTurno(act)"><UIcon name="i-heroicons-plus" class="w-3 h-3" /> Turno</button>
                  <button class="cr-icon-btn danger" title="Quitar actividad" @click="quitarActividad(act.id)"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" /></button>
                </div>
              </div>

              <div v-if="!act.turnos.length" class="cr-act-empty">Sin turnos definidos</div>
              <div v-for="t in act.turnos" :key="t.id" class="cr-turno">
                <UIcon name="i-heroicons-clock" class="w-4 h-4" style="color: var(--purple)" />
                <span class="cr-turno-name">{{ t.horario_nombre || 'Sin horario' }}</span>
                <span v-if="t.hora_inicio" class="cr-turno-hora">{{ t.hora_inicio }}<span v-if="t.hora_fin"> – {{ t.hora_fin }}</span></span>
                <span class="cr-turno-dias">{{ diasChip(t.dias_semana) }}</span>
                <button v-if="editable" class="cr-icon-btn danger cr-turno-x" @click="quitarTurno(t.id)"><UIcon name="i-heroicons-x-mark" class="w-3.5 h-3.5" /></button>
              </div>
            </div>
          </div>
        </div>

        <!-- ─── Barra lateral ─── -->
        <aside class="cr-side">
          <div class="cr-widget">
            <div class="cr-widget-h"><UIcon name="i-heroicons-list-bullet" class="w-4 h-4" style="color: var(--navy)" /> Pasos</div>
            <ul class="cr-steps">
              <li v-for="(p, i) in pasos" :key="i" :class="{ done: p.done }">
                <UIcon :name="p.done ? 'i-heroicons-check-circle-solid' : 'i-heroicons-minus-circle'" class="w-4 h-4" />
                {{ p.label }}
              </li>
            </ul>
          </div>

          <div class="cr-widget">
            <div class="cr-widget-h"><UIcon name="i-heroicons-document-text" class="w-4 h-4" style="color: var(--teal)" /> Resumen</div>
            <div class="cr-sum"><span>Modalidad</span><b>{{ modalidadLabel(categoria, tipo) }}</b></div>
            <div class="cr-sum"><span>Período</span><b>{{ periodoLabel(rol.mes, rol.anio) }}</b></div>
            <div class="cr-sum"><span>Estado</span><b><span class="badge" :class="estadoRol(rol.status).badge">{{ estadoRol(rol.status).label }}</span></b></div>
            <div class="cr-sum"><span>Creado por</span><b>{{ rol.created_by || '—' }}</b></div>
          </div>

          <div class="cr-widget cr-tip">
            <UIcon name="i-heroicons-light-bulb" class="w-4 h-4 shrink-0" style="color: var(--amber)" />
            <span>Un rol solo se puede enviar cuando cada empleado tiene actividades y cada actividad al menos un turno.</span>
          </div>
        </aside>
      </div>
    </template>

    <!-- Modal: agregar personal -->
    <SPickerModal
      v-model="showPersonal"
      title="Agregar personal"
      subtitle="Empleados del servicio seleccionado"
      icon="i-heroicons-user-plus"
      search-placeholder="Buscar por nombre o DNI..."
      empty-text="No hay más personal disponible para este servicio"
      confirm-text="Agregar al rol"
      :items="personalOpciones"
      @confirm="onPersonal"
    />

    <!-- Modal: agregar actividades -->
    <SPickerModal
      v-model="actModal.open"
      title="Agregar actividades"
      :subtitle="actModal.empNombre"
      icon="i-heroicons-bolt"
      icon-bg="var(--orange-soft)"
      icon-color="var(--orange)"
      search-placeholder="Buscar actividad..."
      empty-text="No hay más actividades disponibles"
      confirm-text="Agregar"
      :items="actModal.open && rol ? actividadOpciones(rol.empleados.find((e:any) => e.id === actModal.empId)) : []"
      @confirm="onActividades"
    />

    <!-- Modal: agregar turno -->
    <SModal
      v-model="turnoModal.open"
      title="Agregar turno"
      :subtitle="turnoModal.actNombre"
      icon="i-heroicons-clock"
      icon-bg="var(--purple-soft)"
      icon-color="var(--purple)"
      width="480px"
    >
      <div class="form-group" style="margin-bottom: 1rem">
        <label class="form-label">Turno / Guardia <span class="required">*</span></label>
        <select v-model="turnoModal.horario_guardia_id" class="input-clinical" style="padding-left: 0.75rem">
          <option value="">Seleccione un horario</option>
          <option v-for="h in horarios" :key="h.id" :value="h.id">{{ h.nombre }}</option>
        </select>
        <p class="field-hint">La hora de inicio y término se toman del horario seleccionado</p>
      </div>

      <div class="form-group">
        <label class="form-label">Días de atención</label>
        <div class="cr-dias-grid">
          <button v-for="d in DIAS_SEMANA" :key="d.v" type="button"
            class="cr-dia" :class="{ on: turnoModal.dias.includes(d.v) }" @click="toggleDiaTurno(d.v)">{{ d.label }}</button>
        </div>
        <p v-if="turnoModal.requiereConsultorio" class="field-hint">Esta actividad requiere consultorio; el consultorio se asigna en la agenda de Consulta Externa.</p>
      </div>

      <template #footer>
        <button class="btn-cancel" @click="turnoModal.open = false">Cancelar</button>
        <button class="btn-primary" :disabled="busy || !turnoModal.horario_guardia_id" @click="guardarTurno">Agregar turno</button>
      </template>
    </SModal>
  </div>
</template>

<style scoped>
.cr { max-width: 1180px; margin: 0 auto; padding: 1.5rem 2rem; }
.cr-mb { margin-bottom: 1rem; }
.cr-center { text-align: center; padding: 3rem; background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); }

.cr-top { display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem; }
.cr-crumb { display: flex; align-items: center; gap: 0.4rem; font-size: 0.72rem; color: var(--ink-soft); margin-bottom: 0.5rem; }
.cr-crumb a { color: var(--ink-soft); text-decoration: none; }
.cr-crumb a:hover { text-decoration: underline; }
.cr-title-row { display: flex; align-items: center; gap: 1rem; }
.cr-badge-icon { width: 46px; height: 46px; border-radius: 13px; background: linear-gradient(135deg, var(--navy-soft), #dbe7ee); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cr-title-row h1 { margin: 0; font-size: 1.4rem; font-weight: 700; color: var(--ink); }
.cr-title-row p { margin: 0.1rem 0 0; font-size: 0.85rem; color: var(--ink-soft); }
.cr-actions { display: flex; align-items: center; gap: 0.6rem; }
.cr-reject { display: flex; gap: 0.6rem; padding: 0.8rem 1rem; border-radius: var(--radius); background: var(--alert-soft); color: var(--alert); font-size: 0.85rem; margin-bottom: 1rem; }

.cr-diag { padding: 0.75rem 1rem; border-radius: var(--radius); font-size: 0.82rem; }
.cr-diag-head { display: flex; align-items: center; gap: 0.5rem; font-weight: 600; }
.cr-diag ul { margin: 0.4rem 0 0; padding-left: 1.5rem; display: flex; flex-direction: column; gap: 0.15rem; }
.cr-diag--error { background: var(--alert-soft); color: var(--alert); }
.cr-diag--warn { background: var(--amber-soft); color: var(--amber); }

/* Layout 2 columnas */
.cr-grid { display: grid; grid-template-columns: 1fr 288px; gap: 1.25rem; align-items: start; }
.cr-main { min-width: 0; }
.cr-side { position: sticky; top: 1rem; display: flex; flex-direction: column; gap: 0.85rem; }

/* Ámbito */
.cr-ambito { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.85rem; margin-bottom: 0.85rem; }
.cr-amb-cell {
  display: flex; align-items: center; gap: 0.7rem; padding: 0.9rem 1rem;
  background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card); border-left: 3px solid var(--c);
}
.cr-amb-ic { width: 34px; height: 34px; border-radius: 9px; background: var(--cs); color: var(--c); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.cr-amb-cell span { display: block; font-size: 0.66rem; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.04em; }
.cr-amb-cell b { display: block; font-size: 0.92rem; font-weight: 700; color: var(--ink); margin-top: 0.1rem; line-height: 1.25; }

/* Progreso */
.cr-progress { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1rem 1.1rem; margin-bottom: 1.25rem; }
.cr-prog-tiles { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.75rem; margin-bottom: 0.85rem; }
.cr-tile { display: flex; align-items: center; gap: 0.65rem; padding: 0.65rem 0.8rem; border-radius: var(--radius); background: var(--cs); color: var(--c); }
.cr-tile b { display: block; font-size: 1.15rem; font-weight: 800; color: var(--ink); line-height: 1; }
.cr-tile span { display: block; font-size: 0.7rem; color: var(--ink-soft); margin-top: 0.15rem; }
.cr-prog-bar { height: 7px; border-radius: 4px; background: var(--mist); overflow: hidden; }
.cr-prog-fill { height: 100%; border-radius: 4px; transition: width .4s ease; }
.cr-prog-legend { display: flex; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem; font-size: 0.75rem; margin-top: 0.5rem; }

.cr-section-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.75rem; }
.cr-section-head h2 { margin: 0; font-size: 1rem; font-weight: 700; color: var(--ink); }

.cr-empty {
  display: flex; flex-direction: column; align-items: center; gap: 0.5rem; text-align: center;
  padding: 2.5rem 1.5rem; background: var(--paper); border: 1px dashed var(--line); border-radius: var(--radius-lg);
}
.cr-empty-ic { width: 52px; height: 52px; border-radius: 14px; background: var(--navy-soft); display: flex; align-items: center; justify-content: center; margin-bottom: 0.3rem; }
.cr-empty p { margin: 0; font-size: 0.9rem; color: var(--ink); }
.cr-empty span { font-size: 0.8rem; color: var(--ink-soft); max-width: 320px; margin-bottom: 0.4rem; }

/* Sidebar widgets */
.cr-widget { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 0.9rem 1rem; }
.cr-widget-h { display: flex; align-items: center; gap: 0.45rem; font-size: 0.78rem; font-weight: 700; color: var(--ink); margin-bottom: 0.7rem; }
.cr-steps { list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 0.5rem; }
.cr-steps li { display: flex; align-items: center; gap: 0.5rem; font-size: 0.78rem; color: var(--ink-soft); }
.cr-steps li :deep(svg) { color: var(--ink-soft); opacity: 0.5; flex-shrink: 0; }
.cr-steps li.done { color: var(--ink); }
.cr-steps li.done :deep(svg) { color: var(--green); opacity: 1; }
.cr-sum { display: flex; justify-content: space-between; align-items: center; gap: 0.5rem; padding: 0.35rem 0; border-bottom: 1px solid var(--line); }
.cr-sum:last-child { border-bottom: none; }
.cr-sum span { font-size: 0.72rem; color: var(--ink-soft); }
.cr-sum b { font-size: 0.75rem; font-weight: 600; color: var(--ink); text-align: right; }
.cr-tip { display: flex; gap: 0.5rem; background: var(--amber-soft); border-color: var(--amber-soft); }
.cr-tip span { font-size: 0.75rem; color: var(--ink); line-height: 1.45; }

.cr-emp { background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 1rem 1.1rem; margin-bottom: 0.85rem; }
.cr-emp.incompleto { border-left: 3px solid var(--amber); }
.cr-emp-head { display: flex; align-items: center; justify-content: space-between; gap: 0.75rem; flex-wrap: wrap; }
.cr-emp-id { display: flex; align-items: center; gap: 0.75rem; min-width: 0; }
.cr-avatar { width: 38px; height: 38px; border-radius: 50%; background: var(--navy-soft); color: var(--navy); display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8rem; flex-shrink: 0; }
.cr-emp-name { font-weight: 700; color: var(--ink); font-size: 0.9rem; }
.cr-emp-dni { font-size: 0.72rem; color: var(--ink-soft); }
.cr-emp-btns { display: flex; align-items: center; gap: 0.4rem; }
.cr-emp-empty { display: flex; align-items: center; gap: 0.4rem; font-size: 0.8rem; color: var(--ink-soft); padding: 0.75rem 0 0.25rem; }

.cr-act { border: 1px solid var(--line); border-radius: var(--radius); padding: 0.7rem 0.8rem; margin-top: 0.7rem; background: var(--mist); }
.cr-act-head { display: flex; align-items: center; justify-content: space-between; gap: 0.5rem; }
.cr-act-name { display: flex; align-items: center; gap: 0.4rem; font-weight: 600; font-size: 0.83rem; color: var(--ink); }
.cr-act-btns { display: flex; align-items: center; gap: 0.35rem; }
.cr-act-empty { font-size: 0.75rem; color: var(--ink-soft); padding: 0.4rem 0 0.15rem; }

.cr-turno { display: flex; align-items: center; gap: 0.55rem; padding: 0.4rem 0.55rem; background: var(--paper); border: 1px solid var(--line); border-radius: 7px; margin-top: 0.35rem; }
.cr-turno-name { font-size: 0.8rem; color: var(--ink); font-weight: 500; }
.cr-turno-hora { font-family: monospace; font-size: 0.72rem; color: var(--ink-soft); }
.cr-turno-dias { font-size: 0.72rem; color: var(--ink-soft); }
.cr-turno-x { margin-left: auto; }

.cr-icon-btn { background: none; border: 1px solid transparent; cursor: pointer; padding: 0.25rem; border-radius: 7px; color: var(--ink-soft); display: flex; }
.cr-icon-btn:hover { background: var(--mist); }
.cr-icon-btn.danger:hover { background: var(--alert-soft); color: var(--alert); }

.btn-sm { padding: 0.4rem 0.8rem !important; font-size: 0.78rem !important; }
.btn-xs { padding: 0.25rem 0.55rem !important; font-size: 0.7rem !important; }

.cr-dias-grid { display: grid; grid-template-columns: repeat(7, 1fr); gap: 0.35rem; }
.cr-dia { padding: 0.5rem 0; border-radius: 8px; border: 1px solid var(--line); background: var(--paper); color: var(--ink-soft); font-size: 0.78rem; font-weight: 600; cursor: pointer; transition: all .12s ease; }
.cr-dia:hover { border-color: var(--navy-soft); }
.cr-dia.on { background: var(--navy); color: white; border-color: var(--navy); }

@media (max-width: 1000px) {
  .cr { padding: 1.25rem; }
  .cr-grid { grid-template-columns: 1fr; }
  .cr-side { position: static; flex-direction: row; flex-wrap: wrap; }
  .cr-side .cr-widget { flex: 1; min-width: 220px; }
  .cr-ambito { grid-template-columns: 1fr; }
}
@media (max-width: 560px) {
  .cr-prog-tiles { grid-template-columns: 1fr; }
}
</style>
