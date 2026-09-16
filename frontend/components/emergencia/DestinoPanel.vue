<script setup lang="ts">
const props = defineProps<{ destino: string; titulo: string; descripcion?: string }>()
const { api } = useApi(); const { link } = useHospitalNav()
const items = ref<any[]>([]); const loading = ref(true); const error = ref('')

// Cada destino se resuelve creando el registro real en el modulo receptor
// (Hospitalizacion/Interconsultas/Referencias) -- no aqui. Marcar el destino
// "completado" sin ese registro dejaba al paciente sin hospitalizacion/
// interconsulta/referencia real, aunque la cola lo mostrara resuelto.
const rutaAdmision: Record<string, string> = {
  HOSPITALIZACION: '/app/hospitalizacion/hospitalizaciones',
  INTERCONSULTA: '/app/hospitalizacion/interconsultas',
  REFERENCIA: '/app/referencias/referencias',
}
const nombreModulo: Record<string, string> = {
  HOSPITALIZACION: 'Hospitalización',
  INTERCONSULTA: 'Interconsultas',
  REFERENCIA: 'Referencias',
}

async function cargar() {
  loading.value = true; error.value = ''
  try { items.value = await api('/app/emergencia/destinos?destino=' + props.destino) }
  catch (e: any) { error.value = e?.data?.detail || 'No se pudo cargar la cola' }
  finally { loading.value = false }
}
onMounted(cargar)
</script>
<template>
  <div class="p-6 space-y-5">
    <div>
      <h1 class="text-2xl font-bold">{{ titulo }}</h1>
      <p class="text-sm" style="color:var(--ink-soft)">{{ descripcion || 'Derivaciones generadas desde atenciones firmadas de Emergencia' }}</p>
    </div>
    <div v-if="error" style="color:var(--alert)">{{ error }}</div>
    <div v-if="items.some(i => i.estado === 'pendiente')" class="hint">
      <UIcon name="i-heroicons-information-circle" class="w-4 h-4 shrink-0" style="display:inline" />
      Las pendientes se resuelven admitiéndolas en
      <NuxtLink :to="link(rutaAdmision[destino])" style="color:var(--teal);font-weight:600">{{ nombreModulo[destino] }}</NuxtLink>
      — ahí se registra el dato clínico real (cama, especialidad u hospital destino) y la cola se actualiza sola.
    </div>
    <div class="box overflow-x-auto">
      <div v-if="loading" class="p-10 text-center">Cargando...</div>
      <table v-else class="w-full text-sm">
        <thead><tr><th>Cuenta</th><th>Paciente</th><th>Estado</th><th>Fecha</th><th>Acción</th></tr></thead>
        <tbody>
          <tr v-for="i in items" :key="i.id">
            <td class="font-mono">{{ i.numero_cuenta }}</td>
            <td>{{ i.paciente_nombre }}</td>
            <td><span class="badge" :class="i.estado === 'pendiente' ? 'badge-pendiente' : 'badge-completado'">{{ i.estado === 'pendiente' ? 'Pendiente' : 'Completado' }}</span></td>
            <td>{{ new Date(i.created_at).toLocaleString('es-PE') }}</td>
            <td>
              <NuxtLink :to="link('/app/emergencia/atencion/' + i.admision_id)" class="mr-3" style="color:var(--teal)">Ver atención</NuxtLink>
              <NuxtLink v-if="i.estado === 'pendiente'" :to="link(rutaAdmision[destino])" style="color:var(--green)">Admitir en {{ nombreModulo[destino] }}</NuxtLink>
            </td>
          </tr>
          <tr v-if="!items.length"><td colspan="5" class="p-10 text-center">Sin derivaciones</td></tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
<style scoped>
.box{background:var(--paper);border:1px solid var(--line);border-radius:var(--radius-lg)}
th,td{padding:.8rem;text-align:left;border-bottom:1px solid var(--line)}
.hint{padding:.75rem 1rem;background:var(--teal-soft);color:var(--ink);border-radius:8px;font-size:.8125rem}
.badge{font-size:.6875rem;font-weight:600;padding:.125rem .5rem;border-radius:999px}
.badge-pendiente{color:var(--amber);background:var(--amber-soft)}
.badge-completado{color:var(--green);background:var(--green-soft)}
</style>
