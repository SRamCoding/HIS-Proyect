<!-- frontend/pages/sigarh/mantenimiento/roles-sistema/create.vue -->
<template>
  <div>
    <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
      <span>Mantenimiento</span><span>/</span><span>Roles del Sistema</span><span>/</span><span>Crear</span>
    </div>
    <h1 class="text-lg font-semibold mb-1" style="color: var(--ink)">Crear Rol del Sistema</h1>
    <p class="text-sm mb-4" style="color: var(--ink-soft)">
      Roles disponibles para asignar a Perfiles de Usuario en este hospital.
    </p>

    <div v-if="error" class="mb-4 p-3 text-sm" style="background: var(--alert-soft); color: var(--alert); border-radius: var(--radius)">
      {{ error }}
    </div>

    <!-- Datos del rol -->
    <div class="p-5 mb-4" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <h2 class="text-sm font-semibold mb-4" style="color: var(--ink)">Datos del Rol</h2>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div>
          <label class="text-xs block mb-1" style="color: var(--ink-soft)">Código interno *</label>
          <input v-model="form.codigo" class="input-clinical w-full" placeholder="medico" />
          <p class="text-xs mt-1" style="color: var(--ink-soft)">Minúsculas y guión bajo. No se puede cambiar fácilmente después.</p>
        </div>
        <div>
          <label class="text-xs block mb-1" style="color: var(--ink-soft)">Nombre visible *</label>
          <input v-model="form.nombre" class="input-clinical w-full" placeholder="Médico" />
        </div>
        <div>
          <label class="text-xs block mb-1" style="color: var(--ink-soft)">Panel asociado *</label>
          <select v-model="form.panel" class="input-clinical w-full">
            <option value="app">Panel Hospital (app)</option>
            <option value="sigarh">Panel SIGARH</option>
            <option value="portal">Portal</option>
          </select>
          <p class="text-xs mt-1" style="color: var(--ink-soft)">A qué panel entra un usuario con este rol.</p>
        </div>
        <div>
          <label class="text-xs block mb-1" style="color: var(--ink-soft)">Módulo requerido</label>
          <select v-model="form.modulo_requerido" class="input-clinical w-full">
            <option value="">— Ninguno (rol siempre disponible) —</option>
            <option v-for="m in todosModulos" :key="m.code" :value="m.code">{{ m.name }}</option>
          </select>
          <p class="text-xs mt-1" style="color: var(--ink-soft)">Si el hospital no tiene este módulo activo, el rol no aparecerá al crear Perfiles.</p>
        </div>
        <div class="sm:col-span-2">
          <label class="text-xs block mb-1" style="color: var(--ink-soft)">Descripción</label>
          <textarea v-model="form.descripcion" class="input-clinical w-full" rows="3" />
        </div>
        <div class="sm:col-span-2 flex items-center gap-2">
          <input type="checkbox" v-model="form.is_active" id="activo" />
          <label for="activo" class="text-sm" style="color: var(--ink)">Activo</label>
        </div>
      </div>
    </div>

    <!-- Módulos permitidos -->
    <div class="p-5 mb-4" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <h2 class="text-sm font-semibold mb-1" style="color: var(--ink)">Módulos permitidos para este rol</h2>
      <p class="text-xs mb-3" style="color: var(--ink-soft)">
        Solo estos módulos podrán marcarse en "Perfiles de Usuario" cuando se elija este rol. Deja vacío para no restringir — se mostrarán todos los módulos del hospital.
      </p>
      <div class="mb-2">
        <button class="text-xs font-medium" style="color: var(--teal)" @click="toggleTodosModulos">
          {{ form.modulos_permitidos.length === todosModulos.length ? 'Ninguno' : 'Seleccionar todos' }}
        </button>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <label v-for="m in modulosApp" :key="m.code" class="flex items-center gap-2 text-sm" style="color: var(--ink)">
          <input type="checkbox" :value="m.code" v-model="form.modulos_permitidos" />
          [Administrativo] {{ m.name }}
        </label>
        <label v-for="m in modulosSigarh" :key="m.code" class="flex items-center gap-2 text-sm" style="color: var(--ink)">
          <input type="checkbox" :value="m.code" v-model="form.modulos_permitidos" />
          [SIGARH] {{ m.name }}
        </label>
      </div>
    </div>

    <!-- Grupos ocupacionales permitidos -->
    <div class="p-5 mb-4" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <h2 class="text-sm font-semibold mb-1" style="color: var(--ink)">Grupos Ocupacionales permitidos para este rol</h2>
      <p class="text-xs mb-3" style="color: var(--ink-soft)">
        Solo empleados de estos grupos ocupacionales podrán vincularse a un usuario con este rol. Deja vacío para no restringir.
      </p>
      <div class="mb-2">
        <button class="text-xs font-medium" style="color: var(--teal)" @click="toggleTodosGrupos">
          {{ form.grupos_ocupacionales_permitidos.length === gruposOcupacionales.length ? 'Ninguno' : 'Seleccionar todos' }}
        </button>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        <label v-for="g in gruposOcupacionales" :key="g.id" class="flex items-center gap-2 text-sm" style="color: var(--ink)">
          <input type="checkbox" :value="g.id" v-model="form.grupos_ocupacionales_permitidos" />
          {{ g.nombre }}
        </label>
        <p v-if="!gruposOcupacionales.length" class="text-sm" style="color: var(--ink-soft)">No hay grupos ocupacionales registrados.</p>
      </div>
    </div>

    <!-- Acciones -->
    <div class="flex items-center gap-3">
      <button class="btn-primary" :disabled="saving" @click="handleCreate(false)">
        {{ saving ? 'Creando...' : 'Crear' }}
      </button>
      <button class="btn-secondary" :disabled="saving" @click="handleCreate(true)">Crear y otro</button>
      <NuxtLink :to="`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId}`" class="text-sm" style="color: var(--ink-soft)">Cancelar</NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

interface Modulo {
  id: string
  code: string
  name: string
  category: string
  is_active: boolean
}

interface GrupoOcupacional {
  id: string
  nombre: string
}

const { api } = useApi()
const route = useRoute()
const router = useRouter()

const tenantId = computed(() => route.query.tenant as string || '')
const saving = ref(false)
const error = ref('')

const todosModulos = ref<Modulo[]>([])
const gruposOcupacionales = ref<GrupoOcupacional[]>([])

const modulosApp = computed(() => todosModulos.value.filter(m => m.category === 'app'))
const modulosSigarh = computed(() => todosModulos.value.filter(m => m.category === 'sigarh'))

const form = reactive({
  codigo: '',
  nombre: '',
  panel: 'app',
  modulo_requerido: '',
  descripcion: '',
  is_active: true,
  modulos_permitidos: [] as string[],
  grupos_ocupacionales_permitidos: [] as string[],
})

const toggleTodosModulos = () => {
  if (form.modulos_permitidos.length === todosModulos.value.length) {
    form.modulos_permitidos = []
  } else {
    form.modulos_permitidos = todosModulos.value.map(m => m.code)
  }
}

const toggleTodosGrupos = () => {
  if (form.grupos_ocupacionales_permitidos.length === gruposOcupacionales.value.length) {
    form.grupos_ocupacionales_permitidos = []
  } else {
    form.grupos_ocupacionales_permitidos = gruposOcupacionales.value.map(g => g.id)
  }
}

const resetForm = () => {
  Object.assign(form, {
    codigo: '', nombre: '', panel: 'app', modulo_requerido: '',
    descripcion: '', is_active: true,
    modulos_permitidos: [], grupos_ocupacionales_permitidos: [],
  })
}

const handleCreate = async (createAnother: boolean) => {
  error.value = ''
  if (!form.codigo.trim() || !form.nombre.trim()) {
    error.value = 'Código y nombre son obligatorios.'
    return
  }
  saving.value = true
  try {
    await api('/sigarh/mantenimiento/roles-sistema', {
      method: 'POST',
      body: {
        codigo: form.codigo.trim(),
        nombre: form.nombre.trim(),
        panel: form.panel,
        modulo_requerido: form.modulo_requerido || null,
        descripcion: form.descripcion || null,
        is_active: form.is_active,
        modulos_permitidos: form.modulos_permitidos,
        grupos_ocupacionales_permitidos: form.grupos_ocupacionales_permitidos,
      },
    })
    if (createAnother) {
      resetForm()
    } else {
      router.push(`/sigarh/mantenimiento/roles-sistema?tenant=${tenantId.value}`)
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo crear el rol'
  } finally {
    saving.value = false
  }
}

const cargarCatalogos = async () => {
  try {
    const [modulos, grupos] = await Promise.all([
      api<Modulo[]>('/sigarh/mantenimiento/modulos-catalogo'),
      api<GrupoOcupacional[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
    ])
    todosModulos.value = modulos
    gruposOcupacionales.value = grupos
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudieron cargar los catálogos'
  }
}

onMounted(cargarCatalogos)
</script>