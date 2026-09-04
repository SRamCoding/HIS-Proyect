<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Catálogos' })
const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string

const lista = ref<any[]>([])
const loading = ref(true)
const categoriaActiva = ref('')

const CATEGORIAS = [
  'tipos_documento', 'tipos_servicio', 'modalidades_atencion',
  'estados_cita', 'tipos_diagnostico', 'tipos_alta',
  'procedencia_emergencia', 'tipos_grupo_ocupacional', 'metodos_pago',
  'tipos_producto', 'estados_emergencia', 'destino_atencion',
  'tipos_comprobante', 'estados_comprobante',
]

async function cargar() {
  loading.value = true
  try {
    const q = categoriaActiva.value ? `?categoria=${categoriaActiva.value}` : ''
    lista.value = await $api(`/sigarh/infraestructura/catalogos${q}`, { tenant })
  } finally { loading.value = false }
}
onMounted(cargar)
watch(categoriaActiva, cargar)
</script>

<template>
  <div class="p-6 space-y-4">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-gray-800">Catálogos</h1>
        <p class="text-sm text-gray-500 mt-0.5">Catálogos genéricos del sistema</p>
      </div>
      <NuxtLink :to="`/sigarh/infraestructura/catalogos/create?tenant=${tenant}`">
        <button class="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-white" style="background:#1e3a5f">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nuevo Catálogo
        </button>
      </NuxtLink>
    </div>

    <!-- Tabs de categorías -->
    <div class="flex gap-2 flex-wrap">
      <button
        @click="categoriaActiva = ''"
        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
        :class="categoriaActiva === '' ? 'text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'"
        :style="categoriaActiva === '' ? 'background:#1e3a5f' : ''"
      >Todos</button>
      <button
        v-for="cat in CATEGORIAS" :key="cat"
        @click="categoriaActiva = cat"
        class="px-3 py-1.5 rounded-lg text-xs font-medium transition-colors"
        :class="categoriaActiva === cat ? 'text-white' : 'bg-white border border-gray-200 text-gray-600 hover:bg-gray-50'"
        :style="categoriaActiva === cat ? 'background:#1e3a5f' : ''"
      >{{ cat.replace(/_/g, ' ') }}</button>
    </div>

    <div class="bg-white rounded-xl border border-gray-200 overflow-hidden">
      <div v-if="loading" class="p-8 text-center text-gray-400">Cargando...</div>
      <div v-else-if="!lista.length" class="p-8 text-center text-gray-400">No hay registros</div>
      <table v-else class="w-full text-sm">
        <thead>
          <tr class="border-b border-gray-100 bg-gray-50">
            <th class="text-left px-4 py-3 font-medium text-gray-600">Categoría</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Código</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Nombre</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Descripción</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Orden</th>
            <th class="text-left px-4 py-3 font-medium text-gray-600">Activo</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in lista" :key="c.id" class="border-b border-gray-50 hover:bg-gray-50">
            <td class="px-4 py-3"><span class="px-2 py-0.5 bg-blue-50 text-blue-700 rounded text-xs">{{ c.categoria }}</span></td>
            <td class="px-4 py-3 text-gray-600 font-mono text-xs">{{ c.codigo }}</td>
            <td class="px-4 py-3 font-medium">{{ c.nombre }}</td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ c.descripcion }}</td>
            <td class="px-4 py-3 text-gray-600">{{ c.orden }}</td>
            <td class="px-4 py-3">
              <span :class="c.is_active ? 'text-green-600' : 'text-gray-400'">
                <UIcon :name="c.is_active ? 'i-heroicons-check-circle' : 'i-heroicons-x-circle'" class="w-4 h-4" />
              </span>
            </td>
            <td class="px-4 py-3">
              <NuxtLink :to="`/sigarh/infraestructura/catalogos/${c.id}?tenant=${tenant}`"
                class="text-blue-600 hover:underline text-xs">Editar</NuxtLink>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>