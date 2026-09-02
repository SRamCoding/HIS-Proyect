<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">
          {{ tipo === 'admin' ? 'Administradores' : 'Usuarios por Hospital' }}
        </h1>
        <p class="text-sm" style="color: var(--ink-soft)">
          {{ tipo === 'admin' ? 'Administradores del panel ERP' : 'Usuarios asignados a hospitales' }}
        </p>
      </div>
      <button class="btn-primary" @click="showForm = !showForm">
        + Nuevo Usuario
      </button>
    </div>

    <!-- Filtro por hospital (solo en vista usuarios por hospital) -->
    <div v-if="tipo !== 'admin'" class="mb-4">
      <select v-model="hospitalFiltro" class="input-clinical max-w-xs">
        <option value="">Todos los hospitales</option>
        <option v-for="h in hospitales" :key="h.id" :value="h.id">{{ h.name }}</option>
      </select>
    </div>

    <!-- Formulario inline -->
    <div
      v-if="showForm"
      class="mb-4 p-5"
      style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)"
    >
      <p class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: var(--ink)">
        👤 Crear Usuario
      </p>
      <div class="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink-soft)">Nombre completo</label>
          <input v-model="form.name" class="input-clinical" placeholder="Ej: Juan Pérez" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink-soft)">Correo electrónico</label>
          <input v-model="form.email" type="email" class="input-clinical" placeholder="usuario@hospital.pe" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink-soft)">Contraseña</label>
          <input v-model="form.password" type="password" class="input-clinical" placeholder="Mínimo 8 caracteres" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink-soft)">Rol</label>
          <select v-model="form.role" class="input-clinical">
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
        <div v-if="tipo !== 'admin'">
          <label class="block text-sm font-medium mb-1" style="color: var(--ink-soft)">Hospital</label>
          <select v-model="form.tenant_id" class="input-clinical">
            <option value="">Sin hospital</option>
            <option v-for="h in hospitales" :key="h.id" :value="h.id">{{ h.name }}</option>
          </select>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1" style="color: var(--ink-soft)">Panel</label>
          <select v-model="form.panel" class="input-clinical">
            <option v-if="tipo === 'admin'" value="admin">Admin ERP</option>
            <option v-else value="app">Panel Hospitalario</option>
            <option v-if="tipo !== 'admin'" value="sigarh">SIGARH</option>
          </select>
        </div>
      </div>
      <div v-if="createError" class="text-sm px-3 py-2 rounded mb-3" style="background: var(--alert-soft); color: var(--alert)">
        {{ createError }}
      </div>
      <div class="flex gap-2">
        <button class="btn-primary" :disabled="creating" @click="handleCreate">
          {{ creating ? 'Guardando...' : '✓ Guardar' }}
        </button>
        <button
          class="text-sm px-4 py-2 rounded"
          style="border: 1px solid var(--line); color: var(--ink-soft)"
          @click="showForm = false"
        >
          ✕ Cancelar
        </button>
      </div>
    </div>

    <!-- Tabla -->
    <div style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <!-- Buscador -->
      <div class="flex justify-end px-4 py-3" style="border-bottom: 1px solid var(--line)">
        <input
          v-model="search"
          class="input-clinical max-w-xs"
          placeholder="Buscar..."
        />
      </div>

      <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
      <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>

      <table v-else class="w-full text-sm">
        <thead>
          <tr style="border-bottom: 1px solid var(--line)">
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Usuario</th>
            <th v-if="tipo !== 'admin'" class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Hospital</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Rol</th>
            <th class="text-left font-medium px-5 py-3" style="color: var(--ink-soft)">Creado</th>
            <th class="text-right font-medium px-5 py-3" style="color: var(--ink-soft)"></th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="u in usuariosFiltrados"
            :key="u.id"
            style="border-bottom: 1px solid var(--line)"
          >
            <td class="px-5 py-3">
              <p class="font-medium" style="color: var(--ink)">{{ u.name }}</p>
              <p class="text-xs" style="color: var(--ink-soft)">{{ u.email }}</p>
            </td>
            <td v-if="tipo !== 'admin'" class="px-5 py-3" style="color: var(--ink-soft)">
              {{ u.tenant_name || '—' }}
            </td>
            <td class="px-5 py-3">
              <span
                class="text-xs px-2 py-1 rounded font-medium"
                :style="rolColor(u.role)"
              >{{ formatRol(u.role) }}</span>
            </td>
            <td class="px-5 py-3 text-xs" style="color: var(--ink-soft)">{{ u.created_at }}</td>
            <td class="px-5 py-3 text-right">
              <button
                class="text-xs font-medium mr-3"
                style="color: var(--teal)"
                @click="editarUsuario(u)"
              >
                ✏ Editar
              </button>
              <button
                class="text-xs font-medium"
                style="color: var(--alert)"
                @click="eliminarUsuario(u)"
              >
                🗑 Eliminar
              </button>
            </td>
          </tr>
          <tr v-if="!usuariosFiltrados.length">
            <td :colspan="tipo !== 'admin' ? 5 : 4" class="px-5 py-8 text-center text-sm" style="color: var(--ink-soft)">
              Sin usuarios registrados.
            </td>
          </tr>
        </tbody>
      </table>
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

const usuarios = ref<Usuario[]>([])
const hospitales = ref<Hospital[]>([])
const loading = ref(true)
const error = ref('')
const search = ref('')
const hospitalFiltro = ref('')
const showForm = ref(false)
const creating = ref(false)
const createError = ref('')

const tipo = computed(() => route.query.tipo as string || '')

const form = reactive({
  name: '',
  email: '',
  password: '',
  role: 'administrador',
  panel: tipo.value === 'admin' ? 'admin' : 'app',
  tenant_id: '',
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

const rolColor = (role: string) => {
  const colors: Record<string, string> = {
    administrador: 'background: #e8f4fd; color: #1a6fa8',
    medico: 'background: #e8f8f0; color: #1a7a45',
    enfermera: 'background: #fdf0e8; color: #a85c1a',
    tuasis: 'background: #e8f0fd; color: #1a3fa8',
    sigarh: 'background: #f8e8fd; color: #7a1aa8',
    admin: 'background: #fde8e8; color: #a81a1a',
  }
  return colors[role] || 'background: var(--mist); color: var(--ink-soft)'
}

const usuariosFiltrados = computed(() => {
  let list = usuarios.value

  // Filtrar por tipo
  if (tipo.value === 'admin') {
    // Administradores = panel admin con tenant (admins de hospital)
    // O panel admin sin tenant pero que no sea el super admin
    list = list.filter(u => u.panel === 'admin')
  } else {
    // Usuarios por Hospital = panel app o sigarh
    list = list.filter(u => u.panel === 'app' || u.panel === 'sigarh')
  }

  // Filtrar por hospital
  if (hospitalFiltro.value) {
    list = list.filter(u => u.tenant_id === hospitalFiltro.value)
  }

  // Filtrar por búsqueda
  if (search.value.trim()) {
    const q = search.value.toLowerCase()
    list = list.filter(u =>
      u.name.toLowerCase().includes(q) ||
      u.email.toLowerCase().includes(q)
    )
  }

  return list
})

const editarUsuario = (u: Usuario) => {
  // Por implementar
  alert(`Editar: ${u.name}`)
}

const eliminarUsuario = async (u: Usuario) => {
  if (!confirm(`¿Eliminar a ${u.name}?`)) return
  // Por implementar
  alert('Función en desarrollo')
}

const handleCreate = async () => {
  creating.value = true
  createError.value = ''
  try {
    const body: any = {
      name: form.name,
      email: form.email,
      password: form.password,
      role: form.role,
      panel: tipo.value === 'admin' ? 'admin' : form.panel,
      tenant_id: form.tenant_id || null,
    }
    const created = await api<any>('/admin/usuarios', {
      method: 'POST',
      body,
    })
    usuarios.value.unshift({
      ...created,
      tenant_name: hospitales.value.find(h => h.id === form.tenant_id)?.name || '—',
      created_at: new Date().toLocaleDateString('es-PE'),
    })
    showForm.value = false
    Object.assign(form, { name: '', email: '', password: '', role: 'administrador', tenant_id: '' })
  } catch (e: any) {
    createError.value = e?.data?.detail || 'No se pudo crear el usuario'
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  try {
    const [u, h] = await Promise.all([
      api<any[]>('/admin/usuarios/con-hospital'),
      api<Hospital[]>('/admin/hospitales'),
    ])
    usuarios.value = u
    hospitales.value = h
  } catch (e: any) {
    error.value = e?.data?.detail || 'Error de conexion'
  } finally {
    loading.value = false
  }
})

watch(() => route.query.tipo, (newTipo) => {
  form.panel = newTipo === 'admin' ? 'admin' : 'app'
})
</script>