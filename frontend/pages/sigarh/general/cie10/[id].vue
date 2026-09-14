<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Detalle del diagnóstico CIE-10' })
type Dx = { codigo_cie10: string; codigo_cie9: string | null; descripcion: string; capitulo: string | null; grupo: string | null; categoria: string | null; sexo: string; edad_minima: number | null; edad_maxima: number | null; is_active: boolean }
const { api } = useApi()
const route = useRoute()
const tenant = route.query.tenant as string
const dx = ref<Dx | null>(null)
const loading = ref(true)
const error = ref('')
async function load() {
  loading.value = true; error.value = ''
  try { dx.value = await api<Dx>(`/sigarh/general/cie10/${route.params.id}`, { tenant }) }
  catch (e: any) { error.value = e?.data?.detail || 'No se pudo cargar el diagnóstico' }
  finally { loading.value = false }
}
onMounted(load)
</script>

<template>
  <div class="sigarh-form-container">
    <div class="mb-6 flex items-center gap-3">
      <NuxtLink :to="`/sigarh/general/cie10?tenant=${tenant}`" class="text-gray-400 hover:text-gray-600"><UIcon name="i-heroicons-arrow-left" class="h-5 w-5" /></NuxtLink>
      <div><h1 class="text-xl font-semibold text-gray-800">Detalle del diagnóstico CIE-10</h1><p class="mt-0.5 text-sm text-gray-500">Información oficial del catálogo MINSA</p></div>
    </div>
    <div v-if="loading" class="form-card flex items-center justify-center gap-3 py-16 text-gray-400"><UIcon name="i-heroicons-arrow-path" class="h-6 w-6 animate-spin" /> Cargando diagnóstico...</div>
    <div v-else-if="error" class="form-card text-center text-red-600"><p>{{ error }}</p><button class="mt-4 rounded-lg border border-red-200 px-3 py-1.5 text-sm" @click="load">Reintentar</button></div>
    <div v-else-if="dx" class="form-card max-w-4xl">
      <div class="mb-6 flex flex-wrap items-start justify-between gap-4 border-b border-gray-100 pb-5">
        <div><span class="font-mono text-2xl font-bold text-teal-700">{{ dx.codigo_cie10 }}</span><h2 class="mt-2 text-lg font-semibold text-gray-900">{{ dx.descripcion }}</h2></div>
        <span :class="dx.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'" class="rounded-full px-3 py-1 text-sm font-medium">{{ dx.is_active ? 'Vigente' : 'Inactivo' }}</span>
      </div>
      <dl class="grid grid-cols-1 gap-5 md:grid-cols-2">
        <div class="md:col-span-2"><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Capítulo</dt><dd class="mt-1 text-sm text-gray-800">{{ dx.capitulo || 'No especificado' }}</dd></div>
        <div class="md:col-span-2"><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Grupo</dt><dd class="mt-1 text-sm text-gray-800">{{ dx.grupo || 'No especificado' }}</dd></div>
        <div class="md:col-span-2"><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Categoría</dt><dd class="mt-1 text-sm text-gray-800">{{ dx.categoria || 'No especificada' }}</dd></div>
        <div><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Código CIE-9 relacionado</dt><dd class="mt-1 text-sm text-gray-800">{{ dx.codigo_cie9 || '—' }}</dd></div>
        <div><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Aplicación por sexo</dt><dd class="mt-1 text-sm capitalize text-gray-800">{{ dx.sexo }}</dd></div>
        <div><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Edad mínima</dt><dd class="mt-1 text-sm text-gray-800">{{ dx.edad_minima ?? 'Sin restricción' }}</dd></div>
        <div><dt class="text-xs font-semibold uppercase tracking-wide text-gray-500">Edad máxima</dt><dd class="mt-1 text-sm text-gray-800">{{ dx.edad_maxima ?? 'Sin restricción' }}</dd></div>
      </dl>
      <div class="mt-6 flex justify-end border-t border-gray-100 pt-5"><NuxtLink :to="`/sigarh/general/cie10?tenant=${tenant}`" class="rounded-lg bg-[#1e3a5f] px-4 py-2 text-sm font-medium text-white">Volver al catálogo</NuxtLink></div>
    </div>
  </div>
</template>
