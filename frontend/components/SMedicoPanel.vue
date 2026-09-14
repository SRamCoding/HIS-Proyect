<script setup lang="ts">
const { api } = useApi()
const { link } = useHospitalNav()
const auth = useAuthStore()
const programaciones = ref<any[]>([])
const citas = ref<any[]>([])
const estados = ref<Record<string, {triaje_registrado: boolean; atencion_estado: string | null}>>({})
const cargando = ref(false)
const error = ref('')
const fecha = ref('')
const puedeProgramacion = computed(() => hospitalPuede(auth.user?.active_modules || [], 'consulta_externa.programacion'))
const puedeAtenciones = computed(() => hospitalPuede(auth.user?.active_modules || [], 'consulta_externa.atenciones'))
const fechaTexto = (valor: string) => valor ? valor.slice(0, 10).split('-').reverse().join('/') : '—'
async function cargar() {
  cargando.value = true; error.value = ''
  const query = fecha.value ? `?fecha=${fecha.value}` : ''
  try {
    const resultados = await Promise.all([
      puedeProgramacion.value ? api<any[]>(`/app/consulta-externa/programacion-medica${query}`) : Promise.resolve([]),
      puedeAtenciones.value ? api<any[]>(`/app/consulta-externa/citas${query}`) : Promise.resolve([]),
      puedeAtenciones.value ? api<any[]>(`/app/consulta-externa/estado-citas-medico${query}`) : Promise.resolve([])
    ])
    ;[programaciones.value, citas.value] = resultados
    estados.value = Object.fromEntries(resultados[2].map(e => [e.cita_id, e]))
  } catch (e) { error.value = apiErr(e, 'No se pudo cargar tu programación') }
  finally { cargando.value = false }
}
onMounted(cargar)
</script>

<template>
  <div class="p-6 space-y-6">
    <div><h1 class="text-2xl font-semibold">Panel del médico</h1><p class="text-slate-500">{{ auth.user?.name }} · Tu programación y tus pacientes</p></div>
    <div class="flex flex-wrap gap-3 items-end"><label>Fecha <input v-model="fecha" type="date" class="input-clinical" /></label><button class="btn-primary" :disabled="cargando" @click="cargar">Consultar</button><button @click="fecha = ''; cargar()">Ver todas las fechas</button></div>
    <p v-if="error" role="alert" class="text-red-600">{{ error }}</p>
    <p v-if="cargando">Cargando...</p>
    <template v-else>
      <section v-if="puedeProgramacion" class="bg-white rounded-xl border p-4 overflow-x-auto">
        <h2 class="font-semibold text-lg mb-3">Mi programación · {{ programaciones.length }} jornadas</h2>
        <table class="w-full text-left"><thead><tr><th>Fecha</th><th>Horario</th><th>Servicio</th><th>Especialidad</th><th>Estado</th></tr></thead><tbody><tr v-for="p in programaciones" :key="p.id" class="border-t"><td class="py-3">{{ fechaTexto(p.fecha) }}</td><td>{{ p.hora_inicio }}–{{ p.hora_fin }}</td><td>{{ p.servicio_nombre }}</td><td>{{ p.especialidad_nombre }}</td><td>{{ p.estado }}</td></tr></tbody></table>
        <p v-if="!programaciones.length" class="text-slate-500 mt-3">No tienes jornadas para este filtro. La programación procede de los roles aprobados en SIGARH.</p>
      </section>
      <section v-if="puedeAtenciones" class="bg-white rounded-xl border p-4 overflow-x-auto">
        <h2 class="font-semibold text-lg mb-3">Mis citas · {{ citas.length }} pacientes</h2>
        <p class="text-sm text-slate-500 mb-3">Enfermería confirma la cita y registra el triaje antes de la atención médica.</p>
        <table class="w-full text-left"><thead><tr><th>Fecha</th><th>Hora</th><th>Paciente</th><th>Estado</th><th>Atención</th></tr></thead><tbody><tr v-for="c in citas" :key="c.id" class="border-t"><td class="py-3">{{ fechaTexto(c.fecha) }}</td><td>{{ c.hora_inicio }}</td><td>{{ c.paciente_nombre }}</td><td>{{ c.estado }}</td><td><NuxtLink v-if="c.estado === 'atendida' || (c.estado === 'confirmada' && estados[c.id]?.triaje_registrado)" class="underline" :to="link('/app/consulta-externa/atenciones-medicas/' + c.id)">{{ c.estado === 'atendida' ? 'Ver atención' : 'Abrir atención' }}</NuxtLink><span v-else class="text-slate-500">{{ c.estado === 'pendiente' ? 'Pendiente de confirmación' : c.estado === 'confirmada' ? 'Pendiente de triaje' : 'Sin atención disponible' }}</span></td></tr></tbody></table>
        <p v-if="!citas.length" class="text-slate-500 mt-3">No tienes citas para este filtro.</p>
      </section>
    </template>
  </div>
</template>
