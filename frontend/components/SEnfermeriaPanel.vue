<script setup lang="ts">
const { api } = useApi()
const { link } = useHospitalNav()
const auth = useAuthStore()
const cargando = ref(false)
const error = ref('')
const fecha = ref(new Intl.DateTimeFormat('en-CA', { timeZone: 'America/Lima' }).format(new Date()))
const citas = ref<any[]>([])
const triajes = ref<any[]>([])
const hospitalizaciones = ref<any[]>([])

const permisos = computed(() => auth.user?.active_modules || [])
const puedeConfirmar = computed(() => hospitalPuede(permisos.value, 'consulta_externa.confirmacion'))
const puedeTriaje = computed(() => hospitalPuede(permisos.value, 'consulta_externa.triaje'))
const puedeSeguimiento = computed(() => hospitalPuede(permisos.value, 'hospitalizacion.seguimiento'))
const sinTriaje = computed(() => triajes.value.filter(x => !x.paso_triaje))
const fechaTexto = (v: string) => v ? v.slice(0, 10).split('-').reverse().join('/') : '—'

async function cargar() {
  cargando.value = true
  error.value = ''
  try {
    const [confirmaciones, pendientes, internados] = await Promise.all([
      puedeConfirmar.value ? api<any[]>(`/app/consulta-externa/citas?estado=separada&fecha=${fecha.value}`) : Promise.resolve([]),
      puedeTriaje.value ? api<any[]>(`/app/consulta-externa/triaje/pendientes?fecha=${fecha.value}`) : Promise.resolve([]),
      puedeSeguimiento.value ? api<any>('/app/hospitalizacion/hospitalizaciones?estado=internado&page_size=100') : Promise.resolve({ items: [] }),
    ])
    citas.value = confirmaciones
    triajes.value = pendientes
    hospitalizaciones.value = internados.items || []
  } catch (e) {
    error.value = apiErr(e, 'No se pudo cargar el panel de Enfermería')
  } finally {
    cargando.value = false
  }
}

onMounted(cargar)
</script>

<template>
  <div class="p-6 space-y-6 max-w-[1500px] mx-auto">
    <header class="flex flex-wrap items-end justify-between gap-4">
      <div>
        <p class="text-sm font-semibold text-teal-700">PANEL ASISTENCIAL</p>
        <h1 class="text-3xl font-bold text-slate-900">Enfermería</h1>
        <p class="text-slate-500">{{ auth.user?.name }} · Confirmación, triaje y seguimiento clínico</p>
      </div>
      <div class="flex items-end gap-3">
        <label class="text-sm">Fecha<input v-model="fecha" type="date" class="input-clinical block mt-1" /></label>
        <button class="btn-primary" :disabled="cargando" @click="cargar">{{ cargando ? 'Actualizando…' : 'Actualizar' }}</button>
      </div>
    </header>

    <p v-if="error" role="alert" class="rounded-xl border border-red-200 bg-red-50 p-4 text-red-700">{{ error }}</p>

    <section class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
      <NuxtLink v-if="puedeConfirmar" :to="link('/app/consulta-externa/citas-por-confirmar')" class="rounded-2xl border bg-white p-5 shadow-sm hover:border-teal-400">
        <div class="flex justify-between"><UIcon name="i-heroicons-calendar-days" class="h-7 w-7 text-teal-600" /><span class="text-3xl font-bold">{{ citas.length }}</span></div>
        <h2 class="mt-3 font-semibold">Citas por confirmar</h2><p class="text-sm text-slate-500">Pacientes que esperan admisión asistencial.</p>
      </NuxtLink>
      <NuxtLink v-if="puedeTriaje" :to="link('/app/consulta-externa/triaje')" class="rounded-2xl border bg-white p-5 shadow-sm hover:border-teal-400">
        <div class="flex justify-between"><UIcon name="i-heroicons-heart" class="h-7 w-7 text-rose-500" /><span class="text-3xl font-bold">{{ sinTriaje.length }}</span></div>
        <h2 class="mt-3 font-semibold">Triajes pendientes</h2><p class="text-sm text-slate-500">Citas confirmadas sin signos vitales.</p>
      </NuxtLink>
      <NuxtLink v-if="puedeSeguimiento" :to="link('/app/hospitalizacion/seguimiento-paciente')" class="rounded-2xl border bg-white p-5 shadow-sm hover:border-teal-400">
        <div class="flex justify-between"><UIcon name="i-heroicons-building-office-2" class="h-7 w-7 text-indigo-600" /><span class="text-3xl font-bold">{{ hospitalizaciones.length }}</span></div>
        <h2 class="mt-3 font-semibold">Pacientes hospitalizados</h2><p class="text-sm text-slate-500">Seguimiento y notas de Enfermería.</p>
      </NuxtLink>
    </section>

    <section v-if="puedeTriaje" class="rounded-2xl border bg-white shadow-sm overflow-hidden">
      <div class="flex items-center justify-between border-b p-5"><div><h2 class="text-lg font-semibold">Cola de triaje</h2><p class="text-sm text-slate-500">{{ fechaTexto(fecha) }}</p></div><NuxtLink :to="link('/app/consulta-externa/triaje')" class="text-sm font-semibold text-teal-700">Ver bandeja →</NuxtLink></div>
      <div class="overflow-x-auto"><table class="w-full text-left"><thead class="bg-slate-50 text-sm text-slate-500"><tr><th class="p-3">Hora</th><th>Paciente</th><th>Servicio</th><th>Médico</th><th>Estado</th></tr></thead><tbody>
        <tr v-for="item in triajes.slice(0, 8)" :key="item.cita_id" class="border-t"><td class="p-3 font-mono">{{ item.hora_inicio }}</td><td class="font-medium">{{ item.paciente_nombre }}</td><td>{{ item.especialidad_nombre || item.servicio_nombre || '—' }}</td><td>{{ item.medico_nombre }}</td><td><NuxtLink :to="link(item.paso_triaje ? `/app/consulta-externa/triaje/${item.cita_id}` : `/app/consulta-externa/triaje/create?cita=${item.cita_id}`)" class="text-teal-700 underline">{{ item.paso_triaje ? 'Registrado' : 'Registrar' }}</NuxtLink></td></tr>
        <tr v-if="!triajes.length"><td colspan="5" class="p-8 text-center text-slate-500">No hay pacientes pendientes para esta fecha.</td></tr>
      </tbody></table></div>
    </section>
  </div>
</template>
