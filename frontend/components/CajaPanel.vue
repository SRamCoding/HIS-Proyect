<template>
  <div class="lab-container">
    <!-- Header -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-banknotes" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="breadcrumb">
            <span style="color: var(--ink-soft); font-size: 0.75rem;">ATENCIÓN HOSPITALARIA</span>
            <h1 class="page-title">Caja · {{ titles[mode] }}</h1>
          </div>
        </div>
      </div>
      <div class="header-actions">
        <button v-if="mode==='comprobantes-pago'" class="btn-secondary btn-sm" @click="download('/reportes/cobros.csv', 'caja-cobros.csv')">
          <UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />
          Exportar CSV
        </button>
      </div>
    </div>

    <!-- Tabs -->
    <div class="lab-tabs">
      <NuxtLink
        v-for="(title, key) in titles"
        :key="key"
        :to="'/app/caja/'+key"
        class="tab-link"
        :class="{ 'tab-link--active': key === mode }"
      >
        {{ title }}
      </NuxtLink>
    </div>

    <!-- Messages -->
    <div v-if="error" class="error-banner">
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>
    <div v-if="notice" class="success-banner">
      <UIcon name="i-heroicons-check-circle" class="w-4 h-4 shrink-0" />
      {{ notice }}
    </div>

    <!-- ══════════════════ MI CAJA ══════════════════ -->
    <template v-if="mode==='mi-caja'">
      <section v-if="cargandoTurno" class="panel"><p style="color: var(--ink-soft)">Cargando turno...</p></section>

      <template v-else-if="!miTurno || miTurno.estado==='cerrada'">
        <section class="panel">
          <div class="card-header-row">
            <h2 class="results-title">Abrir turno de caja</h2>
          </div>
          <form class="editor-form" @submit.prevent="abrirTurno">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Caja</label>
                <select v-model="aperturaForm.caja_id" class="input-clinical" required>
                  <option value="">Seleccionar</option>
                  <option v-for="c in catalogs.cajas" :key="c.id" :value="c.id">{{ c.nombre }}</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Monto de apertura S/</label>
                <input v-model="aperturaForm.monto_apertura" type="number" class="input-clinical" min="0" step="0.01" required />
              </div>
              <div class="form-group full-width">
                <label class="form-label">Observaciones</label>
                <textarea v-model="aperturaForm.observaciones_apertura" class="input-clinical" rows="2" maxlength="2000"></textarea>
              </div>
            </div>
            <div class="form-actions">
              <button class="btn-primary" :disabled="busy">
                <UIcon name="i-heroicons-lock-open" class="w-4 h-4" />
                Abrir turno
              </button>
            </div>
          </form>
        </section>

        <section v-if="miTurno && miTurno.estado==='cerrada'" class="panel">
          <h2 class="results-title">Último cierre</h2>
          <div class="detail-info">
            <p>{{ miTurno.caja_nombre }} · Cerrado {{ miTurno.cerrada_at }} UTC</p>
            <p>Apertura S/ {{ money(miTurno.monto_apertura) }} · Sistema S/ {{ money(miTurno.monto_cierre_sistema) }} · Declarado S/ {{ money(miTurno.monto_cierre_declarado) }}</p>
            <p :style="{ color: Number(miTurno.diferencia) !== 0 ? 'var(--alert)' : 'var(--green)' }">
              Diferencia S/ {{ money(miTurno.diferencia) }}
            </p>
          </div>
        </section>
      </template>

      <template v-else>
        <section class="panel">
          <div class="card-header-row">
            <h2 class="results-title">Turno abierto — {{ miTurno.caja_nombre }}</h2>
            <span class="status-badge">{{ miTurno.numero }}</span>
          </div>
          <div class="detail-info">
            <p>Cajero {{ miTurno.cajero_nombre }} · Abierto {{ miTurno.abierta_at }} UTC</p>
            <p>Monto de apertura S/ {{ money(miTurno.monto_apertura) }}</p>
          </div>
          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th>Forma de pago</th><th>Cobros</th><th>Total S/</th></tr></thead>
              <tbody>
                <tr v-for="r in miTurno.resumen_formas_pago" :key="r.forma_pago">
                  <td>{{ r.forma_pago }}</td><td>{{ r.cantidad }}</td><td>{{ money(r.total) }}</td>
                </tr>
                <tr v-if="!miTurno.resumen_formas_pago.length">
                  <td colspan="3" style="text-align:center;color:var(--ink-soft)">Sin cobros todavía en este turno.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </section>

        <section class="panel">
          <h2 class="results-title">Cerrar turno</h2>
          <form class="editor-form" @submit.prevent="cerrarTurno">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Monto contado en caja S/</label>
                <input v-model="cierreForm.monto_cierre_declarado" type="number" class="input-clinical" min="0" step="0.01" required />
              </div>
              <div class="form-group full-width">
                <label class="form-label">Observaciones</label>
                <textarea v-model="cierreForm.observaciones_cierre" class="input-clinical" rows="2" maxlength="2000"></textarea>
              </div>
            </div>
            <p class="field-hint">El sistema calculará la diferencia frente al efectivo cobrado durante el turno.</p>
            <div class="form-actions">
              <button class="btn-danger" :disabled="busy">
                <UIcon name="i-heroicons-lock-closed" class="w-4 h-4" />
                Cerrar turno
              </button>
            </div>
          </form>
        </section>
      </template>
    </template>

    <!-- ══════════════════ CUENTAS ══════════════════ -->
    <template v-else-if="mode==='cuentas'">
      <section class="panel">
        <form class="editor-form" @submit.prevent="buscarCuentas">
          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">Buscar por N.° de cuenta, DNI o apellido</label>
              <input v-model="cuentaQuery" class="input-clinical" minlength="2" required />
            </div>
          </div>
          <div class="form-actions">
            <button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button>
          </div>
        </form>
        <div class="choices">
          <button v-for="c in cuentasEncontradas" :key="c.numero_cuenta" class="choice-btn" @click="verCuenta(c.numero_cuenta)">
            {{ c.numero_cuenta }} · {{ c.paciente }} · {{ c.dni }}
          </button>
        </div>
      </section>

      <section v-if="cuentaActual" class="panel">
        <div class="detail-header">
          <div>
            <h2 class="detail-title">Cuenta {{ cuentaActual.numero_cuenta }}</h2>
            <p class="detail-subtitle">{{ cuentaActual.paciente?.nombre || 'Sin paciente identificado' }} · HC {{ cuentaActual.paciente?.historia || '—' }}</p>
          </div>
        </div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Origen</th><th>Descripción</th><th>Cargo S/</th><th>Cobrado S/</th><th>Pendiente S/</th></tr></thead>
            <tbody>
              <tr v-for="i in cuentaActual.items" :key="i.origen+i.origen_id">
                <td>{{ i.origen }}</td>
                <td>{{ i.descripcion }} <span v-if="!i.tarifa_configurada" class="field-hint" style="color:var(--alert)">(sin tarifa configurada)</span></td>
                <td>{{ money(i.cargo) }}</td>
                <td>{{ money(i.cobrado) }}</td>
                <td>{{ money(i.pendiente) }}</td>
              </tr>
              <tr v-if="!cuentaActual.items.length">
                <td colspan="5" style="text-align:center;color:var(--ink-soft)">Esta cuenta no tiene cargos registrados.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p class="total">Total pendiente S/ {{ money(cuentaActual.total_pendiente) }}</p>
        <div class="form-actions">
          <NuxtLink :to="'/app/caja/cobro-por-paciente?cuenta='+cuentaActual.numero_cuenta" class="btn-primary">
            <UIcon name="i-heroicons-credit-card" class="w-4 h-4" />
            Cobrar esta cuenta
          </NuxtLink>
        </div>
      </section>
    </template>

    <!-- ══════════════════ COBRO POR PACIENTE ══════════════════ -->
    <template v-else-if="mode==='cobro-por-paciente'">
      <section v-if="cargandoTurno" class="panel"><p style="color: var(--ink-soft)">Verificando turno...</p></section>
      <section v-else-if="!miTurno || miTurno.estado!=='abierta'" class="panel">
        <p>No tiene un turno de caja abierto.</p>
        <NuxtLink to="/app/caja/mi-caja" class="btn-primary" style="margin-top:0.75rem;display:inline-flex">
          <UIcon name="i-heroicons-lock-open" class="w-4 h-4" />
          Abrir turno en Mi Caja
        </NuxtLink>
      </section>

      <template v-else>
        <section class="panel">
          <form class="editor-form" @submit.prevent="buscarCuentasPago">
            <div class="form-grid">
              <div class="form-group full-width">
                <label class="form-label">Buscar por N.° de cuenta, DNI o apellido</label>
                <input v-model="cuentaQuery" class="input-clinical" minlength="2" required />
              </div>
            </div>
            <div class="form-actions">
              <button class="btn-primary" :disabled="busy"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button>
            </div>
          </form>
          <div class="choices">
            <button v-for="c in cuentasEncontradas" :key="c.numero_cuenta" class="choice-btn" @click="cargarCuentaPago(c.numero_cuenta)">
              {{ c.numero_cuenta }} · {{ c.paciente }} · {{ c.dni }}
            </button>
          </div>
        </section>

        <section v-if="cuentaActual" class="panel">
          <div class="patient-info-card">
            <div class="patient-info-header">
              <div class="patient-avatar" :style="{ background: getColorPaciente(cuentaActual.paciente?.nombre) }">
                <span>{{ getInitials(cuentaActual.paciente?.nombre) }}</span>
              </div>
              <div class="patient-info">
                <span class="patient-name">{{ cuentaActual.paciente?.nombre || 'Sin paciente identificado' }}</span>
                <div class="patient-details">
                  <span>HC {{ cuentaActual.paciente?.historia || '—' }}</span>
                  <span class="patient-separator">•</span>
                  <span>Cuenta {{ cuentaActual.numero_cuenta }}</span>
                </div>
              </div>
            </div>
          </div>

          <div class="table-responsive">
            <table class="lab-table">
              <thead><tr><th></th><th>Origen</th><th>Descripción</th><th>Pendiente S/</th><th>A cobrar S/</th></tr></thead>
              <tbody>
                <tr v-for="i in cuentaActual.items.filter(x => Number(x.pendiente) > 0)" :key="i.origen+i.origen_id">
                  <td><input type="checkbox" v-model="seleccion[i.origen+i.origen_id]" /></td>
                  <td>{{ i.origen }}</td>
                  <td>{{ i.descripcion }}</td>
                  <td>{{ money(i.pendiente) }}</td>
                  <td>
                    <input v-model="montos[i.origen+i.origen_id]" type="number" class="input-clinical input-sm"
                      min="0.01" :max="i.pendiente" step="0.01" :disabled="!seleccion[i.origen+i.origen_id]" />
                  </td>
                </tr>
                <tr v-if="!cuentaActual.items.some(x => Number(x.pendiente) > 0)">
                  <td colspan="5" style="text-align:center;color:var(--ink-soft)">Esta cuenta no tiene saldo pendiente.</td>
                </tr>
              </tbody>
            </table>
          </div>

          <form class="editor-form" @submit.prevent="registrarCobro" style="margin-top:1rem;">
            <div class="form-grid">
              <div class="form-group">
                <label class="form-label">Forma de pago</label>
                <select v-model="cobroForm.forma_pago" class="input-clinical" required>
                  <option value="EFECTIVO">Efectivo</option>
                  <option value="TARJETA">Tarjeta</option>
                  <option value="TRANSFERENCIA">Transferencia</option>
                  <option value="SEGURO">Seguro</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">Fuente de financiamiento</label>
                <input v-model="cobroForm.fuente_financiamiento" class="input-clinical" maxlength="100" list="caja-seguros" />
                <datalist id="caja-seguros">
                  <option v-for="s in catalogs.seguros" :key="s.id" :value="s.nombre" />
                </datalist>
              </div>
            </div>
            <p class="total">Total a cobrar S/ {{ money(totalACobrar) }}</p>
            <div class="form-actions">
              <button class="btn-primary" :disabled="busy || totalACobrar<=0">
                <UIcon name="i-heroicons-check" class="w-4 h-4" />
                Registrar cobro
              </button>
            </div>
          </form>
        </section>

        <section v-if="ultimoCobro" class="panel">
          <h2 class="results-title">Cobro registrado</h2>
          <div class="detail-info"><p>{{ ultimoCobro.numero }} · S/ {{ money(ultimoCobro.monto) }}</p></div>
          <div class="form-actions">
            <button class="btn-secondary" @click="download('/cobros/'+ultimoCobro.id+'/comprobante.pdf', 'comprobante-caja.pdf')">
              <UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" />
              Comprobante PDF
            </button>
          </div>
        </section>
      </template>
    </template>

    <!-- ══════════════════ COMPROBANTES DE PAGO ══════════════════ -->
    <template v-else-if="mode==='comprobantes-pago'">
      <section class="panel search-panel">
        <form class="search-form" @submit.prevent="buscarCobros">
          <div class="search-grid">
            <div class="search-field"><label class="form-label">N.° comprobante</label><input v-model="filtro.numero" class="input-clinical" /></div>
            <div class="search-field"><label class="form-label">N.° cuenta</label><input v-model="filtro.cuenta" class="input-clinical" /></div>
            <div class="search-field"><label class="form-label">Fecha</label><input v-model="filtro.fecha" type="date" class="input-clinical" /></div>
            <div class="search-field">
              <label class="form-label">Estado</label>
              <select v-model="filtro.estado" class="input-clinical">
                <option value="">Todos</option><option value="registrado">Registrado</option><option value="anulado">Anulado</option>
              </select>
            </div>
            <div class="search-field">
              <label class="form-label">Forma de pago</label>
              <select v-model="filtro.forma_pago" class="input-clinical">
                <option value="">Todas</option>
                <option value="EFECTIVO">Efectivo</option><option value="TARJETA">Tarjeta</option>
                <option value="TRANSFERENCIA">Transferencia</option><option value="SEGURO">Seguro</option>
              </select>
            </div>
          </div>
          <div class="search-actions">
            <button class="btn-primary" :disabled="loading"><UIcon name="i-heroicons-magnifying-glass" class="w-4 h-4" />Buscar</button>
          </div>
        </form>
      </section>

      <section class="panel results-panel">
        <div class="results-header"><h2 class="results-title">Comprobantes · {{ total }} registros</h2></div>
        <div v-if="loading" class="loading-state"><UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" /></div>
        <div v-else class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>N.°</th><th>Fecha</th><th>Cuenta</th><th>Paciente</th><th>Forma pago</th><th>Monto S/</th><th>Estado</th><th>Acciones</th></tr></thead>
            <tbody>
              <tr v-for="c in cobrosLista" :key="c.id">
                <td>{{ c.numero }}</td><td>{{ c.created_at }}</td><td>{{ c.numero_cuenta }}</td>
                <td>{{ c.paciente || '—' }}</td><td>{{ c.forma_pago }}</td><td>{{ money(c.monto) }}</td><td>{{ c.estado }}</td>
                <td>
                  <div class="action-buttons">
                    <button class="action-btn action-view" @click="verCobro(c.id)"><UIcon name="i-heroicons-eye" class="w-4 h-4" /></button>
                    <button class="action-btn action-pdf" @click="download('/cobros/'+c.id+'/comprobante.pdf', 'comprobante-caja.pdf')"><UIcon name="i-heroicons-document-arrow-down" class="w-4 h-4" /></button>
                  </div>
                </td>
              </tr>
              <tr v-if="!cobrosLista.length"><td colspan="8" style="text-align:center;color:var(--ink-soft)">Sin comprobantes.</td></tr>
            </tbody>
          </table>
        </div>
        <nav class="pagination">
          <button class="btn-secondary btn-sm" :disabled="page<=1" @click="cambiarPagina(page-1)"><UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />Anterior</button>
          <span class="page-info">{{ page }} / {{ pages }}</span>
          <button class="btn-secondary btn-sm" :disabled="page>=pages" @click="cambiarPagina(page+1)">Siguiente<UIcon name="i-heroicons-chevron-right" class="w-4 h-4" /></button>
        </nav>
      </section>

      <section v-if="cobroDetalle" class="panel detail-panel">
        <div class="detail-header">
          <div><h2 class="detail-title">{{ cobroDetalle.numero }}</h2><p class="detail-subtitle">{{ cobroDetalle.estado }}</p></div>
          <button class="btn-secondary" @click="cobroDetalle=null"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Cerrar</button>
        </div>
        <div class="detail-info">
          <p>Cuenta {{ cobroDetalle.numero_cuenta }} · {{ cobroDetalle.paciente?.nombre || '—' }} · Caja {{ cobroDetalle.caja_nombre }} · Sesión {{ cobroDetalle.sesion_numero }}</p>
        </div>
        <div class="table-responsive">
          <table class="lab-table">
            <thead><tr><th>Origen</th><th>Descripción</th><th>Monto S/</th></tr></thead>
            <tbody><tr v-for="i in cobroDetalle.items" :key="i.id"><td>{{ i.origen }}</td><td>{{ i.descripcion }}</td><td>{{ money(i.monto) }}</td></tr></tbody>
          </table>
        </div>
        <p class="total">Total S/ {{ money(cobroDetalle.monto) }}</p>
        <form v-if="cobroDetalle.estado==='registrado'" class="cancel-form" @submit.prevent="anularCobro">
          <div class="form-group">
            <label class="form-label">Motivo de anulación</label>
            <textarea v-model="motivoAnulacion" class="input-clinical" required rows="2" maxlength="2000"></textarea>
          </div>
          <button class="btn-danger" :disabled="busy"><UIcon name="i-heroicons-x-mark" class="w-4 h-4" />Anular cobro</button>
        </form>
        <p v-if="cobroDetalle.motivo_anulacion" class="field-hint">Motivo: {{ cobroDetalle.motivo_anulacion }}</p>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
type Mode = 'mi-caja' | 'cuentas' | 'cobro-por-paciente' | 'comprobantes-pago'

const props = defineProps<{ mode: Mode }>()
const route = useRoute()
const { api } = useApi()
const endpoint = '/app/caja'

const titles = {
  'mi-caja': 'Mi Caja',
  'cuentas': 'Cuentas',
  'cobro-por-paciente': 'Cobro por Paciente',
  'comprobantes-pago': 'Comprobantes de Pago'
}

const error = ref('')
const notice = ref('')
const loading = ref(false)
const busy = ref(false)
const cargandoTurno = ref(false)

const catalogs = reactive<Record<string, any[]>>({ cajas: [], seguros: [] })

// Mi caja
const miTurno = ref<any>(null)
const aperturaForm = reactive({ caja_id: '', monto_apertura: '0', observaciones_apertura: '' })
const cierreForm = reactive({ monto_cierre_declarado: '0', observaciones_cierre: '' })

// Cuentas / cobro
const cuentaQuery = ref('')
const cuentasEncontradas = ref<any[]>([])
const cuentaActual = ref<any>(null)
const seleccion = reactive<Record<string, boolean>>({})
const montos = reactive<Record<string, string>>({})
const cobroForm = reactive({ forma_pago: 'EFECTIVO', fuente_financiamiento: '' })
const ultimoCobro = ref<any>(null)

// Comprobantes
const filtro = reactive<Record<string, any>>({ numero: '', cuenta: '', fecha: '', estado: '', forma_pago: '' })
const cobrosLista = ref<any[]>([])
const total = ref(0)
const page = ref(1)
const pageSize = ref(20)
const pages = computed(() => Math.max(1, Math.ceil(total.value / pageSize.value)))
const cobroDetalle = ref<any>(null)
const motivoAnulacion = ref('')

const money = (n: any) => Number(n || 0).toFixed(2)
const totalACobrar = computed(() => {
  if (!cuentaActual.value) return 0
  return cuentaActual.value.items.reduce((sum: number, i: any) => {
    const key = i.origen + i.origen_id
    return seleccion[key] ? sum + Number(montos[key] || 0) : sum
  }, 0)
})

function err(e: any) {
  const d = e?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map((x: any) => x.msg).join('; ')
  return 'No se pudo completar la operación.'
}

const getInitials = (name?: string) => {
  if (!name) return '??'
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)
}
const getColorPaciente = (name?: string) => {
  const colors = ['var(--teal-soft)', 'var(--purple-soft)', 'var(--navy-soft)', 'var(--amber-soft)', 'var(--green-soft)', 'var(--pink-soft)']
  if (!name) return colors[0]
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

async function run(fn: () => Promise<void>) {
  if (busy.value) return
  busy.value = true
  error.value = ''
  notice.value = ''
  try { await fn() } catch (e) { error.value = err(e) } finally { busy.value = false }
}

async function cargarTurno() {
  cargandoTurno.value = true
  try { miTurno.value = await api<any>(endpoint + '/sesiones/mi-turno') }
  catch (e) { error.value = err(e) }
  finally { cargandoTurno.value = false }
}

async function getCatalogs() {
  catalogs.cajas = await api<any[]>(endpoint + '/catalogos/cajas')
}

async function getSeguros() {
  catalogs.seguros = await api<any[]>(endpoint + '/catalogos/seguros')
}

async function abrirTurno() {
  await run(async () => {
    miTurno.value = await api(endpoint + '/sesiones', { method: 'POST', body: { ...aperturaForm, monto_apertura: Number(aperturaForm.monto_apertura) } })
    notice.value = 'Turno abierto.'
  })
}

async function cerrarTurno() {
  await run(async () => {
    miTurno.value = await api(endpoint + '/sesiones/' + miTurno.value.id + '/cerrar', {
      method: 'POST', body: { ...cierreForm, monto_cierre_declarado: Number(cierreForm.monto_cierre_declarado) }
    })
    notice.value = 'Turno cerrado.'
  })
}

async function buscarCuentas() {
  await run(async () => {
    cuentasEncontradas.value = await api<any[]>(endpoint + '/cuentas/buscar', { query: { q: cuentaQuery.value } })
    if (!cuentasEncontradas.value.length) notice.value = 'No se encontraron cuentas.'
  })
}

async function verCuenta(numero: string) {
  await run(async () => {
    cuentaActual.value = await api(endpoint + '/cuentas/' + encodeURIComponent(numero))
    cuentasEncontradas.value = []
  })
}

async function buscarCuentasPago() {
  await run(async () => {
    cuentasEncontradas.value = await api<any[]>(endpoint + '/cuentas/buscar', { query: { q: cuentaQuery.value } })
    if (!cuentasEncontradas.value.length) notice.value = 'No se encontraron cuentas.'
  })
}

async function cargarCuentaPago(numero: string) {
  await run(async () => {
    cuentaActual.value = await api(endpoint + '/cuentas/' + encodeURIComponent(numero))
    cuentasEncontradas.value = []
    ultimoCobro.value = null
    Object.keys(seleccion).forEach(k => delete seleccion[k])
    Object.keys(montos).forEach(k => delete montos[k])
    for (const i of cuentaActual.value.items) {
      const key = i.origen + i.origen_id
      if (Number(i.pendiente) > 0) { seleccion[key] = true; montos[key] = money(i.pendiente) }
    }
  })
}

async function registrarCobro() {
  await run(async () => {
    const items = cuentaActual.value.items
      .filter((i: any) => seleccion[i.origen + i.origen_id])
      .map((i: any) => ({ origen: i.origen, origen_id: i.origen_id, descripcion: i.descripcion, monto: Number(montos[i.origen + i.origen_id]) }))
    ultimoCobro.value = await api(endpoint + '/sesiones/' + miTurno.value.id + '/cobros', {
      method: 'POST',
      body: { numero_cuenta: cuentaActual.value.numero_cuenta, patient_id: cuentaActual.value.paciente?.id || null,
        forma_pago: cobroForm.forma_pago, fuente_financiamiento: cobroForm.fuente_financiamiento, items }
    })
    notice.value = 'Cobro registrado.'
    cuentaActual.value = await api(endpoint + '/cuentas/' + encodeURIComponent(cuentaActual.value.numero_cuenta))
    await cargarTurno()
  })
}

async function buscarCobros() {
  page.value = 1
  await cargarCobros()
}

async function cargarCobros() {
  loading.value = true
  error.value = ''
  try {
    const q = Object.fromEntries(Object.entries(filtro).filter(([, v]) => v))
    const data = await api<any>(endpoint + '/cobros', { query: { ...q, page: page.value, page_size: pageSize.value } })
    cobrosLista.value = data.items
    total.value = data.total
  } catch (e) { error.value = err(e) } finally { loading.value = false }
}

async function cambiarPagina(p: number) { page.value = p; await cargarCobros() }

async function verCobro(id: string) {
  await run(async () => { cobroDetalle.value = await api(endpoint + '/cobros/' + id); motivoAnulacion.value = '' })
}

async function anularCobro() {
  await run(async () => {
    cobroDetalle.value = await api(endpoint + '/cobros/' + cobroDetalle.value.id + '/anular', { method: 'POST', body: { motivo: motivoAnulacion.value } })
    notice.value = 'Cobro anulado.'
    await cargarCobros()
  })
}

async function download(path: string, name: string) {
  await run(async () => {
    const blob = await api<Blob>(endpoint + path, { responseType: 'blob' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = name; a.click()
    setTimeout(() => URL.revokeObjectURL(url), 1000)
  })
}

onMounted(async () => {
  if (props.mode === 'mi-caja') { await getCatalogs(); await cargarTurno() }
  else if (props.mode === 'cobro-por-paciente') {
    await Promise.all([cargarTurno(), getSeguros()])
    const cuenta = route.query.cuenta as string | undefined
    if (cuenta) { cuentaQuery.value = cuenta; await cargarCuentaPago(cuenta) }
  }
  else if (props.mode === 'comprobantes-pago') { await cargarCobros() }
})
</script>

<style scoped>
.lab-container { max-width: 1400px; margin: 0 auto; padding: 1.5rem 2rem; }
.page-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.5rem; flex-wrap: wrap; gap: 1rem; }
.header-left { display: flex; align-items: center; gap: 1rem; }
.header-icon { width: 48px; height: 48px; border-radius: 14px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--ink); margin: 0; line-height: 1.2; }
.breadcrumb { display: flex; flex-direction: column; }
.header-actions { display: flex; align-items: center; gap: 0.75rem; flex-wrap: wrap; }
.btn-primary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--teal); color: white; border: none; cursor: pointer; transition: all 0.2s ease; text-decoration: none; }
.btn-primary:hover:not(:disabled) { background: var(--teal-dark); transform: translateY(-1px); box-shadow: var(--shadow-md); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.btn-secondary { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.5rem 1rem; border-radius: 6px; font-size: 0.8125rem; font-weight: 500; border: 1px solid var(--line); background: var(--paper); color: var(--ink); cursor: pointer; transition: all 0.2s ease; }
.btn-secondary:hover { background: var(--mist); }
.btn-danger { display: inline-flex; align-items: center; gap: 0.5rem; padding: 0.625rem 1.5rem; border-radius: 8px; font-size: 0.875rem; font-weight: 500; background: var(--alert); color: white; border: none; cursor: pointer; transition: all 0.2s ease; }
.btn-danger:hover { background: var(--alert-dark); }
.btn-sm { padding: 0.375rem 0.75rem; font-size: 0.75rem; }
.lab-tabs { display: flex; gap: 0.25rem; border-bottom: 2px solid var(--line); margin-bottom: 1.5rem; flex-wrap: wrap; }
.tab-link { padding: 0.625rem 1.25rem; font-size: 0.875rem; font-weight: 500; color: var(--ink-soft); text-decoration: none; border-bottom: 2px solid transparent; transition: all 0.2s ease; margin-bottom: -2px; }
.tab-link:hover { color: var(--ink); }
.tab-link--active { color: var(--teal); border-bottom-color: var(--teal); }
.error-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--alert-soft); color: var(--alert); font-size: 0.875rem; margin-bottom: 1.5rem; }
.success-banner { display: flex; align-items: center; gap: 0.75rem; padding: 0.75rem 1rem; border-radius: 8px; background: var(--green-soft); color: var(--green); font-size: 0.875rem; margin-bottom: 1.5rem; }
.panel { background: var(--paper); border-radius: var(--radius-lg); border: 1px solid var(--line); padding: 1.25rem; margin-bottom: 1.5rem; box-shadow: var(--shadow-sm); }
.card-header-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; }
.status-badge { font-size: 0.75rem; font-weight: 600; color: var(--teal); background: var(--teal-soft); padding: 0.25rem 0.625rem; border-radius: 999px; }
.search-form { display: flex; flex-direction: column; gap: 1rem; }
.search-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 1rem; }
.search-field { display: flex; flex-direction: column; gap: 0.25rem; }
.search-actions { display: flex; gap: 0.75rem; justify-content: flex-end; }
.results-header { display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 1rem; margin-bottom: 1rem; }
.results-title { font-size: 1rem; font-weight: 600; color: var(--ink); margin: 0; }
.loading-state { display: flex; align-items: center; justify-content: center; padding: 2rem; }
.table-responsive { overflow-x: auto; }
.lab-table { width: 100%; border-collapse: collapse; font-size: 0.8125rem; }
.lab-table thead { background: var(--mist); }
.lab-table th { padding: 0.625rem 0.75rem; text-align: left; font-weight: 600; color: var(--ink-soft); font-size: 0.6875rem; text-transform: uppercase; letter-spacing: 0.05em; border-bottom: 1px solid var(--line); }
.lab-table td { padding: 0.625rem 0.75rem; border-bottom: 1px solid var(--line); vertical-align: middle; }
.lab-table tr:hover { background: var(--mist); }
.action-buttons { display: flex; gap: 0.25rem; }
.action-btn { display: inline-flex; align-items: center; justify-content: center; width: 28px; height: 28px; border-radius: 4px; border: 1px solid transparent; background: transparent; color: var(--ink-soft); cursor: pointer; transition: all 0.2s ease; }
.action-btn:hover { background: var(--mist); }
.action-view:hover { color: var(--teal); border-color: var(--teal-soft); background: var(--teal-soft); }
.action-pdf:hover { color: var(--alert); border-color: var(--alert-soft); background: var(--alert-soft); }
.pagination { display: flex; align-items: center; gap: 0.75rem; justify-content: center; margin-top: 1rem; padding-top: 1rem; border-top: 1px solid var(--line); }
.page-info { font-size: 0.8125rem; color: var(--ink-soft); }
.editor-form { display: flex; flex-direction: column; gap: 1rem; }
.form-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; }
.form-group.full-width { grid-column: 1 / -1; }
.form-label { display: block; font-size: 0.8125rem; font-weight: 500; color: var(--ink); margin-bottom: 0.25rem; }
.input-clinical { width: 100%; padding: 0.5rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.875rem; transition: all 0.2s ease; }
.input-clinical:focus { outline: none; border-color: var(--teal); box-shadow: 0 0 0 3px var(--teal-soft); }
.input-clinical:disabled { opacity: 0.6; cursor: not-allowed; }
.input-sm { padding: 0.375rem 0.625rem; font-size: 0.8125rem; }
.field-hint { font-size: 0.75rem; color: var(--ink-soft); margin-top: 0.25rem; }
.form-actions { display: flex; gap: 0.75rem; flex-wrap: wrap; margin-top: 0.5rem; }
.choices { display: flex; gap: 0.5rem; flex-wrap: wrap; margin: 0.75rem 0; }
.choice-btn { padding: 0.375rem 0.75rem; border-radius: 6px; border: 1px solid var(--line); background: var(--paper); color: var(--ink); font-size: 0.8125rem; cursor: pointer; transition: all 0.2s ease; }
.choice-btn:hover { background: var(--teal-soft); border-color: var(--teal); }
.patient-info-card { background: var(--paper); border-radius: var(--radius); border: 1px solid var(--line); padding: 0.75rem 1rem; margin: 0.75rem 0; }
.patient-info-header { display: flex; align-items: center; gap: 0.75rem; }
.patient-avatar { width: 40px; height: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.75rem; font-weight: 600; color: var(--ink); flex-shrink: 0; }
.patient-info { display: flex; flex-direction: column; }
.patient-name { font-size: 0.875rem; font-weight: 500; color: var(--ink); }
.patient-details { display: flex; flex-wrap: wrap; gap: 0.25rem; font-size: 0.75rem; color: var(--ink-soft); }
.patient-separator { color: var(--line); }
.total { text-align: right; font-weight: 600; font-size: 1rem; color: var(--ink); margin: 0.5rem 0; }
.detail-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.detail-title { font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0; }
.detail-subtitle { font-size: 0.875rem; color: var(--ink-soft); margin: 0.125rem 0 0 0; }
.detail-info { font-size: 0.875rem; color: var(--ink); padding: 0.5rem 0; }
.cancel-form { border-top: 1px solid var(--alert-soft); padding-top: 1rem; margin-top: 1rem; display: flex; flex-direction: column; gap: 0.75rem; }
@media (max-width: 768px) {
  .lab-container { padding: 0.75rem; }
  .page-header { flex-direction: column; align-items: flex-start; }
  .search-grid { grid-template-columns: 1fr; }
  .form-grid { grid-template-columns: 1fr; }
}
</style>
