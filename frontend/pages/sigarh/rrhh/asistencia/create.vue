<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/rrhh/asistencia?tenant=${tenantId}`" style="color: var(--ink-soft)">Registro de Asistencia</NuxtLink>
        <span>/</span><span>Registrar</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Registrar Asistencia</h1>
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
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha*</label>
          <input v-model="form.fecha" type="date" class="input-clinical" />
        </div>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Hora de Entrada</label>
            <input v-model="form.hora_entrada" type="time" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Hora de Salida</label>
            <input v-model="form.hora_salida" type="time" class="input-clinical" />
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Estado</label>
          <select v-model="form.estado" class="input-clinical">
            <option value="presente">Presente</option>
            <option value="ausente">Ausente</option>
            <option value="tardanza">Tardanza</option>
            <option value="justificado">Justificado</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Observacion</label>
          <textarea v-model="form.observacion" class="input-clinical" rows="2" />
        </div>
      </div>
      <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>
      <div class="flex gap-3 mt-6">
        <button class="btn-primary" :disabled="saving" @click="handleCreate(false)">{{ saving ? 'Guardando...' : 'Registrar' }}</button>
        <button class="px-4 py-2 rounded text-sm font-medium" style="border: 1px solid var(--line); color: var(--ink)" :disabled="saving" @click="handleCreate(true)">Registrar otro</button>
        <NuxtLink :to="`/sigarh/rrhh/asistencia?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
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
const form = reactive({
  empleado_id: '',
  fecha: new Date().toISOString().split('T')[0],
  hora_entrada: '',
  hora_salida: '',
  estado: 'presente',
  observacion: '',
})
const handleCreate = async (createAnother: boolean) => {
  if (!form.empleado_id) { error.value = 'El empleado es requerido'; return }
  if (!form.fecha) { error.value = 'La fecha es requerida'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/rrhh/asistencia', {
      method: 'POST',
      body: {
        ...form,
        hora_entrada: form.hora_entrada || null,
        hora_salida: form.hora_salida || null,
        observacion: form.observacion || null,
      }
    })
    if (createAnother) {
      Object.assign(form, { empleado_id: '', hora_entrada: '', hora_salida: '', estado: 'presente', observacion: '' })
    } else {
      router.push(`/sigarh/rrhh/asistencia?tenant=${tenantId.value}`)
    }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo registrar' }
  finally { saving.value = false }
}
onMounted(async () => {
  empleados.value = await api<any[]>('/sigarh/rrhh/empleados')
})
</script>