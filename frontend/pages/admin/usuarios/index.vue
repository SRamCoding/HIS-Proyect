<template>
  <div class="sigarh-index-container">
    <div class="sigarh-page-header">
      <div class="sigarh-header-left">
        <div class="sigarh-header-icon" :style="{ background: isAdminView ? 'var(--navy-soft)' : 'var(--teal-soft)' }">
          <UIcon
            :name="isAdminView ? 'i-heroicons-user-group' : 'i-heroicons-users'"
            class="w-5 h-5"
            :style="{ color: isAdminView ? 'var(--navy)' : 'var(--teal)' }"
          />
        </div>
        <div>
          <h1 class="page-title">{{ pageTitle }}</h1>
          <p class="page-subtitle">{{ pageSubtitle }}</p>
        </div>
      </div>
      <NuxtLink :to="createPath" class="btn-primary">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Usuario
      </NuxtLink>
    </div>

    <div v-if="partialWarning" class="report-note" style="background: var(--alert-soft); border-color: var(--alert); color: var(--alert); margin-bottom: 1rem;">
      <strong>Lista incompleta:</strong> {{ partialWarning }}
    </div>

    <div class="sigarh-stats-grid">
      <div class="sigarh-stat-card" :style="{ borderLeftColor: isAdminView ? 'var(--navy)' : 'var(--teal)' }">
        <div class="sigarh-stat-icon" :style="{ background: isAdminView ? 'var(--navy-soft)' : 'var(--teal-soft)' }">
          <UIcon name="i-heroicons-users" class="w-5 h-5" :style="{ color: isAdminView ? 'var(--navy)' : 'var(--teal)' }" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ filteredUsers.length }}</div>
          <div class="sigarh-stat-label">Total Usuarios</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ activeUsers }}</div>
          <div class="sigarh-stat-label">Activos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ inactiveUsers }}</div>
          <div class="sigarh-stat-label">Inactivos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-chart-pie" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ uniqueRoles }}</div>
          <div class="sigarh-stat-label">Roles Diferentes</div>
        </div>
      </div>
    </div>

    <div class="sigarh-table-container">
      <div class="sigarh-filter-bar">
        <div class="sigarh-filter-left">
          <div class="sigarh-search-wrapper">
            <UIcon name="i-heroicons-magnifying-glass" class="sigarh-search-icon" />
            <input v-model="searchQuery" type="text" placeholder="Buscar por nombre o email..." class="sigarh-search-input" />
          </div>
          <div class="sigarh-filter-group">
            <button
              v-for="filter in filters"
              :key="filter.value"
              class="sigarh-filter-btn"
              :class="{ active: activeFilter === filter.value }"
              @click="activeFilter = filter.value"
            >
              {{ filter.label }}
              <span class="sigarh-filter-count">{{ filter.count }}</span>
            </button>
          </div>
          <select v-if="!isAdminView" v-model="hospitalFilter" class="input-clinical" style="max-width: 220px;" @change="loadData">
            <option value="">Todos los hospitales</option>
            <option v-for="h in hospitales" :key="h.id" :value="h.id">{{ h.name }}</option>
          </select>
        </div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span class="sigarh-result-count">{{ filteredUsers.length }} resultados</span>
          <button v-if="searchQuery || activeFilter !== 'all'" class="sigarh-clear-btn" @click="clearFilters">Limpiar</button>
        </div>
      </div>

      <div v-if="loading" class="sigarh-table-state">
        <UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" />
        <p style="color: var(--ink-soft)">Cargando usuarios...</p>
      </div>

      <div v-else-if="error" class="sigarh-table-state">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-outline" @click="loadData">Reintentar</button>
      </div>

      <div v-else-if="filteredUsers.length === 0" class="sigarh-table-state">
        <UIcon name="i-heroicons-users" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">No hay usuarios registrados</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">Comienza creando tu primer usuario</p>
        </div>
        <NuxtLink :to="createPath" class="btn-primary">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Crear Usuario
        </NuxtLink>
      </div>

      <div v-else class="sigarh-table-responsive">
        <table class="sigarh-table">
          <thead>
            <tr>
              <th>Usuario</th>
              <th v-if="!isAdminView">Hospital</th>
              <th>Rol</th>
              <th>Panel</th>
              <th>Estado</th>
              <th>Creado</th>
              <th class="text-right">Acciones</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="user in filteredUsers" :key="user.id">
              <td>
                <div class="sigarh-item-cell">
                  <div class="sigarh-item-icon" :style="{ background: getUserColor(user.name) }">
                    <span style="font-size: 0.6875rem; font-weight: 600; color: var(--ink)">{{ getUserInitials(user.name) }}</span>
                  </div>
                  <div>
                    <p class="sigarh-item-name" style="margin: 0">{{ user.name }}</p>
                    <p style="font-size: 0.75rem; color: var(--ink-soft); margin: 0">{{ user.email }}</p>
                  </div>
                </div>
              </td>
              <td v-if="!isAdminView" style="color: var(--ink-soft)">{{ user.tenant_name || '—' }}</td>
              <td>
                <span class="badge" :class="getRoleClass(user.role)">{{ formatRol(user.role) }}</span>
              </td>
              <td>
                <span class="badge" :class="user.panel === 'admin' ? 'badge--panel-admin' : user.panel === 'sigarh' ? 'badge--panel-sigarh' : 'badge--panel-app'">
                  <UIcon
                    :name="user.panel === 'admin' ? 'i-heroicons-user-group' : user.panel === 'sigarh' ? 'i-heroicons-folder-open' : 'i-heroicons-squares-2x2'"
                    class="w-3.5 h-3.5"
                  />
                  {{ formatPanel(user.panel) }}
                </span>
              </td>
              <td>
                <span class="badge" :class="user.is_active ? 'badge--ok' : 'badge--neutral'">
                  {{ user.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td style="font-size: 0.75rem; color: var(--ink-soft)">{{ formatDate(user.created_at) }}</td>
              <td class="text-right">
                <div class="sigarh-actions">
                  <button class="sigarh-action-btn" title="Editar usuario" @click="editUser(user)">
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" style="color: var(--teal)" />
                  </button>
                  <button
                    class="sigarh-action-btn"
                    :title="user.is_active ? 'Desactivar' : 'Activar'"
                    :disabled="togglingId === user.id"
                    @click="toggleUserStatus(user)"
                  >
                    <UIcon v-if="togglingId === user.id" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
                    <UIcon v-else :name="user.is_active ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'" class="w-4 h-4" style="color: var(--amber)" />
                  </button>
                  <button class="sigarh-action-btn danger" title="Eliminar usuario" @click="confirmDelete(user)">
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="filteredUsers.length > 0" class="sigarh-table-footer">
        Mostrando {{ filteredUsers.length }} de {{ allUsers.length }} usuarios
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="sigarh-modal-overlay" @click.self="showDeleteModal = false">
      <div class="sigarh-modal">
        <div style="display: flex; align-items: center; gap: 0.75rem; margin-bottom: 1rem;">
          <div style="width: 48px; height: 48px; border-radius: 12px; display: flex; align-items: center; justify-content: center; background: var(--alert-soft); flex-shrink: 0;">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" style="color: var(--alert)" />
          </div>
          <h3 style="font-size: 1.125rem; font-weight: 600; color: var(--ink); margin: 0">Confirmar Eliminación</h3>
        </div>
        <p style="color: var(--ink); margin-bottom: 1.5rem; line-height: 1.6">
          ¿Estás seguro de que deseas eliminar al usuario <strong>{{ userToDelete?.name }}</strong>?
          <br><span style="color: var(--ink-soft); font-size: 0.875rem">Esta acción no se puede deshacer.</span>
        </p>
        <div style="display: flex; justify-content: flex-end; gap: 0.75rem;">
          <button class="btn-outline" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-primary" style="background: var(--alert)" @click="deleteUser">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" />
            Eliminar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

interface Usuario {
  id: string
  name: string
  email: string
  role: string
  panel: string
  is_active: boolean
  tenant_name?: string
  tenant_id?: string
  created_at: string
}

interface UsuariosConHospitalResponse {
  items: Usuario[]
  hospitales_no_disponibles: string[]
  es_parcial: boolean
}

interface Hospital {
  id: string
  name: string
  domain: string
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const allUsers = ref<Usuario[]>([])
const hospitales = ref<Hospital[]>([])
const loading = ref(true)
const error = ref('')
const partialWarning = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const hospitalFilter = ref('')
const showDeleteModal = ref(false)
const togglingId = ref<string | null>(null)
const userToDelete = ref<Usuario | null>(null)

const isAdminView = computed(() => route.query.tipo === 'admin')
const createPath = computed(() => isAdminView.value ? '/admin/usuarios/create?tipo=admin' : '/admin/usuarios/create')

const pageTitle = computed(() => isAdminView.value ? 'Administradores' : 'Usuarios por Hospital')
const pageSubtitle = computed(() => isAdminView.value ? 'Administradores del panel ERP' : 'Usuarios asignados a hospitales')

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: allUsers.value.length },
  { label: 'Activos', value: 'active', count: activeUsers.value },
  { label: 'Inactivos', value: 'inactive', count: inactiveUsers.value },
])

const activeUsers = computed(() => allUsers.value.filter(u => u.is_active).length)
const inactiveUsers = computed(() => allUsers.value.filter(u => !u.is_active).length)
const uniqueRoles = computed(() => new Set(allUsers.value.map(u => u.role)).size)

const filteredUsers = computed(() => {
  let result = allUsers.value

  result = isAdminView.value
    ? result.filter(u => u.panel === 'admin')
    : result.filter(u => u.panel === 'app' || u.panel === 'sigarh')

  if (activeFilter.value === 'active') result = result.filter(u => u.is_active)
  else if (activeFilter.value === 'inactive') result = result.filter(u => !u.is_active)

  if (searchQuery.value.trim()) {
    const q = searchQuery.value.toLowerCase().trim()
    result = result.filter(u => u.name.toLowerCase().includes(q) || u.email.toLowerCase().includes(q))
  }

  return result
})

const formatRol = (role: string) => {
  const map: Record<string, string> = {
    administrador: 'Administrativo', medico: 'Médico', enfermera: 'Enfermera',
    farmaceutico: 'Farmacéutico', laboratorista: 'Laboratorista', cajero: 'Cajero',
    tuasis: 'TUASIS', sigarh: 'SIGARH', admin: 'Admin ERP',
  }
  return map[role] || role
}

const formatPanel = (panel: string) => {
  const map: Record<string, string> = { admin: 'Admin ERP', app: 'Hospitalario', sigarh: 'SIGARH' }
  return map[panel] || panel
}

const getRoleClass = (role: string) => {
  const map: Record<string, string> = {
    administrador: 'badge--role-admin', medico: 'badge--ok', enfermera: 'badge--role-pink',
    farmaceutico: 'badge--role-teal', laboratorista: 'badge--role-purple', cajero: 'badge--warning',
    tuasis: 'badge--role-blue', sigarh: 'badge--role-purple', admin: 'badge--danger',
  }
  return map[role] || 'badge--neutral'
}

const getUserInitials = (name: string) => name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2)

const getUserColor = (name: string) => {
  const colors = ['var(--teal-soft)', 'var(--purple-soft)', 'var(--navy-soft)', 'var(--amber-soft)', 'var(--green-soft)', 'var(--pink-soft)']
  let hash = 0
  for (let i = 0; i < name.length; i++) hash = name.charCodeAt(i) + ((hash << 5) - hash)
  return colors[Math.abs(hash) % colors.length]
}

const formatDate = (date: string) => new Date(date).toLocaleDateString('es-PE', { day: '2-digit', month: '2-digit', year: 'numeric' })

const clearFilters = () => { searchQuery.value = ''; activeFilter.value = 'all' }

const editUser = (user: Usuario) => {
  const params = new URLSearchParams()
  if (isAdminView.value) params.set('tipo', 'admin')
  if (user.tenant_id) params.set('tenant_id', user.tenant_id)
  const qs = params.toString()
  router.push(`/admin/usuarios/${user.id}${qs ? `?${qs}` : ''}`)
}

const toggleUserStatus = async (user: Usuario) => {
  togglingId.value = user.id
  error.value = ''
  try {
    await api(`/admin/usuarios/${user.id}/toggle?is_active=${!user.is_active}`, { method: 'PATCH' })
    user.is_active = !user.is_active
  } catch (e: any) {
    error.value = apiErr(e, 'No se pudo actualizar el estado')
  } finally {
    togglingId.value = null
  }
}

const confirmDelete = (user: Usuario) => { userToDelete.value = user; showDeleteModal.value = true }

const deleteUser = async () => {
  if (!userToDelete.value) return
  try {
    await api(`/admin/usuarios/${userToDelete.value.id}`, { method: 'DELETE' })
    allUsers.value = allUsers.value.filter(u => u.id !== userToDelete.value?.id)
    showDeleteModal.value = false
    userToDelete.value = null
  } catch (e: any) {
    error.value = apiErr(e, 'No se pudo eliminar el usuario')
    showDeleteModal.value = false
  }
}

const loadData = async () => {
  loading.value = true
  error.value = ''
  partialWarning.value = ''
  try {
    const usuariosUrl = hospitalFilter.value
      ? `/admin/usuarios/con-hospital?tenant_id=${hospitalFilter.value}`
      : '/admin/usuarios/con-hospital'
    const [usuariosResp, hospitals] = await Promise.all([
      api<UsuariosConHospitalResponse>(usuariosUrl),
      api<Hospital[]>('/admin/hospitales'),
    ])
    allUsers.value = usuariosResp.items
    hospitales.value = hospitals
    if (usuariosResp.es_parcial) {
      partialWarning.value = `No se pudo consultar: ${usuariosResp.hospitales_no_disponibles.join(', ')}. La lista está incompleta.`
    }
  } catch (e: any) {
    error.value = apiErr(e, 'Error de conexión')
  } finally {
    loading.value = false
  }
}

onMounted(loadData)
</script>

<style scoped>
.badge--panel-admin { background: var(--navy-soft); color: var(--navy); }
.badge--panel-app { background: var(--teal-soft); color: var(--teal); }
.badge--panel-sigarh { background: var(--purple-soft); color: var(--purple); }

.badge--role-admin { background: var(--navy-soft); color: var(--navy); }
.badge--role-pink { background: var(--pink-soft); color: var(--pink); }
.badge--role-teal { background: var(--teal-soft); color: var(--teal); }
.badge--role-purple { background: var(--purple-soft); color: var(--purple); }
.badge--role-blue { background: var(--blue-soft); color: var(--blue); }
</style>
