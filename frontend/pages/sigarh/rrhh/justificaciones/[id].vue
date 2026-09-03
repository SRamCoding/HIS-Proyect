<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/rrhh/justificaciones?tenant=${tenantId}`" style="color: var(--ink-soft)">Justificaciones</NuxtLink>
        <span>/</span><span>Detalle</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Detalle de Justificacion</h1>
    </div>

    <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>

    <template v-else>
      <div class="p-6 space-y-4" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Empleado</label>
            <p class="text-sm" style="color: var(--ink-soft)">{{ form.empleado_nombre || '—' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Motivo</label>
            <p class="text-sm" style="color: var(--ink-soft)">{{ form.motivo_nombre || '—' }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha Inicio</label>
            <p class="text-sm font-mono" style="color: var(--ink-soft)">{{ form.fecha_inicio }}</p>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha Fin</label>
            <p class="text-sm font-mono" style="color: var(--ink-soft)">{{ form.fecha_fin }}</p>
          </div>
          <div class="col-span-2">
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Descripcion</label>
            <p class="text-sm" style="color: var(--ink-soft)">{{ form.descripcion || '—' }}</p>
          </div>
        </div>

        <div>
          <label class="block text-sm font-medium mb-2" style="color: var(--ink)">Estado</label>
          <select v-model="form.estado" class="input-clinical max-w-xs">
            <option value="pendiente">Pendiente</option>
            <option value="aprobado">Aprobado</option>
            <option value="rechazado">Rechazado</option>
          </select>
        </div>

        <div v-if="error" class="text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>

        <div class="flex gap-3 pt-2">
          <button class="btn-primary" :disabled="saving" @click="handleSave">{{ saving ? 'Guardando...' : 'Actualizar Estado' }}</button>
          <NuxtLink :to="`/sigarh/rrhh/justificaciones?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Volver</NuxtLink>
        </div>
      </div>
    </template>
  </div>
</template>

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
  empleado_nombre: '',
  motivo_nombre: '',
  fecha_inicio: '',
  fecha_fin: '',
  descripcion: '',
  estado: 'pendiente',
})
const handleSave = async () => {
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/rrhh/justificaciones/${id.value}`, { method: 'PATCH', body: { estado: form.estado } })
    router.push(`/sigarh/rrhh/justificaciones?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo guardar' }
  finally { saving.value = false }
}
onMounted(async () => {
  try {
    const data = await api<any>(`/sigarh/rrhh/justificaciones/${id.value}`)
    form.empleado_nombre = data.empleado_nombre || ''
    form.motivo_nombre = data.motivo_nombre || ''
    form.fecha_inicio = data.fecha_inicio
    form.fecha_fin = data.fecha_fin
    form.descripcion = data.descripcion || ''
    form.estado = data.estado
  } catch { error.value = 'No se pudo cargar' }
  finally { loading.value = false }
})
</script>