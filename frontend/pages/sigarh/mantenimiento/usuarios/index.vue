<template>
  <div class="page-container">
    <PageHeader
      title="Usuarios"
      subtitle="Usuarios del sistema SIGARH"
      icon="i-heroicons-user"
      icon-color="var(--teal)"
      icon-bg="var(--teal-soft)"
    >
      <template #actions>
        <NuxtLink :to="`/sigarh/mantenimiento/usuarios/create?tenant=${tenantId}`" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Nuevo Usuario
        </NuxtLink>
      </template>
    </PageHeader>

    <DashboardStats :items="statsItems" />

    <FilterBar
      v-model:search="search"
      :filters="filters"
      v-model:activeFilter="activeFilter"
      :total-count="items.length"
      :result-count="`${filteredItems.length} resultados`"
      :show-clear="filteredItems.length < items.length || search || activeFilter !== 'all'"
      @clear="clearFilters"
    />

    <DataTable
      :data="filteredItems"
      :columns="columns"
      :loading="loading"
      :error="error"
      empty-icon="i-heroicons-user"
      empty-title="No hay usuarios registrados"
      empty-message="Comienza creando un usuario del sistema"
      @retry="cargar"
    >
      <template #cell-username="{ row }">
        <div class="user-cell" :style="{ display: 'flex', alignItems: 'center', gap: '0.625rem' }">
          <div class="user-avatar" :style="{
            width: '32px',
            height: '32px',
            borderRadius: '50%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '0.6875rem',
            fontWeight: 600,
            color: 'var(--ink)',
            flexShrink: 0,
            background: getUserColor(row.username)
          }">
            {{ getInitials(row.username) }}
          </div>
          <span style="font-weight: 500; color: var(--ink)">{{ row.username }}</span>
        </div>
      </template>

      <template #cell-email="{ row }">
        <span style="color: var(--ink-soft)">{{ row.email }}</span>
      </template>

      <template #cell-status="{ row }">
        <span class="badge" :class="row.is_active ? 'badge--ok' : 'badge--neutral'">
          {{ row.is_active ? 'Activo' : 'Inactivo' }}
        </span>
      </template>

      <template #cell-actions="{ row }">
        <ActionButtons :actions="getActions(row)" />
      </template>
    </DataTable>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-content" :style="{
        maxWidth: '420px',
        width: '100%',
        padding: '1.5rem',
        boxShadow: 'var(--shadow-lg)',
        background: 'var(--paper)',
        borderRadius: 'var(--radius-lg)'
      }">
        <div class="modal-header" :style="{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }">
          <div class="modal-icon" :style="{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0,
            background: 'var(--alert-soft)'
          }">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" style="color: var(--alert)" />
          </div>
          <h3 class="modal-title" style="font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0">Confirmar Eliminación</h3>
        </div>
        <p class="modal-body" style="color: var(--ink); margin-bottom: 1.5rem; line-height: 1.6">
          ¿Estás seguro de que deseas eliminar al usuario <strong>{{ itemToDelete?.username }}</strong>?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta acción no se puede deshacer.
          </span>
        </p>
        <div class="modal-footer" :style="{ display: 'flex', justifyContent: 'flex-end', gap: '0.75rem' }">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-danger" @click="deleteItem">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

interface Item {
  id: string
  username: string
  email: string
  perfil_id: string | null
  is_active: boolean
}

const { api } = useApi()
const route = useRoute()

const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const activeFilter = ref('all')
const showDeleteModal = ref(false)
const itemToDelete = ref<Item | null>(null)

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: items.value.length },
  { label: 'Activos', value: 'active', count: activeItems.value },
  { label: 'Inactivos', value: 'inactive', count: inactiveItems.value },
])

const activeItems = computed(() => items.value.filter(i => i.is_active).length)
const inactiveItems = computed(() => items.value.filter(i => !i.is_active).length)

const statsItems = computed(() => [
  {
    label: 'Total Usuarios',
    value: items.value.length,
    icon: 'i-heroicons-users',
    iconColor: 'var(--teal)',
    iconBg: 'var(--teal-soft)',
    color: 'var(--teal)'
  },
  {
    label: 'Activos',
    value: activeItems.value,
    icon: 'i-heroicons-check-circle',
    iconColor: 'var(--green)',
    iconBg: 'var(--green-soft)',
    color: 'var(--green)'
  },
  {
    label: 'Inactivos',
    value: inactiveItems.value,
    icon: 'i-heroicons-x-circle',
    iconColor: 'var(--amber)',
    iconBg: 'var(--amber-soft)',
    color: 'var(--amber)'
  },
  {
    label: 'Con Perfil',
    value: items.value.filter(i => i.perfil_id).length,
    icon: 'i-heroicons-user-group',
    iconColor: 'var(--purple)',
    iconBg: 'var(--purple-soft)',
    color: 'var(--purple)'
  }
])

const columns = [
  { key: 'username', label: 'Usuario', icon: 'i-heroicons-user' },
  { key: 'email', label: 'Email', icon: 'i-heroicons-envelope' },
  { key: 'status', label: 'Estado', icon: 'i-heroicons-check-circle' },
  { key: 'actions', label: 'Acciones', align: 'right' as const, width: '120px' }
]

const filteredItems = computed(() => {
  let result = items.value

  if (activeFilter.value === 'active') {
    result = result.filter(i => i.is_active)
  } else if (activeFilter.value === 'inactive') {
    result = result.filter(i => !i.is_active)
  }

  if (search.value.trim()) {
    const q = search.value.toLowerCase().trim()
    result = result.filter(i =>
      i.username.toLowerCase().includes(q) ||
      i.email.toLowerCase().includes(q)
    )
  }

  return result
})

const getInitials = (name: string) => {
  if (!name) return '?'
  return name
    .split(' ')
    .map(word => word[0])
    .join('')
    .toUpperCase()
    .slice(0, 2)
}

const getUserColor = (name: string) => {
  const colors = [
    'var(--teal-soft)',
    'var(--purple-soft)',
    'var(--navy-soft)',
    'var(--amber-soft)',
    'var(--green-soft)',
    'var(--pink-soft)',
    'var(--blue-soft)',
    'var(--orange-soft)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const getActions = (row: Item) => [
  {
    label: 'Editar',
    icon: 'i-heroicons-pencil-square',
    title: 'Editar usuario',
    color: 'var(--teal)',
    onClick: () => navigateTo(`/sigarh/mantenimiento/usuarios/${row.id}?tenant=${tenantId.value}`)
  },
  {
    label: 'Eliminar',
    icon: 'i-heroicons-trash',
    title: 'Eliminar usuario',
    color: 'var(--alert)',
    onClick: () => confirmarEliminar(row)
  }
]

const clearFilters = () => {
  search.value = ''
  activeFilter.value = 'all'
}

const confirmarEliminar = (item: Item) => {
  itemToDelete.value = item
  showDeleteModal.value = true
}

const deleteItem = async () => {
  if (!itemToDelete.value) return
  try {
    await api(`/sigarh/mantenimiento/usuarios/${itemToDelete.value.id}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id !== itemToDelete.value?.id)
    showDeleteModal.value = false
    itemToDelete.value = null
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar'
  }
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    items.value = await api<Item[]>('/sigarh/mantenimiento/usuarios')
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

onMounted(cargar)
</script>

<style scoped>
.page-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

@media (max-width: 768px) {
  .page-container {
    padding: 1rem;
  }
}

@media (max-width: 480px) {
  .modal-content {
    margin: 1rem;
  }
}
</style>