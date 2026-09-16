<template>
  <div class="dash-container">
    <!-- HEADER -->
    <div class="dash-header">
      <div class="header-left">
        <div class="header-badge">
          <UIcon name="i-heroicons-sparkles" class="w-4 h-4" />
          <span>Panel operativo</span>
        </div>
        <h1 class="dash-title">Escritorio</h1>
        <p class="dash-subtitle">
          {{ saludo }}, <b>{{ nombreCorto }}</b> · <span class="cap">{{ fechaLarga }}</span>
        </p>
      </div>
      <div class="header-right">
        <div class="live-pill">
          <span class="live-dot" />
          <span>En vivo</span>
        </div>
        <button class="btn-secondary btn-sm" :disabled="cargando" @click="cargar">
          <UIcon name="i-heroicons-arrow-path" class="w-4 h-4" :class="{ 'animate-spin': cargando }" />
          Actualizar
        </button>
      </div>
    </div>

    <div v-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />{{ error }}
    </div>

    <!-- KPIs -->
    <section v-if="tarjetas.length" class="stats-row">
      <NuxtLink
        v-for="t in tarjetas"
        :key="t.label"
        :to="link(t.path)"
        class="stat-card"
        :class="{ 'stat-card--alert': t.alerta }"
      >
        <div class="stat-icon" :style="{ background: t.colorSoft }">
          <UIcon :name="t.icon" class="w-5 h-5" :style="{ color: t.color }" />
        </div>
        <div class="stat-body">
          <span class="stat-num">{{ cargando ? '—' : t.valor }}</span>
          <span class="stat-label">{{ t.label }}</span>
          <span v-if="t.hint" class="stat-hint">{{ t.hint }}</span>
        </div>
        <div class="stat-glow" :style="{ background: t.color }" />
        <UIcon name="i-heroicons-arrow-up-right" class="stat-arrow w-4 h-4" />
      </NuxtLink>
    </section>
    <p v-else-if="!cargando" class="empty-hint">
      No tienes módulos activos con indicadores para mostrar aquí todavía.
    </p>

    <!-- GRÁFICOS -->
    <section v-if="tarjetas.length" class="charts-row">
      <!-- Ocupación de camas (anillo) -->
      <div v-if="puedeHospitalizacion" class="panel chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" /> Ocupación de camas
          </h2>
          <span class="panel-tag">Hoy</span>
        </div>
        <div class="donut-wrap">
          <svg viewBox="0 0 120 120" class="donut">
            <circle cx="60" cy="60" r="48" class="donut-track" />
            <circle
              cx="60" cy="60" r="48"
              class="donut-fill"
              :stroke-dasharray="ocupacionCircunferencia"
              :stroke-dashoffset="ocupacionOffset"
            />
          </svg>
          <div class="donut-center">
            <span class="donut-value">{{ ocupacionPct }}%</span>
            <span class="donut-label">ocupadas</span>
          </div>
        </div>
        <div class="donut-legend">
          <div class="legend-item">
            <span class="legend-dot" style="background: var(--teal)" />
            <span>Ocupadas</span>
            <b>{{ censo.total_internados }}</b>
          </div>
          <div class="legend-item">
            <span class="legend-dot" style="background: var(--line)" />
            <span>Disponibles</span>
            <b>{{ Math.max(censo.total_camas - censo.total_internados, 0) }}</b>
          </div>
        </div>
      </div>

      <!-- Movimiento del día (barras) -->
      <div v-if="puedeHospitalizacion || puedeConsultaExterna" class="panel chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-chart-bar" class="w-4 h-4" /> Movimiento del día
          </h2>
        </div>
        <div class="bars">
          <div v-for="b in barrasDia" :key="b.label" class="bar-item">
            <div class="bar-track">
              <div class="bar-fill" :style="{ height: b.pct + '%', background: b.color }" />
            </div>
            <span class="bar-value">{{ b.valor }}</span>
            <span class="bar-label">{{ b.label }}</span>
          </div>
        </div>
      </div>

      <!-- Citas (barra segmentada) -->
      <div v-if="puedeConsultaExterna" class="panel chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-clipboard-document-check" class="w-4 h-4" /> Citas de hoy
          </h2>
          <span class="panel-tag">{{ citasHoy.total }} total</span>
        </div>
        <div class="citas-nums">
          <div class="cita-num">
            <span class="cita-dot" style="background: var(--navy)" />
            <div>
              <b>{{ citasHoy.pendientes }}</b>
              <span>Por atender</span>
            </div>
          </div>
          <div class="cita-num">
            <span class="cita-dot" style="background: var(--green)" />
            <div>
              <b>{{ citasHoy.atendidas }}</b>
              <span>Atendidas</span>
            </div>
          </div>
        </div>
        <div class="progress-stack">
          <div class="progress-seg" :style="{ flex: Math.max(citasHoy.atendidas, 0) || 0.001, background: 'var(--green)' }" />
          <div class="progress-seg" :style="{ flex: Math.max(citasHoy.pendientes, 0) || 0.001, background: 'var(--navy)' }" />
        </div>
      </div>

      <!-- Estado general (mini rings) -->
      <div class="panel chart-panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-signal" class="w-4 h-4" /> Estado general
          </h2>
        </div>
        <div class="rings-grid">
          <div v-for="r in ringsEstado" :key="r.label" class="ring-item">
            <svg viewBox="0 0 36 36" class="mini-ring">
              <circle cx="18" cy="18" r="15.9" class="mini-track" />
              <circle
                cx="18" cy="18" r="15.9"
                class="mini-fill"
                :style="{ stroke: r.color, strokeDasharray: `${r.pct}, 100` }"
              />
            </svg>
            <span class="ring-value">{{ r.valor }}</span>
            <span class="ring-label">{{ r.label }}</span>
          </div>
        </div>
      </div>
    </section>

    <div class="dash-grid">
      <!-- Actividad reciente -->
      <section v-if="puedeAuditoria" class="panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-document-magnifying-glass" class="w-4 h-4" /> Actividad reciente
          </h2>
          <NuxtLink :to="link('/app/auditoria/auditoria')" class="panel-link">Ver todo →</NuxtLink>
        </div>
        <div v-if="cargando" class="loading-state">
          <UIcon name="i-heroicons-arrow-path" class="w-5 h-5 animate-spin" />
        </div>
        <ul v-else-if="actividad.length" class="activity-list">
          <li v-for="a in actividad" :key="a.id" class="activity-item">
            <span class="activity-dot" :class="'dot-' + (a.action || '').toLowerCase()">
              <UIcon :name="iconoAccion(a.action)" class="w-3 h-3" />
            </span>
            <div class="activity-body">
              <span class="activity-text">
                <b>{{ a.user_name || 'Usuario' }}</b> {{ accionTexto(a.action) }}
                <b>{{ a.model }}</b>
              </span>
              <span class="activity-time">{{ formatFechaHora(a.created_at) }}</span>
            </div>
          </li>
        </ul>
        <p v-else class="empty-hint">Sin actividad registrada todavía.</p>
      </section>

      <!-- Accesos rápidos -->
      <section class="panel">
        <div class="panel-header">
          <h2 class="panel-title">
            <UIcon name="i-heroicons-squares-2x2" class="w-4 h-4" /> Módulos
          </h2>
        </div>
        <div class="modules-grid">
          <component
            :is="tieneAlguno([grupo.modulo]) ? 'NuxtLink' : 'div'"
            v-for="grupo in gruposVisibles"
            :key="grupo.label"
            :to="tieneAlguno([grupo.modulo]) ? link(grupo.items[0]?.path || '/app') : undefined"
            class="module-card"
            :class="{ 'module-card--off': !tieneAlguno([grupo.modulo]) }"
          >
            <span class="module-icon">
              <UIcon :name="grupo.icon || 'i-heroicons-folder'" class="w-4 h-4" />
            </span>
            <span class="truncate">{{ grupo.label }}</span>
            <UIcon
              v-if="tieneAlguno([grupo.modulo])"
              name="i-heroicons-chevron-right"
              class="w-3 h-3 module-chevron"
            />
          </component>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
const { api } = useApi()
const { link, gruposVisibles } = useHospitalNav()
const authStore = useAuthStore()

const tieneAlguno = (codes: string[]) =>
  codes.some(c => authStore.user?.active_modules?.some((p: string) => p === c || p.startsWith(c + '.')) ?? false)

const puedeHospitalizacion = computed(() => tieneAlguno(['hospitalizacion']))
const puedeConsultaExterna = computed(() => tieneAlguno(['consulta_externa']))
const puedeEmergencia = computed(() => tieneAlguno(['emergencia']))
const puedeLaboratorio = computed(() => tieneAlguno(['laboratorio']))
const puedeFarmacia = computed(() => tieneAlguno(['farmacia']))
const puedeAuditoria = computed(() => tieneAlguno(['auditoria']))

const cargando = ref(false)
const error = ref('')
const actividad = ref<any[]>([])

const censo = reactive<any>({ total_camas: 0, total_internados: 0, ingresos_del_dia: 0, altas_del_dia: 0 })
const citasHoy = reactive<{ total: number; pendientes: number; atendidas: number }>({ total: 0, pendientes: 0, atendidas: 0 })
const emergenciasEnAtencion = ref(0)
const labPendientes = ref(0)
const recetasPendientes = ref(0)

function hoy() {
  return new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima', year: 'numeric', month: '2-digit', day: '2-digit' }).format(new Date())
}

const nombreCorto = computed(() => (authStore.user?.name || 'Usuario').split(' ')[0])
const horaActual = new Date().getHours()
const saludo = computed(() => horaActual < 12 ? 'Buenos días' : horaActual < 19 ? 'Buenas tardes' : 'Buenas noches')
const fechaLarga = computed(() => new Date().toLocaleDateString('es-PE', { weekday: 'long', day: '2-digit', month: 'long', year: 'numeric' }))

function accionTexto(accion: string) {
  const mapa: Record<string, string> = {
    crear: 'creó', editar: 'editó', actualizar: 'actualizó', anular: 'anuló',
    firmar: 'firmó', confirmar: 'confirmó', dispensar: 'dispensó', resultados: 'registró resultados en',
  }
  return mapa[accion] || (accion || 'modificó')
}
function iconoAccion(accion: string) {
  const mapa: Record<string, string> = {
    crear: 'i-heroicons-plus', editar: 'i-heroicons-pencil', actualizar: 'i-heroicons-arrow-path',
    anular: 'i-heroicons-x-mark', firmar: 'i-heroicons-pencil-square', confirmar: 'i-heroicons-check',
    dispensar: 'i-heroicons-beaker', resultados: 'i-heroicons-clipboard-document-list',
  }
  return mapa[accion] || 'i-heroicons-ellipsis-horizontal'
}
function formatFechaHora(f: string) {
  if (!f) return '—'
  return new Date(f).toLocaleString('es-PE', { day: '2-digit', month: '2-digit', hour: '2-digit', minute: '2-digit' })
}

const tarjetas = computed(() => {
  const items: any[] = []
  if (puedeHospitalizacion.value) {
    items.push({
      label: 'Camas ocupadas', valor: `${censo.total_internados} / ${censo.total_camas}`,
      hint: `${censo.ingresos_del_dia} ingresos · ${censo.altas_del_dia} altas hoy`,
      icon: 'i-heroicons-building-office-2', color: 'var(--teal)', colorSoft: 'var(--teal-soft)',
      path: '/app/hospitalizacion/panel-camas',
    })
  }
  if (puedeConsultaExterna.value) {
    items.push({
      label: 'Citas de hoy', valor: citasHoy.total,
      hint: `${citasHoy.pendientes} por atender · ${citasHoy.atendidas} atendidas`,
      icon: 'i-heroicons-clipboard-document-check', color: 'var(--navy)', colorSoft: 'rgba(30,58,95,0.08)',
      path: '/app/consulta-externa/citas-por-confirmar',
    })
  }
  if (puedeEmergencia.value) {
    items.push({
      label: 'Emergencias en atención', valor: emergenciasEnAtencion.value,
      icon: 'i-heroicons-exclamation-triangle', color: 'var(--alert)', colorSoft: 'var(--alert-soft)',
      path: '/app/emergencia/atenciones', alerta: emergenciasEnAtencion.value > 0,
    })
  }
  if (puedeLaboratorio.value) {
    items.push({
      label: 'Órdenes de laboratorio pendientes', valor: labPendientes.value,
      icon: 'i-heroicons-beaker', color: 'var(--amber)', colorSoft: 'var(--amber-soft)',
      path: '/app/laboratorio/ordenes',
    })
  }
  if (puedeFarmacia.value) {
    items.push({
      label: 'Recetas pendientes', valor: recetasPendientes.value,
      icon: 'i-heroicons-document-text', color: 'var(--green)', colorSoft: 'var(--green-soft)',
      path: '/app/farmacia/recetas',
    })
  }
  return items
})

/* ---- Derivados para gráficos (solo lectura, no tocan backend) ---- */
const ocupacionPct = computed(() => {
  if (!censo.total_camas) return 0
  return Math.round((censo.total_internados / censo.total_camas) * 100)
})
const ocupacionCircunferencia = 2 * Math.PI * 48
const ocupacionOffset = computed(() => {
  return ocupacionCircunferencia * (1 - ocupacionPct.value / 100)
})

const barrasDia = computed(() => {
  const ingresos = censo.ingresos_del_dia || 0
  const altas = censo.altas_del_dia || 0
  const citas = citasHoy.total || 0
  const max = Math.max(ingresos, altas, citas, 1)
  return [
    { label: 'Ingresos', valor: ingresos, pct: (ingresos / max) * 100, color: 'linear-gradient(180deg, var(--teal), #0d9488)' },
    { label: 'Altas', valor: altas, pct: (altas / max) * 100, color: 'linear-gradient(180deg, #34d399, var(--green))' },
    { label: 'Citas', valor: citas, pct: (citas / max) * 100, color: 'linear-gradient(180deg, #64748b, var(--navy))' },
  ]
})

const ringsEstado = computed(() => {
  const totalCitas = citasHoy.total || 0
  const atendidasPct = totalCitas ? (citasHoy.atendidas / totalCitas) * 100 : 0
  const labMax = 20
  const labPct = Math.min((labPendientes.value / labMax) * 100, 100)
  const recMax = 20
  const recPct = Math.min((recetasPendientes.value / recMax) * 100, 100)
  return [
    { label: 'Citas atendidas', valor: `${Math.round(atendidasPct)}%`, pct: atendidasPct, color: 'var(--green)' },
    { label: 'Lab pendientes', valor: labPendientes.value, pct: labPct, color: 'var(--amber)' },
    { label: 'Recetas pend.', valor: recetasPendientes.value, pct: recPct, color: 'var(--alert)' },
  ]
})

async function cargar() {
  cargando.value = true
  error.value = ''
  const fecha = hoy()
  try {
    const tareas: Promise<any>[] = []

    if (puedeHospitalizacion.value) {
      tareas.push(api<any>('/app/hospitalizacion/censo-diario', { query: { fecha } }).then(d => Object.assign(censo, d)))
    }
    if (puedeConsultaExterna.value) {
      tareas.push(api<any[]>('/app/consulta-externa/citas', { query: { fecha } }).then(citas => {
        citasHoy.total = citas.length
        citasHoy.pendientes = citas.filter((c: any) => c.estado === 'separada').length
        citasHoy.atendidas = citas.filter((c: any) => c.estado === 'atendida').length
      }))
    }
    if (puedeEmergencia.value) {
      tareas.push(api<any[]>('/app/emergencia/admisiones', { query: { estado: 'en_atencion' } }).then(a => { emergenciasEnAtencion.value = a.length }))
    }
    if (puedeLaboratorio.value) {
      tareas.push(api<any>('/app/laboratorio/ordenes', { query: { estado: 'pendiente', page: 1, page_size: 1 } }).then(d => { labPendientes.value = d.total }))
    }
    if (puedeFarmacia.value) {
      tareas.push(api<any[]>('/app/farmacia/recetas', { query: { estado: 'pendiente' } }).then(r => { recetasPendientes.value = r.length }))
    }
    if (puedeAuditoria.value) {
      tareas.push(api<any>('/app/auditoria/auditoria', { query: { page: 1, page_size: 6 } }).then(d => { actividad.value = d.items }))
    }

    await Promise.all(tareas)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudieron cargar algunos indicadores del escritorio'
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
/* ============ CONTENEDOR ============ */
.dash-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem 3rem;
  background:
    radial-gradient(1200px 400px at 10% -10%, rgba(13, 148, 136, 0.06), transparent 60%),
    radial-gradient(900px 400px at 100% 0%, rgba(30, 58, 95, 0.05), transparent 60%);
}

/* ============ HEADER ============ */
.dash-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  margin-bottom: 1.75rem;
  flex-wrap: wrap;
  gap: 1rem;
}
.header-left { display: flex; flex-direction: column; gap: 0.5rem; }
.header-badge {
  display: inline-flex; align-items: center; gap: 0.375rem;
  font-size: 0.6875rem; font-weight: 600; letter-spacing: 0.04em;
  text-transform: uppercase;
  color: var(--teal);
  background: var(--teal-soft, rgba(13,148,136,0.1));
  padding: 0.25rem 0.625rem; border-radius: 999px;
  width: fit-content;
}
.dash-title {
  font-size: 1.875rem; font-weight: 800; color: var(--ink);
  margin: 0; line-height: 1.1; letter-spacing: -0.02em;
}
.dash-subtitle {
  font-size: 0.875rem; color: var(--ink-soft);
  margin: 0; text-transform: capitalize;
}
.dash-subtitle .cap { text-transform: capitalize; }
.dash-subtitle b { color: var(--ink); font-weight: 600; }

.header-right { display: flex; align-items: center; gap: 0.75rem; }
.live-pill {
  display: inline-flex; align-items: center; gap: 0.4rem;
  font-size: 0.75rem; font-weight: 600; color: var(--green);
  background: var(--green-soft, rgba(34,197,94,0.1));
  padding: 0.35rem 0.75rem; border-radius: 999px;
}
.live-dot {
  width: 7px; height: 7px; border-radius: 999px; background: var(--green);
  box-shadow: 0 0 0 0 rgba(34,197,94,0.6);
  animation: pulse 1.8s infinite;
}
@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(34,197,94,0.6); }
  70% { box-shadow: 0 0 0 8px rgba(34,197,94,0); }
  100% { box-shadow: 0 0 0 0 rgba(34,197,94,0); }
}

.btn-secondary {
  display: inline-flex; align-items: center; gap: 0.5rem;
  padding: 0.5rem 1rem; border-radius: 8px;
  font-size: 0.8125rem; font-weight: 500;
  border: 1px solid var(--line); background: var(--paper); color: var(--ink);
  cursor: pointer; transition: all 0.15s ease;
}
.btn-secondary:hover:not(:disabled) { background: var(--mist); transform: translateY(-1px); }
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }

.error-banner {
  display: flex; align-items: center; gap: 0.75rem;
  padding: 0.75rem 1rem; border-radius: 10px;
  background: var(--alert-soft); color: var(--alert);
  font-size: 0.875rem; margin-bottom: 1.5rem;
}
.empty-hint { color: var(--ink-soft); font-size: 0.875rem; padding: 1rem 0; }

/* ============ KPIs ============ */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 1rem; margin-bottom: 1.5rem;
}
.stat-card {
  position: relative;
  display: flex; align-items: center; gap: 1rem;
  padding: 1.125rem 1.25rem;
  border-radius: 16px; border: 1px solid var(--line);
  background: var(--paper);
  box-shadow: 0 1px 2px rgba(15,23,42,0.04);
  text-decoration: none;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  overflow: hidden;
}
.stat-card:hover { transform: translateY(-3px); box-shadow: 0 12px 28px -12px rgba(15,23,42,0.18); }
.stat-card--alert { border-color: color-mix(in srgb, var(--alert) 30%, transparent); }
.stat-glow {
  position: absolute; top: -40%; right: -20%;
  width: 120px; height: 120px; border-radius: 999px;
  opacity: 0.08; filter: blur(20px);
  pointer-events: none;
}
.stat-arrow {
  position: absolute; top: 0.75rem; right: 0.75rem;
  color: var(--ink-soft); opacity: 0;
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.stat-card:hover .stat-arrow { opacity: 1; transform: translate(2px, -2px); }
.stat-icon {
  width: 46px; height: 46px; border-radius: 14px;
  display: flex; align-items: center; justify-content: center;
  flex-shrink: 0;
}
.stat-body { display: flex; flex-direction: column; min-width: 0; }
.stat-num { font-size: 1.5rem; font-weight: 800; color: var(--ink); line-height: 1.2; letter-spacing: -0.02em; }
.stat-label { font-size: 0.8125rem; color: var(--ink-soft); font-weight: 500; }
.stat-hint { font-size: 0.6875rem; color: var(--ink-soft); opacity: 0.85; margin-top: 0.125rem; }

/* ============ CHARTS ============ */
.charts-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 1rem; margin-bottom: 1.5rem;
}
.chart-panel { display: flex; flex-direction: column; }
.panel-tag {
  font-size: 0.6875rem; font-weight: 600; color: var(--ink-soft);
  background: var(--mist); padding: 0.2rem 0.5rem; border-radius: 999px;
}

/* Donut */
.donut-wrap { position: relative; width: 160px; height: 160px; margin: 0.5rem auto 1rem; }
.donut { width: 100%; height: 100%; transform: rotate(-90deg); }
.donut-track { fill: none; stroke: var(--mist); stroke-width: 12; }
.donut-fill {
  fill: none; stroke: url(#gradTeal); stroke-width: 12; stroke-linecap: round;
  stroke: var(--teal);
  transition: stroke-dashoffset 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.donut-center {
  position: absolute; inset: 0;
  display: flex; flex-direction: column; align-items: center; justify-content: center;
}
.donut-value { font-size: 1.75rem; font-weight: 800; color: var(--ink); line-height: 1; }
.donut-label { font-size: 0.6875rem; color: var(--ink-soft); text-transform: uppercase; letter-spacing: 0.05em; margin-top: 0.25rem; }
.donut-legend { display: flex; flex-direction: column; gap: 0.5rem; }
.legend-item {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.8125rem; color: var(--ink-soft);
}
.legend-item b { margin-left: auto; color: var(--ink); font-weight: 700; }
.legend-dot { width: 10px; height: 10px; border-radius: 999px; flex-shrink: 0; }

/* Bars */
.bars {
  display: flex; align-items: flex-end; justify-content: space-around;
  gap: 1rem; height: 160px; padding: 0.5rem 0;
}
.bar-item { display: flex; flex-direction: column; align-items: center; gap: 0.375rem; flex: 1; height: 100%; justify-content: flex-end; }
.bar-track {
  width: 100%; max-width: 46px; height: 100%;
  background: var(--mist); border-radius: 10px;
  display: flex; align-items: flex-end; overflow: hidden;
}
.bar-fill {
  width: 100%; border-radius: 10px;
  transition: height 0.7s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 4px;
}
.bar-value { font-size: 0.8125rem; font-weight: 700; color: var(--ink); }
.bar-label { font-size: 0.6875rem; color: var(--ink-soft); text-align: center; }

/* Citas */
.citas-nums { display: flex; gap: 1.5rem; margin: 0.5rem 0 1rem; }
.cita-num { display: flex; align-items: center; gap: 0.625rem; }
.cita-dot { width: 10px; height: 10px; border-radius: 999px; flex-shrink: 0; }
.cita-num b { display: block; font-size: 1.25rem; font-weight: 800; color: var(--ink); line-height: 1; }
.cita-num span { font-size: 0.75rem; color: var(--ink-soft); }
.progress-stack {
  display: flex; height: 12px; border-radius: 999px;
  overflow: hidden; background: var(--mist);
}
.progress-seg { transition: flex 0.6s ease; }

/* Mini rings */
.rings-grid { display: flex; justify-content: space-around; gap: 0.5rem; padding: 0.5rem 0; }
.ring-item { display: flex; flex-direction: column; align-items: center; gap: 0.25rem; }
.mini-ring { width: 64px; height: 64px; transform: rotate(-90deg); }
.mini-track { fill: none; stroke: var(--mist); stroke-width: 3; }
.mini-fill {
  fill: none; stroke-width: 3; stroke-linecap: round;
  transition: stroke-dasharray 0.8s cubic-bezier(0.4, 0, 0.2, 1);
}
.ring-value { font-size: 0.9375rem; font-weight: 800; color: var(--ink); margin-top: -0.5rem; }
.ring-label { font-size: 0.6875rem; color: var(--ink-soft); text-align: center; }

/* ============ PANELS ============ */
.dash-grid { display: grid; grid-template-columns: 1.1fr 1fr; gap: 1.25rem; align-items: start; }
.panel {
  background: var(--paper);
  border-radius: 16px; border: 1px solid var(--line);
  padding: 1.25rem;
  box-shadow: 0 1px 2px rgba(15,23,42,0.04);
}
.panel-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.panel-title {
  font-size: 0.9375rem; font-weight: 700; color: var(--ink);
  margin: 0; display: flex; align-items: center; gap: 0.5rem;
}
.panel-link { font-size: 0.75rem; color: var(--teal); text-decoration: none; font-weight: 600; }
.panel-link:hover { text-decoration: underline; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 1.5rem; }

/* ============ ACTIVITY ============ */
.activity-list { display: flex; flex-direction: column; gap: 0.875rem; }
.activity-item { display: flex; align-items: flex-start; gap: 0.75rem; }
.activity-dot {
  width: 26px; height: 26px; border-radius: 999px; flex-shrink: 0;
  display: flex; align-items: center; justify-content: center;
  background: var(--teal-soft, rgba(13,148,136,0.12)); color: var(--teal);
  margin-top: 0.125rem;
}
.dot-anular { background: var(--alert-soft); color: var(--alert); }
.dot-crear { background: var(--green-soft); color: var(--green); }
.dot-firmar, .dot-confirmar { background: var(--amber-soft); color: var(--amber); }
.activity-body { display: flex; flex-direction: column; min-width: 0; }
.activity-text { font-size: 0.8125rem; color: var(--ink); line-height: 1.4; }
.activity-text b { font-weight: 600; }
.activity-time { font-size: 0.6875rem; color: var(--ink-soft); margin-top: 0.125rem; }

/* ============ MODULES ============ */
.modules-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 0.625rem; }
.module-card {
  display: flex; align-items: center; gap: 0.625rem;
  padding: 0.75rem 0.875rem;
  border-radius: 12px; border: 1px solid var(--line);
  background: var(--paper); color: var(--ink);
  font-size: 0.8125rem; font-weight: 500; text-decoration: none;
  transition: all 0.15s ease;
}
.module-card:hover:not(.module-card--off) {
  background: var(--mist); transform: translateY(-1px);
  border-color: color-mix(in srgb, var(--teal) 30%, var(--line));
}
.module-card--off { opacity: 0.45; cursor: not-allowed; background: var(--mist); }
.module-icon {
  width: 28px; height: 28px; border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  background: var(--teal-soft, rgba(13,148,136,0.1)); color: var(--teal);
  flex-shrink: 0;
}
.module-card--off .module-icon { background: var(--line); color: var(--ink-soft); }
.module-chevron { margin-left: auto; color: var(--ink-soft); }

/* ============ RESPONSIVE ============ */
@media (max-width: 900px) {
  .dash-grid { grid-template-columns: 1fr; }
}
@media (max-width: 640px) {
  .dash-container { padding: 1rem 1rem 2rem; }
  .dash-header { flex-direction: column; align-items: flex-start; }
  .dash-title { font-size: 1.5rem; }
  .charts-row { grid-template-columns: 1fr; }
}
</style>