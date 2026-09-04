<!-- pages/sigarh/mantenimiento/usuarios/create.vue -->
<template>
  <div class="max-w-2xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/mantenimiento/usuarios?tenant=${tenantId}`" style="color: var(--ink-soft)">Usuarios</NuxtLink>
        <span>/</span><span>Crear</span>
      </div>
    </div>

    <PageHeader
      title="Nuevo Usuario"
      subtitle="Registra un nuevo usuario del sistema"
      icon="i-heroicons-user-plus"
      icon-color="var(--teal)"
      icon-bg="var(--teal-soft)"
    />

    <CardBase>
      <div v-if="loadingPerfiles" class="text-sm" style="color: var(--ink-soft)">
        Cargando perfiles...
      </div>
      <div v-else-if="loadError" class="text-sm px-3 py-2 rounded mb-4" style="background: var(--alert-soft); color: var(--alert)">
        {{ loadError }}
        <button class="ml-2 underline" @click="cargarPerfiles">Reintentar</button>
      </div>

      <div v-if="!loadingPerfiles" class="form-grid">
        <FormField
          v-model="form.username"
          label="Usuario (login)"
          required
          placeholder="Ej: jperez"
          hint="Se genera automáticamente con el DNI."
        />
        <FormField
          v-model="form.email"
          type="email"
          label="Correo electrónico"
          required
          placeholder="usuario@hospital.pe"
        />
        <FormField
          v-model="form.perfil_id"
          type="select"
          label="Perfil"
          required
          hint="El rol y los módulos se toman del perfil seleccionado."
          full-width
        >
          <option value="">Seleccione una opción</option>
          <option v-for="p in perfiles" :key="p.id" :value="p.id">{{ p.nombre }}</option>
        </FormField>
        <FormField
          v-model="form.password"
          type="password"
          label="Contraseña"
          placeholder="Por defecto: DNI del empleado"
          hint="Si no ingresa, se usará el DNI del empleado."
          full-width
        />
        <div class="full-width">
          <ToggleSwitch v-model="form.is_active" label="Usuario activo" />
        </div>
      </div>

      <!-- Perfil asignado preview -->
      <div v-if="!loadingPerfiles" class="mt-4 p-4 rounded" style="border: 1px solid var(--line)">
        <p class="text-sm font-semibold mb-2" style="color: var(--ink)">Perfil asignado</p>
        <p v-if="perfilSeleccionado" class="text-xs" style="color: var(--ink-soft)">
          Rol del sistema: <span style="color: var(--ink)">{{ perfilSeleccionado.nombre }}</span>
        </p>
        <p v-else class="text-xs" style="color: var(--ink-soft)">— Seleccione un perfil —</p>
      </div>

      <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">
        {{ error }}
      </div>

      <div class="flex gap-3 mt-6">
        <button class="btn-primary" :disabled="saving || loadingPerfiles" @click="handleCreate(false)">
          {{ saving ? 'Guardando...' : 'Crear' }}
        </button>
        <button class="btn-secondary" :disabled="saving || loadingPerfiles" @click="handleCreate(true)">
          Crear y crear otro
        </button>
        <NuxtLink :to="`/sigarh/mantenimiento/usuarios?tenant=${tenantId}`" class="btn-secondary">
          Cancelar
        </NuxtLink>
      </div>
    </CardBase>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

interface Perfil {
  id: string
  nombre: string
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.query.tenant as string || '')

const saving = ref(false)
const error = ref('')
const loadingPerfiles = ref(true)
const loadError = ref('')
const perfiles = ref<Perfil[]>([])

const form = reactive({
  username: '',
  email: '',
  password: '',
  perfil_id: '',
  is_active: true,
})

const perfilSeleccionado = computed(() =>
  perfiles.value.find(p => p.id === form.perfil_id) || null
)

const cargarPerfiles = async () => {
  loadingPerfiles.value = true
  loadError.value = ''
  try {
    perfiles.value = await api<Perfil[]>('/sigarh/mantenimiento/perfiles-usuario')
  } catch (e: any) {
    loadError.value = e?.data?.detail || 'No se pudieron cargar los perfiles'
  } finally {
    loadingPerfiles.value = false
  }
}

const handleCreate = async (createAnother: boolean) => {
  if (!form.username.trim()) { error.value = 'El usuario es requerido'; return }
  if (!form.email.trim()) { error.value = 'El correo es requerido'; return }
  if (!form.perfil_id) { error.value = 'El perfil es requerido'; return }

  saving.value = true
  error.value = ''
  try {
    await api('/sigarh/mantenimiento/usuarios', {
      method: 'POST',
      body: { ...form, perfil_id: form.perfil_id || null, password: form.password || form.username }
    })
    if (createAnother) {
      Object.assign(form, { username: '', email: '', password: '', perfil_id: '', is_active: true })
    } else {
      router.push(`/sigarh/mantenimiento/usuarios?tenant=${tenantId.value}`)
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo crear'
  } finally {
    saving.value = false
  }
}

onMounted(cargarPerfiles)
</script>