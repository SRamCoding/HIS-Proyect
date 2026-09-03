<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/rrhh/justificaciones?tenant=${tenantId}`" style="color: var(--ink-soft)">Justificaciones</NuxtLink>
        <span>/</span><span>Crear</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Nueva Justificacion</h1>
    </div>

    <div class="p-6" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Empleado*</label>
          <select v-model="form.empleado_id" class="input-clinical">
            <option value="">Seleccione un empleado</option>
            <option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre_completo }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Motivo de Justificacion</label>
          <select v-model="form.motivo_id" class="input-clinical">
            <option value="">Sin motivo especifico</option>
            <option v-for="m in motivos" :key="m.id" :value="m.id">{{ m.nombre }}</option>
          </select>
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha Inicio*</label>
            <input v-model="form.fecha_inicio" type="date" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha Fin*</label>
            <input v-model="form.fecha_fin" type="date" class="input-clinical" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Descripcion</label>
          <textarea v-model="form.descripcion" class="input-clinical" rows="3" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Estado</label>
          <select v-model="form.estado" class="input-clinical">
            <option value="pendiente">Pendiente</option>
            <option value="aprobado">Aprobado</option>
            <option value="rechazado">Rechazado</option>
          </select>
        </div>
      </div>
      <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>
      <div class="flex gap-3 mt-6">
        <button class="btn-primary" :disabled="saving" @click="handleCreate">{{ saving ? 'Guardando...' : 'Crear' }}</button>
        <NuxtLink :to="`/sigarh/rrhh/justificaciones?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')
const empleados = ref<any[]>([])
const motivos = ref<any[]>([])
const form = reactive({ empleado_id: '', motivo_id: '', fecha_inicio: '', fecha_fin: '', descripcion: '', estado: 'pendiente' })
const handleCreate = async () => {
  if (!form.empleado_id) { error.value = 'El empleado es requerido'; return }
  if (!form.fecha_inicio || !form.fecha_fin) { error.value = 'Las fechas son requeridas'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/rrhh/justificaciones', {
      method: 'POST',
      body: { ...form, motivo_id: form.motivo_id || null }
    })
    router.push(`/sigarh/rrhh/justificaciones?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear' }
  finally { saving.value = false }
}
onMounted(async () => {
  const [emp, mot] = await Promise.all([
    api<any[]>('/sigarh/rrhh/empleados'),
    api<any[]>('/sigarh/rrhh/motivos-justificacion'),
  ])
  empleados.value = emp
  motivos.value = mot
})
</script>