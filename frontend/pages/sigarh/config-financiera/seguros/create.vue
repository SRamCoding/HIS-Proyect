<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/config-financiera/seguros?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Seguros</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Nuevo Seguro</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-shield-check" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">Crear Seguro</h1>
            <p class="page-subtitle">Registra un nuevo seguro o convenio</p>
          </div>
        </div>
      </div>

      <SFormCard title="Configuracion del Seguro" subtitle="Ingresa los datos del seguro o convenio"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">

        <div class="form-group full-width">
          <label class="form-label">Nombre del Seguro <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-shield-check" class="input-icon" />
            <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Seguro Integral de Salud"
              :class="{ 'input-error': errors.nombre }" @focus="errors.nombre = ''" />
          </div>
          <span v-if="errors.nombre" class="error-message">{{ errors.nombre }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">RUC <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-document" class="input-icon" />
            <input v-model="form.ruc" maxlength="11" class="input-clinical font-mono-data" placeholder="20123456789"
              :class="{ 'input-error': errors.ruc }" @focus="errors.ruc = ''" />
          </div>
          <span v-if="errors.ruc" class="error-message">{{ errors.ruc }}</span>
          <p class="field-hint">11 digitos</p>
        </div>

        <div class="form-group">
          <label class="form-label">Tipo <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-list-bullet" class="input-icon" />
            <select v-model="form.tipo" class="input-clinical">
              <option v-for="t in tiposSeguro" :key="t.value" :value="t.value">{{ t.label }}</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Cobertura (%) <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-chart-pie" class="input-icon" />
            <input v-model.number="form.porcentaje_cobertura" type="number" min="0" max="100"
              class="input-clinical font-mono-data" placeholder="100"
              :class="{ 'input-error': errors.porcentaje_cobertura }" @focus="errors.porcentaje_cobertura = ''" />
          </div>
          <span v-if="errors.porcentaje_cobertura" class="error-message">{{ errors.porcentaje_cobertura }}</span>
        </div>

        <div class="form-group">
          <label class="form-label">Contacto</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-user" class="input-icon" />
            <input v-model="form.contacto" class="input-clinical" placeholder="Ej: Juan Perez" />
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Telefono</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-phone" class="input-icon" />
            <input v-model="form.telefono" class="input-clinical" placeholder="(01) 234-5678" />
          </div>
        </div>

        <div class="form-group full-width">
          <label class="form-label">Direccion</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-map-pin" class="input-icon" />
            <input v-model="form.direccion" class="input-clinical" placeholder="Direccion de la aseguradora" />
          </div>
        </div>

        <div class="form-group full-width">
          <div class="status-toggle">
            <span class="toggle-label">Seguro Activo</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
              <span class="toggle-slider" />
            </button>
          </div>
          <p class="field-hint">Los seguros inactivos no estaran disponibles</p>
        </div>

        <SFormPreview
          :nombre="form.nombre"
          :extra="`${formatTipo(form.tipo)} · ${form.porcentaje_cobertura ?? 0}%`"
          :active="form.is_active"
          icon="i-heroicons-shield-check"
          :icon-color="getTipoColor(form.tipo)"
          :icon-bg="getTipoBgColor(form.tipo)"
        />

        <template #actions>
          <SFormActions :saving="saving" save-text="Crear Seguro" saving-text="Creando..."
            :cancel-to="`/sigarh/config-financiera/seguros?tenant=${tenantId}`"
            :show-create-another="true" @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['El RUC debe tener 11 digitos validos', 'La cobertura se expresa en porcentaje (0-100%)', 'Los seguros pueden ser de diferentes tipos', 'Los seguros inactivos no se pueden usar']" />
      <SWidgetSummary :items="[
        { label: 'Nombre', value: form.nombre },
        { label: 'RUC', value: form.ruc, mono: true },
        { label: 'Tipo', value: formatTipo(form.tipo) },
        { label: 'Cobertura', value: `${form.porcentaje_cobertura ?? 0}%` },
        { divider: true },
        { label: 'Estado', slot: 'estado' },
      ]">
        <template #estado>
          <span class="status-badge-mini" :class="form.is_active ? 'status-active-mini' : 'status-inactive-mini'">
            <span class="status-dot-mini" :class="form.is_active ? 'dot-active-mini' : 'dot-inactive-mini'" />
            {{ form.is_active ? 'Activo' : 'Inactivo' }}
          </span>
        </template>
      </SWidgetSummary>
      <SWidgetTip text="Verifica que el RUC y el porcentaje de cobertura sean correctos para evitar errores en la facturacion y atencion." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')

const form = reactive({
  nombre: '', ruc: '', tipo: 'SIS', porcentaje_cobertura: 100,
  contacto: '', telefono: '', direccion: '', is_active: true,
})
const saving = ref(false)
const error = ref('')
const errors = reactive({ nombre: '', ruc: '', porcentaje_cobertura: '' })

const tiposSeguro = [
  { value: 'SIS', label: 'SIS' }, { value: 'ESSALUD', label: 'EsSalud' }, { value: 'SOAT', label: 'SOAT' },
  { value: 'PRIVADO', label: 'Privado' }, { value: 'CONVENIO', label: 'Convenio' }, { value: 'PARTICULAR', label: 'Particular' },
]

const getTipoColor = (tipo: string) => {
  const map: Record<string, string> = { sis: 'var(--purple)', essalud: 'var(--green)', soat: 'var(--amber)', privado: 'var(--teal)', convenio: 'var(--navy)', particular: 'var(--ink-soft)' }
  return map[tipo?.toLowerCase()] || 'var(--ink-soft)'
}
const getTipoBgColor = (tipo: string) => {
  const map: Record<string, string> = { sis: 'var(--purple-soft)', essalud: 'var(--green-soft)', soat: 'var(--amber-soft)', privado: 'var(--teal-soft)', convenio: 'var(--navy-soft)', particular: 'var(--mist)' }
  return map[tipo?.toLowerCase()] || 'var(--mist)'
}
const formatTipo = (tipo: string) => {
  const map: Record<string, string> = { sis: 'SIS', essalud: 'EsSalud', soat: 'SOAT', privado: 'Privado', convenio: 'Convenio', particular: 'Particular' }
  return tipo ? (map[tipo.toLowerCase()] || tipo) : '-'
}

const validateForm = (): boolean => {
  errors.nombre = !form.nombre.trim() ? 'El nombre del seguro es requerido' : ''
  errors.ruc = !form.ruc.trim() ? 'El RUC es requerido' : !/^\d{11}$/.test(form.ruc) ? 'El RUC debe tener 11 digitos' : ''
  errors.porcentaje_cobertura = form.porcentaje_cobertura === null || form.porcentaje_cobertura === undefined
    ? 'El porcentaje de cobertura es requerido'
    : (form.porcentaje_cobertura < 0 || form.porcentaje_cobertura > 100) ? 'El porcentaje debe estar entre 0 y 100' : ''
  return !(errors.nombre || errors.ruc || errors.porcentaje_cobertura)
}

const buildBody = () => ({
  nombre: form.nombre, ruc: form.ruc, tipo: form.tipo, porcentaje_cobertura: form.porcentaje_cobertura,
  contacto: form.contacto || null, telefono: form.telefono || null, direccion: form.direccion || null,
  is_active: form.is_active,
})

const handleCreate = async (createAnother: boolean) => {
  if (!validateForm()) return
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/config-financiera/seguros', { method: 'POST', tenant: tenantId.value, body: buildBody() })
    if (createAnother) {
      Object.assign(form, { nombre: '', ruc: '', tipo: 'SIS', porcentaje_cobertura: 100, contacto: '', telefono: '', direccion: '', is_active: true })
    } else {
      router.push(`/sigarh/config-financiera/seguros?tenant=${tenantId.value}`)
    }
  } catch (e: any) { error.value = apiErr(e, 'Error al guardar') }
  finally { saving.value = false }
}
</script>
