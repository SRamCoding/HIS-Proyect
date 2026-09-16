<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const { CATEGORIAS_PERSONAL, MODALIDADES, tipoLabel, modalidadLabel, periodoLabel } = useRolesTurno()
const tenantId = computed(() => route.query.tenant as string || '')

const items = ref<any[]>([])
const loading = ref(true)
const error = ref('')
const fCat = ref('')
const fTipo = ref('')
const fAnio = ref<number | ''>('')
const fMes = ref<number | ''>('')
const tiposFiltro = computed(() => fCat.value ? (MODALIDADES[fCat.value] || []) : [])

const cargar = async () => {
  loading.value = true; error.value = ''
  const q = new URLSearchParams()
  if (fCat.value) q.set('categoria', fCat.value)
  if (fTipo.value) q.set('tipo', fTipo.value)
  if (fAnio.value) q.set('anio', String(fAnio.value))
  if (fMes.value) q.set('mes', String(fMes.value))
  try { items.value = await api<any[]>(`/sigarh/roles-aprobados/roles?${q}`) }
  catch (e: any) { error.value = apiErr(e, 'Error de conexión') }
  finally { loading.value = false }
}
watch([fCat, fTipo, fAnio, fMes], cargar)
onMounted(cargar)
</script>

<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-badge" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <h1 class="page-title">Roles Aprobados</h1>
          <p class="page-subtitle">Programación autorizada</p>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left" style="flex-wrap: wrap">
          <select v-model="fCat" class="input-clinical" style="max-width: 220px; padding-left: 0.75rem" @change="fTipo = ''">
            <option value="">Todas las categorías</option>
            <option v-for="c in CATEGORIAS_PERSONAL" :key="c.key" :value="c.key">{{ c.label }}</option>
          </select>
          <select v-model="fTipo" class="input-clinical" style="max-width: 220px; padding-left: 0.75rem" :disabled="!fCat">
            <option value="">Todas las modalidades</option>
            <option v-for="t in tiposFiltro" :key="t" :value="t">{{ tipoLabel(t) }}</option>
          </select>
          <input v-model.number="fAnio" type="number" placeholder="Año" class="input-clinical font-mono-data" style="max-width: 110px; padding-left: 0.75rem" />
          <select v-model.number="fMes" class="input-clinical" style="max-width: 140px; padding-left: 0.75rem">
            <option value="">Mes</option>
            <option v-for="m in 12" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
        <span class="sigarh-result-count">{{ items.length }} aprobados</span>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--green)" />
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
      </div>
      <div v-else-if="!items.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-check-circle" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <p style="color: var(--ink-soft)">No hay roles aprobados</p>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 22%">Modalidad</th>
              <th style="width: 18%">Servicio</th>
              <th style="width: 12%">Período</th>
              <th style="width: 9%">Personal</th>
              <th style="width: 16%">Aprobado por</th>
              <th style="width: 13%">Fecha aprob.</th>
              <th style="width: 10%; text-align: right"></th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="it in items" :key="it.id">
              <td style="font-size: 0.8rem">{{ modalidadLabel(it.categoria_personal, it.tipo_rol) }}</td>
              <td class="sigarh-item-name">{{ it.servicio_nombre || '—' }}</td>
              <td style="font-size: 0.8125rem">{{ periodoLabel(it.mes, it.anio) }}</td>
              <td style="font-family: monospace; color: var(--ink-soft)">{{ it.total_empleados }}</td>
              <td style="font-size: 0.8125rem; color: var(--ink-soft)">{{ it.reviewed_by || '—' }}</td>
              <td style="font-size: 0.75rem; color: var(--ink-soft)">{{ it.reviewed_at ? new Date(it.reviewed_at).toLocaleDateString('es-PE') : '—' }}</td>
              <td style="text-align: right">
                <NuxtLink :to="`/sigarh/roles-aprobados/${it.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Ver">
                  <UIcon name="i-heroicons-eye" class="w-4 h-4" style="color: var(--teal)" />
                </NuxtLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>
