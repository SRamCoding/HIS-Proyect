<template>
  <div class="max-w-3xl mx-auto">
    <!-- Header -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
          <NuxtLink to="/admin/hospitales" style="color: var(--ink-soft)">Hospitales</NuxtLink>
          <span>/</span>
          <span>Editar</span>
        </div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">Editar Hospital</h1>
      </div>
      <button
        class="px-4 py-2 rounded text-sm font-medium"
        style="background: var(--alert); color: white"
        @click="confirmarEliminar"
      >
        Borrar
      </button>
    </div>

    <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>
    <div v-else-if="error" class="p-6 text-sm" style="color: var(--alert)">{{ error }}</div>

    <template v-else>
      <!-- Identidad -->
      <section class="mb-4 p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <p class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: var(--ink)">
          🏥 Identidad del Hospital
        </p>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Nombre oficial*</label>
            <input v-model="form.name" class="input-clinical" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Subdominio*</label>
            <input v-model="subdomain" class="input-clinical" disabled style="opacity: 0.6" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Nivel del establecimiento</label>
            <input v-model="form.hospital_level" class="input-clinical" placeholder="II-2, III-1..." />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">RUC</label>
            <input v-model="form.ruc" class="input-clinical" maxlength="11" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Teléfono</label>
            <input v-model="form.phone" class="input-clinical" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Email</label>
            <input v-model="form.email" type="email" class="input-clinical" />
          </div>
          <div class="col-span-2">
            <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Dirección</label>
            <input v-model="form.address" class="input-clinical" />
          </div>
          <div class="col-span-2 flex items-center gap-2">
            <input type="checkbox" v-model="form.is_active" id="activo" class="rounded" />
            <label for="activo" class="text-sm" style="color: var(--ink)">Hospital activo</label>
          </div>
        </div>
      </section>

      <!-- Misión, Visión y Valores -->
      <section class="mb-4" style="border: 1px solid var(--line); border-radius: var(--radius)">
        <button
          class="w-full flex items-center justify-between p-4 text-sm font-medium"
          style="color: var(--ink)"
          @click="toggleSection('mision')"
        >
          <span>🎯 Misión, Visión y Valores</span>
          <span>{{ openSections.mision ? '▲' : '▼' }}</span>
        </button>
        <div v-if="openSections.mision" class="px-5 pb-5 space-y-3" style="border-top: 1px solid var(--line)">
          <div class="pt-3">
            <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Misión</label>
            <textarea v-model="form.mission" class="input-clinical" rows="3" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Visión</label>
            <textarea v-model="form.vision" class="input-clinical" rows="3" />
          </div>
          <div>
            <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Valores</label>
            <textarea v-model="form.values" class="input-clinical" rows="3" />
          </div>
        </div>
      </section>

      <!-- Módulos Panel Administrativo -->
      <section class="mb-4 p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <p class="text-sm font-semibold mb-1" style="color: var(--ink)">⚙ Módulos del Panel Administrativo (/app)</p>
        <p class="text-xs mb-4" style="color: var(--ink-soft)">Módulos clínicos y administrativos del panel principal del hospital.</p>

        <input v-model="searchModApp" class="input-clinical mb-3" placeholder="Teclea para buscar..." />

        <button class="text-xs mb-3" style="color: var(--teal)" @click="deseleccionarTodos('app')">
          Deseleccionar todos
        </button>

        <div class="grid grid-cols-3 gap-2">
          <label
            v-for="mod in modulosFiltradosApp"
            :key="mod.code"
            class="flex items-center gap-2 text-sm cursor-pointer"
            style="color: var(--ink)"
          >
            <input
              type="checkbox"
              :value="mod.code"
              v-model="modulosActivos"
              class="rounded"
            />
            {{ mod.name }}
          </label>
        </div>
      </section>

      <!-- Módulos Panel SIGARH -->
      <section class="mb-4 p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <p class="text-sm font-semibold mb-1" style="color: var(--ink)">🗂 Módulos del Panel SIGARH (/sigarh)</p>
        <p class="text-xs mb-4" style="color: var(--ink-soft)">Módulos de configuración y RRHH del panel SIGARH.</p>

        <input v-model="searchModSigarh" class="input-clinical mb-3" placeholder="Teclea para buscar..." />

        <button class="text-xs mb-3" style="color: var(--teal)" @click="deseleccionarTodos('sigarh')">
          Deseleccionar todos
        </button>

        <div class="grid grid-cols-3 gap-2">
          <label
            v-for="mod in modulosFiltradosSigarh"
            :key="mod.code"
            class="flex items-center gap-2 text-sm cursor-pointer"
            style="color: var(--ink)"
          >
            <input
              type="checkbox"
              :value="mod.code"
              v-model="modulosActivos"
              class="rounded"
            />
            {{ mod.name }}
          </label>
        </div>
      </section>

      <!-- Error -->
      <div v-if="saveError" class="mb-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">
        {{ saveError }}
      </div>

      <!-- Acciones -->
      <div class="flex gap-3">
        <button class="btn-primary" :disabled="saving" @click="handleSave">
          {{ saving ? 'Guardando...' : 'Guardar cambios' }}
        </button>
        <NuxtLink to="/admin/hospitales" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">
          Cancelar
        </NuxtLink>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const id = computed(() => route.params.id as string)

interface Modulo {
  id: string
  code: string
  name: string
  category: string
}

const loading = ref(true)
const error = ref('')
const saving = ref(false)
const saveError = ref('')
const searchModApp = ref('')
const searchModSigarh = ref('')
const modulosActivos = ref<string[]>([])
const todosModulos = ref<Modulo[]>([])

const openSections = reactive({
  mision: false,
})

const form = reactive({
  name: '',
  hospital_level: '',
  ruc: '',
  phone: '',
  email: '',
  address: '',
  mission: '',
  vision: '',
  values: '',
  is_active: true,
})

const subdomain = ref('')

const modulosFiltradosApp = computed(() =>
  todosModulos.value
    .filter(m => m.category === 'app')
    .filter(m => !searchModApp.value || m.name.toLowerCase().includes(searchModApp.value.toLowerCase()))
)

const modulosFiltradosSigarh = computed(() =>
  todosModulos.value
    .filter(m => m.category === 'sigarh')
    .filter(m => !searchModSigarh.value || m.name.toLowerCase().includes(searchModSigarh.value.toLowerCase()))
)

const toggleSection = (key: keyof typeof openSections) => {
  openSections[key] = !openSections[key]
}

const deseleccionarTodos = (category: string) => {
  const codes = todosModulos.value.filter(m => m.category === category).map(m => m.code)
  modulosActivos.value = modulosActivos.value.filter(c => !codes.includes(c))
}

const confirmarEliminar = async () => {
  if (!confirm('¿Estás seguro de eliminar este hospital? Esta acción no se puede deshacer.')) return
  alert('Función en desarrollo')
}

const handleSave = async () => {
  saving.value = true
  saveError.value = ''
  try {
    // Actualizar datos del hospital
    await api(`/admin/hospitales/${id.value}`, {
      method: 'PATCH',
      body: {
        name: form.name,
        hospital_level: form.hospital_level,
        ruc: form.ruc || null,
        phone: form.phone || null,
        email: form.email || null,
        address: form.address || null,
        mission: form.mission || null,
        vision: form.vision || null,
        values: form.values || null,
      },
    })

    // Actualizar módulos
    await api('/admin/hospitales/modulos', {
      method: 'PUT',
      body: {
        tenant_id: id.value,
        module_codes: modulosActivos.value,
      },
    })

    router.push('/admin/hospitales')
  } catch (e: any) {
    saveError.value = e?.data?.detail || 'No se pudo guardar'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  try {
    const [hospital, modulos] = await Promise.all([
      api<any>(`/admin/hospitales/${id.value}`),
      api<Modulo[]>('/admin/modulos/catalogo'),
    ])

    form.name = hospital.name
    form.hospital_level = hospital.hospital_level || ''
    form.ruc = hospital.ruc || ''
    form.phone = hospital.phone || ''
    form.email = hospital.email || ''
    form.address = hospital.address || ''
    form.mission = hospital.mission || ''
    form.vision = hospital.vision || ''
    form.values = hospital.values || ''
    form.is_active = hospital.is_active
    subdomain.value = hospital.domain?.split('.')[0] || ''
    modulosActivos.value = hospital.active_modules || []
    todosModulos.value = modulos
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo cargar el hospital'
  } finally {
    loading.value = false
  }
})
</script>