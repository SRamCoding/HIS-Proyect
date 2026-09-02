<template>
  <div class="max-w-3xl mx-auto">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-3" style="color: var(--ink-soft)">
        <NuxtLink to="/admin/hospitales" style="color: var(--ink-soft)">Hospitales</NuxtLink>
        <span>/</span>
        <span>Crear</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Crear Hospital</h1>
    </div>

    <!-- Pasos -->
    <div class="flex gap-0 mb-8 overflow-x-auto">
      <div
        v-for="(paso, i) in pasos"
        :key="i"
        class="flex items-center gap-2 px-4 py-3 text-sm font-medium flex-shrink-0"
        :style="{
          background: stepActual === i ? 'var(--teal)' : 'var(--paper)',
          color: stepActual === i ? '#fff' : stepActual > i ? 'var(--teal)' : 'var(--ink-soft)',
          border: '1px solid var(--line)',
          borderRight: i < pasos.length - 1 ? 'none' : '1px solid var(--line)',
          borderRadius: i === 0 ? 'var(--radius) 0 0 var(--radius)' : i === pasos.length - 1 ? '0 var(--radius) var(--radius) 0' : '0',
          cursor: stepActual > i ? 'pointer' : 'default',
        }"
        @click="stepActual > i ? stepActual = i : null"
      >
        <span
          class="w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
          :style="{
            background: stepActual === i ? 'rgba(255,255,255,0.3)' : stepActual > i ? 'var(--teal)' : 'var(--line)',
            color: stepActual >= i ? '#fff' : 'var(--ink-soft)',
          }"
        >{{ i + 1 }}</span>
        {{ paso.label }}
      </div>
    </div>

    <!-- Step 1: Nivel -->
    <div v-if="stepActual === 0" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px">
      <div class="mb-6">
        <h2 class="font-semibold mb-1" style="color: var(--ink)">Nivel de Complejidad — MINSA Peru</h2>
        <p class="text-sm" style="color: var(--ink-soft)">El nivel determina los modulos disponibles automaticamente.</p>
      </div>

      <div v-if="loadingNiveles" class="text-sm py-4" style="color: var(--ink-soft)">Cargando niveles...</div>

      <div v-else class="grid gap-3">
        <div
          v-for="nivel in niveles"
          :key="nivel.code"
          class="flex items-start gap-3 p-4 cursor-pointer transition-all"
          :style="{
            border: `2px solid ${form.nivel_code === nivel.code ? nivel.color || 'var(--teal)' : 'var(--line)'}`,
            borderRadius: 'var(--radius)',
            background: form.nivel_code === nivel.code ? `${nivel.color}15` : 'transparent',
          }"
          @click="seleccionarNivel(nivel)"
        >
          <!-- Badge código -->
          <span
            class="text-xs font-bold px-2 py-1 rounded flex-shrink-0 mt-0.5"
            :style="{
              background: nivel.color || 'var(--teal)',
              color: '#fff',
            }"
          >{{ nivel.code }}</span>

          <div class="flex-1 min-w-0">
            <p class="font-medium text-sm" style="color: var(--ink)">{{ nivel.name }}</p>
            <p class="text-xs mt-1" style="color: var(--ink-soft)">{{ nivel.description }}</p>

            <!-- Modulos por panel -->
            <div v-if="form.nivel_code === nivel.code && modulosNivel" class="mt-3 space-y-2">
              <div v-if="modulosNivel.app?.length">
                <p class="text-xs font-medium mb-1" style="color: var(--ink-soft)">
                  PANEL ADMINISTRATIVO ({{ modulosNivel.app.length }})
                </p>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="mod in modulosNivel.app"
                    :key="mod"
                    class="text-xs px-2 py-0.5 rounded"
                    style="background: var(--teal-soft, #e6f7f5); color: var(--teal)"
                  >{{ formatModulo(mod) }}</span>
                </div>
              </div>
              <div v-if="modulosNivel.sigarh?.length">
                <p class="text-xs font-medium mb-1 mt-2" style="color: var(--ink-soft)">
                  PANEL SIGARH ({{ modulosNivel.sigarh.length }})
                </p>
                <div class="flex flex-wrap gap-1">
                  <span
                    v-for="mod in modulosNivel.sigarh"
                    :key="mod"
                    class="text-xs px-2 py-0.5 rounded"
                    style="background: #f0f0ff; color: #6366f1"
                  >{{ formatModulo(mod) }}</span>
                </div>
              </div>
            </div>

            <!-- Loading modulos -->
            <div v-else-if="form.nivel_code === nivel.code && loadingModulos" class="mt-2 text-xs" style="color: var(--ink-soft)">
              Cargando modulos...
            </div>
          </div>

          <!-- Check -->
          <div
            class="w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 mt-0.5"
            :style="{
              borderColor: form.nivel_code === nivel.code ? nivel.color || 'var(--teal)' : 'var(--line)',
              background: form.nivel_code === nivel.code ? nivel.color || 'var(--teal)' : 'transparent',
            }"
          >
            <span v-if="form.nivel_code === nivel.code" style="color: #fff; font-size: 10px">✓</span>
          </div>
        </div>
      </div>

      <div v-if="!form.nivel_code" class="mt-4 text-sm" style="color: var(--ink-soft)">
        Selecciona un nivel para continuar.
      </div>
    </div>

    <!-- Step 2: Identidad (placeholder) -->
    <div v-if="stepActual === 1" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px">
      <h2 class="font-semibold mb-4" style="color: var(--ink)">Identidad del hospital</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">Nombre del hospital</label>
          <input v-model="form.name" class="input-clinical" placeholder="Ej: Hospital Tuman" required />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">Subdominio</label>
          <div class="flex items-center gap-0">
            <input v-model="form.subdomain" class="input-clinical rounded-r-none" placeholder="hospital-tuman" />
            <span class="px-3 py-2 text-sm border border-l-0" style="background: var(--bg-soft, #f5f5f5); color: var(--ink-soft); border-color: var(--line); border-radius: 0 var(--radius) var(--radius) 0">.erp.local</span>
          </div>
        </div>
        <div>
          <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">RUC</label>
          <input v-model="form.ruc" class="input-clinical" placeholder="20123456789" maxlength="11" />
        </div>
      </div>
    </div>

    <!-- Step 3: Usuarios (placeholder) -->
    <div v-if="stepActual === 2" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px">
      <h2 class="font-semibold mb-4" style="color: var(--ink)">Usuarios del hospital</h2>
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">Nombre del administrador</label>
          <input v-model="form.admin_name" class="input-clinical" placeholder="Juan Perez" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">Email del administrador</label>
          <input v-model="form.admin_email" class="input-clinical" type="email" placeholder="admin@hospital.pe" />
        </div>
        <div>
          <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">Contrasena temporal</label>
          <input v-model="form.admin_password" class="input-clinical" type="password" placeholder="Min. 8 caracteres" />
        </div>
      </div>
    </div>

    <!-- Step 4: Modulos (placeholder) -->
    <div v-if="stepActual === 3" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius); padding: 24px">
      <h2 class="font-semibold mb-2" style="color: var(--ink)">Modulos activados</h2>
      <p class="text-sm mb-4" style="color: var(--ink-soft)">
        Basado en el nivel <strong>{{ form.nivel_code }}</strong>. Puedes personalizar antes de crear.
      </p>

      <div v-if="modulosNivel" class="space-y-4">
        <div>
          <p class="text-xs font-medium mb-2" style="color: var(--ink-soft)">PANEL ADMINISTRATIVO</p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="mod in modulosNivel.app"
              :key="mod"
              class="text-sm px-3 py-1 rounded"
              style="background: var(--teal-soft, #e6f7f5); color: var(--teal)"
            >{{ formatModulo(mod) }}</span>
          </div>
        </div>
        <div>
          <p class="text-xs font-medium mb-2" style="color: var(--ink-soft)">PANEL SIGARH</p>
          <div class="flex flex-wrap gap-2">
            <span
              v-for="mod in modulosNivel.sigarh"
              :key="mod"
              class="text-sm px-3 py-1 rounded"
              style="background: #f0f0ff; color: #6366f1"
            >{{ formatModulo(mod) }}</span>
          </div>
        </div>
      </div>

      <div v-if="createError" class="mt-4 text-sm rounded px-3 py-2" style="background: var(--alert-soft); color: var(--alert)">
        {{ createError }}
      </div>
    </div>

    <!-- Navegacion -->
    <div class="flex items-center justify-between mt-6">
      <button
        v-if="stepActual > 0"
        class="text-sm font-medium px-4 py-2"
        style="color: var(--ink-soft)"
        @click="stepActual--"
      >
        Atras
      </button>
      <NuxtLink
        v-else
        to="/admin/hospitales"
        class="text-sm font-medium px-4 py-2"
        style="color: var(--ink-soft)"
      >
        Cancelar
      </NuxtLink>

      <button
        v-if="stepActual < pasos.length - 1"
        class="btn-primary"
        :disabled="!puedeAvanzar"
        @click="stepActual++"
      >
        Siguiente
      </button>

      <button
        v-else
        class="btn-primary"
        :disabled="creating"
        @click="handleCreate"
      >
        {{ creating ? 'Creando...' : 'Crear hospital' }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'admin', middleware: ['auth', 'panel'] })

const { api } = useApi()
const router = useRouter()

interface Nivel {
  id: string
  code: string
  name: string
  description: string
  color: string | null
  default_modules: { app: string[]; sigarh: string[] } | null
  sort_order: number
}

const pasos = [
  { label: 'Nivel' },
  { label: 'Identidad' },
  { label: 'Usuarios' },
  { label: 'Modulos' },
]

const stepActual = ref(0)
const niveles = ref<Nivel[]>([])
const loadingNiveles = ref(true)
const loadingModulos = ref(false)
const modulosNivel = ref<{ app: string[]; sigarh: string[] } | null>(null)
const creating = ref(false)
const createError = ref('')

const form = reactive({
  nivel_code: '',
  name: '',
  subdomain: '',
  ruc: '',
  admin_name: '',
  admin_email: '',
  admin_password: '',
})

const puedeAvanzar = computed(() => {
  if (stepActual.value === 0) return !!form.nivel_code
  if (stepActual.value === 1) return !!form.name && !!form.subdomain
  if (stepActual.value === 2) return !!form.admin_email
  return true
})

const formatModulo = (code: string) => {
  return code
    .replace('sigarh_', '')
    .replace(/_/g, ' ')
    .replace(/\b\w/g, c => c.toUpperCase())
}

const seleccionarNivel = async (nivel: Nivel) => {
  form.nivel_code = nivel.code
  modulosNivel.value = null

  if (nivel.default_modules) {
    modulosNivel.value = nivel.default_modules
    return
  }

  // Si no tiene default_modules en la lista, pedir al endpoint
  loadingModulos.value = true
  try {
    const data = await api<any>(`/admin/niveles-hospitalarios/${nivel.code}/modulos`)
    modulosNivel.value = data.default_modules
  } catch {
    modulosNivel.value = { app: [], sigarh: [] }
  } finally {
    loadingModulos.value = false
  }
}

const handleCreate = async () => {
  creating.value = true
  createError.value = ''
  try {
    const domain = `${form.subdomain}.erp.local`
    const activeModules = [
      ...(modulosNivel.value?.app || []),
      ...(modulosNivel.value?.sigarh || []),
    ]

    await api('/admin/hospitales', {
      method: 'POST',
      body: {
        name: form.name,
        domain,
        ruc: form.ruc || null,
        hospital_level: form.nivel_code,
        active_modules: activeModules,
      },
    })

    router.push('/admin/hospitales')
  } catch (e: any) {
    createError.value = e?.data?.detail || 'No se pudo crear el hospital'
    stepActual.value = 3
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  try {
    niveles.value = await api<Nivel[]>('/admin/niveles-hospitalarios')
  } catch {
    //
  } finally {
    loadingNiveles.value = false
  }
})
</script>