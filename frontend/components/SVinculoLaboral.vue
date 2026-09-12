<script setup lang="ts">
const emit = defineEmits<{ valido: [value: boolean] }>()
const codigo = defineModel<string>({ default: '' })
const { api } = useApi()
const route = useRoute()
interface Vinculo { codigo: string; regimen_codigo: string; regimen_nombre: string; condicion_nombre: string; norma: string; fuente_url: string }
const catalogo = ref<Vinculo[]>([])
const regimen = ref('')
const loading = ref(true)
const error = ref('')
const seleccionado = computed(() => catalogo.value.find(v => v.codigo === codigo.value))
const regimenes = computed(() => [...new Map(catalogo.value.map(v => [v.regimen_codigo, v.regimen_nombre])).entries()])
const condiciones = computed(() => catalogo.value.filter(v => v.regimen_codigo === regimen.value))
watch([regimen, codigo, seleccionado, loading, error], () => emit('valido', !loading.value && !error.value &&
  ((!regimen.value && !codigo.value) || seleccionado.value?.regimen_codigo === regimen.value)), { immediate: true })
watch(seleccionado, v => { if (v) regimen.value = v.regimen_codigo }, { immediate: true })
function cambiarRegimen() { codigo.value = condiciones.value.length === 1 ? condiciones.value[0]!.codigo : '' }
async function cargar() {
  loading.value = true
  error.value = ''
  try { catalogo.value = await api<Vinculo[]>('/sigarh/rrhh/vinculos-laborales', { tenant: route.query.tenant }) }
  catch { error.value = 'No se pudo cargar el catálogo laboral.' }
  finally { loading.value = false }
}
onMounted(cargar)
</script>

<template>
  <div class="col-span-full rounded-xl border border-slate-200 p-4 space-y-3">
    <p class="font-semibold text-slate-700">Régimen y condición laboral</p>
    <p class="text-sm text-slate-500">Selecciona el vínculo que figura en el contrato o resolución del trabajador.</p>
    <p v-if="loading" class="text-sm text-slate-500">Cargando catálogo…</p>
    <div v-else-if="error" class="text-sm text-red-600" role="alert">{{ error }} <button type="button" class="underline" @click="cargar">Reintentar</button></div>
    <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <label class="space-y-1"><span class="text-sm">Régimen laboral</span>
        <select v-model="regimen" class="input-clinical" @change="cambiarRegimen"><option value="">Sin registrar</option><option v-for="[id, nombre] in regimenes" :key="id" :value="id">{{ nombre }}</option></select>
      </label>
      <label class="space-y-1"><span class="text-sm">Condición laboral</span>
        <select v-model="codigo" class="input-clinical" :disabled="!regimen"><option value="">Seleccione</option><option v-for="v in condiciones" :key="v.codigo" :value="v.codigo">{{ v.condicion_nombre }}</option></select>
      </label>
    </div>
    <p v-if="seleccionado" class="text-xs text-slate-500">Base normativa: <a :href="seleccionado.fuente_url" target="_blank" rel="noopener noreferrer" class="underline">{{ seleccionado.norma }}</a></p>
    <p class="text-xs text-slate-500">La duración y demás condiciones del contrato se verifican en el documento laboral.</p>
  </div>
</template>
