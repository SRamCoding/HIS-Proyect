<script setup lang="ts">
const props = defineProps<{ tenantId: string; role: string }>()
const perfilId = defineModel<string>({ default: '' })
const { api } = useApi()
interface Perfil { id: string; nombre: string; role: string; modulos: string[]; is_active: boolean }
const perfiles = ref<Perfil[]>([])
const catalogo = ref<{code: string; label: string}[]>([])
const error = ref('')
const cargando = ref(false)
const guardando = ref(false)
const editor = ref(false)
const editarId = ref('')
const nombre = ref('')
const modulos = ref<string[]>([])
const activo = ref(true)
let solicitud = 0
const opciones = computed(() => perfiles.value.filter(p => p.role === props.role))
const MODULOS_ROL: Record<string, string[]> = {
  medico: ['consulta_externa.programacion', 'consulta_externa.atenciones'],
  enfermera: ['consulta_externa.confirmacion', 'consulta_externa.triaje', 'hospitalizacion.seguimiento'],
}
const permitidos = computed(() => MODULOS_ROL[props.role]
  ? catalogo.value.filter(m => MODULOS_ROL[props.role]!.includes(m.code)) : catalogo.value)
const seleccionado = computed(() => perfiles.value.find(p => p.id === perfilId.value))
async function cargar() {
  const actual = ++solicitud
  error.value = ''
  perfiles.value = []; catalogo.value = []
  if (!props.tenantId) return
  cargando.value = true
  try {
    const resultados = await Promise.all([
      api<Perfil[]>(`/admin/usuarios/perfiles-hospital?tenant_id=${props.tenantId}`),
      api<{code: string; label: string}[]>(`/admin/usuarios/perfiles-hospital/catalogo?tenant_id=${props.tenantId}`)
    ])
    if (actual !== solicitud) return
    ;[perfiles.value, catalogo.value] = resultados
  } catch (e) { if (actual === solicitud) error.value = apiErr(e, 'No se pudieron cargar los perfiles') }
  finally { if (actual === solicitud) cargando.value = false }
}
watch(() => props.tenantId, (nuevo, anterior) => { if (anterior && nuevo !== anterior) perfilId.value = ''; editor.value = false; cargar() }, { immediate: true })
watch(() => props.role, () => { if (seleccionado.value && seleccionado.value.role !== props.role) perfilId.value = ''; editor.value = false })
function abrir(editar = false) {
  const p = editar ? seleccionado.value : undefined
  editarId.value = p?.id || ''
  nombre.value = p?.nombre || (props.role === 'medico' ? 'Médico de consulta externa' : props.role === 'enfermera' ? 'Enfermería asistencial' : '')
  modulos.value = p ? [...p.modulos] : MODULOS_ROL[props.role] ? permitidos.value.map(m => m.code) : []
  activo.value = p?.is_active ?? true
  editor.value = true
}
async function guardar() {
  if (guardando.value || !nombre.value.trim()) return
  guardando.value = true; error.value = ''
  try {
    const p = await api<Perfil>(`/admin/usuarios/perfiles-hospital${editarId.value ? '/' + editarId.value : ''}?tenant_id=${props.tenantId}`, {
      method: editarId.value ? 'PUT' : 'POST', body: { nombre: nombre.value, role: props.role, modulos: modulos.value, is_active: activo.value }
    })
    await cargar(); perfilId.value = p.id; editor.value = false
  } catch (e) { error.value = apiErr(e, 'No se pudo guardar el perfil') }
  finally { guardando.value = false }
}
</script>

<template>
  <div class="col-span-full rounded-xl border border-slate-200 p-4 space-y-3">
    <p class="font-semibold">Perfil del panel hospitalario</p>
    <p class="text-sm text-slate-500">El perfil concede accesos dentro de los módulos habilitados para este hospital.</p>
    <p v-if="error" role="alert" class="text-red-600">{{ error }} <button type="button" class="underline" @click="cargar">Reintentar</button></p>
    <p v-if="!tenantId" class="text-sm">Selecciona primero el hospital.</p>
    <template v-else>
      <label class="block">Perfil
        <select v-model="perfilId" class="input-clinical" :disabled="cargando">
          <option value="">{{ role === 'administrador' ? 'Administrador general del hospital' : 'Seleccione un perfil' }}</option>
          <option v-for="p in opciones" :key="p.id" :value="p.id">{{ p.nombre }}{{ p.is_active ? '' : ' (inactivo)' }}</option>
        </select>
      </label>
      <div class="flex gap-4">
        <button type="button" class="underline" :disabled="cargando" @click="abrir()">Crear perfil</button>
        <button v-if="seleccionado" type="button" class="underline" @click="abrir(true)">Editar accesos del perfil</button>
      </div>
      <p v-if="role === 'medico'" class="text-sm text-slate-500">El médico consulta su programación y atiende sus citas. Debe estar vinculado al empleado médico correspondiente.</p>
      <p v-if="role === 'enfermera'" class="text-sm text-slate-500">Enfermería confirma citas, registra triaje y documenta el seguimiento del paciente hospitalizado. La cuenta debe vincularse a un empleado de Enfermería.</p>
      <div v-if="editor" class="border rounded-lg p-4 space-y-3">
        <p class="text-sm">Estos cambios se aplican a todos los usuarios que tienen este perfil.</p>
        <label class="block">Nombre del perfil <input v-model="nombre" class="input-clinical" maxlength="100" /></label>
        <div class="grid md:grid-cols-2 gap-2">
          <label v-for="m in permitidos" :key="m.code" class="flex gap-2 items-center"><input v-model="modulos" type="checkbox" :value="m.code" />{{ m.label }}</label>
        </div>
        <label class="flex gap-2"><input v-model="activo" type="checkbox" />Perfil activo</label>
        <div class="flex gap-4"><button type="button" class="underline" :disabled="guardando || !nombre.trim()" @click="guardar">{{ guardando ? 'Guardando...' : 'Guardar perfil' }}</button><button type="button" @click="editor = false">Cancelar</button></div>
      </div>
    </template>
  </div>
</template>
