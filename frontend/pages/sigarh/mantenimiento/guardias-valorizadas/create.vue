<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/mantenimiento/guardias-valorizadas?tenant=${tenantId}`" style="color: var(--ink-soft)">Guardias Valorizadas</NuxtLink>
        <span>/</span><span>Crear</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Nueva Guardia Valorizada</h1>
    </div>

    <div class="p-6" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Tipo de Guardia</label>
          <select v-model="form.tipo_guardia_id" class="input-clinical">
            <option value="">Seleccionar...</option>
            <option v-for="t in tiposGuardia" :key="t.id" :value="t.id">{{ t.nombre }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Grupo Ocupacional</label>
          <select v-model="form.grupo_ocupacional_id" class="input-clinical">
            <option value="">Seleccionar...</option>
            <option v-for="g in gruposOcupacionales" :key="g.id" :value="g.id">{{ g.nombre }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nivel Remunerativo</label>
          <select v-model="form.nivel_remunerativo_id" class="input-clinical">
            <option value="">Seleccionar...</option>
            <option v-for="n in nivelesRemunerativos" :key="n.id" :value="n.id">{{ n.nombre }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Valor (S/.)*</label>
          <input v-model.number="form.valor" type="number" step="0.01" class="input-clinical" placeholder="0.00" />
        </div>
        <div class="flex items-center gap-2">
          <input type="checkbox" v-model="form.is_active" id="activo" />
          <label for="activo" class="text-sm" style="color: var(--ink)">Activo</label>
        </div>
      </div>
      <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>
      <div class="flex gap-3 mt-6">
        <button class="btn-primary" :disabled="saving" @click="handleCreate(false)">{{ saving ? 'Guardando...' : 'Crear' }}</button>
        <button class="px-4 py-2 rounded text-sm font-medium" style="border: 1px solid var(--line); color: var(--ink)" :disabled="saving" @click="handleCreate(true)">Crear y crear otro</button>
        <NuxtLink :to="`/sigarh/mantenimiento/guardias-valorizadas?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">Cancelar</NuxtLink>
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
const tiposGuardia = ref<any[]>([])
const gruposOcupacionales = ref<any[]>([])
const nivelesRemunerativos = ref<any[]>([])
const form = reactive({ tipo_guardia_id: '', grupo_ocupacional_id: '', nivel_remunerativo_id: '', valor: 0, is_active: true })
const handleCreate = async (createAnother: boolean) => {
  if (!form.valor) { error.value = 'El valor es requerido'; return }
  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/guardias-valorizadas', {
      method: 'POST',
      body: {
        ...form,
        tipo_guardia_id: form.tipo_guardia_id || null,
        grupo_ocupacional_id: form.grupo_ocupacional_id || null,
        nivel_remunerativo_id: form.nivel_remunerativo_id || null,
      }
    })
    if (createAnother) { Object.assign(form, { tipo_guardia_id: '', grupo_ocupacional_id: '', nivel_remunerativo_id: '', valor: 0, is_active: true }) }
    else { router.push(`/sigarh/mantenimiento/guardias-valorizadas?tenant=${tenantId.value}`) }
  } catch (e: any) { error.value = e?.data?.detail || 'No se pudo crear' }
  finally { saving.value = false }
}
onMounted(async () => {
  const [tg, go, nr] = await Promise.all([
    api<any[]>('/sigarh/mantenimiento/tipos-guardia'),
    api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
    api<any[]>('/sigarh/mantenimiento/niveles-remunerativos'),
  ])
  tiposGuardia.value = tg
  gruposOcupacionales.value = go
  nivelesRemunerativos.value = nr
})
</script>