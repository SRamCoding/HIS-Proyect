<template>
  <div class="p-6 space-y-5 max-w-[1400px] mx-auto">
    <div class="flex justify-between items-start gap-4 flex-wrap">
      <div><p class="text-xs text-slate-500 uppercase">Atención hospitalaria</p><h1 class="text-2xl font-bold">{{ asignaciones ? 'Asignaciones de procedimientos' : 'Atenciones de procedimientos' }}</h1><p class="text-sm text-slate-500">{{ asignaciones ? 'Habilita al personal responsable para cada procedimiento.' : 'Programa, documenta y completa procedimientos con consentimiento informado.' }}</p></div>
      <button class="btn" @click="cargar">Actualizar</button>
    </div>
    <p v-if="error" class="alert">{{ error }}</p><p v-if="notice" class="ok">{{ notice }}</p>

    <section v-if="asignaciones" class="card">
      <h2 class="font-semibold mb-3">Nueva asignación</h2>
      <div class="grid md:grid-cols-3 gap-3">
        <select v-model="formAsignacion.tiempo_procedimiento_id" class="field"><option value="">Seleccione procedimiento</option><option v-for="p in catalogo" :key="p.id" :value="p.id">{{ p.codigo }} · {{ p.nombre }}</option></select>
        <select v-model="formAsignacion.empleado_id" class="field"><option value="">Seleccione empleado</option><option v-for="e in empleados" :key="e.id" :value="e.id">{{ e.nombre }} · {{ e.documento }}</option></select>
        <button class="primary" :disabled="busy || !formAsignacion.tiempo_procedimiento_id || !formAsignacion.empleado_id" @click="crearAsignacion">Asignar</button>
      </div>
    </section>

    <section v-else class="card">
      <h2 class="font-semibold mb-3">Programar procedimiento</h2>
      <div class="grid md:grid-cols-2 gap-3">
        <select v-model="formAtencion.patient_id" class="field"><option value="">Seleccione paciente</option><option v-for="p in pacientes" :key="p.id" :value="p.id">{{ p.nombre }} · {{ p.documento }}</option></select>
        <select v-model="formAtencion.tiempo_procedimiento_id" class="field"><option value="">Seleccione procedimiento</option><option v-for="p in catalogo" :key="p.id" :value="p.id">{{ p.codigo }} · {{ p.nombre }}</option></select>
        <select v-model="formAtencion.empleado_ejecutor_id" class="field"><option value="">Seleccione profesional habilitado</option><option v-for="a in ejecutores" :key="a.id" :value="a.empleado_id">{{ a.empleado_nombre }}</option></select>
        <input v-model="formAtencion.fecha_hora" type="datetime-local" class="field" />
        <label class="flex gap-2 items-center text-sm"><input v-model="formAtencion.consentimiento_informado" type="checkbox"> Consentimiento informado registrado</label>
        <button class="primary" :disabled="busy || !puedeProgramar" @click="crearAtencion">Programar</button>
      </div>
    </section>

    <section class="card overflow-x-auto">
      <table class="w-full text-sm"><thead><tr v-if="asignaciones"><th>Procedimiento</th><th>Empleado</th><th>Acción</th></tr><tr v-else><th>Número</th><th>Paciente</th><th>Procedimiento</th><th>Ejecutor</th><th>Fecha</th><th>Estado</th><th>Acciones</th></tr></thead>
        <tbody><template v-if="asignaciones"><tr v-for="a in lista" :key="a.id"><td>{{ a.tiempo_procedimiento_nombre }}</td><td>{{ a.empleado_nombre }}</td><td><button class="danger" @click="quitar(a)">Desasignar</button></td></tr></template>
        <template v-else><tr v-for="a in lista" :key="a.id"><td class="font-mono">{{ a.numero_atencion }}</td><td>{{ a.paciente_nombre }}</td><td>{{ a.procedimiento_nombre }}</td><td>{{ a.empleado_ejecutor_nombre }}</td><td>{{ fecha(a.fecha_hora) }}</td><td>{{ a.estado }}</td><td class="space-x-2"><button v-if="a.estado==='programado' && !a.consentimiento_informado" class="btn" @click="consentir(a)">Consentimiento</button><button v-if="a.estado==='programado'" class="primary" @click="realizar(a)">Realizar</button><button v-if="a.estado==='programado'" class="danger" @click="cancelar(a)">Cancelar</button></td></tr></template>
        <tr v-if="!lista.length"><td :colspan="asignaciones ? 3 : 7" class="py-8 text-center text-slate-500">No hay registros.</td></tr></tbody></table>
    </section>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{ modo: 'asignaciones' | 'atenciones' }>()
const asignaciones = computed(() => props.modo === 'asignaciones')
const { api } = useApi(); const endpoint = '/app/procedimientos'
const lista = ref<any[]>([]), catalogo = ref<any[]>([]), empleados = ref<any[]>([]), pacientes = ref<any[]>([]), ejecutores = ref<any[]>([])
const busy = ref(false), error = ref(''), notice = ref('')
const formAsignacion = reactive({ tiempo_procedimiento_id: '', empleado_id: '' })
const formAtencion = reactive({ patient_id: '', tiempo_procedimiento_id: '', empleado_ejecutor_id: '', fecha_hora: '', consentimiento_informado: false })
const puedeProgramar = computed(() => formAtencion.patient_id && formAtencion.tiempo_procedimiento_id && formAtencion.empleado_ejecutor_id)
watch(() => formAtencion.tiempo_procedimiento_id, async id => { ejecutores.value = id ? await api(endpoint + '/asignaciones', { query: { tiempo_procedimiento_id: id } }).catch(() => []) : []; formAtencion.empleado_ejecutor_id = '' })
const msg = (e:any) => typeof e?.data?.detail === 'string' ? e.data.detail : 'No se pudo completar la operación.'
const fecha = (v:string) => v ? new Date(v).toLocaleString('es-PE') : '—'
async function cargar(){ error.value=''; try { const common=await Promise.all([api(endpoint+'/catalogo'), api(endpoint+'/asignaciones')]); catalogo.value=common[0] as any[]; if(asignaciones.value){ empleados.value=await api(endpoint+'/catalogos/empleados'); lista.value=common[1] as any[] } else { pacientes.value=await api(endpoint+'/catalogos/pacientes'); lista.value=await api(endpoint+'/atenciones') } } catch(e){error.value=msg(e)} }
async function run(fn:()=>Promise<any>, ok:string){busy.value=true;error.value='';notice.value='';try{await fn();notice.value=ok;await cargar()}catch(e){error.value=msg(e)}finally{busy.value=false}}
const crearAsignacion=()=>run(()=>api(endpoint+'/asignaciones',{method:'POST',body:formAsignacion}),'Personal asignado.')
const quitar=(a:any)=>run(()=>api(`${endpoint}/asignaciones/${a.tiempo_procedimiento_id}/${a.empleado_id}`,{method:'DELETE'}),'Asignación retirada.')
const crearAtencion=()=>run(()=>api(endpoint+'/atenciones',{method:'POST',body:{...formAtencion,fecha_hora:formAtencion.fecha_hora||null}}),'Procedimiento programado.')
const consentir=(a:any)=>run(()=>api(`${endpoint}/atenciones/${a.id}/consentimiento`,{method:'POST'}),'Consentimiento registrado.')
function realizar(a:any){const hallazgos=prompt('Registre los hallazgos del procedimiento:')?.trim();if(hallazgos)run(()=>api(`${endpoint}/atenciones/${a.id}/realizar`,{method:'POST',body:{hallazgos}}),'Procedimiento realizado.')}
function cancelar(a:any){const motivo=prompt('Indique el motivo de cancelación:')?.trim();if(motivo)run(()=>api(`${endpoint}/atenciones/${a.id}/cancelar`,{method:'POST',body:{motivo}}),'Procedimiento cancelado.')}
onMounted(cargar)
</script>

<style scoped>
.card{background:white;border:1px solid #dbe3e8;border-radius:14px;padding:1.25rem}.field{border:1px solid #cbd5e1;border-radius:8px;padding:.65rem .75rem;background:white}.btn,.primary,.danger{padding:.55rem .85rem;border-radius:8px;border:1px solid #cbd5e1}.primary{background:#0f8a83;color:white;border-color:#0f8a83}.danger{color:#b42318;background:#fff}.alert{background:#fee4e2;color:#b42318;padding:.75rem;border-radius:8px}.ok{background:#dcfae6;color:#067647;padding:.75rem;border-radius:8px}th,td{text-align:left;padding:.7rem;border-bottom:1px solid #e2e8f0}button:disabled{opacity:.5}
</style>
