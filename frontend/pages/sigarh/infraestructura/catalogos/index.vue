<template>
  <div class="sigarh-index-container">

    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-swatch" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Catálogos</h1>
          <p class="page-subtitle">Opciones de las listas desplegables del sistema</p>
        </div>
      </div>
      <NuxtLink :to="`/sigarh/infraestructura/catalogos/create?tenant=${tenantId}`" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nueva Opción
      </NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-swatch" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.length }}</div>
          <div class="sigarh-stat-label">Total Opciones</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-rectangle-group" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ categoriasUsadas }}</div>
          <div class="sigarh-stat-label">Categorías con datos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ activeCount }}</div>
          <div class="sigarh-stat-label">Activas</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.length - activeCount }}</div>
          <div class="sigarh-stat-label">Inactivas</div>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="search" type="text" placeholder="Buscar por nombre o codigo..." class="sigarh-search-input" />
          </div>
          <select v-model="filtroCategoria" class="input-clinical" style="max-width: 240px; padding-left: 0.75rem;">
            <option value="">Todas las categorías</option>
            <option v-for="c in categorias" :key="c" :value="c">{{ fmtCategoria(c) }}</option>
          </select>
        </div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span class="sigarh-result-count">{{ filteredItems.length }} resultados</span>
          <button v-if="search || filtroCategoria" @click="search = ''; filtroCategoria = ''" class="sigarh-clear-btn">Limpiar</button>
        </div>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
        <p style="color: var(--ink-soft)">Cargando catálogos...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button @click="cargar" class="btn-outline">Reintentar</button>
      </div>
      <div v-else-if="!filteredItems.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-swatch" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">Sin opciones registradas</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Comienza agregando una opción a un catálogo</p>
        </div>
        <NuxtLink :to="`/sigarh/infraestructura/catalogos/create?tenant=${tenantId}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Nueva Opción
        </NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th style="width: 20%">Categoría</th>
              <th style="width: 12%">Código</th>
              <th style="width: 24%">Nombre</th>
              <th style="width: 24%">Descripción</th>
              <th style="width: 8%">Orden</th>
              <th style="width: 6%">Estado</th>
              <th style="width: 6%; text-align: right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredItems" :key="item.id">
              <td><span class="badge badge--neutral">{{ fmtCategoria(item.categoria) }}</span></td>
              <td>
                <span v-if="item.codigo" class="sigarh-code-badge">{{ item.codigo }}</span>
                <span v-else style="color: var(--ink-soft)">-</span>
              </td>
              <td class="sigarh-item-name">{{ item.nombre }}</td>
              <td style="color: var(--ink-soft); font-size: 0.8125rem">{{ item.descripcion || '-' }}</td>
              <td style="font-family: monospace; color: var(--ink-soft)">{{ item.orden }}</td>
              <td>
                <span class="badge" :class="item.is_active ? 'badge--ok' : 'badge--neutral'">
                  {{ item.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td style="text-align: right">
                <div class="sigarh-actions">
                  <NuxtLink :to="`/sigarh/infraestructura/catalogos/${item.id}?tenant=${tenantId}`" class="sigarh-action-btn" title="Editar">
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" />
                  </NuxtLink>
                  <button class="sigarh-action-btn danger" title="Eliminar" @click="eliminar(item)">
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        <div class="sigarh-table-footer">
          Mostrando <strong>{{ filteredItems.length }}</strong> de <strong>{{ items.length }}</strong> opciones
        </div>
      </div>
    </div>

  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

interface Item {
  id: string
  categoria: string
  codigo: string | null
  nombre: string
  descripcion: string | null
  orden: number
  is_active: boolean
}

const { api } = useApi()
const route = useRoute()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const categorias = ref<string[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const filtroCategoria = ref('')

const fmtCategoria = (c: string) => c.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())
const activeCount = computed(() => items.value.filter(i => i.is_active).length)
const categoriasUsadas = computed(() => new Set(items.value.map(i => i.categoria)).size)

const filteredItems = computed(() => {
  let r = items.value
  if (filtroCategoria.value) r = r.filter(i => i.categoria === filtroCategoria.value)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    r = r.filter(i => i.nombre.toLowerCase().includes(q) || (i.codigo || '').toLowerCase().includes(q))
  }
  return r
})

const eliminar = async (item: Item) => {
  if (!confirm(`Eliminar la opción "${item.nombre}"?`)) return
  try {
    await api(`/sigarh/infraestructura/catalogos/${item.id}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id !== item.id)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    const [lista, cats] = await Promise.all([
      api<Item[]>('/sigarh/infraestructura/catalogos'),
      api<{ categorias: string[] }>('/sigarh/infraestructura/catalogos/categorias').catch(() => ({ categorias: [] })),
    ])
    items.value = lista
    categorias.value = cats.categorias
  } catch (e: any) { error.value = apiErr(e, 'Error de conexion') }
  finally { loading.value = false }
}

onMounted(cargar)
</script>
