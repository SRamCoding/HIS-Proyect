<template>
  <div class="max-w-3xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink to="/admin/niveles-hospitalarios" style="color: var(--ink-soft)">Niveles Hospitalarios</NuxtLink>
        <span>/</span><span>Crear</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Crear Nivel Hospitalario</h1>
    </div>

    <!-- Datos del Nivel -->
    <section class="mb-4 p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <p class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: var(--ink)">
        🏛 Datos del Nivel
      </p>
      <div class="grid grid-cols-2 gap-4">
        <div>
          <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Código MINSA*</label>
          <input v-model="form.code" class="input-clinical" placeholder="Ej: III-1" />
        </div>
        <div>
          <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Nombre*</label>
          <input v-model="form.name" class="input-clinical" placeholder="Ej: Hospital Nacional / Especializado" />
        </div>
        <div class="col-span-2">
          <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Descripción</label>
          <textarea v-model="form.description" class="input-clinical" rows="2" />
        </div>
        <div>
          <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Color identificador*</label>
          <div class="flex items-center gap-2">
            <input v-model="form.color" class="input-clinical flex-1" placeholder="#6b7280" />
            <input type="color" v-model="form.color" class="w-8 h-8 rounded cursor-pointer border" style="border-color: var(--line)" />
          </div>
        </div>
        <div>
          <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Orden</label>
          <input v-model.number="form.sort_order" type="number" class="input-clinical" />
        </div>
        <div class="col-span-2 flex items-center gap-2">
          <input type="checkbox" v-model="form.is_active" id="activo" />
          <label for="activo" class="text-sm" style="color: var(--ink)">Activo</label>
        </div>
      </div>
    </section>

    <!-- Módulos App -->
    <section class="mb-4 p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <p class="text-sm font-semibold mb-1" style="color: var(--ink)">⚙ Módulos del Panel Administrativo (/app)</p>
      <p class="text-xs mb-3" style="color: var(--ink-soft)">Módulos que se activarán automáticamente al crear un hospital de este nivel.</p>
      <button class="text-xs mb-3" style="color: var(--teal)" @click="seleccionarTodos('app')">Seleccionar todos</button>
      <div class="grid grid-cols-3 gap-2">
        <label v-for="mod in modulosApp" :key="mod.code" class="flex items-center gap-2 text-sm cursor-pointer" style="color: var(--ink)">
          <input type="checkbox" :value="mod.code" v-model="modulosSeleccionados" />
          {{ mod.name }}
        </label>
      </div>
    </section>

    <!-- Módulos SIGARH -->
    <section class="mb-4 p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
      <p class="text-sm font-semibold mb-1" style="color: var(--ink)">🗂 Módulos del Panel SIGARH (/sigarh)</p>
      <p class="text-xs mb-3" style="color: var(--ink-soft)">Módulos de configuración y RRHH que se activarán para este nivel.</p>
      <button class="text-xs mb-3" style="color: var(--teal)" @click="seleccionarTodos('sigarh')">Seleccionar todos</button>
      <div class="grid grid-cols-3 gap-2">
        <label v-for="mod in modulosSigarh" :key="mod.code" class="flex items-center gap-2 text-sm cursor-pointer" style="color: var(--ink)">
          <input type="checkbox" :value="mod.code" v-model="modulosSeleccionados" />
          {{ mod.name }}
        </label>
      </div>
    </section>

    <div v-if="error" class="mb-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">
      {{ error }}
    </div>

    <div class="flex gap-3">
      <button class="btn-primary" :disabled="saving" @click="handleCreate(false)">
        {{ saving ? 'Creando...' : 'Crear' }}
      </button>
      <button
        class="px-4 py-2 rounded text-sm font-medium"
        style="border: 1px solid var(--line); color: var(--ink)"
        :disabled="saving"
        @click="handleCreate(true)"
      >
        Crear y crear otro
      </button>
      <NuxtLink to="/admin/niveles-hospitalarios" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">
        Cancelar
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

const { api } = useApi()
const router = useRouter()

const saving = ref(false)
const error = ref('')
const modulosSeleccionados = ref<string[]>([])
const todosModulos = ref<any[]>([])

const form = reactive({
  code: '',
  name: '',
  description: '',
  color: '#6b7280',
  sort_order: 99,
  is_active: true,
})

const modulosApp = computed(() => todosModulos.value.filter(m => m.category === 'app'))
const modulosSigarh = computed(() => todosModulos.value.filter(m => m.category === 'sigarh'))

const seleccionarTodos = (category: string) => {
  const codes = todosModulos.value.filter(m => m.category === category).map(m => m.code)
  codes.forEach(c => {
    if (!modulosSeleccionados.value.includes(c)) modulosSeleccionados.value.push(c)
  })
}

const handleCreate = async (createAnother: boolean) => {
  saving.value = true
  error.value = ''
  try {
    const appMods = modulosSeleccionados.value.filter(c =>
      modulosApp.value.some(m => m.code === c)
    )
    const sigarhMods = modulosSeleccionados.value.filter(c =>
      modulosSigarh.value.some(m => m.code === c)
    )

    await api('/admin/niveles-hospitalarios', {
      method: 'POST',
      body: {
        code: form.code,
        name: form.name,
        description: form.description || null,
        color: form.color,
        sort_order: form.sort_order,
        default_modules: { app: appMods, sigarh: sigarhMods },
        default_roles: [],
      },
    })

    if (createAnother) {
      Object.assign(form, { code: '', name: '', description: '', color: '#6b7280', sort_order: 99, is_active: true })
      modulosSeleccionados.value = []
    } else {
      router.push('/admin/niveles-hospitalarios')
    }
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo crear el nivel'
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  todosModulos.value = await api<any[]>('/admin/modulos/catalogo')
})
</script>