<template>
  <div class="lab-container">
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-inbox" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div class="breadcrumb">
          <span style="color: var(--ink-soft); font-size: 0.75rem;">CONSULTA EXTERNA</span>
          <h1 class="page-title">Bandeja Electrónica</h1>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-secondary btn-sm" @click="cargar"><UIcon name="i-heroicons-arrow-path" class="w-4 h-4" />Actualizar</button>
      </div>
    </div>

    <div v-if="error" class="error-banner"><UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}</div>
    <p v-if="!cargando && sinEmpleado" class="field-hint" style="margin-bottom:1rem">
      Esta bandeja depende de tu vínculo como médico (empleado). Tu cuenta no tiene un empleado asociado, así que no hay tareas que mostrarte aquí.
    </p>

    <div v-if="cargando" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>

    <template v-else>
      <!-- Atenciones sin firmar -->
      <section class="panel">
        <div class="results-header">
          <h2 class="results-title"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" /> Atenciones pendientes de firmar</h2>
          <span class="card-badge" :class="{ 'card-badge--alert': data.atenciones_pendientes_firma.length }">{{ data.atenciones_pendientes_firma.length }}</span>
        </div>
        <div v-if="!data.atenciones_pendientes_firma.length" class="empty-state-small">
          <UIcon name="i-heroicons-check-circle" class="w-8 h-8" style="color: var(--green)" />
          <span>No tienes atenciones pendientes de firmar.</span>
        </div>
        <div v-else class="items-list">
          <NuxtLink v-for="a in data.atenciones_pendientes_firma" :key="a.cita_id" :to="link('/app/consulta-externa/atenciones-medicas/'+a.cita_id)" class="item-row">
            <div class="item-main">
              <span class="item-title">{{ a.paciente_nombre }}</span>
              <span class="badge badge-off">Borrador</span>
            </div>
            <div class="item-sub">{{ formatFecha(a.fecha) }} · {{ a.hora_inicio }} · {{ a.especialidad_nombre || a.servicio_nombre || '—' }}</div>
          </NuxtLink>
        </div>
      </section>

      <!-- Citas de hoy pendientes -->
      <section class="panel">
        <div class="results-header">
          <h2 class="results-title"><UIcon name="i-heroicons-clock" class="w-4 h-4" /> Citas de hoy pendientes de atender</h2>
          <span class="card-badge">{{ data.citas_hoy_pendientes.length }}</span>
        </div>
        <div v-if="!data.citas_hoy_pendientes.length" class="empty-state-small">
          <UIcon name="i-heroicons-calendar" class="w-8 h-8" style="color: var(--ink-soft)" />
          <span>No tienes citas pendientes para hoy.</span>
        </div>
        <div v-else class="items-list">
          <NuxtLink v-for="c in data.citas_hoy_pendientes" :key="c.id" :to="link('/app/consulta-externa/atenciones-medicas/'+c.id)" class="item-row">
            <div class="item-main">
              <span class="item-title">{{ c.paciente_nombre }}</span>
              <span class="badge badge-info">{{ c.hora_inicio }}</span>
            </div>
            <div class="item-sub">HC {{ c.paciente_record || '—' }} · {{ c.tipo_consulta || 'Consulta' }}</div>
          </NuxtLink>
        </div>
      </section>

      <!-- Interconsultas de mi especialidad -->
      <section class="panel">
        <div class="results-header">
          <h2 class="results-title"><UIcon name="i-heroicons-arrow-path-rounded-square" class="w-4 h-4" /> Interconsultas dirigidas a mi especialidad</h2>
          <span class="card-badge" :class="{ 'card-badge--alert': data.interconsultas_pendientes.length }">{{ data.interconsultas_pendientes.length }}</span>
        </div>
        <div v-if="!data.interconsultas_pendientes.length" class="empty-state-small">
          <UIcon name="i-heroicons-check-circle" class="w-8 h-8" style="color: var(--green)" />
          <span>No hay interconsultas pendientes para tu especialidad.</span>
        </div>
        <div v-else class="items-list">
          <div v-for="i in data.interconsultas_pendientes" :key="i.id" class="item-row item-row--static">
            <div class="item-main">
              <span class="item-title">{{ i.paciente_nombre }}</span>
              <span class="badge" :class="i.urgente ? 'badge-off' : 'badge-info'">{{ i.urgente ? 'Urgente' : i.origen }}</span>
            </div>
            <div class="item-sub">{{ i.motivo }}</div>
          </div>
        </div>
        <p v-if="data.interconsultas_pendientes.length" class="field-hint">
          Para programarlas como cita, ve a
          <NuxtLink :to="link('/app/admision/agendamiento')" style="color: var(--teal)">Admisión · Agendamiento</NuxtLink>.
        </p>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const { link } = useHospitalNav()

const error = ref('')
const cargando = ref(false)
const sinEmpleado = ref(false)
const data = reactive<{ atenciones_pendientes_firma: any[]; citas_hoy_pendientes: any[]; interconsultas_pendientes: any[] }>({
  atenciones_pendientes_firma: [], citas_hoy_pendientes: [], interconsultas_pendientes: [],
})

function formatFecha(f: string) {
  if (!f) return '—'
  const d = new Date(`${String(f).slice(0, 10)}T00:00:00`)
  return d.toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })
}

async function cargar() {
  cargando.value = true; error.value = ''
  try {
    const r = await api<any>('/app/consulta-externa/bandeja-electronica')
    data.atenciones_pendientes_firma = r.atenciones_pendientes_firma
    data.citas_hoy_pendientes = r.citas_hoy_pendientes
    data.interconsultas_pendientes = r.interconsultas_pendientes
    sinEmpleado.value = !r.atenciones_pendientes_firma.length && !r.citas_hoy_pendientes.length && !r.interconsultas_pendientes.length
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar la bandeja electrónica'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.lab-container { max-width: 1100px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.header-actions { display: flex; align-items: center; gap: 0.75rem; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; }
.btn-secondary:hover { background: var(--mist); }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.5rem; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.25rem; box-shadow: var(--shadow-sm); }
.results-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.results-title { font-size: 0.9375rem; font-weight: 600; color: var(--ink); margin: 0; display: flex; align-items: center; gap: 0.5rem; }
.card-badge { font-size: 0.6875rem; font-weight: 700; padding: 0.125rem 0.625rem; border-radius: 999px; background: var(--green-soft); color: var(--green); }
.card-badge--alert { background: var(--amber-soft); color: var(--amber); }
.empty-state-small { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 1.5rem 1rem; gap: 0.5rem; color: var(--ink-soft); font-size: 0.875rem; }
.items-list { display: flex; flex-direction: column; gap: 0.5rem; }
.item-row { display: block; text-align: left; padding: 0.75rem 1rem; border-radius: var(--radius); border: 1px solid var(--line); background: var(--paper); text-decoration: none; cursor: pointer; }
.item-row:not(.item-row--static):hover { background: var(--mist); border-color: var(--teal-soft); }
.item-row--static { cursor: default; }
.item-main { display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem; }
.item-title { font-weight: 500; color: var(--ink); font-size: 0.875rem; }
.item-sub { font-size: 0.75rem; color: var(--ink-soft); }
.badge { font-size: 0.6875rem; font-weight: 600; padding: 0.125rem 0.5rem; border-radius: 999px; white-space: nowrap; }
.badge-off { color: var(--alert); background: var(--alert-soft); }
.badge-info { color: var(--teal); background: var(--teal-soft); }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
}
</style>
