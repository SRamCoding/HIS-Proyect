<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const { DIAS_SEMANA } = useRolesTurno()
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)

const rol = ref<any>(null)
const loading = ref(true)
const error = ref('')
const busy = ref(false)

const empleados = ref<any[]>([])
const actividadesCat = ref<any[]>([])
const horarios = ref<any[]>([])

const showForm = ref(false)
const showEmpPicker = ref(false)
const form = reactive<{ empleado_id: string; motivo: string; actividades: any[] }>({ empleado_id: '', motivo: '', actividades: [] })

const empSel = computed(() => empleados.value.find(e => e.id === form.empleado_id))
const empOpciones = computed(() => empleados.value.map(e => ({ id: e.id, label: e.nombre_completo, sublabel: `DNI ${e.dni}` })))
const actOpciones = computed(() => actividadesCat.value.map(a => ({ id: a.id, label: a.nombre })))

const abrirForm = () => {
  Object.assign(form, { empleado_id: '', motivo: '', actividades: [] })
  showForm.value = true
}
const addActividad = () => form.actividades.push({ actividad_id: '', turnos: [] })
const addTurno = (a: any) => a.turnos.push({ horario_guardia_id: '', dias_semana: [] })
const toggleDia = (t: any, d: number) => {
  t.dias_semana = t.dias_semana.includes(d) ? t.dias_semana.filter((x: number) => x !== d) : [...t.dias_semana, d]
}
const actNombre = (aid: string) => actividadesCat.value.find(a => a.id === aid)?.nombre || 'Actividad'

const cargar = async () => {
  loading.value = true; error.value = ''
  try {
    const [r, emps, acts, hors] = await Promise.all([
      api<any>(`/sigarh/roles-aprobados/roles/${id.value}`),
      api<any[]>('/sigarh/rrhh/empleados').catch(() => []),
      api<any[]>('/sigarh/mantenimiento/actividades').catch(() => []),
      api<any[]>('/sigarh/mantenimiento/horarios-guardia').catch(() => []),
    ])
    rol.value = r
    empleados.value = emps
    actividadesCat.value = acts.filter((a: any) => a.is_active)
    horarios.value = hors.filter((h: any) => h.is_active)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo cargar') }
  finally { loading.value = false }
}

const enviarSolicitud = async () => {
  if (!form.empleado_id) { error.value = 'Selecciona un empleado'; return }
  if (form.motivo.trim().length < 5) { error.value = 'El motivo es obligatorio'; return }
  busy.value = true; error.value = ''
  try {
    const schedule_data = {
      actividades: form.actividades.filter(a => a.actividad_id).map(a => ({
        actividad_id: a.actividad_id,
        turnos: a.turnos.filter((t: any) => t.horario_guardia_id).map((t: any) => ({
          horario_guardia_id: t.horario_guardia_id, dias_semana: t.dias_semana,
        })),
      })),
    }
    await api(`/sigarh/roles-aprobados/roles/${id.value}/solicitudes-modificacion`, {
      method: 'POST', body: { empleado_id: form.empleado_id, motivo: form.motivo, schedule_data },
    })
    router.push(`/sigarh/roles-pendientes/solicitudes?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo enviar la solicitud') }
  finally { busy.value = false }
}
onMounted(cargar)
</script>

<template>
  <div class="ra">
    <div class="ra-top">
      <div>
        <div class="ra-crumb">
          <NuxtLink :to="`/sigarh/roles-aprobados?tenant=${tenantId}`">Roles Aprobados</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span>Detalle</span>
        </div>
        <div class="ra-title-row">
          <div class="ra-badge-icon"><UIcon name="i-heroicons-check-badge" class="w-6 h-6" style="color: var(--green)" /></div>
          <div>
            <h1>{{ rol ? (rol.servicio_nombre || 'Rol aprobado') : '' }}</h1>
            <p>Programación autorizada</p>
          </div>
        </div>
      </div>
      <button class="btn-primary" @click="abrirForm">
        <UIcon name="i-heroicons-user-plus" class="w-4 h-4" /> Solicitar incorporación
      </button>
    </div>

    <div v-if="error && !showForm" class="error-banner ra-mb">{{ error }}</div>

    <div v-if="loading" class="ra-center"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--green)" /></div>
    <SRolDetalle v-else-if="rol" :rol="rol" />

    <!-- Modal solicitud -->
    <SModal
      v-model="showForm"
      title="Solicitud de incorporación de personal"
      subtitle="Se enviará a Roles Pendientes → Solicitudes de Modificación"
      icon="i-heroicons-user-plus"
      width="640px"
      persistent
    >
      <div v-if="error" class="error-banner" style="margin-bottom: 0.9rem">{{ error }}</div>

      <div class="form-group" style="margin-bottom: 0.9rem">
        <label class="form-label">Empleado a agregar <span class="required">*</span></label>
        <button type="button" class="ra-pick" @click="showEmpPicker = true">
          <UIcon name="i-heroicons-user" class="w-4 h-4" style="color: var(--ink-soft)" />
          <span :style="{ color: empSel ? 'var(--ink)' : 'var(--ink-soft)' }">
            {{ empSel ? `${empSel.nombre_completo} — ${empSel.dni}` : 'Seleccionar empleado' }}
          </span>
          <UIcon name="i-heroicons-chevron-down" class="w-4 h-4" style="color: var(--ink-soft); margin-left: auto" />
        </button>
      </div>

      <div class="form-group" style="margin-bottom: 0.9rem">
        <label class="form-label">Motivo de la modificación <span class="required">*</span></label>
        <textarea v-model="form.motivo" rows="2" class="input-clinical" style="padding-left: 0.75rem" placeholder="Sustento de la incorporación..." />
      </div>

      <div class="ra-sched">
        <div class="ra-sched-head">
          <span class="form-label" style="margin: 0">Programación propuesta</span>
          <button type="button" class="btn-outline btn-xs" @click="addActividad"><UIcon name="i-heroicons-plus" class="w-3 h-3" /> Actividad</button>
        </div>
        <p v-if="!form.actividades.length" class="ra-sched-empty">Sin actividades propuestas (opcional).</p>

        <div v-for="(a, i) in form.actividades" :key="i" class="ra-sa">
          <div class="ra-sa-head">
            <select v-model="a.actividad_id" class="input-clinical" style="padding-left: 0.75rem; flex: 1">
              <option value="">Actividad...</option>
              <option v-for="act in actividadesCat" :key="act.id" :value="act.id">{{ act.nombre }}</option>
            </select>
            <button type="button" class="btn-outline btn-xs" @click="addTurno(a)"><UIcon name="i-heroicons-plus" class="w-3 h-3" /> Turno</button>
            <button type="button" class="ra-x" @click="form.actividades.splice(i, 1)"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" style="color: var(--alert)" /></button>
          </div>
          <div v-for="(t, j) in a.turnos" :key="j" class="ra-st">
            <select v-model="t.horario_guardia_id" class="input-clinical" style="padding-left: 0.75rem; max-width: 220px">
              <option value="">Horario...</option>
              <option v-for="h in horarios" :key="h.id" :value="h.id">{{ h.nombre }}</option>
            </select>
            <div class="ra-dias">
              <button v-for="d in DIAS_SEMANA" :key="d.v" type="button" class="ra-dia" :class="{ on: t.dias_semana.includes(d.v) }" @click="toggleDia(t, d.v)">{{ d.label }}</button>
            </div>
            <button type="button" class="ra-x" @click="a.turnos.splice(j, 1)"><UIcon name="i-heroicons-x-mark" class="w-3.5 h-3.5" style="color: var(--alert)" /></button>
          </div>
        </div>
      </div>

      <template #footer>
        <button class="btn-cancel" @click="showForm = false">Cancelar</button>
        <button class="btn-primary" :disabled="busy || !form.empleado_id || form.motivo.trim().length < 5" @click="enviarSolicitud">Enviar solicitud</button>
      </template>
    </SModal>

    <SPickerModal
      v-model="showEmpPicker"
      title="Seleccionar empleado"
      icon="i-heroicons-user"
      :multiple="false"
      search-placeholder="Buscar por nombre o DNI..."
      confirm-text="Elegir"
      :items="empOpciones"
      @confirm="(id: string) => form.empleado_id = id"
    />
  </div>
</template>

<style scoped>
.ra { max-width: 1000px; margin: 0 auto; padding: 1.5rem 2rem; }
.ra-mb { margin-bottom: 1rem; }
.ra-center { text-align: center; padding: 3rem; }
.ra-top { display: flex; align-items: flex-start; justify-content: space-between; flex-wrap: wrap; gap: 1rem; margin-bottom: 1.25rem; }
.ra-crumb { display: flex; align-items: center; gap: 0.4rem; font-size: 0.72rem; color: var(--ink-soft); margin-bottom: 0.5rem; }
.ra-crumb a { color: var(--ink-soft); text-decoration: none; }
.ra-crumb a:hover { text-decoration: underline; }
.ra-title-row { display: flex; align-items: center; gap: 1rem; }
.ra-badge-icon { width: 46px; height: 46px; border-radius: 13px; background: var(--green-soft); display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.ra-title-row h1 { margin: 0; font-size: 1.4rem; font-weight: 700; color: var(--ink); }
.ra-title-row p { margin: 0.1rem 0 0; font-size: 0.85rem; color: var(--ink-soft); }

.ra-pick { width: 100%; display: flex; align-items: center; gap: 0.5rem; padding: 0.6rem 0.75rem; border: 1px solid var(--line); border-radius: 8px; background: var(--paper); font-size: 0.875rem; cursor: pointer; }
.ra-pick:hover { border-color: var(--navy-soft); }

.ra-sched { border-top: 1px solid var(--line); padding-top: 0.85rem; margin-top: 0.3rem; }
.ra-sched-head { display: flex; align-items: center; justify-content: space-between; margin-bottom: 0.5rem; }
.ra-sched-empty { font-size: 0.78rem; color: var(--ink-soft); margin: 0; }
.ra-sa { border: 1px solid var(--line); border-radius: 8px; padding: 0.6rem; margin-bottom: 0.5rem; background: var(--mist); }
.ra-sa-head { display: flex; align-items: center; gap: 0.5rem; }
.ra-st { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.45rem; flex-wrap: wrap; }
.ra-dias { display: flex; gap: 0.25rem; }
.ra-dia { font-size: 0.7rem; padding: 0.3rem 0.42rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink-soft); cursor: pointer; }
.ra-dia.on { background: var(--navy); color: white; border-color: var(--navy); }
.ra-x { background: none; border: none; cursor: pointer; padding: 0.2rem; }
.btn-xs { padding: 0.25rem 0.55rem !important; font-size: 0.7rem !important; }
</style>
