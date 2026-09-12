<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const items = ref<any[]>([])
const grupos = ref<any[]>([])
const search = ref('')
const error = ref('')
const loading = ref(true)
const saving = ref(false)
const editing = ref<any>(null)
const showForm = ref(false)
const form = reactive({ nombre: '', codigo: '', grupo_ocupacional_id: '', colegio_profesional: '', categoria_personal: '', is_active: true })
const filtered = computed(() => items.value.filter(p => `${p.nombre} ${p.codigo} ${grupo(p.grupo_ocupacional_id)}`.toLowerCase().includes(search.value.toLowerCase())))
function grupo(id: string) { return grupos.value.find(g => g.id === id)?.nombre || '' }
function abrir(item: any = null) {
  editing.value = item
  Object.assign(form, item ? { nombre: item.nombre, codigo: item.codigo, grupo_ocupacional_id: item.grupo_ocupacional_id, colegio_profesional: item.colegio_profesional || '', categoria_personal: item.categoria_personal || '', is_active: item.is_active } : { nombre: '', codigo: '', grupo_ocupacional_id: '', colegio_profesional: '', categoria_personal: '', is_active: true })
  showForm.value = true
  error.value = ''
}
async function cargar() {
  loading.value = true
  try {
    const [p, g] = await Promise.all([api<any[]>('/sigarh/mantenimiento/profesiones?limit=500'), api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales?limit=500')])
    items.value = p; grupos.value = g
  } catch (e: any) { error.value = apiErr(e, 'No se pudo cargar el catálogo') }
  finally { loading.value = false }
}
async function guardar() {
  saving.value = true; error.value = ''
  try {
    const body = editing.value?.es_base ? { is_active: form.is_active } : { ...form, colegio_profesional: form.colegio_profesional || null, categoria_personal: form.categoria_personal || null }
    await api(`/sigarh/mantenimiento/profesiones${editing.value ? '/' + editing.value.id : ''}`, { method: editing.value ? 'PATCH' : 'POST', body })
    showForm.value = false
    await cargar()
  } catch (e: any) { error.value = apiErr(e, 'No se pudo guardar') }
  finally { saving.value = false }
}
onMounted(cargar)
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6 gap-4">
      <div><h1 class="page-title">Profesiones y formación ocupacional</h1><p class="page-subtitle">Catálogo común del personal de salud y su grupo ocupacional</p></div>
      <button class="btn-primary" @click="abrir()">Crear profesión</button>
    </div>
    <p class="mb-4 text-sm" style="color: var(--ink-soft)">Base: profesiones del D. Leg. 1153, técnicos y auxiliares asistenciales. La clasificación administrativa es una configuración operativa. La categoría del hospital define su cartera asistencial; no cambia la profesión del trabajador.</p>
    <p v-if="error" class="error-message mb-4">{{ error }}</p>
    <form v-if="showForm" class="bg-white border rounded-xl p-6 mb-6 grid grid-cols-1 md:grid-cols-2 gap-4" @submit.prevent="guardar">
      <label class="form-group">Nombre<input v-model="form.nombre" class="input-clinical" required maxlength="255" :disabled="editing?.es_base" /></label>
      <label class="form-group">Código interno<input v-model="form.codigo" class="input-clinical" required maxlength="20" :disabled="editing?.es_base" /></label>
      <label class="form-group">Grupo ocupacional<select v-model="form.grupo_ocupacional_id" class="input-clinical" required :disabled="editing?.es_base"><option value="">Selecciona</option><option v-for="g in grupos.filter(g => g.is_active || g.id === form.grupo_ocupacional_id)" :key="g.id" :value="g.id">{{ g.nombre }}</option></select></label>
      <label class="form-group">Colegio profesional<input v-model="form.colegio_profesional" class="input-clinical" maxlength="255" :disabled="editing?.es_base" /></label>
      <label class="form-group">Categoría para roles de turno<select v-model="form.categoria_personal" class="input-clinical" :disabled="editing?.es_base"><option value="">Personal administrativo</option><option value="medicos">Médicos</option><option value="otros_profesionales">Otros profesionales de salud</option><option value="tecnicos">Técnicos y auxiliares</option></select></label>
      <label class="flex items-center gap-2"><input v-model="form.is_active" type="checkbox" /> Activa</label>
      <div class="md:col-span-2 flex gap-3"><button class="btn-primary" :disabled="saving">{{ saving ? 'Guardando...' : 'Guardar' }}</button><button type="button" class="btn-outline" @click="showForm = false">Cancelar</button></div>
    </form>
    <input v-model="search" class="input-clinical mb-4" placeholder="Buscar profesión, código o grupo ocupacional" />
    <p v-if="loading">Cargando catálogo...</p>
    <div v-else class="overflow-x-auto bg-white border rounded-xl">
      <table class="w-full text-sm"><thead><tr class="text-left border-b"><th class="p-4">Profesión</th><th class="p-4">Grupo ocupacional</th><th class="p-4">Colegio profesional</th><th class="p-4">Estado</th><th class="p-4">Acciones</th></tr></thead>
        <tbody><tr v-for="p in filtered" :key="p.id" class="border-b"><td class="p-4"><strong>{{ p.nombre }}</strong><div class="text-xs">{{ p.codigo }} · {{ p.es_base ? 'Catálogo base' : 'Registro del hospital' }}</div></td><td class="p-4">{{ grupo(p.grupo_ocupacional_id) }}</td><td class="p-4">{{ p.colegio_profesional || 'No aplica' }}</td><td class="p-4">{{ p.is_active ? 'Activa' : 'Inactiva' }}</td><td class="p-4"><button class="btn-outline" @click="abrir(p)">{{ p.es_base ? 'Configurar' : 'Editar' }}</button></td></tr><tr v-if="!filtered.length"><td colspan="5" class="p-4">No hay resultados.</td></tr></tbody>
      </table>
    </div>
  </div>
</template>
