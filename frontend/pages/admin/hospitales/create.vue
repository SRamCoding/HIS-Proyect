<template>
  <div class="max-w-7xl mx-auto px-4 lg:px-8">
    <!-- Header -->
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-3" style="color: var(--ink-soft)">
        <NuxtLink to="/admin/hospitales" class="hover:underline" style="color: var(--ink-soft)">Hospitales</NuxtLink>
        <UIcon name="i-heroicons-chevron-right" class="w-3.5 h-3.5" />
        <span style="color: var(--ink)">Crear</span>
      </div>
      <h1 class="text-xl font-semibold" style="color: var(--ink)">Crear hospital</h1>
    </div>

    <!-- Stepper -->
    <div class="mb-8 overflow-x-auto -mx-4 px-4 lg:mx-0 lg:px-0">
      <div class="flex items-center min-w-[560px] lg:min-w-0 lg:max-w-2xl">
        <template v-for="(paso, i) in pasos" :key="i">
          <div
            class="flex flex-col items-center gap-2 shrink-0"
            :class="stepActual > i ? 'cursor-pointer' : ''"
            style="width: 120px"
            @click="stepActual > i ? stepActual = i : null"
          >
            <div
              class="w-9 h-9 rounded-full flex items-center justify-center text-sm font-semibold transition-colors"
              :style="{
                background: stepActual === i ? 'var(--navy)' : stepActual > i ? 'var(--teal)' : 'var(--paper)',
                color: stepActual >= i ? '#fff' : 'var(--ink-soft)',
                border: stepActual === i ? '2px solid var(--navy)' : '2px solid var(--line)',
              }"
            >
              <UIcon v-if="stepActual > i" name="i-heroicons-check" class="w-4 h-4" />
              <span v-else>{{ i + 1 }}</span>
            </div>
            <span
              class="text-xs font-medium text-center"
              :style="{ color: stepActual === i ? 'var(--ink)' : 'var(--ink-soft)' }"
            >{{ paso.label }}</span>
          </div>

          <div
            v-if="i < pasos.length - 1"
            class="flex-1 h-0.5 mb-6 mx-1"
            :style="{ background: stepActual > i ? 'var(--teal)' : 'var(--line)' }"
          />
        </template>
      </div>
    </div>

    <!-- Layout 2 columnas -->
    <div class="grid grid-cols-1 lg:grid-cols-[1fr_340px] gap-6 items-start">

      <!-- Columna principal -->
      <div>
        <!-- Step 1: Nivel -->
        <div
          v-if="stepActual === 0"
          style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 24px"
        >
          <div class="mb-6">
            <h2 class="font-semibold mb-1 text-base" style="color: var(--ink)">Nivel de complejidad — MINSA Perú</h2>
            <p class="text-sm" style="color: var(--ink-soft)">El nivel determina los módulos disponibles automáticamente.</p>
          </div>

          <div v-if="loadingNiveles" class="flex items-center gap-2 text-sm py-6" style="color: var(--ink-soft)">
            <UIcon name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            Cargando niveles...
          </div>

          <div v-else class="grid gap-3">
            <div
              v-for="nivel in niveles"
              :key="nivel.code"
              class="flex items-start gap-3 p-4 cursor-pointer transition-all"
              :style="{
                border: `2px solid ${form.nivel_code === nivel.code ? (nivel.color || 'var(--teal)') : 'var(--line)'}`,
                borderRadius: 'var(--radius-lg)',
                background: form.nivel_code === nivel.code ? `${nivel.color}12` : 'var(--paper)',
              }"
              @click="seleccionarNivel(nivel)"
            >
              <span
                class="text-xs font-bold px-2 py-1 rounded-md shrink-0 mt-0.5"
                :style="{ background: nivel.color || 'var(--teal)', color: '#fff' }"
              >{{ nivel.code }}</span>

              <div class="flex-1 min-w-0">
                <p class="font-medium text-sm" style="color: var(--ink)">{{ nivel.name }}</p>
                <p class="text-xs mt-1" style="color: var(--ink-soft)">{{ nivel.description }}</p>

                <div v-if="form.nivel_code === nivel.code && modulosNivel" class="mt-3 space-y-3">
                  <div v-if="modulosNivel.app?.length">
                    <p class="text-xs font-semibold mb-1.5 tracking-wide uppercase" style="color: var(--ink-soft)">
                      Panel administrativo ({{ modulosNivel.app.length }})
                    </p>
                    <div class="flex flex-wrap gap-1.5">
                      <span
                        v-for="mod in modulosNivel.app"
                        :key="mod"
                        class="text-xs px-2.5 py-1 rounded-full font-medium"
                        style="background: var(--teal-soft); color: var(--teal)"
                      >{{ formatModulo(mod) }}</span>
                    </div>
                  </div>
                  <div v-if="modulosNivel.sigarh?.length">
                    <p class="text-xs font-semibold mb-1.5 tracking-wide uppercase" style="color: var(--ink-soft)">
                      Panel SIGARH ({{ modulosNivel.sigarh.length }})
                    </p>
                    <div class="flex flex-wrap gap-1.5">
                      <span
                        v-for="mod in modulosNivel.sigarh"
                        :key="mod"
                        class="text-xs px-2.5 py-1 rounded-full font-medium"
                        style="background: #eef0fd; color: #6366f1"
                      >{{ formatModulo(mod) }}</span>
                    </div>
                  </div>
                </div>

                <div v-else-if="form.nivel_code === nivel.code && loadingModulos" class="mt-2 flex items-center gap-1.5 text-xs" style="color: var(--ink-soft)">
                  <UIcon name="i-heroicons-arrow-path" class="w-3.5 h-3.5 animate-spin" />
                  Cargando módulos...
                </div>
              </div>

              <div
                class="w-5 h-5 rounded-full border-2 flex items-center justify-center shrink-0 mt-0.5"
                :style="{
                  borderColor: form.nivel_code === nivel.code ? (nivel.color || 'var(--teal)') : 'var(--line)',
                  background: form.nivel_code === nivel.code ? (nivel.color || 'var(--teal)') : 'transparent',
                }"
              >
                <UIcon v-if="form.nivel_code === nivel.code" name="i-heroicons-check" class="w-3 h-3 text-white" />
              </div>
            </div>
          </div>

          <p v-if="!form.nivel_code" class="mt-4 text-sm" style="color: var(--ink-soft)">
            Selecciona un nivel para continuar.
          </p>
        </div>

        <!-- Step 2: Identidad -->
        <div
          v-if="stepActual === 1"
          style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 24px"
        >
          <h2 class="font-semibold mb-4 text-base" style="color: var(--ink)">Identidad del hospital</h2>
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">Nombre del hospital</label>
              <input v-model="form.name" class="input-clinical" placeholder="Ej: Hospital Túmán" required />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">Subdominio</label>
              <div class="flex items-stretch">
                <input v-model="form.subdomain" class="input-clinical rounded-r-none flex-1 min-w-0" placeholder="hospital-tuman" />
                <span
                  class="px-3 flex items-center text-sm border border-l-0 shrink-0"
                  style="background: var(--mist); color: var(--ink-soft); border-color: var(--line); border-radius: 0 var(--radius) var(--radius) 0"
                >.erp.local</span>
              </div>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1.5" style="color: var(--ink)">RUC</label>
              <input v-model="form.ruc" class="input-clinical" placeholder="20123456789" maxlength="11" />
            </div>
          </div>
        </div>

        <!-- Step 3: Usuarios -->
        <div
          v-if="stepActual === 2"
          style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 24px"
          class="space-y-6"
        >
          <div class="p-4 rounded-xl" style="border: 1px solid var(--line)">
            <p class="text-sm font-semibold mb-1 flex items-center gap-2" style="color: var(--ink)">
              <UIcon name="i-heroicons-user-circle" class="w-4 h-4" style="color: var(--teal)" />
              Administrador del hospital
            </p>
            <p class="text-xs mb-4" style="color: var(--ink-soft)">Acceso al panel de admisiones, caja y operaciones clínicas.</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Nombre completo*</label>
                <input v-model="form.admin_name" class="input-clinical" placeholder="Lic. Carmen Flores Medina" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Correo electrónico*</label>
                <input v-model="form.admin_email" type="email" class="input-clinical" placeholder="admin@hospital.pe" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Contraseña*</label>
                <input v-model="form.admin_password" type="password" class="input-clinical" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Confirmar contraseña*</label>
                <input v-model="form.admin_password_confirm" type="password" class="input-clinical" />
              </div>
            </div>
          </div>

          <div class="p-4 rounded-xl" style="border: 1px solid var(--line)">
            <p class="text-sm font-semibold mb-1 flex items-center gap-2" style="color: var(--ink)">
              <UIcon name="i-heroicons-folder-open" class="w-4 h-4" style="color: #6366f1" />
              Usuario SIGARH
            </p>
            <p class="text-xs mb-4" style="color: var(--ink-soft)">Acceso a configuración: médicos, turnos, recursos humanos.</p>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Nombre completo*</label>
                <input v-model="form.sigarh_name" class="input-clinical" placeholder="Ing. Marco Quispe Huanca" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Correo electrónico*</label>
                <input v-model="form.sigarh_email" type="email" class="input-clinical" placeholder="sigarh@hospital.pe" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Contraseña*</label>
                <input v-model="form.sigarh_password" type="password" class="input-clinical" />
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--ink-soft)">Confirmar contraseña*</label>
                <input v-model="form.sigarh_password_confirm" type="password" class="input-clinical" />
              </div>
            </div>
          </div>
        </div>

        <!-- Step 4: Modulos -->
        <div
          v-if="stepActual === 3"
          style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 24px"
        >
          <h2 class="font-semibold mb-2 text-base" style="color: var(--ink)">Módulos activados</h2>
          <p class="text-sm mb-4" style="color: var(--ink-soft)">
            Basado en el nivel <span class="font-medium" style="color: var(--ink)">{{ form.nivel_code }}</span>. Puedes personalizar antes de crear.
          </p>

          <div v-if="modulosNivel" class="space-y-4">
            <div>
              <p class="text-xs font-semibold mb-2 tracking-wide uppercase" style="color: var(--ink-soft)">Panel administrativo</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="mod in modulosNivel.app"
                  :key="mod"
                  class="text-sm px-3 py-1 rounded-full font-medium"
                  style="background: var(--teal-soft); color: var(--teal)"
                >{{ formatModulo(mod) }}</span>
              </div>
            </div>
            <div>
              <p class="text-xs font-semibold mb-2 tracking-wide uppercase" style="color: var(--ink-soft)">Panel SIGARH</p>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="mod in modulosNivel.sigarh"
                  :key="mod"
                  class="text-sm px-3 py-1 rounded-full font-medium"
                  style="background: #eef0fd; color: #6366f1"
                >{{ formatModulo(mod) }}</span>
              </div>
            </div>
          </div>

          <div v-if="createError" class="mt-4 flex items-center gap-2 text-sm rounded-lg px-3 py-2.5" style="background: var(--alert-soft); color: var(--alert)">
            <UIcon name="i-heroicons-exclamation-triangle" class="w-4 h-4 shrink-0" />
            {{ createError }}
          </div>
        </div>

        <!-- Navegacion -->
        <div class="flex items-center justify-between mt-6 gap-3">
          <button
            v-if="stepActual > 0"
            class="text-sm font-medium px-4 py-2 flex items-center gap-1.5"
            style="color: var(--ink-soft)"
            @click="stepActual--"
          >
            <UIcon name="i-heroicons-arrow-left" class="w-4 h-4" />
            Atrás
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
            class="btn-primary flex items-center gap-1.5"
            :disabled="!puedeAvanzar"
            @click="stepActual++"
          >
            Siguiente
            <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" />
          </button>

          <button
            v-else
            class="btn-primary flex items-center gap-1.5"
            :disabled="creating"
            @click="handleCreate"
          >
            <UIcon v-if="creating" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" />
            {{ creating ? 'Creando...' : 'Crear hospital' }}
          </button>
        </div>

        <!-- Hospitales creados recientemente -->
        <div v-if="hospitalesRecientes.length" class="mt-8">
          <p class="text-xs font-semibold mb-3 tracking-wide uppercase" style="color: var(--ink-soft)">Creados recientemente</p>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-3">
            <div
              v-for="h in hospitalesRecientes"
              :key="h.id"
              class="flex items-center gap-2.5 p-3"
              style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card)"
            >
              <div class="w-8 h-8 rounded-lg flex items-center justify-center shrink-0" style="background: var(--mist)">
                <UIcon name="i-heroicons-building-office-2" class="w-4 h-4" style="color: var(--navy)" />
              </div>
              <div class="min-w-0">
                <p class="text-xs font-medium truncate" style="color: var(--ink)">{{ h.name }}</p>
                <p class="text-[11px] truncate font-mono-data" style="color: var(--ink-soft)">{{ h.hospital_level ?? '—' }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Columna lateral — contexto dinámico -->
      <aside class="hidden lg:block sticky top-6 space-y-4">

        <!-- Resumen del hospital que se está creando -->
        <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
          <div class="flex items-center justify-between mb-4">
            <p class="text-xs font-semibold tracking-wide uppercase" style="color: var(--ink-soft)">Resumen</p>
            <div class="relative w-10 h-10 shrink-0">
              <svg viewBox="0 0 36 36" class="w-10 h-10 -rotate-90">
                <circle cx="18" cy="18" r="15.5" fill="none" stroke="var(--mist)" stroke-width="3" />
                <circle
                  cx="18" cy="18" r="15.5" fill="none" stroke="var(--teal)" stroke-width="3"
                  stroke-linecap="round"
                  :stroke-dasharray="`${(porcentajeProgreso / 100) * 97.4} 97.4`"
                />
              </svg>
              <span class="absolute inset-0 flex items-center justify-center text-[10px] font-bold" style="color: var(--ink)">
                {{ porcentajeProgreso }}%
              </span>
            </div>
          </div>

          <div class="flex items-center gap-3 mb-4 pb-4" style="border-bottom: 1px solid var(--line)">
            <div
              class="w-11 h-11 rounded-xl flex items-center justify-center shrink-0"
              style="background: var(--mist)"
            >
              <UIcon name="i-heroicons-building-office-2" class="w-5 h-5" style="color: var(--navy)" />
            </div>
            <div class="min-w-0">
              <p class="text-sm font-medium truncate" style="color: var(--ink)">
                {{ form.name || 'Nombre del hospital' }}
              </p>
              <p class="text-xs truncate font-mono-data" style="color: var(--ink-soft)">
                {{ form.subdomain ? `${form.subdomain}.erp.local` : 'subdominio.erp.local' }}
              </p>
            </div>
          </div>

          <div class="space-y-3 text-sm">
            <div class="flex items-center justify-between">
              <span style="color: var(--ink-soft)">Nivel</span>
              <span
                v-if="nivelSeleccionado"
                class="text-xs font-bold px-2 py-0.5 rounded-md"
                :style="{ background: nivelSeleccionado.color || 'var(--teal)', color: '#fff' }"
              >{{ nivelSeleccionado.code }}</span>
              <span v-else style="color: var(--ink-soft)">—</span>
            </div>
            <div class="flex items-center justify-between">
              <span style="color: var(--ink-soft)">Módulos</span>
              <span style="color: var(--ink)">{{ totalModulos || '—' }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span style="color: var(--ink-soft)">RUC</span>
              <span class="font-mono-data" style="color: var(--ink)">{{ form.ruc || '—' }}</span>
            </div>
          </div>

          <!-- Distribución de módulos App vs SIGARH -->
          <div v-if="totalModulos" class="mt-4 pt-4" style="border-top: 1px solid var(--line)">
            <div class="flex items-center justify-between text-xs mb-1.5">
              <span style="color: var(--ink-soft)">Panel admin</span>
              <span style="color: var(--ink-soft)">Panel SIGARH</span>
            </div>
            <div class="flex h-2 rounded-full overflow-hidden" style="background: var(--mist)">
              <div :style="{ width: `${porcentajeApp}%`, background: 'var(--teal)' }" />
              <div :style="{ width: `${100 - porcentajeApp}%`, background: '#6366f1' }" />
            </div>
            <div class="flex items-center justify-between text-xs mt-1.5" style="color: var(--ink)">
              <span>{{ modulosNivel?.app.length || 0 }}</span>
              <span>{{ modulosNivel?.sigarh.length || 0 }}</span>
            </div>
          </div>
        </div>

        <!-- Checklist de progreso -->
        <div style="background: var(--paper); border-radius: var(--radius-lg); box-shadow: var(--shadow-card); padding: 20px">
          <p class="text-xs font-semibold mb-4 tracking-wide uppercase" style="color: var(--ink-soft)">Progreso</p>
          <div class="space-y-3">
            <div v-for="(paso, i) in pasos" :key="i" class="flex items-center gap-2.5 text-sm">
              <div
                class="w-5 h-5 rounded-full flex items-center justify-center shrink-0"
                :style="{
                  background: stepActual > i ? 'var(--teal)' : stepActual === i ? 'var(--navy)' : 'var(--mist)',
                }"
              >
                <UIcon
                  v-if="stepActual > i"
                  name="i-heroicons-check"
                  class="w-3 h-3 text-white"
                />
                <span
                  v-else
                  class="text-[10px] font-bold"
                  :style="{ color: stepActual === i ? '#fff' : 'var(--ink-soft)' }"
                >{{ i + 1 }}</span>
              </div>
              <span :style="{ color: stepActual === i ? 'var(--ink)' : 'var(--ink-soft)', fontWeight: stepActual === i ? 500 : 400 }">
                {{ paso.label }}
              </span>
            </div>
          </div>
        </div>

        <!-- Tip contextual según el paso -->
        <div
          class="p-4 flex gap-3"
          style="background: var(--teal-soft); border-radius: var(--radius-lg)"
        >
          <UIcon name="i-heroicons-light-bulb" class="w-5 h-5 shrink-0" style="color: var(--teal)" />
          <p class="text-xs leading-relaxed" style="color: var(--ink)">
            {{ tipActual }}
          </p>
        </div>
      </aside>
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

interface HospitalResumen {
  id: string
  name: string
  hospital_level?: string
}

const pasos = [
  { label: 'Nivel' },
  { label: 'Identidad' },
  { label: 'Usuarios' },
  { label: 'Módulos' },
]

const tips = [
  'El nivel MINSA determina qué módulos clínicos y administrativos estarán disponibles automáticamente para este hospital.',
  'El subdominio será la URL de acceso del hospital, por ejemplo hospital-tuman.erp.local. No podrá cambiarse después de creado.',
  'Se crean dos cuentas de acceso: una para el panel administrativo del hospital y otra para el panel SIGARH de recursos humanos.',
  'Puedes ajustar los módulos activados antes de confirmar la creación. Los cambios posteriores se hacen desde la edición del hospital.',
]

const stepActual = ref(0)
const niveles = ref<Nivel[]>([])
const loadingNiveles = ref(true)
const loadingModulos = ref(false)
const modulosNivel = ref<{ app: string[]; sigarh: string[] } | null>(null)
const creating = ref(false)
const createError = ref('')
const hospitalesRecientes = ref<HospitalResumen[]>([])

const form = reactive({
  nivel_code: '',
  name: '',
  subdomain: '',
  ruc: '',
  admin_name: '',
  admin_email: '',
  admin_password: '',
  admin_password_confirm: '',
  sigarh_name: '',
  sigarh_email: '',
  sigarh_password: '',
  sigarh_password_confirm: '',
})

const nivelSeleccionado = computed(() => niveles.value.find(n => n.code === form.nivel_code) || null)
const totalModulos = computed(() => (modulosNivel.value?.app.length || 0) + (modulosNivel.value?.sigarh.length || 0))
const tipActual = computed(() => tips[stepActual.value])

const porcentajeProgreso = computed(() =>
  Math.round(((stepActual.value + (puedeAvanzar.value ? 1 : 0)) / pasos.length) * 100)
)

const porcentajeApp = computed(() =>
  totalModulos.value
    ? Math.round(((modulosNivel.value?.app.length || 0) / totalModulos.value) * 100)
    : 50
)

const puedeAvanzar = computed(() => {
  if (stepActual.value === 0) return !!form.nivel_code
  if (stepActual.value === 1) return !!form.name && !!form.subdomain
  if (stepActual.value === 2) {
    return !!form.admin_email && !!form.admin_password &&
           form.admin_password === form.admin_password_confirm &&
           !!form.sigarh_email && !!form.sigarh_password &&
           form.sigarh_password === form.sigarh_password_confirm
  }
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
        admin_name: form.admin_name,
        admin_email: form.admin_email,
        admin_password: form.admin_password,
        sigarh_name: form.sigarh_name,
        sigarh_email: form.sigarh_email,
        sigarh_password: form.sigarh_password,
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

  try {
    const todos = await api<HospitalResumen[]>('/admin/hospitales')
    hospitalesRecientes.value = todos.slice(-3).reverse()
  } catch {
    //
  }
})
</script>