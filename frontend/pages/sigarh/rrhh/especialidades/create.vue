<script setup lang="ts">
definePageMeta({ layout:'sigarh', middleware:['auth'] })
const { api } = useApi(), router = useRouter(), route = useRoute()
const saving = ref(false), loading = ref(true), error = ref('')
const bases = ref<any[]>([])
const form = reactive({ nombre:'', codigo:'', descripcion:'', tipo:'especialidad', parent_id:'', is_active:true })
async function guardar() {
  saving.value=true; error.value=''
  try {
    await api('/sigarh/rrhh/especialidades', { method:'POST', body:{ ...form, codigo:form.codigo||null, descripcion:form.descripcion||null, parent_id:form.tipo==='subespecialidad'?form.parent_id:null } })
    router.push('/sigarh/rrhh/especialidades')
  } catch(e:any) { error.value=apiErr(e,'No se pudo crear') } finally { saving.value=false }
}
onMounted(async() => { try {
  bases.value=(await api<any[]>('/sigarh/rrhh/especialidades')).filter(e=>e.tipo==='especialidad')
  if(route.query.tipo==='subespecialidad'){form.tipo='subespecialidad';form.parent_id=String(route.query.parent_id||'')}
} catch(e:any) { error.value=apiErr(e,'No se pudo cargar las especialidades base') } finally { loading.value=false } })
</script>
<template><SFormLayout><template #main>
  <div class="mb-8"><NuxtLink to="/sigarh/rrhh/especialidades" class="text-sm hover:underline" style="color:var(--ink-soft)">← Especialidades y subespecialidades</NuxtLink><h1 class="page-title mt-3">Nuevo registro hospitalario</h1><p class="page-subtitle">Agrega una especialidad propia o una subespecialidad vinculada</p></div>
  <SFormCard title="Datos del registro" subtitle="Los registros propios complementan el catálogo oficial CONAREME" icon="i-heroicons-plus-circle" icon-bg="var(--purple-soft)" icon-color="var(--purple)" :error="error">
    <div class="form-group"><label class="form-label">Tipo <span class="required">*</span></label><select v-model="form.tipo" class="input-clinical" @change="form.parent_id=''" :disabled="loading"><option value="especialidad">Especialidad</option><option value="subespecialidad">Subespecialidad</option></select></div>
    <div v-if="form.tipo==='subespecialidad'" class="form-group"><label class="form-label">Especialidad principal <span class="required">*</span></label><select v-model="form.parent_id" class="input-clinical" required><option value="">Seleccione...</option><option v-for="base in bases" :key="base.id" :value="base.id">{{ base.nombre }}</option></select></div>
    <div class="form-group full-width"><label class="form-label">Nombre <span class="required">*</span></label><input v-model="form.nombre" class="input-clinical" maxlength="100" placeholder="Nombre de la especialidad" /></div>
    <div class="form-group"><label class="form-label">Código interno</label><input v-model="form.codigo" class="input-clinical font-mono-data" maxlength="20" placeholder="Ej. ESP-LOCAL-01" /></div>
    <div class="form-group"><label class="form-label">Estado</label><div class="status-toggle"><span class="toggle-label">Disponible en SIGARH y APP</span><button type="button" class="toggle-switch" :class="{'toggle-active':form.is_active}" @click="form.is_active=!form.is_active"><span class="toggle-slider" /></button></div></div>
    <div class="form-group full-width"><label class="form-label">Descripción / notas</label><textarea v-model="form.descripcion" class="input-clinical" rows="3" /></div>
    <template #actions><SFormActions :saving="saving" save-text="Crear registro" saving-text="Creando..." cancel-to="/sigarh/rrhh/especialidades" @save="guardar" /></template>
  </SFormCard>
</template><template #sidebar><SWidgetInfo :items="['El catálogo oficial se conserva sin cambios', 'Una subespecialidad siempre pertenece a una especialidad principal', 'Los registros activos aparecen en RR. HH. y APP', 'Puedes desactivar un registro sin perder su historial']" /></template></SFormLayout></template>
