<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Entrega de Raciones' })
const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string
const dni = ref('')
const fecha = ref(new Date().toISOString().split('T')[0])
const racion = ref<any>(null)
const buscando = ref(false)
const entregando = ref(false)
const mensaje = ref('')

async function buscar() {
  if (!dni.value || dni.value.length < 8) return
  buscando.value = true; racion.value = null; mensaje.value = ''
  try {
    racion.value = await $api('/sigarh/nutricion/raciones/buscar', {
      method: 'POST', tenant, body: { dni: dni.value, fecha: fecha.value }
    })
    if (!racion.value) mensaje.value = 'No se encontró ración para este DNI en la fecha seleccionada'
  } finally { buscando.value = false }
}

async function entregar() {
  if (!racion.value) return
  entregando.value = true
  try {
    await $api(`/sigarh/nutricion/raciones/${racion.value.id}/entregar`, { method: 'POST', tenant })
    racion.value.entregado = true
    racion.value.fecha_entrega = new Date().toISOString()
    mensaje.value = '✓ Ración entregada correctamente'
  } finally { entregando.value = false }
}
</script>
<template>
  <div class="p-6 max-w-lg space-y-4">
    <div><h1 class="text-xl font-semibold text-gray-800">Entrega de Raciones</h1><p class="text-sm text-gray-500 mt-0.5">Busca al personal por DNI para registrar la entrega</p></div>
    <div class="bg-white rounded-xl border border-gray-200 p-5 space-y-4">
      <div class="grid grid-cols-2 gap-3">
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">DNI del Personal</label>
          <div class="flex gap-2">
            <input v-model="dni" type="text" maxlength="8" placeholder="Ingrese DNI" @keyup.enter="buscar"
              class="flex-1 px-3 py-2 border border-gray-200 rounded-lg text-sm" />
            <button @click="buscar" :disabled="buscando"
              class="px-4 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#1e3a5f">
              {{ buscando ? '...' : 'Buscar' }}
            </button>
          </div>
        </div>
        <div class="col-span-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">Fecha</label>
          <input v-model="fecha" type="date" class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" />
        </div>
      </div>

      <div v-if="mensaje" class="p-3 rounded-lg text-sm" :class="racion?.entregado ? 'bg-green-50 text-green-700' : 'bg-yellow-50 text-yellow-700'">{{ mensaje }}</div>

      <div v-if="racion" class="border border-gray-100 rounded-lg p-4 space-y-2">
        <div class="flex justify-between"><span class="text-xs text-gray-500">Nombre</span><span class="text-sm font-medium">{{ racion.nombre_completo }}</span></div>
        <div class="flex justify-between"><span class="text-xs text-gray-500">Dependencia</span><span class="text-sm text-gray-600">{{ racion.dependencia }}</span></div>
        <div class="flex justify-between"><span class="text-xs text-gray-500">Tipo Ración</span><span class="px-2 py-0.5 bg-orange-50 text-orange-700 rounded text-xs">{{ racion.tipo_racion }}</span></div>
        <div class="flex justify-between"><span class="text-xs text-gray-500">Estado</span>
          <span :class="racion.entregado ? 'text-green-600' : 'text-yellow-600'" class="text-sm font-medium">
            {{ racion.entregado ? '✓ Entregado' : 'Pendiente' }}
          </span>
        </div>
        <button v-if="!racion.entregado" @click="entregar" :disabled="entregando"
          class="w-full mt-2 py-2 rounded-lg text-sm font-medium text-white disabled:opacity-50" style="background:#10b981">
          {{ entregando ? 'Registrando...' : 'Confirmar Entrega' }}
        </button>
      </div>
    </div>
  </div>
</template>