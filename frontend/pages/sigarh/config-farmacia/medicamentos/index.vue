<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
interface Item {
  id: string; codigo_interno: string; nombre_comercial: string; nombre_generico: string | null
  presentacion: string | null; unidad: string | null; concentracion: string | null
  forma_farmaceutica: string | null; condicion_venta: string | null; tipo_producto_nombre: string | null
  controlado: boolean; fiscalizado_digemid: boolean; reporte_sismed: boolean
  requiere_cadena_frio: boolean; stock_minimo_alerta: number; is_active: boolean
}
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const f = reactive({ condicion_venta: '', forma_farmaceutica: '', controlado: '', fiscalizado_digemid: '', reporte_sismed: '', requiere_cadena_frio: '', estado: 'active' })

const CV: Record<string, string> = { sin_receta: 'Sin receta', receta_simple: 'Receta simple', receta_retenida: 'Receta retenida', control_medico: 'Control médico' }
const FF: Record<string, string> = { tableta: 'Tableta', capsula: 'Cápsula', ampolla: 'Ampolla', frasco_ampolla: 'Frasco ampolla', jarabe: 'Jarabe', suspension: 'Suspensión', solucion: 'Solución', crema: 'Crema', pomada: 'Pomada', gel: 'Gel', parche: 'Parche', supositorio: 'Supositorio', colirio: 'Colirio', inhalador: 'Inhalador', polvo_reconstituir: 'Polvo p/ reconstituir', otro: 'Otro' }

const cargar = async () => {
  loading.value = true; error.value = ''
  const q = new URLSearchParams()
  if (search.value.trim()) q.set('search', search.value.trim())
  if (f.estado !== 'all') q.set('is_active', String(f.estado === 'active'))
  if (f.condicion_venta) q.set('condicion_venta', f.condicion_venta)
  if (f.forma_farmaceutica) q.set('forma_farmaceutica', f.forma_farmaceutica)
  for (const k of ['controlado', 'fiscalizado_digemid', 'reporte_sismed', 'requiere_cadena_frio'] as const) {
    if ((f as any)[k]) q.set(k, (f as any)[k])
  }
  try { items.value = await api<Item[]>(`/sigarh/config-farmacia/medicamentos?${q}`) }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
const eliminar = async (it: Item) => {
  if (!confirm(`Desactivar el producto "${it.nombre_comercial}"?`)) return
  try { await api(`/sigarh/config-farmacia/medicamentos/${it.id}`, { method: 'DELETE' }); cargar() }
  catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}
let t: any
watch([search, () => ({ ...f })], () => { clearTimeout(t); t = setTimeout(cargar, 300) }, { deep: true })
onMounted(cargar)
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-beaker" class="w-5 h-5" style="color: var(--teal)" /></div>
        <div><h1 class="page-title">Medicamentos e Insumos</h1><p class="page-subtitle">Catálogo de productos que utiliza el hospital</p></div>
      </div>
      <NuxtLink :to="`/sigarh/config-farmacia/medicamentos/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Producto</NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-beaker" class="w-5 h-5" style="color: var(--teal)" /></div>
        <div><div class="sigarh-stat-value">{{ items.length }}</div><div class="sigarh-stat-label">Productos</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--alert)">
        <div class="sigarh-stat-icon" style="background: var(--alert-soft, #fde8e8)"><UIcon name="i-heroicons-lock-closed" class="w-5 h-5" style="color: var(--alert)" /></div>
        <div><div class="sigarh-stat-value">{{ items.filter(i => i.controlado).length }}</div><div class="sigarh-stat-label">Controlados</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--navy)">
        <div class="sigarh-stat-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-shield-check" class="w-5 h-5" style="color: var(--navy)" /></div>
        <div><div class="sigarh-stat-value">{{ items.filter(i => i.fiscalizado_digemid).length }}</div><div class="sigarh-stat-label">Fiscalizados DIGEMID</div></div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)"><UIcon name="i-heroicons-snowflake" class="w-5 h-5" style="color: var(--purple)" /></div>
        <div><div class="sigarh-stat-value">{{ items.filter(i => i.requiere_cadena_frio).length }}</div><div class="sigarh-stat-label">Cadena de frío</div></div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left" style="flex-wrap: wrap; gap: 0.5rem">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Nombre, código, DCI..." class="sigarh-search-input" />
          </div>
          <select v-model="f.condicion_venta" class="input-clinical" style="max-width: 150px; padding-left: 0.75rem">
            <option value="">Condición: todas</option><option v-for="(v, k) in CV" :key="k" :value="k">{{ v }}</option>
          </select>
          <select v-model="f.forma_farmaceutica" class="input-clinical" style="max-width: 150px; padding-left: 0.75rem">
            <option value="">Forma: todas</option><option v-for="(v, k) in FF" :key="k" :value="k">{{ v }}</option>
          </select>
          <select v-model="f.controlado" class="input-clinical" style="max-width: 130px; padding-left: 0.75rem"><option value="">Controlado</option><option value="true">Sí</option><option value="false">No</option></select>
          <select v-model="f.fiscalizado_digemid" class="input-clinical" style="max-width: 120px; padding-left: 0.75rem"><option value="">DIGEMID</option><option value="true">Sí</option><option value="false">No</option></select>
          <select v-model="f.reporte_sismed" class="input-clinical" style="max-width: 120px; padding-left: 0.75rem"><option value="">SISMED</option><option value="true">Sí</option><option value="false">No</option></select>
          <select v-model="f.requiere_cadena_frio" class="input-clinical" style="max-width: 130px; padding-left: 0.75rem"><option value="">Cadena frío</option><option value="true">Sí</option><option value="false">No</option></select>
          <div class="sigarh-filter-group">
            <button @click="f.estado = 'active'" class="sigarh-filter-btn" :class="{ active: f.estado === 'active' }">Activos</button>
            <button @click="f.estado = 'inactive'" class="sigarh-filter-btn" :class="{ active: f.estado === 'inactive' }">Inactivos</button>
            <button @click="f.estado = 'all'" class="sigarh-filter-btn" :class="{ active: f.estado === 'all' }">Todos</button>
          </div>
        </div>
        <span class="sigarh-result-count">{{ items.length }} resultados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" /></div>
      <div v-else-if="error" class="sigarh-table-state"><UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" /><p style="color: var(--alert)">{{ error }}</p><button @click="cargar" class="btn-outline">Reintentar</button></div>
      <div v-else-if="!items.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-beaker" class="w-12 h-12" style="color: var(--ink-soft); opacity: .4" />
        <p style="color: var(--ink-soft)">Sin productos para el filtro seleccionado</p>
        <NuxtLink :to="`/sigarh/config-farmacia/medicamentos/create?tenant=${tenantId}`" class="btn-primary"><UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo</NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead><tr>
            <th style="width: 11%">Código</th><th style="width: 26%">Producto</th><th style="width: 13%">Presentación</th>
            <th style="width: 11%">Forma</th><th style="width: 13%">Cond. venta</th><th style="width: 12%">Marcas</th>
            <th style="width: 7%">Mín.</th><th style="width: 7%; text-align: right">Acc.</th>
          </tr></thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td><span class="sigarh-code-badge">{{ it.codigo_interno }}</span></td>
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-beaker" class="w-4 h-4" style="color: var(--teal)" /></div>
                  <div>
                    <span class="sigarh-item-name">{{ it.nombre_comercial }}</span>
                    <div style="font-size: 0.72rem; color: var(--ink-soft)">{{ it.nombre_generico }}<span v-if="it.concentracion"> · {{ it.concentracion }}</span></div>
                  </div>
                </div>
              </td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.presentacion || '—' }}</td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ FF[it.forma_farmaceutica || ''] || '—' }}</td>
              <td><span class="badge badge--neutral">{{ CV[it.condicion_venta || ''] || '—' }}</span></td>
              <td>
                <div style="display: flex; gap: 0.2rem; flex-wrap: wrap">
                  <span v-if="it.controlado" class="badge badge--danger" title="Controlado">C</span>
                  <span v-if="it.fiscalizado_digemid" class="badge badge--warning" title="Fiscalizado DIGEMID">D</span>
                  <span v-if="it.reporte_sismed" class="badge badge--ok" title="Reporta SISMED">S</span>
                  <span v-if="it.requiere_cadena_frio" class="badge" style="background: var(--purple-soft); color: var(--purple)" title="Cadena de frío">❄</span>
                  <span v-if="!it.is_active" class="badge badge--neutral">Inactivo</span>
                </div>
              </td>
              <td class="font-mono-data" style="font-size: 0.8125rem">{{ it.stock_minimo_alerta }}</td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/config-farmacia/medicamentos/${it.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar"><UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" /></NuxtLink>
                  <button v-if="it.is_active" class="sigarh-action-btn danger" title="Desactivar" @click="eliminar(it)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" /></button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">Marcas: <strong>C</strong> controlado · <strong>D</strong> DIGEMID · <strong>S</strong> SISMED · <strong>❄</strong> cadena de frío</div>
      </div>
    </div>
  </div>
</template>
