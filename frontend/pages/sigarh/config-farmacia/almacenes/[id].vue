<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const form = reactive({
  codigo: '', nombre: '', tipo: 'farmacia', fuente_financiamiento: '',
  ubicacion_fisica: '', despacha_recetas: true, is_active: true,
})

const TIPOS = { farmacia: 'Farmacia', almacen_central: 'Almacén Central', laboratorio: 'Laboratorio', dispensacion: 'Dispensación' }
const FUENTES = { sismed: 'SISMED', donaciones: 'Donaciones', mixto: 'Mixto' }

const handleSave = async () => {
  if (!form.codigo.trim()) { error.value = 'El código es requerido'; return }
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true; error.value = ''
  try {
    await api(`/sigarh/config-farmacia/almacenes/${id.value}`, { method: 'PATCH', body: {
      codigo: form.codigo, nombre: form.nombre, tipo: form.tipo,
      fuente_financiamiento: form.fuente_financiamiento || null,
      ubicacion_fisica: form.ubicacion_fisica || null,
      despacha_recetas: form.despacha_recetas, is_active: form.is_active,
    } })
    router.push(`/sigarh/config-farmacia/almacenes?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const d = await api<any>(`/sigarh/config-farmacia/almacenes/${id.value}`)
    form.codigo = d.codigo; form.nombre = d.nombre; form.tipo = d.tipo || 'farmacia'
    form.fuente_financiamiento = d.fuente_financiamiento || ''
    form.ubicacion_fisica = d.ubicacion_fisica || ''
    form.despacha_recetas = d.despacha_recetas; form.is_active = d.is_active
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/config-farmacia/almacenes?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Almacenes</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Editar</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-building-storefront" class="w-6 h-6" style="color: var(--navy)" /></div>
          <div><h1 class="page-title">{{ form.nombre || 'Editar Almacén' }}</h1><p class="page-subtitle">Actualiza los datos del establecimiento</p></div>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--navy)" /></div>
      <SFormCard v-else title="Datos del Almacén" subtitle="Identificación y clasificación"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">
        <div class="form-group">
          <label class="form-label">Código interno <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-hashtag" class="input-icon" /><input v-model="form.codigo" class="input-clinical font-mono-data" maxlength="20" @focus="error = ''" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Nombre <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-building-storefront" class="input-icon" /><input v-model="form.nombre" class="input-clinical" maxlength="100" @focus="error = ''" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Tipo <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-tag" class="input-icon" />
            <select v-model="form.tipo" class="input-clinical"><option v-for="(t, k) in TIPOS" :key="k" :value="k">{{ t }}</option></select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Fuente de financiamiento</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-banknotes" class="input-icon" />
            <select v-model="form.fuente_financiamiento" class="input-clinical">
              <option value="">Sin especificar</option>
              <option v-for="(f, k) in FUENTES" :key="k" :value="k">{{ f }}</option>
            </select>
          </div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Ubicación física</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-map-pin" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.ubicacion_fisica" class="input-clinical" rows="2" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Despacha recetas médicas</label>
          <div class="status-toggle"><span class="toggle-label">Disponible en el selector de despacho</span>
            <button type="button" @click="form.despacha_recetas = !form.despacha_recetas" class="toggle-switch" :class="{ 'toggle-active': form.despacha_recetas }"><span class="toggle-slider" /></button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Estado</label>
          <div class="status-toggle"><span class="toggle-label">Almacén Activo</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }"><span class="toggle-slider" /></button>
          </div>
        </div>
        <template #actions>
          <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
            :cancel-to="`/sigarh/config-farmacia/almacenes?tenant=${tenantId}`" @save="handleSave" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetSummary :items="[
        { label: 'Código', value: form.codigo, mono: true },
        { label: 'Tipo', value: TIPOS[form.tipo] },
        { label: 'Financiamiento', value: form.fuente_financiamiento ? FUENTES[form.fuente_financiamiento] : '—' },
        { divider: true },
        { label: 'Despacha recetas', value: form.despacha_recetas ? 'Sí' : 'No' },
        { label: 'Estado', value: form.is_active ? 'Activo' : 'Inactivo' },
      ]" />
      <SWidgetInfo :items="['No se puede eliminar si tiene existencias con stock mayor que cero', 'Desactivarlo lo saca de los selectores pero conserva su historial de movimientos']" />
    </template>
  </SFormLayout>
</template>
