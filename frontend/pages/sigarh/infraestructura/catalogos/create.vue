<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/infraestructura/catalogos?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Catálogos</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Nueva Opción</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)">
            <UIcon name="i-heroicons-swatch" class="w-6 h-6" style="color: var(--teal)" />
          </div>
          <div>
            <h1 class="page-title">Nueva Opción de Catálogo</h1>
            <p class="page-subtitle">Registra un valor para una lista desplegable del sistema</p>
          </div>
        </div>
      </div>

      <SFormCard title="Datos de la Opción" subtitle="Selecciona la categoría y define el valor"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">

        <div class="form-group full-width">
          <label class="form-label">Categoría <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-rectangle-group" class="input-icon" />
            <select v-model="form.categoria" class="input-clinical" @change="error = ''">
              <option value="">Seleccione una categoría</option>
              <option v-for="c in categorias" :key="c" :value="c">{{ fmtCategoria(c) }}</option>
            </select>
          </div>
          <p class="field-hint">Define a qué lista pertenece esta opción</p>
        </div>

        <div class="form-group full-width">
          <label class="form-label">Nombre <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-tag" class="input-icon" />
            <input v-model="form.nombre" class="input-clinical" maxlength="100" placeholder="Texto que verá el usuario" @focus="error = ''" />
          </div>
          <p class="field-hint">Máximo 100 caracteres</p>
        </div>

        <div class="form-group">
          <label class="form-label">Código</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-barcode" class="input-icon" />
            <input v-model="form.codigo" class="input-clinical font-mono-data" maxlength="20" placeholder="Identificador técnico" />
          </div>
          <p class="field-hint">Máximo 20 caracteres</p>
        </div>

        <div class="form-group">
          <label class="form-label">Orden</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-bars-arrow-down" class="input-icon" />
            <input v-model.number="form.orden" type="number" min="0" class="input-clinical font-mono-data" @input="form.orden = Math.max(0, Math.floor(form.orden || 0))" />
          </div>
          <p class="field-hint">Posición en la lista de opciones</p>
        </div>

        <div class="form-group">
          <label class="form-label">Estado</label>
          <div class="status-toggle">
            <span class="toggle-label">Opción Activa</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }">
              <span class="toggle-slider" />
            </button>
          </div>
        </div>

        <div class="form-group full-width">
          <label class="form-label">Descripcion</label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-document-text" class="input-icon" style="top: 0.75rem; transform: none;" />
            <textarea v-model="form.descripcion" class="input-clinical" rows="2" maxlength="255" placeholder="Explicación adicional (máx. 255)" />
          </div>
        </div>

        <SFormPreview
          :nombre="form.nombre"
          :codigo="form.codigo"
          :extra="form.categoria ? fmtCategoria(form.categoria) : ''"
          :active="form.is_active"
          icon="i-heroicons-swatch"
          icon-color="var(--teal)"
          icon-bg="var(--teal-soft)"
        />

        <template #actions>
          <SFormActions :saving="saving" save-text="Crear Opción" saving-text="Creando..."
            :cancel-to="`/sigarh/infraestructura/catalogos?tenant=${tenantId}`"
            :show-create-another="true" @save="handleCreate(false)" @save-another="handleCreate(true)" />
        </template>
      </SFormCard>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="['Los módulos que consultan esta categoría recuperan sus valores activos ordenados por Orden', 'Crear una opción no crea funcionalidad nueva, solo agrega un valor a la lista', 'El código es un identificador técnico opcional', 'Las opciones inactivas no aparecen en los selectores']" />
      <SWidgetSummary :items="[
        { label: 'Categoría', value: form.categoria ? fmtCategoria(form.categoria) : '' },
        { label: 'Nombre', value: form.nombre },
        { label: 'Código', value: form.codigo, mono: true },
        { label: 'Orden', value: String(form.orden ?? 0), mono: true },
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
      <SWidgetTip text="Usa el campo Orden para controlar cómo se listan las opciones en los formularios que las consumen." />
    </template>
  </SFormLayout>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const categorias = ref<string[]>([])
const form = reactive({ categoria: '', codigo: '', nombre: '', descripcion: '', orden: 0, is_active: true })

const fmtCategoria = (c: string) => c.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())

const handleCreate = async (createAnother: boolean) => {
  if (!form.categoria) { error.value = 'La categoría es requerida'; return }
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/infraestructura/catalogos', {
      method: 'POST',
      body: {
        categoria: form.categoria,
        codigo: form.codigo || null,
        nombre: form.nombre,
        descripcion: form.descripcion || null,
        orden: form.orden || 0,
        is_active: form.is_active,
      },
    })
    if (createAnother) { Object.assign(form, { codigo: '', nombre: '', descripcion: '', orden: 0, is_active: true }) }
    else { router.push(`/sigarh/infraestructura/catalogos?tenant=${tenantId.value}`) }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const cats = await api<{ categorias: string[] }>('/sigarh/infraestructura/catalogos/categorias')
    categorias.value = cats.categorias
    if (route.query.categoria && categorias.value.includes(route.query.categoria as string)) {
      form.categoria = route.query.categoria as string
    }
  } catch {}
})
</script>
