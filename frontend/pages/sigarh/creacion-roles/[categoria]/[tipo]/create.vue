<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const { modalidadLabel, tipoValido, MESES } = useRolesTurno()
const tenantId = computed(() => route.query.tenant as string || '')
const categoria = computed(() => route.params.categoria as string)
const tipo = computed(() => route.params.tipo as string)

const saving = ref(false)
const error = ref('')
const departamentos = ref<any[]>([])
const servicios = ref<any[]>([])
const now = new Date()
const form = reactive({ departamento_id: '', servicio_id: '', mes: now.getMonth() + 1, anio: now.getFullYear() })

const serviciosFiltrados = computed(() =>
  form.departamento_id ? servicios.value.filter(s => s.departamento_id === form.departamento_id) : servicios.value
)

const crear = async () => {
  if (!form.departamento_id) { error.value = 'El departamento es requerido'; return }
  if (!form.servicio_id) { error.value = 'El servicio es requerido'; return }
  saving.value = true; error.value = ''
  try {
    const rol = await api<any>('/sigarh/creacion-roles/roles', {
      method: 'POST',
      body: { categoria_personal: categoria.value, tipo_rol: tipo.value, ...form },
    })
    router.push(`/sigarh/creacion-roles/${categoria.value}/${tipo.value}/${rol.id}?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear el rol' }
  finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [deps, servs] = await Promise.all([
      api<any[]>('/sigarh/mantenimiento/departamentos').catch(() => []),
      api<any[]>('/sigarh/mantenimiento/servicios').catch(() => []),
    ])
    departamentos.value = deps
    servicios.value = servs
  } catch { error.value = 'Error al cargar catálogos' }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/creacion-roles/${categoria}/${tipo}?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Roles</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" />
          <span style="color: var(--ink)">Nuevo Rol</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--navy-soft)">
            <UIcon name="i-heroicons-calendar-days" class="w-6 h-6" style="color: var(--navy)" />
          </div>
          <div>
            <h1 class="page-title">Nuevo Rol</h1>
            <p class="page-subtitle">{{ modalidadLabel(categoria, tipo) }}</p>
          </div>
        </div>
      </div>

      <div v-if="!tipoValido(categoria, tipo)" class="form-card" style="color: var(--alert)">Modalidad no válida.</div>

      <SFormCard v-else title="Datos generales del rol" subtitle="Define el ámbito y el período de la programación"
        icon="i-heroicons-cog-6-tooth" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="error">

        <div class="form-group">
          <label class="form-label">Departamento <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-building-office-2" class="input-icon" />
            <select v-model="form.departamento_id" class="input-clinical" @change="form.servicio_id = ''; error = ''">
              <option value="">Seleccione un departamento</option>
              <option v-for="d in departamentos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
            </select>
          </div>
          <p class="field-hint">Al cambiarlo se limpia el servicio</p>
        </div>

        <div class="form-group">
          <label class="form-label">Servicio <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-squares-2x2" class="input-icon" />
            <select v-model="form.servicio_id" class="input-clinical" :disabled="!form.departamento_id" @change="error = ''">
              <option value="">Seleccione un servicio</option>
              <option v-for="s in serviciosFiltrados" :key="s.id" :value="s.id">{{ s.nombre }}</option>
            </select>
          </div>
          <p class="field-hint">Determina qué personal se ofrece para agregar</p>
        </div>

        <div class="form-group">
          <label class="form-label">Mes de cobertura <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-calendar" class="input-icon" />
            <select v-model.number="form.mes" class="input-clinical">
              <option v-for="m in 12" :key="m" :value="m">{{ MESES[m] }}</option>
            </select>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label">Año <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-hashtag" class="input-icon" />
            <input v-model.number="form.anio" type="number" min="2000" max="2100" class="input-clinical font-mono-data" />
          </div>
        </div>

        <template #actions>
          <SFormActions :saving="saving" save-text="Crear y continuar" saving-text="Creando..."
            :cancel-to="`/sigarh/creacion-roles/${categoria}/${tipo}?tenant=${tenantId}`"
            @save="crear" />
        </template>
      </SFormCard>
    </template>

    <template #sidebar>
      <SWidgetInfo :items="[
        'Primero defines departamento, servicio y período',
        'Luego agregas personal, sus actividades y los turnos de cada actividad',
        'El rol se guarda como borrador; después usas Enviar para pasarlo a revisión',
        'Un rol enviado ya no se puede editar hasta que sea rechazado',
      ]" />
      <SWidgetTip text="En la modalidad médica ordinaria no se permite más de un rol por departamento, servicio y período." />
    </template>
  </SFormLayout>
</template>
