<template>
  <div class="usuarios-container">
    <!-- Header with Stats -->
    <div class="page-header">
      <div class="header-left">
        <div class="header-icon" :style="{ background: isAdminView ? 'var(--navy-soft)' : 'var(--teal-soft)' }">
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
      <button class="btn-primary" @click="showForm = true">
        <UIcon name="i-heroicons-plus" class="w-4 h-4" />
        Nuevo Usuario
      </button>
    </div>

    <!-- Dashboard Widgets Grid -->
    <div class="widgets-grid">
      <!-- Total Users -->
      <div class="stat-widget" :style="{ background: 'var(--paper)', borderLeft: `4px solid ${isAdminView ? 'var(--navy)' : 'var(--teal)'}` }">
        <div class="stat-icon" :style="{ background: isAdminView ? 'var(--navy-soft)' : 'var(--teal-soft)' }">
          <UIcon name="i-heroicons-users" class="w-5 h-5" :style="{ color: isAdminView ? 'var(--navy)' : 'var(--teal)' }" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ filteredUsers.length }}</span>
          <span class="stat-label">Total Usuarios</span>
        </div>
      </div>

      <!-- Active Users -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--green)">
        <div class="stat-icon" style="background: var(--green-soft)">
          <UIcon name="i-heroicons-check-circle" class="w-5 h-5" style="color: var(--green)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ activeUsers }}</span>
          <span class="stat-label">Activos</span>
        </div>
      </div>

      <!-- Inactive Users -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--amber)">
        <div class="stat-icon" style="background: var(--amber-soft)">
          <UIcon name="i-heroicons-x-circle" class="w-5 h-5" style="color: var(--amber)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ inactiveUsers }}</span>
          <span class="stat-label">Inactivos</span>
        </div>
      </div>

      <!-- Roles Distribution -->
      <div class="stat-widget" style="background: var(--paper); border-left: 4px solid var(--purple)">
        <div class="stat-icon" style="background: var(--purple-soft)">
          <UIcon name="i-heroicons-chart-pie" class="w-5 h-5" style="color: var(--purple)" />
        </div>
        <div class="stat-content">
          <span class="stat-value">{{ uniqueRoles }}</span>
          <span class="stat-label">Roles Diferentes</span>
        </div>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <div class="search-wrapper">
          <UIcon name="i-heroicons-magnifying-glass" class="search-icon" />
          <input
            v-model="searchQuery"
            type="text"
            placeholder="Buscar por nombre o email..."
            class="search-input"
            style="border: 1px solid var(--line); background: var(--paper)"
          />
        </div>
        <div class="filter-group">
          <button
            v-for="filter in filters"
            :key="filter.value"
            class="filter-chip"
            :class="{ 'filter-chip--active': activeFilter === filter.value }"
            @click="activeFilter = filter.value"
          >
            {{ filter.label }}
            <span class="filter-count" :style="{ background: activeFilter === filter.value ? 'var(--teal)' : 'var(--mist)' }">
              {{ filter.count }}
            </span>
          </button>
        </div>
      </div>
      <div class="filter-right">
        <span class="result-count">{{ filteredUsers.length }} resultados</span>
      </div>
    </div>

    <!-- Create User Modal -->
    <div v-if="showForm" class="modal-overlay" @click.self="showForm = false">
      <div class="modal-content modal-lg" style="background: var(--paper); border-radius: var(--radius-lg)">
        <div class="modal-header">
          <div class="modal-icon" :style="{ background: isAdminView ? 'var(--navy-soft)' : 'var(--teal-soft)' }">
            <UIcon 
              :name="isAdminView ? 'i-heroicons-user-plus' : 'i-heroicons-user-plus'" 
              class="w-6 h-6" 
              :style="{ color: isAdminView ? 'var(--navy)' : 'var(--teal)' }" 
            />
          </div>
          <div>
            <h3 class="modal-title">Crear Nuevo Usuario</h3>
            <p class="modal-subtitle">{{ isAdminView ? 'Administradores del panel ERP' : 'Usuarios para hospitales' }}</p>
          </div>
          <button class="modal-close" @click="showForm = false">
            <UIcon name="i-heroicons-x-mark" class="w-5 h-5" style="color: var(--ink-soft)" />
          </button>
        </div>

        <div class="modal-body">
          <div class="form-grid">
            <div class="form-group full-width">
              <label class="form-label">Nombre Completo <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-user" class="input-icon" />
                <input 
                  v-model="form.name" 
                  class="input-clinical" 
                  placeholder="Ej: Juan Pérez"
                  :class="{ 'input-error': errors.name }"
                />
              </div>
              <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
            </div>

            <div class="form-group full-width">
              <label class="form-label">Correo Electrónico <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-envelope" class="input-icon" />
                <input 
                  v-model="form.email" 
                  type="email" 
                  class="input-clinical" 
                  placeholder="usuario@hospital.pe"
                  :class="{ 'input-error': errors.email }"
                />
              </div>
              <span v-if="errors.email" class="error-message">{{ errors.email }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Contraseña <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-key" class="input-icon" />
                <input 
                  v-model="form.password" 
                  type="password" 
                  class="input-clinical" 
                  placeholder="Mínimo 8 caracteres"
                  :class="{ 'input-error': errors.password }"
                />
              </div>
              <span v-if="errors.password" class="error-message">{{ errors.password }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Confirmar Contraseña <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-shield-check" class="input-icon" />
                <input 
                  v-model="form.password_confirm" 
                  type="password" 
                  class="input-clinical" 
                  placeholder="Confirmar contraseña"
                  :class="{ 'input-error': errors.password_confirm }"
                />
              </div>
              <span v-if="errors.password_confirm" class="error-message">{{ errors.password_confirm }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Rol <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-briefcase" class="input-icon" />
                <select v-model="form.role" class="input-clinical" :class="{ 'input-error': errors.role }">
                  <option value="administrador">Administrativo</option>
                  <option value="medico">Médico</option>
                  <option value="enfermera">Enfermera</option>
                  <option value="farmaceutico">Farmacéutico</option>
                  <option value="laboratorista">Laboratorista</option>
                  <option value="cajero">Cajero</option>
                  <option value="tuasis">TUASIS</option>
                  <option value="sigarh">SIGARH</option>
                </select>
              </div>
              <span v-if="errors.role" class="error-message">{{ errors.role }}</span>
            </div>

            <div class="form-group">
              <label class="form-label">Panel <span class="required">*</span></label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-squares-2x2" class="input-icon" />
                <select v-model="form.panel" class="input-clinical">
                  <option v-if="isAdminView" value="admin">Admin ERP</option>
                  <option v-else value="app">Panel Hospitalario</option>
                  <option v-if="!isAdminView" value="sigarh">SIGARH</option>
                </select>
              </div>
            </div>

            <div v-if="!isAdminView" class="form-group">
              <label class="form-label">Hospital</label>
              <div class="input-wrapper">
                <UIcon name="i-heroicons-building-office-2" class="input-icon" />
                <select v-model="form.tenant_id" class="input-clinical">
                  <option value="">Sin hospital</option>
                  <option v-for="h in hospitales" :key="h.id" :value="h.id">{{ h.name }}</option>
                </select>
              </div>
            </div>

            <div class="form-group full-width">
              <label class="form-label">Estado</label>
              <div class="status-toggle">
                <span class="toggle-label">Usuario Activo</span>
                <button
                  type="button"
                  role="switch"
                  :aria-checked="form.is_active"
                  @click="form.is_active = !form.is_active"
                  class="toggle-switch"
                  :class="{ 'toggle-active': form.is_active }"
                >
                  <span class="toggle-slider" />
                </button>
              </div>
            </div>
          </div>

          <div v-if="createError" class="error-banner">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ createError }}
          </div>
        </div>

        <div class="modal-footer">
          <button class="btn-secondary" @click="showForm = false">Cancelar</button>
          <button class="btn-primary" :disabled="creating" @click="handleCreate">
            <UIcon v-if="creating" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            <UIcon v-else name="i-heroicons-check" class="w-4 h-4" />
            {{ creating ? 'Creando...' : 'Crear Usuario' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Main Table Card -->
    <div class="table-card" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
      <!-- Loading State -->
      <div v-if="loading" class="table-loading">
        <div class="loading-spinner">
          <UIcon name="i-heroicons-arrow-path" class="w-6 h-6 animate-spin" style="color: var(--teal)" />
        </div>
        <p style="color: var(--ink-soft)">Cargando usuarios...</p>
      </div>

      <!-- Error State -->
      <div v-else-if="error" class="table-error">
        <UIcon name="i-heroicons-exclamation-triangle" class="w-8 h-8" style="color: var(--alert)" />
        <p style="color: var(--alert)">{{ error }}</p>
        <button class="btn-secondary" @click="loadData">Reintentar</button>
      </div>

      <!-- Empty State -->
      <div v-else-if="filteredUsers.length === 0" class="table-empty">
        <div class="empty-icon" style="background: var(--mist)">
          <UIcon name="i-heroicons-users" class="w-12 h-12" style="color: var(--ink-soft)" />
        </div>
        <h3 style="color: var(--ink)">No hay usuarios registrados</h3>
        <p style="color: var(--ink-soft)">Comienza creando tu primer usuario</p>
        <button class="btn-primary" @click="showForm = true">
          <UIcon name="i-heroicons-plus" class="w-4 h-4" />
          Crear Usuario
        </button>
      </div>

      <!-- Table -->
      <div v-else class="table-responsive">
        <table class="usuarios-table">
          <thead>
            <tr>
              <th class="col-user">
                <span class="th-content">Usuario</span>
              </th>
              <th v-if="!isAdminView" class="col-hospital">
                <span class="th-content">Hospital</span>
              </th>
              <th class="col-role">
                <span class="th-content">Rol</span>
              </th>
              <th class="col-panel">
                <span class="th-content">Panel</span>
              </th>
              <th class="col-status">
                <span class="th-content">Estado</span>
              </th>
              <th class="col-created">
                <span class="th-content">Creado</span>
              </th>
              <th class="col-actions">
                <span class="th-content">Acciones</span>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="user in filteredUsers"
              :key="user.id"
              class="table-row"
            >
              <td class="col-user">
                <div class="user-cell">
                  <div class="user-avatar" :style="{ background: getUserColor(user.name) }">
                    <span>{{ getUserInitials(user.name) }}</span>
                  </div>
                  <div>
                    <p class="user-name">{{ user.name }}</p>
                    <p class="user-email">{{ user.email }}</p>
                  </div>
                </div>
              </td>
              <td v-if="!isAdminView" class="col-hospital">
                <span class="hospital-name">{{ user.tenant_name || '—' }}</span>
              </td>
              <td class="col-role">
                <span class="role-badge" :class="getRoleClass(user.role)">
                  {{ formatRol(user.role) }}
                </span>
              </td>
              <td class="col-panel">
                <span class="panel-badge" :class="user.panel === 'admin' ? 'panel-admin' : user.panel === 'sigarh' ? 'panel-sigarh' : 'panel-app'">
                  <UIcon 
                    :name="user.panel === 'admin' ? 'i-heroicons-user-group' : user.panel === 'sigarh' ? 'i-heroicons-folder-open' : 'i-heroicons-squares-2x2'" 
                    class="w-3.5 h-3.5" 
                  />
                  {{ formatPanel(user.panel) }}
                </span>
              </td>
              <td class="col-status">
                <span class="status-badge" :class="user.is_active ? 'status-active' : 'status-inactive'">
                  <span class="status-dot" :class="user.is_active ? 'dot-active' : 'dot-inactive'" />
                  {{ user.is_active ? 'Activo' : 'Inactivo' }}
                </span>
              </td>
              <td class="col-created">
                <span class="created-date">{{ formatDate(user.created_at) }}</span>
              </td>
              <td class="col-actions">
                <div class="action-buttons">
                  <button
                    class="action-btn action-edit"
                    title="Editar usuario"
                    @click="editUser(user)"
                  >
                    <UIcon name="i-heroicons-pencil-square" class="w-4 h-4" />
                  </button>
                  <button
                    class="action-btn action-toggle"
                    :title="user.is_active ? 'Desactivar' : 'Activar'"
                    @click="toggleUserStatus(user)"
                    :disabled="togglingId === user.id"
                  >
                    <UIcon
                      v-if="togglingId === user.id"
                      name="i-heroicons-arrow-path" 
                      class="w-4 h-4 animate-spin"
                    />
                    <UIcon
                      v-else
                      :name="user.is_active ? 'i-heroicons-eye-slash' : 'i-heroicons-eye'"
                      class="w-4 h-4"
                    />
                  </button>
                  <button
                    class="action-btn action-delete"
                    title="Eliminar usuario"
                    @click="confirmDelete(user)"
                  >
                    <UIcon name="i-heroicons-trash" class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Table Footer -->
      <div v-if="filteredUsers.length > 0" class="table-footer">
        <span class="footer-info">
          Mostrando <strong>{{ filteredUsers.length }}</strong> de <strong>{{ allUsers.length }}</strong> usuarios
        </span>
        <div class="footer-actions">
          <button
            v-if="filteredUsers.length < allUsers.length || searchQuery || activeFilter !== 'all'"
            class="btn-secondary btn-sm"
            @click="clearFilters"
          >
            Limpiar filtros
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div v-if="showDeleteModal" class="modal-overlay" @click.self="showDeleteModal = false">
      <div class="modal-content" style="background: var(--paper); border-radius: var(--radius-lg)">
        <div class="modal-header">
          <div class="modal-icon" style="background: var(--alert-soft)">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-6 h-6" style="color: var(--alert)" />
          </div>
          <h3 class="modal-title">Confirmar Eliminación</h3>
        </div>
        <p class="modal-body">
          ¿Estás seguro de que deseas eliminar al usuario <strong>{{ userToDelete?.name }}</strong>?
          <br>
          <span style="color: var(--ink-soft); font-size: 0.875rem">
            Esta acción no se puede deshacer.
          </span>
        </p>
        <div class="modal-footer">
          <button class="btn-secondary" @click="showDeleteModal = false">Cancelar</button>
          <button class="btn-danger" @click="deleteUser">
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

interface Hospital {
  id: string
  name: string
  domain: string
}

const { api } = useApi()
const route = useRoute()

const allUsers = ref<Usuario[]>([])
const hospitales = ref<Hospital[]>([])
const loading = ref(true)
const error = ref('')
const searchQuery = ref('')
const activeFilter = ref('all')
const showForm = ref(false)
const showDeleteModal = ref(false)
const creating = ref(false)
const createError = ref('')
const togglingId = ref<string | null>(null)
const userToDelete = ref<Usuario | null>(null)

const isAdminView = computed(() => route.query.tipo === 'admin')

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

  // Filter by type (admin vs hospital)
  if (isAdminView.value) {
    result = result.filter(u => u.panel === 'admin')
  } else {
    result = result.filter(u => u.panel === 'app' || u.panel === 'sigarh')
  }

  // Filter by status
  if (activeFilter.value === 'active') {
    result = result.filter(u => u.is_active)
  } else if (activeFilter.value === 'inactive') {
    result = result.filter(u => !u.is_active)
  }

  // Filter by search
  if (searchQuery.value.trim()) {
    const query = searchQuery.value.toLowerCase().trim()
    result = result.filter(u =>
      u.name.toLowerCase().includes(query) ||
      u.email.toLowerCase().includes(query)
    )
  }

  return result
})

const form = reactive({
  name: '',
  email: '',
  password: '',
  password_confirm: '',
  role: 'administrador',
  panel: 'app',
  tenant_id: '',
  is_active: true,
})

const errors = reactive({
  name: '',
  email: '',
  password: '',
  password_confirm: '',
  role: '',
})

const formatRol = (role: string) => {
  const map: Record<string, string> = {
    administrador: 'Administrativo',
    medico: 'Médico',
    enfermera: 'Enfermera',
    farmaceutico: 'Farmacéutico',
    laboratorista: 'Laboratorista',
    cajero: 'Cajero',
    tuasis: 'TUASIS',
    sigarh: 'SIGARH',
    admin: 'Admin ERP',
  }
  return map[role] || role
}

const formatPanel = (panel: string) => {
  const map: Record<string, string> = {
    admin: 'Admin ERP',
    app: 'Hospitalario',
    sigarh: 'SIGARH',
  }
  return map[panel] || panel
}

const getRoleClass = (role: string) => {
  const map: Record<string, string> = {
    administrador: 'role-admin',
    medico: 'role-medico',
    enfermera: 'role-enfermera',
    farmaceutico: 'role-farma',
    laboratorista: 'role-lab',
    cajero: 'role-cajero',
    tuasis: 'role-tuasis',
    sigarh: 'role-sigarh',
    admin: 'role-admin-erp',
  }
  return map[role] || 'role-default'
}

const getUserInitials = (name: string) => {
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
    'var(--pink-soft)'
  ]
  let hash = 0
  for (let i = 0; i < name.length; i++) {
    hash = name.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

const formatDate = (date: string) => {
  return new Date(date).toLocaleDateString('es-PE', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric'
  })
}

const validateForm = (): boolean => {
  let valid = true
  errors.name = !form.name ? 'El nombre es requerido' : ''
  errors.email = !form.email ? 'El correo es requerido' : ''
  errors.password = !form.password ? 'La contraseña es requerida' : ''
  errors.password_confirm = form.password !== form.password_confirm ? 'Las contraseñas no coinciden' : ''
  errors.role = !form.role ? 'El rol es requerido' : ''
  
  if (errors.name || errors.email || errors.password || errors.password_confirm || errors.role) {
    valid = false
  }
  return valid
}

const clearFilters = () => {
  searchQuery.value = ''
  activeFilter.value = 'all'
}

const editUser = (user: Usuario) => {
  // Implement edit functionality
  alert(`Editar: ${user.name}`)
}

const toggleUserStatus = async (user: Usuario) => {
  togglingId.value = user.id
  try {
    await api(`/admin/usuarios/${user.id}/toggle`, {
      method: 'PATCH',
      body: { is_active: !user.is_active }
    })
    user.is_active = !user.is_active
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo actualizar el estado'
  } finally {
    togglingId.value = null
  }
}

const confirmDelete = (user: Usuario) => {
  userToDelete.value = user
  showDeleteModal.value = true
}

const deleteUser = async () => {
  if (!userToDelete.value) return
  try {
    await api(`/admin/usuarios/${userToDelete.value.id}`, { method: 'DELETE' })
    allUsers.value = allUsers.value.filter(u => u.id !== userToDelete.value?.id)
    showDeleteModal.value = false
    userToDelete.value = null
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar el usuario'
  }
}

const handleCreate = async () => {
  if (!validateForm()) return

  creating.value = true
  createError.value = ''
  try {
    const body: any = {
      name: form.name,
      email: form.email,
      password: form.password,
      role: form.role,
      panel: isAdminView.value ? 'admin' : form.panel,
      tenant_id: form.tenant_id || null,
      is_active: form.is_active,
    }

    const created = await api<Usuario>('/admin/usuarios', {
      method: 'POST',
      body,
    })

    allUsers.value.unshift({
      ...created,
      tenant_name: hospitales.value.find(h => h.id === form.tenant_id)?.name || '—',
      created_at: new Date().toISOString(),
    })

    showForm.value = false
    Object.assign(form, { 
      name: '', 
      email: '', 
      password: '', 
      password_confirm: '',
      role: 'administrador', 
      tenant_id: '',
      is_active: true,
      panel: isAdminView.value ? 'admin' : 'app'
    })
  } catch (e: any) {
    createError.value = e?.data?.detail || 'No se pudo crear el usuario'
  } finally {
    creating.value = false
  }
}

const loadData = async () => {
  loading.value = true
  error.value = ''
  try {
    const [users, hospitals] = await Promise.all([
      api<Usuario[]>('/admin/usuarios/con-hospital'),
      api<Hospital[]>('/admin/hospitales'),
    ])
    allUsers.value = users
    hospitales.value = hospitals
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexión'
  } finally {
    loading.value = false
  }
}

watch(() => route.query.tipo, (newTipo) => {
  form.panel = newTipo === 'admin' ? 'admin' : 'app'
})

onMounted(loadData)
</script>

<style scoped>
.usuarios-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 1.5rem 2rem;
}

/* Page Header */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 2rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-icon {
  width: 48px;
  height: 48px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  margin: 0;
  line-height: 1.2;
}

.page-subtitle {
  font-size: 0.875rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--teal);
  color: white;
  border: none;
  text-decoration: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: var(--teal-dark);
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.8125rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: var(--mist);
}

.btn-danger {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  background: var(--alert);
  color: white;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-danger:hover {
  background: var(--alert-dark);
}

.btn-sm {
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
}

/* Widgets Grid */
.widgets-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-widget {
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
  border-radius: var(--radius);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
}

.stat-widget:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

.stat-icon {
  width: 44px;
  height: 44px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--ink);
  line-height: 1.2;
}

.stat-label {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Filter Bar */
.filter-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  flex: 1;
}

.search-wrapper {
  position: relative;
  min-width: 200px;
  flex: 1;
  max-width: 300px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--ink-soft);
}

.search-input {
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.5rem;
  border-radius: 8px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.filter-group {
  display: flex;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.filter-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid var(--line);
  background: transparent;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.filter-chip:hover {
  background: var(--mist);
}

.filter-chip--active {
  background: var(--teal-soft);
  border-color: var(--teal);
  color: var(--teal);
}

.filter-count {
  padding: 0.0625rem 0.375rem;
  border-radius: 10px;
  font-size: 0.625rem;
  font-weight: 600;
  color: var(--ink-soft);
  background: var(--mist);
  transition: all 0.2s ease;
}

.filter-chip--active .filter-count {
  background: var(--teal);
  color: white;
}

.filter-right {
  display: flex;
  align-items: center;
}

.result-count {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

/* Table States */
.table-loading,
.table-error,
.table-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  gap: 1rem;
}

.loading-spinner {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.empty-icon {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.table-empty h3 {
  font-size: 1.125rem;
  margin: 0;
}

.table-empty p {
  margin: 0;
}

/* Table Card */
.table-card {
  overflow: hidden;
}

.table-responsive {
  overflow-x: auto;
}

.usuarios-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.usuarios-table thead {
  background: var(--mist);
}

.usuarios-table th {
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 600;
  color: var(--ink-soft);
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--line);
}

.th-content {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.usuarios-table td {
  padding: 0.875rem 1rem;
  border-bottom: 1px solid var(--line);
  vertical-align: middle;
}

.table-row {
  transition: background 0.15s ease;
}

.table-row:hover {
  background: var(--mist);
}

.col-user { width: 22%; }
.col-hospital { width: 15%; }
.col-role { width: 13%; }
.col-panel { width: 13%; }
.col-status { width: 10%; }
.col-created { width: 12%; }
.col-actions { width: 15%; text-align: right; }

/* User Cell */
.user-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--ink);
  flex-shrink: 0;
}

.user-name {
  font-weight: 500;
  color: var(--ink);
  margin: 0;
}

.user-email {
  font-size: 0.75rem;
  color: var(--ink-soft);
  margin: 0;
}

/* Role Badge */
.role-badge {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.role-admin { background: var(--navy-soft); color: var(--navy); }
.role-medico { background: var(--green-soft); color: var(--green); }
.role-enfermera { background: var(--pink-soft); color: var(--pink); }
.role-farma { background: var(--teal-soft); color: var(--teal); }
.role-lab { background: var(--purple-soft); color: var(--purple); }
.role-cajero { background: var(--amber-soft); color: var(--amber); }
.role-tuasis { background: var(--blue-soft); color: var(--blue); }
.role-sigarh { background: #f8e8fd; color: #7a1aa8; }
.role-admin-erp { background: var(--alert-soft); color: var(--alert); }
.role-default { background: var(--mist); color: var(--ink-soft); }

/* Panel Badge */
.panel-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.1875rem 0.625rem;
  border-radius: 12px;
  font-size: 0.6875rem;
  font-weight: 500;
}

.panel-admin { background: var(--navy-soft); color: var(--navy); }
.panel-app { background: var(--teal-soft); color: var(--teal); }
.panel-sigarh { background: var(--purple-soft); color: var(--purple); }

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-active {
  background: var(--green-soft);
  color: var(--green);
}

.status-inactive {
  background: var(--mist);
  color: var(--ink-soft);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  display: inline-block;
}

.dot-active {
  background: var(--green);
}

.dot-inactive {
  background: var(--ink-soft);
}

.hospital-name {
  color: var(--ink-soft);
}

.created-date {
  font-size: 0.75rem;
  color: var(--ink-soft);
}

/* Action Buttons */
.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.25rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: 1px solid transparent;
  background: transparent;
  color: var(--ink-soft);
  cursor: pointer;
  transition: all 0.2s ease;
}

.action-btn:hover {
  background: var(--mist);
}

.action-edit:hover {
  color: var(--teal);
  border-color: var(--teal-soft);
  background: var(--teal-soft);
}

.action-toggle:hover {
  color: var(--amber);
  border-color: var(--amber-soft);
  background: var(--amber-soft);
}

.action-delete:hover {
  color: var(--alert);
  border-color: var(--alert-soft);
  background: var(--alert-soft);
}

.action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Table Footer */
.table-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  border-top: 1px solid var(--line);
  flex-wrap: wrap;
  gap: 0.5rem;
}

.footer-info {
  font-size: 0.8125rem;
  color: var(--ink-soft);
}

.footer-actions {
  display: flex;
  gap: 0.5rem;
}

/* Modal */
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

.modal-content {
  max-width: 520px;
  width: 100%;
  padding: 1.5rem;
  box-shadow: var(--shadow-lg);
}

.modal-content.modal-lg {
  max-width: 680px;
}

.modal-header {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
  position: relative;
}

.modal-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.modal-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--ink);
  margin: 0;
}

.modal-subtitle {
  font-size: 0.8125rem;
  color: var(--ink-soft);
  margin: 0.125rem 0 0 0;
}

.modal-close {
  position: absolute;
  top: -0.25rem;
  right: -0.25rem;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  border: none;
  background: transparent;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
}

.modal-close:hover {
  background: var(--mist);
}

.modal-body {
  margin-bottom: 1.5rem;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
}

/* Form */
.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.25rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--ink);
  margin-bottom: 0.5rem;
}

.required {
  color: var(--alert);
}

.input-wrapper {
  position: relative;
}

.input-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  width: 1rem;
  height: 1rem;
  color: var(--ink-soft);
}

.input-clinical {
  width: 100%;
  padding: 0.625rem 0.875rem;
  padding-left: 2.5rem;
  border-radius: 8px;
  border: 1px solid var(--line);
  background: var(--paper);
  color: var(--ink);
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.input-clinical:focus {
  outline: none;
  border-color: var(--teal);
  box-shadow: 0 0 0 3px var(--teal-soft);
}

.input-clinical.input-error {
  border-color: var(--alert);
}

.input-clinical.input-error:focus {
  box-shadow: 0 0 0 3px var(--alert-soft);
}

.input-clinical[type="select"],
.input-clinical select {
  appearance: none;
  cursor: pointer;
}

.error-message {
  display: block;
  font-size: 0.75rem;
  color: var(--alert);
  margin-top: 0.25rem;
}

/* Status Toggle */
.status-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--mist);
}

.toggle-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--ink);
}

.toggle-switch {
  position: relative;
  width: 44px;
  height: 24px;
  border-radius: 12px;
  background: var(--line);
  border: none;
  cursor: pointer;
  transition: background 0.3s ease;
  padding: 0;
}

.toggle-switch.toggle-active {
  background: var(--teal);
}

.toggle-slider {
  position: absolute;
  top: 2px;
  left: 2px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: white;
  transition: transform 0.3s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.2);
}

.toggle-active .toggle-slider {
  transform: translateX(20px);
}

/* Error Banner */
.error-banner {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 8px;
  background: var(--alert-soft);
  color: var(--alert);
  font-size: 0.875rem;
  margin-top: 1rem;
}

/* Responsive */
@media (max-width: 1200px) {
  .widgets-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 1024px) {
  .usuarios-container {
    padding: 1rem 1.5rem;
  }

  .filter-bar {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-left {
    flex-direction: column;
    align-items: stretch;
  }

  .search-wrapper {
    max-width: none;
  }
}

@media (max-width: 768px) {
  .usuarios-container {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .page-header .btn-primary {
    width: 100%;
    justify-content: center;
  }

  .widgets-grid {
    grid-template-columns: 1fr 1fr;
  }

  .filter-group {
    flex-wrap: wrap;
  }

  .col-actions {
    min-width: 100px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .modal-content.modal-lg {
    max-width: 100%;
    margin: 1rem;
  }
}

@media (max-width: 480px) {
  .widgets-grid {
    grid-template-columns: 1fr;
  }

  .filter-chip {
    font-size: 0.6875rem;
    padding: 0.25rem 0.5rem;
  }

  .table-responsive {
    margin: 0 -0.5rem;
  }

  .usuarios-table td,
  .usuarios-table th {
    padding: 0.5rem 0.625rem;
    font-size: 0.8125rem;
  }

  .col-user {
    min-width: 150px;
  }

  .col-actions {
    min-width: 80px;
  }

  .action-buttons {
    gap: 0.125rem;
  }

  .action-btn {
    width: 28px;
    height: 28px;
  }
}
</style>