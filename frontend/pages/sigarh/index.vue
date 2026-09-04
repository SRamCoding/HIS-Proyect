<script setup lang="ts">
definePageMeta({ layout: 'sigarh', title: 'Escritorio', middleware: ['auth'] })
const { $api } = useNuxtApp()
const route = useRoute()
const tenant = route.query.tenant as string

const data = ref<any>(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    data.value = await $api('/sigarh/dashboard', { tenant })
  } catch (e: any) {
    error.value = 'No se pudo cargar el dashboard'
  } finally {
    loading.value = false
  }
})

const porcentajeAsistencia = computed(() => {
  if (!data.value?.total_empleados) return 0
  return Math.round((data.value.asistencia_hoy / data.value.total_empleados) * 100)
})

const porcentajeCamas = computed(() => {
  if (!data.value?.camas?.total) return 0
  return Math.round((data.value.camas.ocupadas / data.value.camas.total) * 100)
})

const totalPendientes = computed(() => {
  if (!data.value?.pendientes) return 0
  return (data.value.pendientes.vacaciones + data.value.pendientes.licencias + data.value.pendientes.papeletas)
})

const estadoColor: Record<string, string> = {
  pendiente: '#f59e0b',
  aprobado: '#10b981',
  rechazado: '#ef4444',
}

const hoy = new Date().toLocaleDateString('es-PE', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
</script>

<template>
  <div class="p-6 space-y-6">

    <!-- Header -->
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-xl font-semibold text-gray-800">Escritorio SIGARH</h1>
        <p class="text-sm text-gray-500 mt-0.5 capitalize">{{ hoy }}</p>
      </div>
      <div v-if="totalPendientes > 0"
        class="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-50 border border-amber-200">
        <UIcon name="i-heroicons-bell-alert" class="w-4 h-4 text-amber-500" />
        <span class="text-sm text-amber-700 font-medium">{{ totalPendientes }} solicitudes pendientes</span>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="loading" class="grid grid-cols-4 gap-4">
      <div v-for="i in 4" :key="i" class="bg-white rounded-xl border border-gray-200 p-5 animate-pulse h-28" />
    </div>

    <!-- Error -->
    <div v-else-if="error" class="p-4 bg-red-50 text-red-600 rounded-xl text-sm">{{ error }}</div>

    <template v-else-if="data">

      <!-- KPIs principales -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-4">

        <!-- Empleados -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Total Empleados</p>
              <p class="text-3xl font-bold text-gray-800 mt-1">{{ data.total_empleados }}</p>
              <p class="text-xs text-gray-500 mt-1">
                <span class="text-green-600 font-medium">{{ data.empleados_activos }}</span> activos
              </p>
            </div>
            <div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(30,58,95,0.08)">
              <UIcon name="i-heroicons-users" class="w-5 h-5" style="color:#1e3a5f" />
            </div>
          </div>
        </div>

        <!-- Asistencia hoy -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Asistencia Hoy</p>
              <p class="text-3xl font-bold text-gray-800 mt-1">{{ data.asistencia_hoy }}</p>
              <p class="text-xs text-gray-500 mt-1">
                <span class="font-medium" :style="`color: ${porcentajeAsistencia >= 80 ? '#10b981' : '#f59e0b'}`">
                  {{ porcentajeAsistencia }}%
                </span> del personal
              </p>
            </div>
            <div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(16,185,129,0.08)">
              <UIcon name="i-heroicons-clipboard-document-check" class="w-5 h-5 text-emerald-500" />
            </div>
          </div>
          <!-- Barra de progreso -->
          <div class="mt-3 h-1.5 bg-gray-100 rounded-full overflow-hidden">
            <div class="h-full rounded-full transition-all"
              :style="`width:${porcentajeAsistencia}%; background: ${porcentajeAsistencia >= 80 ? '#10b981' : '#f59e0b'}`" />
          </div>
        </div>

        <!-- Pendientes -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Solicitudes Pendientes</p>
              <p class="text-3xl font-bold text-gray-800 mt-1">{{ totalPendientes }}</p>
              <div class="flex gap-2 mt-1">
                <span class="text-xs text-gray-500">V:{{ data.pendientes.vacaciones }}</span>
                <span class="text-xs text-gray-500">L:{{ data.pendientes.licencias }}</span>
                <span class="text-xs text-gray-500">P:{{ data.pendientes.papeletas }}</span>
              </div>
            </div>
            <div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(245,158,11,0.08)">
              <UIcon name="i-heroicons-clock" class="w-5 h-5 text-amber-500" />
            </div>
          </div>
        </div>

        <!-- Justificaciones -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-start justify-between">
            <div>
              <p class="text-xs font-medium text-gray-500 uppercase tracking-wide">Justificaciones Pend.</p>
              <p class="text-3xl font-bold text-gray-800 mt-1">{{ data.justificaciones_pendientes }}</p>
              <p class="text-xs text-gray-500 mt-1">Por revisar</p>
            </div>
            <div class="w-10 h-10 rounded-lg flex items-center justify-center" style="background: rgba(99,102,241,0.08)">
              <UIcon name="i-heroicons-document-text" class="w-5 h-5 text-indigo-500" />
            </div>
          </div>
        </div>
      </div>

      <!-- Fila 2: Movimientos del mes + Camas -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

        <!-- Movimientos del mes -->
        <div class="lg:col-span-2 bg-white rounded-xl border border-gray-200 p-5">
          <h2 class="text-sm font-semibold text-gray-700 mb-4">Movimientos del Mes</h2>
          <div class="grid grid-cols-2 gap-3">

            <NuxtLink :to="`/sigarh/movimientos/vacaciones?tenant=${tenant}`"
              class="flex items-center gap-3 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
              <div class="w-9 h-9 rounded-lg flex items-center justify-center bg-orange-50">
                <UIcon name="i-heroicons-sun" class="w-4 h-4 text-orange-500" />
              </div>
              <div>
                <p class="text-xl font-bold text-gray-800">{{ data.movimientos_mes.vacaciones }}</p>
                <p class="text-xs text-gray-500">Vacaciones</p>
              </div>
              <div v-if="data.pendientes.vacaciones > 0"
                class="ml-auto px-1.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                {{ data.pendientes.vacaciones }}
              </div>
            </NuxtLink>

            <NuxtLink :to="`/sigarh/movimientos/licencias?tenant=${tenant}`"
              class="flex items-center gap-3 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
              <div class="w-9 h-9 rounded-lg flex items-center justify-center bg-blue-50">
                <UIcon name="i-heroicons-paper-airplane" class="w-4 h-4 text-blue-500" />
              </div>
              <div>
                <p class="text-xl font-bold text-gray-800">{{ data.movimientos_mes.licencias }}</p>
                <p class="text-xs text-gray-500">Licencias</p>
              </div>
              <div v-if="data.pendientes.licencias > 0"
                class="ml-auto px-1.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                {{ data.pendientes.licencias }}
              </div>
            </NuxtLink>

            <NuxtLink :to="`/sigarh/movimientos/papeletas/estado?tenant=${tenant}`"
              class="flex items-center gap-3 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
              <div class="w-9 h-9 rounded-lg flex items-center justify-center bg-purple-50">
                <UIcon name="i-heroicons-document-duplicate" class="w-4 h-4 text-purple-500" />
              </div>
              <div>
                <p class="text-xl font-bold text-gray-800">{{ data.movimientos_mes.papeletas }}</p>
                <p class="text-xs text-gray-500">Papeletas</p>
              </div>
              <div v-if="data.pendientes.papeletas > 0"
                class="ml-auto px-1.5 py-0.5 rounded-full text-xs font-medium bg-amber-100 text-amber-700">
                {{ data.pendientes.papeletas }}
              </div>
            </NuxtLink>

            <NuxtLink :to="`/sigarh/movimientos/cambio-turno/estado?tenant=${tenant}`"
              class="flex items-center gap-3 p-3 rounded-lg border border-gray-100 hover:bg-gray-50 transition-colors">
              <div class="w-9 h-9 rounded-lg flex items-center justify-center bg-teal-50">
                <UIcon name="i-heroicons-arrows-right-left" class="w-4 h-4 text-teal-500" />
              </div>
              <div>
                <p class="text-xl font-bold text-gray-800">{{ data.movimientos_mes.cambios_turno }}</p>
                <p class="text-xs text-gray-500">Cambios Turno</p>
              </div>
            </NuxtLink>

          </div>
        </div>

        <!-- Estado de Camas -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold text-gray-700">Estado de Camas</h2>
            <NuxtLink :to="`/sigarh/infraestructura-hosp/camas?tenant=${tenant}`"
              class="text-xs text-blue-600 hover:underline">Ver todas</NuxtLink>
          </div>

          <div v-if="data.camas.total === 0" class="text-center py-4 text-gray-400 text-sm">
            No hay camas registradas
          </div>
          <div v-else class="space-y-3">
            <!-- Barra total ocupación -->
            <div>
              <div class="flex justify-between text-xs text-gray-500 mb-1">
                <span>Ocupación</span>
                <span class="font-medium">{{ porcentajeCamas }}%</span>
              </div>
              <div class="h-2 bg-gray-100 rounded-full overflow-hidden">
                <div class="h-full rounded-full transition-all"
                  :style="`width:${porcentajeCamas}%; background: ${porcentajeCamas > 80 ? '#ef4444' : '#1e3a5f'}`" />
              </div>
            </div>

            <!-- Detalle por estado -->
            <div class="space-y-2 pt-1">
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-2.5 h-2.5 rounded-full bg-emerald-400" />
                  <span class="text-xs text-gray-600">Disponibles</span>
                </div>
                <span class="text-sm font-semibold text-gray-800">{{ data.camas.disponibles }}</span>
              </div>
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-2.5 h-2.5 rounded-full bg-red-400" />
                  <span class="text-xs text-gray-600">Ocupadas</span>
                </div>
                <span class="text-sm font-semibold text-gray-800">{{ data.camas.ocupadas }}</span>
              </div>
              <div class="flex items-center justify-between">
                <div class="flex items-center gap-2">
                  <div class="w-2.5 h-2.5 rounded-full bg-amber-400" />
                  <span class="text-xs text-gray-600">Mantenimiento</span>
                </div>
                <span class="text-sm font-semibold text-gray-800">{{ data.camas.mantenimiento }}</span>
              </div>
              <div class="pt-2 border-t border-gray-100 flex items-center justify-between">
                <span class="text-xs font-medium text-gray-500">Total</span>
                <span class="text-sm font-bold text-gray-800">{{ data.camas.total }}</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Fila 3: Últimas solicitudes -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">

        <!-- Últimas vacaciones -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold text-gray-700">Últimas Vacaciones / Justificaciones</h2>
            <NuxtLink :to="`/sigarh/movimientos/vacaciones?tenant=${tenant}`"
              class="text-xs text-blue-600 hover:underline">Ver todas</NuxtLink>
          </div>
          <div v-if="!data.ultimas_vacaciones.length" class="text-center py-4 text-gray-400 text-sm">
            No hay solicitudes recientes
          </div>
          <div v-else class="space-y-2">
            <div v-for="v in data.ultimas_vacaciones" :key="v.id"
              class="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
              <div class="min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ v.empleado_nombre || 'Empleado' }}</p>
                <p class="text-xs text-gray-500">{{ v.tipo }} · {{ v.fecha_inicio }} → {{ v.fecha_fin }}</p>
              </div>
              <span class="ml-3 px-2 py-0.5 rounded-full text-xs font-medium text-white shrink-0"
                :style="`background:${estadoColor[v.estado] || '#6b7280'}`">
                {{ v.estado }}
              </span>
            </div>
          </div>
        </div>

        <!-- Últimas licencias -->
        <div class="bg-white rounded-xl border border-gray-200 p-5">
          <div class="flex items-center justify-between mb-4">
            <h2 class="text-sm font-semibold text-gray-700">Últimas Licencias</h2>
            <NuxtLink :to="`/sigarh/movimientos/licencias?tenant=${tenant}`"
              class="text-xs text-blue-600 hover:underline">Ver todas</NuxtLink>
          </div>
          <div v-if="!data.ultimas_licencias.length" class="text-center py-4 text-gray-400 text-sm">
            No hay licencias recientes
          </div>
          <div v-else class="space-y-2">
            <div v-for="l in data.ultimas_licencias" :key="l.id"
              class="flex items-center justify-between py-2 border-b border-gray-50 last:border-0">
              <div class="min-w-0">
                <p class="text-sm font-medium text-gray-800 truncate">{{ l.empleado_nombre || 'Empleado' }}</p>
                <p class="text-xs text-gray-500">Tramitada: {{ l.fecha_tramite }}</p>
              </div>
              <span class="ml-3 px-2 py-0.5 rounded-full text-xs font-medium text-white shrink-0"
                :style="`background:${estadoColor[l.estado] || '#6b7280'}`">
                {{ l.estado }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Fila 4: Accesos rápidos -->
      <div class="bg-white rounded-xl border border-gray-200 p-5">
        <h2 class="text-sm font-semibold text-gray-700 mb-4">Accesos Rápidos</h2>
        <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          <NuxtLink v-for="acceso in [
            { label: 'Empleados',       icon: 'i-heroicons-users',                    path: '/sigarh/rrhh/empleados' },
            { label: 'Asistencia',      icon: 'i-heroicons-clipboard-document-check',  path: '/sigarh/rrhh/asistencia' },
            { label: 'Vacaciones',      icon: 'i-heroicons-sun',                       path: '/sigarh/movimientos/vacaciones' },
            { label: 'Licencias',       icon: 'i-heroicons-paper-airplane',            path: '/sigarh/movimientos/licencias' },
            { label: 'Camas',           icon: 'i-heroicons-home',                      path: '/sigarh/infraestructura-hosp/camas' },
            { label: 'CIE-10',          icon: 'i-heroicons-document-magnifying-glass', path: '/sigarh/general/cie10' },
          ]" :key="acceso.path" :to="`${acceso.path}?tenant=${tenant}`"
            class="flex flex-col items-center gap-2 p-3 rounded-xl border border-gray-100 hover:border-gray-300 hover:bg-gray-50 transition-all text-center">
            <div class="w-9 h-9 rounded-lg flex items-center justify-center" style="background: rgba(30,58,95,0.06)">
              <UIcon :name="acceso.icon" class="w-4 h-4" style="color:#1e3a5f" />
            </div>
            <span class="text-xs text-gray-600 font-medium leading-tight">{{ acceso.label }}</span>
          </NuxtLink>
        </div>
      </div>

    </template>
  </div>
</template>