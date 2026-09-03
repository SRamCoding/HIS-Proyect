<template>
  <div class="max-w-7xl mx-auto px-4 lg:px-8">
    <!-- Header -->
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-6">
      <div>
        <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
          <NuxtLink to="/admin/hospitales" class="hover:underline" style="color: var(--ink-soft)">Hospitales</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3.5 h-3.5" />
          <span style="color: var(--ink)">Editar</span>
        </div>
        <h1 class="text-xl font-semibold" style="color: var(--ink)">Editar hospital</h1>
      </div>
      <button
        class="px-4 py-2 rounded-lg text-sm font-medium flex items-center justify-center gap-1.5 shrink-0 transition-opacity hover:opacity-90"
        style="background: var(--alert); color: white"
        @click="confirmarEliminar"
      >
        <UIcon name="i-heroicons-trash" class="w-4 h-4" />
        Borrar
      </button>
    </div>

    <div
      v-if="loading"
      class="flex items-center gap-2 p-8 text-sm justify-center"
      style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); color: var(--ink-soft)"
    >
      <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
      Cargando...
    </div>
    <div
      v-else-if="error"
      class="flex items-center gap-2 p-6 text-sm"
      style="background: var(--alert-soft); color: var(--alert); border-radius: var(--radius-lg)"
    >
      <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
      {{ error }}
    </div>

    <!-- Layout 2 columnas -->
    <div v-else class="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6 items-start">

      <!-- Columna principal -->
      <div>
        <!-- Identidad -->
        <section class="mb-4 p-5" style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
          <p class="text-sm font-semibold mb-4 flex items-center gap-2" style="color: var(--ink)">
            <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" style="color: var(--navy)" />
            Identidad del hospital
          </p>
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
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
            <div class="sm:col-span-2">
              <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Dirección</label>
              <input v-model="form.address" class="input-clinical" />
            </div>
            <div class="sm:col-span-2 flex items-center gap-2 pt-1">
              <input type="checkbox" v-model="form.is_active" id="activo" class="rounded" style="accent-color: var(--teal)" />
              <label for="activo" class="text-sm" style="color: var(--ink)">Hospital activo</label>
            </div>
          </div>
        </section>

        <!-- Misión, Visión y Valores -->
        <section class="mb-4 overflow-hidden" style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
          <button
            class="w-full flex items-center justify-between p-4 text-sm font-medium"
            style="color: var(--ink)"
            @click="toggleSection('mision')"
          >
            <span class="flex items-center gap-2">
              <UIcon name="i-heroicons-flag" class="w-4 h-4" style="color: var(--navy)" />
              Misión, visión y valores
            </span>
            <UIcon
              name="i-heroicons-chevron-down"
              class="w-4 h-4 transition-transform"
              :style="{ transform: openSections.mision ? 'rotate(180deg)' : 'rotate(0deg)' }"
            />
          </button>
          <div v-if="openSections.mision" class="px-5 pb-5 space-y-3" style="border-top: 1px solid var(--line)">
            <div class="pt-4">
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
        <section class="mb-4 p-5" style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
          <p class="text-sm font-semibold mb-1 flex items-center gap-2" style="color: var(--ink)">
            <UIcon name="i-heroicons-squares-plus" class="w-4 h-4" style="color: var(--teal)" />
            Módulos del panel administrativo
            <span class="text-xs font-normal font-mono-data" style="color: var(--ink-soft)">/app</span>
          </p>
          <p class="text-xs mb-4" style="color: var(--ink-soft)">Módulos clínicos y administrativos del panel principal del hospital.</p>

          <div class="flex items-center gap-3 mb-3">
            <UInput
              v-model="searchModApp"
              icon="i-heroicons-magnifying-glass"
              placeholder="Buscar módulo..."
              size="sm"
              class="flex-1"
            />
            <button class="text-xs font-medium shrink-0" style="color: var(--teal)" @click="deseleccionarTodos('app')">
              Deseleccionar todos
            </button>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
            <label
              v-for="mod in modulosFiltradosApp"
              :key="mod.code"
              class="flex items-center gap-2 text-sm cursor-pointer px-3 py-2 rounded-lg transition-colors"
              style="color: var(--ink); border: 1px solid var(--line)"
            >
              <input
                type="checkbox"
                :value="mod.code"
                v-model="modulosActivos"
                class="rounded shrink-0"
                style="accent-color: var(--teal)"
              />
              <span class="truncate">{{ mod.name }}</span>
            </label>
          </div>
        </section>

        <!-- Módulos Panel SIGARH -->
        <section class="mb-4 p-5" style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)">
          <p class="text-sm font-semibold mb-1 flex items-center gap-2" style="color: var(--ink)">
            <UIcon name="i-heroicons-folder-open" class="w-4 h-4" style="color: #6366f1" />
            Módulos del panel SIGARH
            <span class="text-xs font-normal font-mono-data" style="color: var(--ink-soft)">/sigarh</span>
          </p>
          <p class="text-xs mb-4" style="color: var(--ink-soft)">Módulos de configuración y recursos humanos del panel SIGARH.</p>

          <div class="flex items-center gap-3 mb-3">
            <UInput
              v-model="searchModSigarh"
              icon="i-heroicons-magnifying-glass"
              placeholder="Buscar módulo..."
              size="sm"
              class="flex-1"
            />
            <button class="text-xs font-medium shrink-0" style="color: var(--teal)" @click="deseleccionarTodos('sigarh')">
              Deseleccionar todos
            </button>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
            <label
              v-for="mod in modulosFiltradosSigarh"
              :key="mod.code"
              class="flex items-center gap-2 text-sm cursor-pointer px-3 py-2 rounded-lg transition-colors"
              style="color: var(--ink); border: 1px solid var(--line)"
            >
              <input
                type="checkbox"
                :value="mod.code"
                v-model="modulosActivos"
                class="rounded shrink-0"
                style="accent-color: var(--teal)"
              />
              <span class="truncate">{{ mod.name }}</span>
            </label>
          </div>
        </section>

        <!-- Error -->
        <div
          v-if="saveError"
          class="mb-4 flex items-center gap-2 text-sm px-3 py-2.5 rounded-lg"
          style="background: var(--alert-soft); color: var(--alert)"
        >
          <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
          {{ saveError }}
        </div>

        <!-- Acciones -->
        <div class="flex flex-col-reverse sm:flex-row gap-3">
          <NuxtLink
            to="/admin/hospitales"
            class="px-4 py-2 rounded-lg text-sm text-center"
            style="border: 1px solid var(--line); color: var(--ink-soft)"
          >
            Cancelar
          </NuxtLink>
          <button class="btn-primary flex items-center justify-center gap-1.5" :disabled="saving" @click="handleSave">
            <UIcon v-if="saving" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            {{ saving ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>
      </div>

      <!-- Columna lateral — contexto dinámico -->
      <aside class="hidden lg:block sticky top-6 space-y-4">

        <!-- Estado del hospital -->
        <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
          <div class="flex items-center justify-between mb-4">
            <p class="text-xs font-semibold tracking-wide uppercase" style="color: var(--ink-soft)">Estado</p>
            <div class="relative w-10 h-10 shrink-0">
              <svg viewBox="0 0 36 36" class="w-10 h-10 -rotate-90">
                <circle cx="18" cy="18" r="15.5" fill="none" stroke="var(--mist)" stroke-width="3" />
                <circle
                  cx="18" cy="18" r="15.5" fill="none" stroke="var(--teal)" stroke-width="3"
                  stroke-linecap="round"
                  :stroke-dasharray="`${(porcentajeModulos / 100) * 97.4} 97.4`"
                />
              </svg>
              <span class="absolute inset-0 flex items-center justify-center text-[10px] font-bold" style="color: var(--ink)">
                {{ modulosActivos.length }}
              </span>
            </div>
          </div>

          <div class="flex items-center gap-3 mb-4 pb-4" style="border-bottom: 1px solid var(--line)">
            <div class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0" style="background: var(--mist)">
              <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--navy)" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium truncate" style="color: var(--ink)">{{ form.name || '—' }}</p>
              <p class="text-xs truncate font-mono-data" style="color: var(--ink-soft)">
                {{ subdomain ? `${subdomain}.erp.local` : '—' }}
              </p>
            </div>
          </div>

          <div class="space-y-3 text-sm">
            <div class="flex items-center justify-between">
              <span style="color: var(--ink-soft)">Estado</span>
              <span class="badge" :class="form.is_active ? 'badge--ok' : 'badge--neutral'">
                {{ form.is_active ? 'Activo' : 'Inactivo' }}
              </span>
            </div>
            <div class="flex items-center justify-between">
              <span style="color: var(--ink-soft)">Nivel</span>
              <span style="color: var(--ink)">{{ form.hospital_level || '—' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span style="color: var(--ink-soft)">Módulos activos</span>
              <span style="color: var(--ink)">{{ modulosActivos.length }} / {{ todosModulos.length }}</span>
            </div>
          </div>

          <!-- Distribución de módulos App vs SIGARH -->
          <div v-if="modulosActivos.length" class="mt-4 pt-4" style="border-top: 1px solid var(--line)">
            <div class="flex items-center justify-between text-xs mb-1.5">
              <span style="color: var(--ink-soft)">Panel admin</span>
              <span style="color: var(--ink-soft)">Panel SIGARH</span>
            </div>
            <div class="flex h-2 rounded-full overflow-hidden" style="background: var(--mist)">
              <div :style="{ width: `${porcentajeApp}%`, background: 'var(--teal)' }" />
              <div :style="{ width: `${100 - porcentajeApp}%`, background: '#6366f1' }" />
            </div>
            <div class="flex items-center justify-between text-xs mt-1.5" style="color: var(--ink)">
              <span>{{ activosApp }}</span>
              <span>{{ activosSigarh }}</span>
            </div>
          </div>
        </div>

        <!-- Accesos rápidos -->
        <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
          <p class="text-xs font-semibold mb-4 tracking-wide uppercase" style="color: var(--ink-soft)">Accesos rápidos</p>
          <div class="space-y-1.5">
            <button
              class="w-full flex items-center gap-2.5 text-sm px-3 py-2 rounded-lg transition-colors text-left"
              style="color: var(--ink)"
              @click="irA('')"
            >
              <UIcon name="i-heroicons-globe-alt" class="w-4 h-4" style="color: var(--ink-soft)" />
              Ver landing
            </button>
            <button
              class="w-full flex items-center gap-2.5 text-sm px-3 py-2 rounded-lg transition-colors text-left"
              style="color: var(--ink)"
              @click="irA('/app')"
            >
              <UIcon name="i-heroicons-squares-2x2" class="w-4 h-4" style="color: var(--teal)" />
              Panel admin
            </button>
            <button
              class="w-full flex items-center gap-2.5 text-sm px-3 py-2 rounded-lg transition-colors text-left"
              style="color: var(--ink)"
              @click="irA('/sigarh')"
            >
              <UIcon name="i-heroicons-folder-open" class="w-4 h-4" style="color: #6366f1" />
              Panel SIGARH
            </button>
          </div>
        </div>

        <!-- Tip contextual -->
        <div class="p-4 flex gap-3" style="background: var(--teal-soft); border-radius: var(--radius-lg)">
          <UIcon name="i-heroicons-light-bulb" class="w-5 h-5 shrink-0" style="color: var(--teal)" />
          <p class="text-xs leading-relaxed" style="color: var(--ink)">
            Los cambios en módulos se aplican de inmediato al guardar. Desactivar un módulo no elimina los datos ya registrados en él.
          </p>
        </div>
      </aside>
    </div>
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

const activosApp = computed(() =>
  todosModulos.value.filter(m => m.category === 'app' && modulosActivos.value.includes(m.code)).length
)

const activosSigarh = computed(() =>
  todosModulos.value.filter(m => m.category === 'sigarh' && modulosActivos.value.includes(m.code)).length
)

const porcentajeApp = computed(() =>
  modulosActivos.value.length
    ? Math.round((activosApp.value / modulosActivos.value.length) * 100)
    : 50
)

const porcentajeModulos = computed(() =>
  todosModulos.value.length
    ? Math.round((modulosActivos.value.length / todosModulos.value.length) * 100)
    : 0
)

const toggleSection = (key: keyof typeof openSections) => {
  openSections[key] = !openSections[key]
}

const deseleccionarTodos = (category: string) => {
  const codes = todosModulos.value.filter(m => m.category === category).map(m => m.code)
  modulosActivos.value = modulosActivos.value.filter(c => !codes.includes(c))
}

const irA = (path: string) => {
  const tenantId = id.value
  if (path === '') {
    window.open(`http://localhost:3000?tenant=${tenantId}`, '_blank')
  } else if (path === '/sigarh') {
    window.open(`http://localhost:3000/sigarh/login?tenant=${tenantId}`, '_blank')
  } else {
    window.open(`http://localhost:3000${path}?tenant=${tenantId}`, '_blank')
  }
}

const confirmarEliminar = async () => {
  if (!confirm('¿Estás seguro de eliminar este hospital? Esta acción no se puede deshacer.')) return
  alert('Función en desarrollo')
}

const handleSave = async () => {
  saving.value = true
  saveError.value = ''
  try {
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