<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const form = reactive({
  codigo: '', nombre: '', tipo: 'farmacia', fuente_financiamiento: '',
  ubicacion_fisica: '', despacha_recetas: true, is_active: true,
})

const TIPOS = { farmacia: 'Farmacia', almacen_central: 'Almacén Central', laboratorio: 'Laboratorio', dispensacion: 'Dispensación' }
const FUENTES = { sismed: 'SISMED', donaciones: 'Donaciones', mixto: 'Mixto' }

const handleCreate = async (otro: boolean) => {
  if (!form.codigo.trim()) { error.value = 'El código es requerido'; return }
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true; error.value = ''
  try {
    await api('/sigarh/config-farmacia/almacenes', { method: 'POST', body: {
      codigo: form.codigo, nombre: form.nombre, tipo: form.tipo,
      fuente_financiamiento: form.fuente_financiamiento || null,
      ubicacion_fisica: form.ubicacion_fisica || null,
      despacha_recetas: form.despacha_recetas, is_active: form.is_active,
    } })
    if (otro) Object.assign(form, { codigo: '', nombre: '', tipo: 'farmacia', fuente_financiamiento: '', ubicacion_fisica: '', despacha_recetas: true, is_active: true })
    else router.push(`/sigarh/config-farmacia/almacenes?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo crear el almacén') }
  finally { saving.value = false }
}
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/config-farmacia/almacenes?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Almacenes</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Nuevo</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)"><UIcon name="i-heroicons-building-storefront" class="w-6 h-6" style="color: var(--navy)" /></div>
          <div><h1 class="page-title">Nuevo Almacén / Farmacia</h1><p class="page-subtitle">Registra un establecimiento que maneja existencias</p></div>
        </div>
      </div>

      <SFormCard title="Datos del Almacén" subtitle="Identificación y clasificación"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">
        <div class="form-group">
          <label class="form-label">Código interno <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-hashtag" class="input-icon" /><input v-model="form.codigo" class="input-clinical font-mono-data" maxlength="20" placeholder="Ej: FAR-001" @focus="error = ''" /></div>
          <p class="field-hint">Máximo 20 caracteres, único. Se guarda en mayúsculas.</p>
        </div>
        <div class="form-group">
          <label class="form-label">Nombre <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-building-storefront" class="input-icon" /><input v-model="form.nombre" class="input-clinical" maxlength="100" placeholder="Ej: Farmacia Principal" @focus="error = ''" /></div>
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
          <div class="input-wrapper"><UIcon name="i-heroicons-map-pin" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.ubicacion_fisica" class="input-clinical" rows="2" placeholder="Ej: Piso 1, ala norte" /></div>
          <p class="field-hint">Es texto libre: no se vincula con pisos, salas ni camas.</p>
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
          <SFormActions :saving="saving" save-text="Crear" saving-text="Creando..."
            :cancel-to="`/sigarh/config-farmacia/almacenes?tenant=${tenantId}`" :show-create-another="true"
            @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
    </template>
    <template #sidebar>
      <SWidgetInfo :items="['Registrar un almacén no le asigna existencias: eso ocurre por los procesos de inventario', 'Solo los activos que despachan recetas aparecen en el despacho', 'El código debe ser único dentro del hospital', 'No se puede eliminar un almacén con stock mayor que cero']" />
      <SWidgetTip text="Usa prefijos consistentes: FAR- para farmacias, ALM- para almacenes, DIS- para dispensación." />
    </template>
  </SFormLayout>
</template>
