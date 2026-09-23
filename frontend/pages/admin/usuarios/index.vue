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
          <div class="sigarh-stat-value">{{ resumen.total }}</div>
          <div class="sigarh-stat-label">Total Usuarios</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--green)">
        <div class="sigarh-stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ resumen.activos }}</div>
          <div class="sigarh-stat-label">Activos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--amber)">
        <div class="sigarh-stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ resumen.inactivos }}</div>
          <div class="sigarh-stat-label">Inactivos</div>
        </div>
      </div>
      <div class="sigarh-stat-card" style="border-left-color: var(--purple)">
        <div class="sigarh-stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-chart-pie" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div>
          <div class="sigarh-stat-value">{{ resumen.roles_unicos }}</div>
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
          <select v-if="!isAdminView" v-model="hospitalFilter" class="input-clinical" style="max-width: 220px;">
            <option value="">Todos los hospitales</option>
            <option v-for="h in hospitales" :key="h.id" :value="h.id">{{ h.name }}</option>
          </select>
        </div>
        <div style="display: flex; align-items: center; gap: 0.75rem;">
          <span class="sigarh-result-count">{{ total }} resultado{{ total === 1 ? '' : 's' }}</span>
          <button v-if="searchQuery || activeFilter !== 'all' || hospitalFilter" class="sigarh-clear-btn" @click="clearFilters">Limpiar</button>
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

      <div v-else-if="pageUsers.length === 0" class="sigarh-table-state">
        <UIcon name="i-heroicons-users" class="w-12 h-12" style="color: var(--ink-soft); opacity: 0.4" />
        <div>
          <p style="font-weight: 600; color: var(--ink); margin: 0">{{ searchQuery || activeFilter !== 'all' || hospitalFilter ? 'No hay coincidencias con los filtros' : isAdminView ? 'No hay administradores adicionales' : 'No hay usuarios registrados' }}</p>
          <p style="color: var(--ink-soft); font-size: 0.875rem; margin: 0.25rem 0 0 0">{{ searchQuery || activeFilter !== 'all' || hospitalFilter ? 'Prueba con otros filtros.' : isAdminView ? 'La cuenta principal protegida no se incluye en este listado.' : 'Comienza creando tu primer usuario' }}</p>
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
            <tr v-for="user in pageUsers" :key="user.id">
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

      <div v-if="total > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ pageUsers.length }}</strong> de <strong>{{ total }}</strong> usuarios
        </span>
        <div class="footer-actions">
          <div class="pagination">
            <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
              <UIcon name="i-heroicons-chevron-left" class="w-4 h-4" />
            </button>
            <span class="page-info">{{ currentPage }} / {{ totalPages }}</span>
            <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
              <UIcon name="i-heroicons-chevron-right" class="w-4 h-4" />
            </button>
          </div>
        </div>
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
  total: number
  hospitales_no_disponibles: string[]
  es_parcial: boolean
}

interface Resumen {
  total: number
  activos: number
  inactivos: number
  roles_unicos: number
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

const pageUsers = ref<Usuario[]>([])
const total = ref(0)
const resumen = ref<Resumen>({ total: 0, activos: 0, inactivos: 0, roles_unicos: 0, hospitales_no_disponibles: [], es_parcial: false })
const hospitales = ref<Hospital[]>([])
const loading = ref(true)
const error = ref('')
const partialWarning = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const hospitalFilter = ref('')
const currentPage = ref(1)
const perPage = 20
const showDeleteModal = ref(false)
const togglingId = ref<string | null>(null)
const userToDelete = ref<Usuario | null>(null)

const isAdminView = computed(() => route.query.tipo === 'admin')
const createPath = computed(() => isAdminView.value ? '/admin/usuarios/create?tipo=admin' : '/admin/usuarios/create')

const pageTitle = computed(() => isAdminView.value ? 'Administradores' : 'Usuarios por Hospital')
const pageSubtitle = computed(() => isAdminView.value ? 'Administradores del panel ERP' : 'Usuarios asignados a hospitales')

const totalPages = computed(() => Math.max(1, Math.ceil(total.value / perPage)))

const filters = computed(() => [
  { label: 'Todos', value: 'all', count: resumen.value.total },
  { label: 'Activos', value: 'active', count: resumen.value.activos },
  { label: 'Inactivos', value: 'inactive', count: resumen.value.inactivos },
])

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

const clearFilters = () => {
  searchQuery.value = ''
  activeFilter.value = 'all'
  hospitalFilter.value = ''
  currentPage.value = 1
}

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
    const tenantQs = user.tenant_id ? `&tenant_id=${user.tenant_id}` : ''
    await api(`/admin/usuarios/${user.id}/toggle?is_active=${!user.is_active}${tenantQs}`, { method: 'PATCH' })
    user.is_active = !user.is_active
    loadResumen()
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
    const tenantQs = userToDelete.value.tenant_id ? `?tenant_id=${userToDelete.value.tenant_id}` : ''
    await api(`/admin/usuarios/${userToDelete.value.id}${tenantQs}`, { method: 'DELETE' })
    showDeleteModal.value = false
    userToDelete.value = null
    await Promise.all([loadData(), loadResumen()])
  } catch (e: any) {
    error.value = apiErr(e, 'No se pudo eliminar el usuario')
    showDeleteModal.value = false
  }
}

const vista = computed(() => isAdminView.value ? 'admin' : 'hospital')

let listRequest = 0
const loadData = async () => {
  const request = ++listRequest
  loading.value = true
  error.value = ''
  partialWarning.value = ''
  try {
    const params = new URLSearchParams({
      vista: vista.value,
      limit: String(perPage),
      offset: String((currentPage.value - 1) * perPage),
    })
    if (hospitalFilter.value) params.set('tenant_id', hospitalFilter.value)
    if (searchQuery.value.trim()) params.set('q', searchQuery.value.trim())
    if (activeFilter.value === 'active') params.set('is_active', 'true')
    else if (activeFilter.value === 'inactive') params.set('is_active', 'false')

    const usuariosResp = await api<UsuariosConHospitalResponse>(`/admin/usuarios/con-hospital?${params}`)
    if (request !== listRequest) return
    pageUsers.value = usuariosResp.items
    total.value = usuariosResp.total
    if (usuariosResp.es_parcial) {
      partialWarning.value = `No se pudo consultar: ${usuariosResp.hospitales_no_disponibles.join(', ')}. La lista está incompleta.`
    }
  } catch (e: any) {
    error.value = apiErr(e, 'Error de conexión')
  } finally {
    if (request === listRequest) loading.value = false
  }
}

const loadResumen = async () => {
  try {
    const params = new URLSearchParams({ vista: vista.value })
    if (hospitalFilter.value) params.set('tenant_id', hospitalFilter.value)
    const requestedView = vista.value
    const result = await api<Resumen>(`/admin/usuarios/resumen?${params}`)
    if (requestedView === vista.value) resumen.value = result
  } catch {
    // los widgets no son criticos: si fallan, se quedan en sus valores por defecto
  }
}

const loadHospitales = async () => {
  try { hospitales.value = await api<Hospital[]>('/admin/hospitales') }
  catch { /* el filtro de hospital simplemente queda vacio si falla */ }
}

let searchDebounce: ReturnType<typeof setTimeout> | null = null
watch(searchQuery, () => {
  if (searchDebounce) clearTimeout(searchDebounce)
  searchDebounce = setTimeout(() => { currentPage.value = 1; loadData() }, 400)
})
watch([activeFilter, hospitalFilter], () => { currentPage.value = 1; loadData(); loadResumen() })
watch(currentPage, loadData)

watch(isAdminView, () => {
  if (searchDebounce) clearTimeout(searchDebounce)
  searchQuery.value = ''
  activeFilter.value = 'all'
  hospitalFilter.value = ''
  currentPage.value = 1
  loadData()
  loadResumen()
  if (!isAdminView.value) loadHospitales()
})

onMounted(() => {
  loadData()
  loadResumen()
  if (!isAdminView.value) loadHospitales()
})
onUnmounted(() => { if (searchDebounce) clearTimeout(searchDebounce) })
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
