<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/rrhh/especialidades?tenant=${tenantId}`" style="color: var(--ink-soft)">Especialidades</NuxtLink>
        <span>/</span><span>Crear</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Crear Especialidad</h1>
    </div>

    <div class="p-6" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <p class="text-sm font-semibold mb-1 flex items-center gap-2" style="color: var(--ink)">
        🎓 Configuracion de Especialidad
      </p>
      <p class="text-xs mb-5" style="color: var(--ink-soft)">Defina las areas medicas disponibles en el centro de salud.</p>

      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nombre de la Especialidad*</label>
          <input v-model="form.nombre" class="input-clinical" placeholder="Ej: Cardiologia, Pediatria, Ginecologia" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Codigo Interno</label>
          <input v-model="form.codigo" class="input-clinical" placeholder="Ej: CARD-01" />
        </div>
      </div>

      <div class="mb-4">
        <div class="flex items-center gap-2 mb-1">
          <input type="checkbox" v-model="form.is_active" id="activo" />
          <label for="activo" class="text-sm font-medium" style="color: var(--ink)">Especialidad Activa</label>
        </div>
        <p class="text-xs ml-6" style="color: var(--ink-soft)">Si se desactiva, no podra ser asignada a nuevos medicos o citas.</p>
      </div>

      <div>
        <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Descripcion / Notas adicionales</label>
        <textarea v-model="form.descripcion" class="input-clinical" rows="3" placeholder="Breve descripcion sobre el alcance de esta especialidad..." />
      </div>

      <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>

      <div class="flex gap-3 mt-6">
        <button class="btn-primary" :disabled="saving" @click="handleCreate(false)">{{ saving ? 'Guardando...' : 'Crear' }}</button>
        <button class="px-4 py-2 rounded text-sm font-medium" style="border: 1px solid var(--line); color: var(--ink)" :disabled="saving" @click="handleCreate(true)">Crear y crear otro</button>
        <NuxtLink :to="`/sigarh/rrhh/especialidades?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
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
const form = reactive({ nombre: '', codigo: '', descripcion: '', is_active: true })
const handleCreate = async (createAnother: boolean) => {
  if (!form.nombre.trim()) { error.value = 'El nombre es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/rrhh/especialidades', { method: 'POST', body: { ...form } })
    if (createAnother) { Object.assign(form, { nombre: '', codigo: '', descripcion: '', is_active: true }) }
    else { router.push(`/sigarh/rrhh/especialidades?tenant=${tenantId.value}`) }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear' }
  finally { saving.value = false }
}
</script>