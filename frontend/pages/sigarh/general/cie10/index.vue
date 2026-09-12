<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Diagnósticos CIE-10' })
type Dx = { id: string; codigo_cie10: string; descripcion: string; categoria: string | null; is_active: boolean }
type Page = { items: Dx[]; total: number; page: number; page_size: number; pages: number }

const { api } = useApi()
const route = useRoute()
const tenant = route.query.tenant as string
const items = ref<Dx[]>([])
const search = ref('')
const page = ref(1)
const pageSize = ref(25)
const total = ref(0)
const pages = ref(1)
const loading = ref(true)
const error = ref('')
let timer: ReturnType<typeof setTimeout> | undefined
let requestId = 0

const from = computed(() => total.value ? (page.value - 1) * pageSize.value + 1 : 0)
const to = computed(() => Math.min(page.value * pageSize.value, total.value))
const visiblePages = computed(() => {
  const start = Math.max(1, Math.min(page.value - 2, pages.value - 4))
  const end = Math.min(pages.value, start + 4)
  return Array.from({ length: Math.max(0, end - start + 1) }, (_, i) => start + i)
})

async function load() {
  const current = ++requestId
  loading.value = true
  error.value = ''
  try {
    const params = new URLSearchParams({ page: String(page.value), page_size: String(pageSize.value) })
    if (search.value.trim()) params.set('q', search.value.trim())
    const data = await api<Page>(`/sigarh/general/cie10?${params}`, { tenant })
    if (current !== requestId) return
    items.value = data.items
    total.value = data.total
    pages.value = data.pages
  } catch (e: any) {
    if (current !== requestId) return
    items.value = []
    total.value = 0
    error.value = e?.data?.detail || 'No se pudo cargar el catálogo CIE-10'
  } finally {
    if (current === requestId) loading.value = false
  }
}

function go(value: number) {
  if (value < 1 || value > pages.value || value === page.value) return
  page.value = value
  load()
}

watch(search, () => {
  page.value = 1
  clearTimeout(timer)
  timer = setTimeout(load, 400)
})
watch(pageSize, () => { page.value = 1; load() })
onMounted(load)
onBeforeUnmount(() => clearTimeout(timer))
</script>

<template>
  <div class="sigarh-index-container">
    <header class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon bg-teal-50 text-teal-600"><UIcon name="i-heroicons-document-magnifying-glass" class="h-6 w-6" /></div>
        <div>
          <h1 class="text-xl font-semibold text-gray-800">Diagnósticos CIE-10</h1>
          <p class="mt-0.5 text-sm text-gray-500">Catálogo oficial MINSA · {{ total.toLocaleString('es-PE') }} códigos</p>
        </div>
      </div>
    </header>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" class="sigarh-search-input" placeholder="Código, diagnóstico o categoría..." autocomplete="off">
          </div>
          <button v-if="search" class="sigarh-clear-btn" @click="search = ''">Limpiar</button>
        </div>
        <label class="flex items-center gap-2 text-sm text-gray-500">Filas
          <select v-model.number="pageSize" class="rounded-lg border border-gray-200 bg-white px-2 py-1.5 text-gray-700">
            <option :value="25">25</option><option :value="50">50</option><option :value="100">100</option>
          </select>
        </label>
      </div>

      <div v-if="loading" class="sigarh-table-state text-gray-400"><UIcon name="i-heroicons-arrow-path" class="h-7 w-7 animate-spin" /><span>Cargando diagnósticos...</span></div>
      <div v-else-if="error" class="sigarh-table-state text-red-600"><UIcon name="i-heroicons-exclamation-circle" class="h-7 w-7" /><span>{{ error }}</span><button class="rounded-lg border border-red-200 px-3 py-1.5 text-sm" @click="load">Reintentar</button></div>
      <div v-else-if="!items.length" class="sigarh-table-state text-gray-400"><UIcon name="i-heroicons-magnifying-glass" class="h-7 w-7" /><span>No se encontraron diagnósticos</span></div>
      <div v-else class="overflow-x-auto">
        <table class="sigarh-table">
          <thead><tr><th>Código</th><th>Diagnóstico</th><th>Categoría</th><th>Estado</th><th class="text-right">Detalle</th></tr></thead>
          <tbody>
            <tr v-for="dx in items" :key="dx.id">
              <td class="font-mono font-semibold text-teal-700">{{ dx.codigo_cie10 }}</td>
              <td class="font-medium">{{ dx.descripcion }}</td>
              <td class="max-w-md text-gray-600">{{ dx.categoria || '—' }}</td>
              <td><span :class="dx.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-100 text-gray-500'" class="inline-flex rounded-full px-2 py-1 text-xs font-medium">{{ dx.is_active ? 'Vigente' : 'Inactivo' }}</span></td>
              <td class="text-right"><NuxtLink :to="`/sigarh/general/cie10/${dx.id}?tenant=${tenant}`" class="inline-flex items-center gap-1 text-sm font-medium text-teal-700 hover:underline">Ver <UIcon name="i-heroicons-chevron-right" class="h-4 w-4" /></NuxtLink></td>
            </tr>
          </tbody>
        </table>
      </div>

      <footer v-if="!loading && !error && total" class="flex flex-wrap items-center justify-between gap-3 border-t border-gray-100 px-4 py-3">
        <p class="text-sm text-gray-500">Mostrando {{ from.toLocaleString('es-PE') }}–{{ to.toLocaleString('es-PE') }} de {{ total.toLocaleString('es-PE') }}</p>
        <nav class="flex items-center gap-1" aria-label="Paginación CIE-10">
          <button class="rounded-lg border border-gray-200 p-2 disabled:opacity-40" :disabled="page === 1" aria-label="Página anterior" @click="go(page - 1)"><UIcon name="i-heroicons-chevron-left" class="h-4 w-4" /></button>
          <button v-for="number in visiblePages" :key="number" :class="number === page ? 'border-teal-600 bg-teal-600 text-white' : 'border-gray-200 text-gray-600 hover:bg-gray-50'" class="min-w-9 rounded-lg border px-3 py-1.5 text-sm" @click="go(number)">{{ number }}</button>
          <button class="rounded-lg border border-gray-200 p-2 disabled:opacity-40" :disabled="page === pages" aria-label="Página siguiente" @click="go(page + 1)"><UIcon name="i-heroicons-chevron-right" class="h-4 w-4" /></button>
        </nav>
      </footer>
    </div>
  </div>
</template>
