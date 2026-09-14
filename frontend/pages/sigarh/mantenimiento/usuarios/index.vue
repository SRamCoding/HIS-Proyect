<template>
  <div class="sigarh-index-container">
    <SAccesosPanelInfo />

    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <h1 class="page-title">Usuarios</h1>
          <p class="page-subtitle">Usuarios del sistema SIGARH</p>
        </div>
      </div>
      <NuxtLink
        :to="puedeAdministrarSeguridad ? `/sigarh/mantenimiento/usuarios/create?tenant=${tenantId}` : ''"
        class="btn-primary"
        :class="{ 'is-disabled': !puedeAdministrarSeguridad }"
        :title="puedeAdministrarSeguridad ? '' : 'Necesitas el permiso Administrar Seguridad para crear usuarios'"
        @click="!puedeAdministrarSeguridad && $event.preventDefault()"
      >
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Usuario
      </NuxtLink>
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" style="border-left-color: var(--teal)">
        <div class="sigarh-stat-icon" style="background: var(--teal-soft)">
          <UIcon name="i-heroicons-users" class="w-5 h-5" style="color: var(--teal)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ items.length }}</div>
          <div class="sigarh-stat-label">Total Usuarios</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ activeItems }}</div>
          <div class="sigarh-stat-label">Activos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ inactiveItems }}</div>
          <div class="sigarh-stat-label">Inactivos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-shield-check" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ conPerfil }}</div>
          <div class="sigarh-stat-label">Con Perfil</div>
        </div>
      </div>
    </div>

    <div class="sigarh-filter-bar">
      <div class="sigarh-filter-left">
        <div class="sigarh-search-wrapper">
          <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
          <input v-model="search" type="text" placeholder="Buscar usuario por nombre o correo..." class="sigarh-search-input" />
        </div>
        <div class="sigarh-filter-group">
          <button @click="activeFilter = 'all'" class="sigarh-filter-btn" :class="{ active: activeFilter === 'all' }">Todos {{ items.length }}</button>
          <button @click="activeFilter = 'active'" class="sigarh-filter-btn" :class="{ active: activeFilter === 'active' }">Activos {{ activeItems }}</button>
          <button @click="activeFilter = 'inactive'" class="sigarh-filter-btn" :class="{ active: activeFilter === 'inactive' }">Inactivos {{ inactiveItems }}</button>
        </div>
      </div>
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <span class="sigarh-result-count">{{ filteredItems.length }} resultados</span>
        <button v-if="search || activeFilter !== 'all'" @click="search = ''; activeFilter = 'all'" class="sigarh-clear-btn">Limpiar</button>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
        <p style="color: var(--ink-soft)">Cargando usuarios...</p>
      </div>
      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button @click="cargar" class="btn-outline">Reintentar</button>
      </div>
      <div v-else-if="!filteredItems.length" class="sigarh-table-state">
        <UIcon name="i-heroicons-users" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">No hay usuarios registrados</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Comienza creando un usuario del sistema</p>
        </div>
      </div>
      <table v-else class="sigarh-table">
        <thead>
          <tr>
            <th>Usuario</th>
            <th>Email</th>
            <th>Estado</th>
            <th class="text-right">Acciones</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredItems" :key="item.id">
            <td>
              <div style="display: flex; align-items: center; gap: 0.625rem;">
                <div :style="{ width: '32px', height: '32px', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.6875rem', fontWeight: 600, color: 'var(--ink)', flexShrink: 0, background: getUserColor(item.username) }">
                  {{ getInitials(item.username) }}
                </div>
                <span style="font-weight: 500">{{ item.username }}</span>
              </div>
            </td>
            <td style="color: var(--ink-soft)">{{ item.email }}</td>
            <td>
              <span class="badge" :class="item.is_active ? 'badge--ok' : 'badge--neutral'">
                {{ item.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </td>
            <td class="text-right">
              <div class="sigarh-actions">
                <button
                  class="sigarh-action-btn"
                  :disabled="!puedeAdministrarSeguridad"
                  :title="puedeAdministrarSeguridad ? 'Editar' : 'Necesitas el permiso Administrar Seguridad'"
                  @click="puedeAdministrarSeguridad && navigateTo(`/sigarh/mantenimiento/usuarios/${item.id}?tenant=${tenantId}`)"
                >
                  <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" />
                </button>
                <button
                  class="sigarh-action-btn danger"
                  :disabled="!puedeAdministrarSeguridad"
                  :title="puedeAdministrarSeguridad ? 'Eliminar' : 'Necesitas el permiso Administrar Seguridad'"
                  @click="puedeAdministrarSeguridad && confirmarEliminar(item)"
                >
                  <UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="filteredItems.length" class="sigarh-table-footer">
        Mostrando {{ filteredItems.length }} de {{ items.length }} usuarios
      </div>
    </div>

    <div v-if="showDeleteModal" class="sigarh-modal-overlay" @click.self="showDeleteModal = false">
      <div class="sigarh-modal">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
          <div style="width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; background: var(--alert-soft); flex-shrink: 0;">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" style="color: var(--alert)" />
          </div>
          <h3 style="font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0">Confirmar Eliminacion</h3>
        </div>
        <p style="color: var(--ink); margin-bottom: 1.5rem; line-height: 1.6">
          Estas seguro de eliminar al usuario <strong>{{ itemToDelete?.username }}</strong>?
          <br><span style="color: var(--ink-soft); font-size: 0.875rem">Esta accion no se puede deshacer.</span>
        </p>
        <div style="display: flex; justify-content: flex-end; gap: 0.75rem;">
          <button class="btn-outline" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-primary" style="background: var(--alert)" @click="deleteItem">
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
const { puedeAdministrarSeguridad } = useSigarhPermisos()
const tenantId = computed(() => route.query.tenant as string || '')
const items = ref<Item[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const activeFilter = ref('all')
const showDeleteModal = ref(false)
const itemToDelete = ref<Item | null>(null)

const activeItems = computed(() => items.value.filter(i => i.is_active).length)
const inactiveItems = computed(() => items.value.filter(i => !i.is_active).length)
const conPerfil = computed(() => items.value.filter(i => i.perfil_id).length)

const filteredItems = computed(() => {
  let result = items.value
  if (activeFilter.value === 'active') result = result.filter(i => i.is_active)
  else if (activeFilter.value === 'inactive') result = result.filter(i => !i.is_active)
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    result = result.filter(i => i.username.toLowerCase().includes(q) || i.email.toLowerCase().includes(q))
  }
  return result
})

const getInitials = (name: string) => name ? name.slice(0, 2).toUpperCase() : '?'

const getUserColor = (name: string) => {
  const colors = ['var(--teal-soft)', 'var(--purple-soft)', 'var(--navy-soft)', 'var(--amber-soft)', 'var(--green-soft)']
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

const confirmarEliminar = (item: Item) => { itemToDelete.value = item; showDeleteModal.value = true }

const deleteItem = async () => {
  if (!itemToDelete.value) return
  try {
    await api(`/sigarh/mantenimiento/usuarios/${itemToDelete.value.id}`, { method: 'DELETE' })
    items.value = items.value.filter(i => i.id !== itemToDelete.value?.id)
    showDeleteModal.value = false
    itemToDelete.value = null
  } catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar') }
}

const cargar = async () => {
  loading.value = true
  error.value = ''
  try {
    items.value = await api<Item[]>('/sigarh/mantenimiento/usuarios')
  } catch (e: any) { error.value = apiErr(e, 'Error de conexion') }
  finally { loading.value = false }
}

onMounted(cargar)
</script>
