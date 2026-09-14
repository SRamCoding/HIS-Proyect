<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')

const pasos = ['Datos Personales', 'Datos Laborales', 'Especialidades', 'Datos Bancarios', 'Ubicación']
const stepActual = ref(0)
const saving = ref(false)
const vinculoValido = ref(true)
const esMedico = ref(false)
const error = ref('')
const registroManual = ref(false)
const dniCargado = ref(false)
const consultandoDni = ref(false)
const verificandoDni = ref(false)
const dniExiste = ref(false)
const dniVerificado = ref(false)
const dniMsg = ref('')
const dniError = ref(false)
let dniTimer: any
let dniSolicitud = 0
onBeforeUnmount(() => { clearTimeout(dniTimer); dniSolicitud++ })

const gruposSanguineos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
const bancosPeru = [
  'Banco de la Nación', 'BCP - Banco de Crédito del Perú', 'BBVA Perú', 'Interbank',
  'Scotiabank Perú', 'BanBif', 'Banco Pichincha', 'MiBanco', 'Banco GNB Perú',
  'BCRP', 'Citibank Perú', 'Banco Falabella', 'Banco Ripley', 'Banco Azteca', 'Compartamos Financiera',
]
const ubigeoDeps = ref<{ id: string; nombre: string }[]>([])
const ubigeoProvs = ref<{ id: string; nombre: string }[]>([])
const ubigeoDists = ref<{ id: string; nombre: string }[]>([])

const tiposTrabajador = ref<any[]>([])
const nivelesRemunerativos = ref<any[]>([])
const profesionesCatalogo = ref<any[]>([])
const gruposOcupacionales = ref<any[]>([])
const departamentos = ref<any[]>([])
const servicios = ref<any[]>([])
const especialidades = ref<any[]>([])

const errors = reactive<Record<string, string>>({
  dni: '', nombres: '', apellido_paterno: '', apellido_materno: '', fecha_nacimiento: '',
  sexo: '', estado_civil: '', grupo_sanguineo: '', celular: '', correo: '',
  tipo_trabajador_id: '', nivel_remunerativo_id: '', grupo_ocupacional_id: '',
  servicio_id: '', cargo_laboral: '', modalidad: '', fecha_ingreso: '',
})

const form = reactive({
  numero_legajo: '',
  jornada_mensual_horas: '' as number | string, jornada_sustento: '',
  titulo_profesional: '',
  institucion_formacion: '',
  documento_vinculo_laboral: '',
  contacto_emergencia_nombre: '',
  contacto_emergencia_telefono: '',
  fecha_titulo: '',

  vinculo_laboral_codigo: '',
  dni: '', nombres: '', apellido_paterno: '', apellido_materno: '', fecha_nacimiento: '',
  sexo: '', estado_civil: '', grupo_sanguineo: '', celular: '', telefono_fijo: '', correo: '',
  is_active: true, profesion_id: '', numero_colegiatura: '', habilitado_colegio: false,
  tipo_trabajador_id: '', nivel_remunerativo_id: '', grupo_ocupacional_id: '',
  departamento_id: '', servicio_id: '', cargo_laboral: '', es_jefe_servicio: false, modalidad: '',
  codigo_minsa: '', numero_cmp: '', fecha_ingreso: '', fecha_nombramiento: '', fecha_cese: '',
  resolucion_nombramiento: '', resolucion_cese: '',
  especialidades: [] as any[],
  banco: '', ruc: '', numero_cuenta: '', numero_cci: '', tipo_cuenta: '',
  departamento_ubigeo: '', provincia_ubigeo: '', distrito_ubigeo: '', direccion: '',
})
const serviciosCompatibles = computed(() => servicios.value.filter(s => !form.departamento_id || s.departamento_id === form.departamento_id))
watch(() => form.departamento_id, () => {
  if (form.servicio_id && !serviciosCompatibles.value.some(s => s.id === form.servicio_id)) form.servicio_id = ''
})
watch(() => form.servicio_id, () => {
  const servicio = servicios.value.find(s => s.id === form.servicio_id)
  if (servicio?.departamento_id) form.departamento_id = servicio.departamento_id
})
const tiposCompatibles = computed(() => tiposTrabajador.value.filter(t => !t.vinculos_codigos?.length || !form.vinculo_laboral_codigo || t.vinculos_codigos.includes(form.vinculo_laboral_codigo)))
const nivelesCompatibles = computed(() => {
  const codigo = profesionesCatalogo.value.find(p => p.id === form.profesion_id)?.codigo
  return nivelesRemunerativos.value.filter(n => !n.profesion_codigo || n.profesion_codigo === codigo)
})
watch(() => form.profesion_id, () => {
  if (form.nivel_remunerativo_id && !nivelesCompatibles.value.some(n => n.id === form.nivel_remunerativo_id)) form.nivel_remunerativo_id = ''
})
watch(() => form.vinculo_laboral_codigo, () => {
  if (tiposCompatibles.value.length === 1) form.tipo_trabajador_id = tiposCompatibles.value[0].id
  else if (!tiposCompatibles.value.some(t => t.id === form.tipo_trabajador_id)) form.tipo_trabajador_id = ''
})


const fullName = computed(() => [form.nombres, form.apellido_paterno, form.apellido_materno].filter(Boolean).join(' '))
const espCount = computed(() => form.especialidades.filter(e => e.especialidad_id).length)

const progress = computed(() => {
  let p = 0
  if (form.dni && form.nombres && form.apellido_paterno && form.apellido_materno && form.fecha_nacimiento && form.sexo && form.estado_civil && form.grupo_sanguineo && form.celular && form.correo) p += 20
  if (form.tipo_trabajador_id && form.nivel_remunerativo_id && form.grupo_ocupacional_id && form.servicio_id && form.cargo_laboral && form.modalidad && form.fecha_ingreso) p += 20
  if (espCount.value) p += 20
  if (form.banco || form.ruc || form.numero_cuenta) p += 20
  if (form.departamento_ubigeo || form.provincia_ubigeo || form.distrito_ubigeo || form.direccion) p += 20
  return p
})

const RE_CORREO = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/
const RE_NOMBRE = /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ][A-Za-zÁÉÍÓÚÜÑáéíóúüñ' .-]*$/
const errNombre = (v: string, label: string) => {
  const t = v.trim()
  if (t.length < 2) return `${label} es requerido`
  if (!RE_NOMBRE.test(t)) return 'Solo se permiten letras, espacios, guiones y apóstrofos'
  return ''
}
const edadEn = (fecha: string) => {
  const fn = new Date(fecha), hoy = new Date()
  let e = hoy.getFullYear() - fn.getFullYear()
  const m = hoy.getMonth() - fn.getMonth()
  if (m < 0 || (m === 0 && hoy.getDate() < fn.getDate())) e--
  return e
}
const calcularAntiguedad = (fecha: string) => {
  if (!fecha) return '—'
  const diff = Math.floor((Date.now() - new Date(fecha).getTime()) / 86400000)
  const y = Math.floor(diff / 365), mo = Math.floor((diff % 365) / 30)
  if (y > 0) return `${y} año(s) y ${mo} mes(es)`
  if (mo > 0) return `${mo} mes(es)`
  return `${diff} día(s)`
}
const formatApiError = (e: any, fallback: string): string => apiErr(e, fallback)

// Verifica automáticamente contra el backend si el DNI ya está registrado.
const checkDni = async () => {
  if (!/^\d{8}$/.test(form.dni)) { dniExiste.value = false; dniVerificado.value = false; return }
  verificandoDni.value = true
  const solicitud = ++dniSolicitud
  const dni = form.dni
  try {
    const existente = await api<any>(`/sigarh/rrhh/empleados/buscar-dni/${dni}`, { tenant: tenantId.value })
    if (solicitud !== dniSolicitud) return
    dniExiste.value = !!(existente && existente.id)
    if (dniExiste.value) errors.dni = `Ya existe un empleado registrado con el DNI ${form.dni}`
    dniVerificado.value = true
  } catch {
    if (solicitud !== dniSolicitud) return
    dniExiste.value = false
    dniVerificado.value = false
  } finally {
    if (solicitud === dniSolicitud) verificandoDni.value = false
  }
}

watch(() => form.dni, (v) => {
  dniSolicitud++
  errors.dni = ''
  dniExiste.value = false
  dniVerificado.value = false
  dniMsg.value = ''
  dniCargado.value = false
  clearTimeout(dniTimer)
  if (v.length === 8) {
    verificandoDni.value = true
    dniTimer = setTimeout(checkDni, 450)
  } else {
    verificandoDni.value = false
  }
})

// Consulta el DNI en el servicio externo (a través del backend) para autocompletar
// nombres. Solo disponible cuando NO es registro manual (el casillero de arriba).
const consultarDni = async () => {
  if (registroManual.value || form.dni.length !== 8) return
  const dni = form.dni
  consultandoDni.value = true; dniMsg.value = ''; dniError.value = false
  try {
    await checkDni()
    if (form.dni !== dni) return
    if (dniExiste.value) return  // el error ya se muestra bajo el campo
    const d = await api<any>(`/sigarh/rrhh/dni-lookup/${dni}`, { tenant: tenantId.value })
    if (form.dni !== dni || registroManual.value) return
    form.nombres = d.nombres || form.nombres
    form.apellido_paterno = d.apellido_paterno || form.apellido_paterno
    form.apellido_materno = d.apellido_materno || form.apellido_materno
    dniMsg.value = 'Datos traídos del servicio de identidad. Verifícalos.'
    dniCargado.value = true
  } catch (e: any) {
    const code = e?.status ?? e?.statusCode ?? e?.response?.status ?? e?.data?.status
    if (code === 404) {
      dniMsg.value = 'El DNI no figura en el servicio. Activa "Registro manual" e ingresa los datos a mano.'
    } else {
      dniMsg.value = 'El servicio de identidad no respondió. Puedes continuar con registro manual.'
    }
    dniError.value = true
  } finally {
    consultandoDni.value = false
  }
}

// ── Ubigeo en cascada (catálogo local compartido, vía backend) ──
const loadDepartamentos = async () => {
  try { ubigeoDeps.value = await api('/sigarh/rrhh/ubigeo/departamentos') } catch { ubigeoDeps.value = [] }
}
const loadProvincias = async (depId: string) => {
  if (!depId) { ubigeoProvs.value = []; return }
  try { ubigeoProvs.value = await api(`/sigarh/rrhh/ubigeo/provincias/${depId}`) } catch { ubigeoProvs.value = [] }
}
const loadDistritos = async (provId: string) => {
  if (!provId) { ubigeoDists.value = []; return }
  try { ubigeoDists.value = await api(`/sigarh/rrhh/ubigeo/distritos/${provId}`) } catch { ubigeoDists.value = [] }
}
watch(() => form.departamento_ubigeo, (dep) => {
  form.provincia_ubigeo = ''
  form.distrito_ubigeo = ''
  ubigeoProvs.value = []
  ubigeoDists.value = []
  loadProvincias(dep)
})
watch(() => form.provincia_ubigeo, (prov) => {
  form.distrito_ubigeo = ''
  ubigeoDists.value = []
  loadDistritos(prov)
})

const validateStep = (step: number): boolean => {
  if (step === 0) {
    errors.dni = !form.dni ? 'El DNI es requerido'
      : !/^\d{8}$/.test(form.dni) ? 'El DNI debe tener 8 dígitos numéricos'
      : dniExiste.value ? `Ya existe un empleado registrado con el DNI ${form.dni}` : ''
    errors.nombres = errNombre(form.nombres, 'Los nombres')
    errors.apellido_paterno = errNombre(form.apellido_paterno, 'El apellido paterno')
    errors.apellido_materno = errNombre(form.apellido_materno, 'El apellido materno')
    errors.sexo = !form.sexo ? 'El sexo es requerido' : ''
    errors.estado_civil = !form.estado_civil ? 'El estado civil es requerido' : ''
    errors.grupo_sanguineo = ''
    errors.celular = !form.celular ? 'El celular es requerido' : !/^\d{9}$/.test(form.celular) ? 'El celular debe tener 9 dígitos' : ''
    errors.correo = !form.correo ? 'El correo es requerido' : !RE_CORREO.test(form.correo) ? 'El correo no tiene un formato válido' : ''
    errors.fecha_nacimiento = !form.fecha_nacimiento ? 'La fecha de nacimiento es requerida'
      : new Date(form.fecha_nacimiento) >= new Date() ? 'La fecha debe ser anterior a hoy'
      : edadEn(form.fecha_nacimiento) < 18 ? 'El empleado debe ser mayor de edad' : ''
    return !['dni', 'nombres', 'apellido_paterno', 'apellido_materno', 'sexo', 'estado_civil', 'grupo_sanguineo', 'celular', 'correo', 'fecha_nacimiento'].some(k => errors[k])
  }
  if (step === 1) {
    errors.tipo_trabajador_id = ''
    errors.nivel_remunerativo_id = ''
    errors.grupo_ocupacional_id = !form.grupo_ocupacional_id ? 'El grupo ocupacional es requerido' : ''
    errors.servicio_id = !form.servicio_id ? 'El servicio es requerido' : ''
    errors.cargo_laboral = !form.cargo_laboral ? 'El cargo laboral es requerido' : ''
    errors.modalidad = ''
    errors.fecha_ingreso = !form.fecha_ingreso ? 'La fecha de ingreso es requerida'
      : form.fecha_nacimiento && new Date(form.fecha_ingreso) <= new Date(form.fecha_nacimiento) ? 'Debe ser posterior a la fecha de nacimiento'
      : form.fecha_cese && new Date(form.fecha_cese) < new Date(form.fecha_ingreso) ? 'La fecha de cese es anterior a la de ingreso'
      : form.fecha_nombramiento && new Date(form.fecha_nombramiento) < new Date(form.fecha_ingreso) ? 'La fecha de nombramiento es anterior a la de ingreso' : ''
    return !['tipo_trabajador_id', 'nivel_remunerativo_id', 'grupo_ocupacional_id', 'servicio_id', 'cargo_laboral', 'modalidad', 'fecha_ingreso'].some(k => errors[k])
  }
  return true
}

const prevStep = () => { if (stepActual.value > 0) stepActual.value--; error.value = '' }
const nextStep = async () => {
  if (stepActual.value === 0) {
    clearTimeout(dniTimer)
    await checkDni()
  }
  if (!validateStep(stepActual.value)) { error.value = 'Completa los campos requeridos de este paso.'; return }
  error.value = ''
  if (stepActual.value < pasos.length - 1) stepActual.value++
}

const handleCreate = async () => {
  if (!vinculoValido.value) { error.value = 'Selecciona la condición del régimen laboral elegido.'; return }
  clearTimeout(dniTimer)
  await checkDni()
  for (const s of [0, 1]) {
    if (!validateStep(s)) { stepActual.value = s; error.value = `Completa los campos requeridos en "${pasos[s]}".`; return }
  }
  saving.value = true; error.value = ''
  try {
    const { especialidades: _esp, ...campos } = form
    const payload = {
      ...campos,
      especialidades: form.especialidades.filter(e => e.especialidad_id).map(e => ({ especialidad_id: e.especialidad_id, numero_rne: e.numero_rne || null, validado: e.validado })),
      profesion_id: form.profesion_id || null,
      numero_colegiatura: form.numero_colegiatura || null,
      numero_legajo: form.numero_legajo || null,
      jornada_mensual_horas: form.jornada_mensual_horas ? Number(form.jornada_mensual_horas) : null,
      jornada_sustento: form.jornada_sustento || null,
      titulo_profesional: form.titulo_profesional || null,
      institucion_formacion: form.institucion_formacion || null,
      documento_vinculo_laboral: form.documento_vinculo_laboral || null,
      contacto_emergencia_nombre: form.contacto_emergencia_nombre || null,
      contacto_emergencia_telefono: form.contacto_emergencia_telefono || null,
      fecha_titulo: form.fecha_titulo || null,
      vinculo_laboral_codigo: form.vinculo_laboral_codigo || null,
      tipo_trabajador_id: form.tipo_trabajador_id || null,
      nivel_remunerativo_id: form.nivel_remunerativo_id || null,
      grupo_ocupacional_id: form.grupo_ocupacional_id || null,
      departamento_id: form.departamento_id || null,
      servicio_id: form.servicio_id || null,
      fecha_nacimiento: form.fecha_nacimiento || null,
      fecha_ingreso: form.fecha_ingreso || null,
      fecha_nombramiento: form.fecha_nombramiento || null,
      fecha_cese: form.fecha_cese || null,
    }
    await api<any>('/sigarh/rrhh/empleados', { method: 'POST', tenant: tenantId.value, body: payload })
    router.push(`/sigarh/rrhh/empleados?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = formatApiError(e, 'No se pudo crear el empleado')
  } finally { saving.value = false }
}

onMounted(async () => {
  try {
    const refs = await api<any>('/sigarh/rrhh/empleados/catalogos', { tenant: tenantId.value })
    profesionesCatalogo.value = refs.profesiones
    const tt = refs.tipos_trabajador, nr = refs.niveles_remunerativos, go = refs.grupos_ocupacionales, dep = refs.departamentos, ser = refs.servicios
    const esp = await api<any[]>('/sigarh/rrhh/especialidades?active_only=true', { tenant: tenantId.value }).catch(() => [])
    tiposTrabajador.value = tt; nivelesRemunerativos.value = nr; gruposOcupacionales.value = go
    departamentos.value = dep; servicios.value = ser; especialidades.value = esp
  } catch (e: any) { error.value = apiErr(e, 'Error al cargar catálogos') }
  loadDepartamentos()
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-6">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/empleados?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Empleados</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Nuevo</span>
        </div>
        <div class="flex items-center gap-4">
          <div class="page-header-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-user-plus" class="w-6 h-6" style="color: var(--teal)" /></div>
          <div><h1 class="page-title">Registrar Empleado</h1><p class="page-subtitle">Paso {{ stepActual + 1 }} de {{ pasos.length }} — {{ pasos[stepActual] }}</p></div>
        </div>
      </div>

      <!-- Stepper -->
      <div class="wiz-steps">
        <button v-for="(s, i) in pasos" :key="i" type="button" class="wiz-step"
          :class="{ done: stepActual > i, active: stepActual === i }"
          @click="i < stepActual && (stepActual = i)">
          <span class="wiz-dot"><UIcon v-if="stepActual > i" name="i-heroicons-check" class="w-3 h-3" /><span v-else>{{ i + 1 }}</span></span>
          <span class="wiz-label">{{ s }}</span>
        </button>
      </div>

      <!-- Paso 1: Datos Personales -->
      <SFormCard v-show="stepActual === 0" title="Identificación Personal" subtitle="Datos de identidad y contacto"
        icon="i-heroicons-identification" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="stepActual === 0 ? error : ''">
        <div class="form-group full-width">
          <div class="status-toggle" style="background: var(--mist)">
            <span class="toggle-label">Registro manual (el empleado no figura en el servicio de DNI)</span>
            <button type="button" @click="registroManual = !registroManual" class="toggle-switch" :class="{ 'toggle-active': registroManual }"><span class="toggle-slider" /></button>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">DNI <span class="required">*</span></label>
          <div class="input-wrapper">
            <UIcon name="i-heroicons-identification" class="input-icon" />
            <input v-model="form.dni" class="input-clinical font-mono-data" maxlength="8" inputmode="numeric" placeholder="Ej: 76557726"
              :class="{ 'input-error': errors.dni }" @input="form.dni = form.dni.replace(/\D/g, '').slice(0, 8)" @blur="checkDni" />
            <UIcon v-if="verificandoDni" name="i-heroicons-arrow-path" class="w-4 h-4 animate-spin" style="position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--ink-soft)" />
            <UIcon v-else-if="dniVerificado && !dniExiste && !errors.dni" name="i-heroicons-check-circle" class="w-4 h-4" style="position: absolute; right: 0.75rem; top: 50%; transform: translateY(-50%); color: var(--green)" />
          </div>
          <span v-if="errors.dni" class="error-message">{{ errors.dni }}</span>
          <p v-else-if="verificandoDni" class="field-hint">Verificando disponibilidad...</p>
          <p v-else-if="dniVerificado && !dniExiste" class="field-hint" style="color: var(--green)">DNI disponible</p>
        </div>
        <div class="form-group" style="display: flex; flex-direction: column; justify-content: flex-end">
          <label class="form-label">&nbsp;</label>
          <button type="button" class="btn-outline" style="width: 100%; justify-content: center"
            :disabled="registroManual || consultandoDni || verificandoDni || form.dni.length !== 8" @click="consultarDni">
            <UIcon :name="consultandoDni ? 'i-heroicons-arrow-path' : 'i-heroicons-magnifying-glass'" class="w-4 h-4" :class="{ 'animate-spin': consultandoDni }" />
            {{ consultandoDni ? 'Consultando...' : 'Consultar DNI (RENIEC)' }}
          </button>
          <p class="field-hint">{{ registroManual ? 'Deshabilitado: registro manual activo' : 'Autocompleta los nombres desde RENIEC' }}</p>
        </div>
        <div v-if="dniMsg" class="form-group full-width">
          <p class="field-hint" :style="{ color: dniError ? 'var(--alert)' : 'var(--green)' }">{{ dniMsg }}</p>
        </div>
        <div class="form-group">
          <label class="form-label">Nombres <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" /><input v-model="form.nombres" class="input-clinical" :disabled="!registroManual && dniCargado" :class="{ 'input-error': errors.nombres }" /></div>
          <span v-if="errors.nombres" class="error-message">{{ errors.nombres }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Apellido Paterno <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" /><input v-model="form.apellido_paterno" class="input-clinical" :disabled="!registroManual && dniCargado" :class="{ 'input-error': errors.apellido_paterno }" /></div>
          <span v-if="errors.apellido_paterno" class="error-message">{{ errors.apellido_paterno }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Apellido Materno <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" /><input v-model="form.apellido_materno" class="input-clinical" :disabled="!registroManual && dniCargado" :class="{ 'input-error': errors.apellido_materno }" /></div>
          <span v-if="errors.apellido_materno" class="error-message">{{ errors.apellido_materno }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha de Nacimiento <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_nacimiento" type="date" class="input-clinical" :class="{ 'input-error': errors.fecha_nacimiento }" /></div>
          <span v-if="errors.fecha_nacimiento" class="error-message">{{ errors.fecha_nacimiento }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Sexo <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-arrows-right-left" class="input-icon" />
            <select v-model="form.sexo" class="input-clinical" :class="{ 'input-error': errors.sexo }"><option value="">Seleccione</option><option value="M">Masculino</option><option value="F">Femenino</option></select>
          </div>
          <span v-if="errors.sexo" class="error-message">{{ errors.sexo }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Estado Civil <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-heart" class="input-icon" />
            <select v-model="form.estado_civil" class="input-clinical" :class="{ 'input-error': errors.estado_civil }">
              <option value="">Seleccione</option><option value="soltero">Soltero(a)</option><option value="casado">Casado(a)</option>
              <option value="divorciado">Divorciado(a)</option><option value="viudo">Viudo(a)</option><option value="conviviente">Conviviente</option>
            </select>
          </div>
          <span v-if="errors.estado_civil" class="error-message">{{ errors.estado_civil }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Grupo Sanguíneo <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-beaker" class="input-icon" />
            <select v-model="form.grupo_sanguineo" class="input-clinical" :class="{ 'input-error': errors.grupo_sanguineo }"><option value="">Seleccione</option><option v-for="g in gruposSanguineos" :key="g" :value="g">{{ g }}</option></select>
          </div>
          <span v-if="errors.grupo_sanguineo" class="error-message">{{ errors.grupo_sanguineo }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Celular <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-phone" class="input-icon" />
            <input v-model="form.celular" class="input-clinical font-mono-data" maxlength="9" inputmode="numeric" placeholder="987654321" :class="{ 'input-error': errors.celular }" @input="form.celular = form.celular.replace(/\D/g, '').slice(0, 9)" />
          </div>
          <span v-if="errors.celular" class="error-message">{{ errors.celular }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Teléfono Fijo</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-phone-arrow-up-right" class="input-icon" /><input v-model="form.telefono_fijo" class="input-clinical" placeholder="(01) 234-5678" /></div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Correo Electrónico <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-envelope" class="input-icon" /><input v-model="form.correo" type="email" class="input-clinical" placeholder="empleado@hospital.pe" :class="{ 'input-error': errors.correo }" /></div>
          <span v-if="errors.correo" class="error-message">{{ errors.correo }}</span>
        </div>
        <div class="form-group full-width">
          <div class="status-toggle"><span class="toggle-label">Empleado Activo</span>
            <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }"><span class="toggle-slider" /></button>
          </div>
        </div>
        <template #actions>
          <div class="wiz-nav">
            <div style="flex: 1" />
            <button type="button" class="btn-primary" @click="nextStep">Siguiente <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" /></button>
          </div>
        </template>
      </SFormCard>

      <!-- Paso 2: Datos Laborales -->
      <SFormCard v-show="stepActual === 1" title="Clasificación Laboral" subtitle="Tipo de trabajador, nivel remunerativo, grupo ocupacional y cargo"
        icon="i-heroicons-briefcase" icon-bg="var(--navy-soft)" icon-color="var(--navy)" :error="stepActual === 1 ? error : ''">
        <div class="form-group">
          <label class="form-label">Tipo de Trabajador <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-user-group" class="input-icon" />
            <select v-model="form.tipo_trabajador_id" class="input-clinical" :class="{ 'input-error': errors.tipo_trabajador_id }"><option value="">Seleccione</option><option v-for="t in tiposCompatibles" :key="t.id" :value="t.id">{{ t.nombre }}</option></select>
          </div>
          <span v-if="errors.tipo_trabajador_id" class="error-message">{{ errors.tipo_trabajador_id }}</span>
        </div>
        <SClasificacionProfesional v-model:profesion-id="form.profesion_id" v-model:numero-colegiatura="form.numero_colegiatura" v-model:habilitado="form.habilitado_colegio" @grupo="form.grupo_ocupacional_id = $event" @medico="esMedico = $event" />
        <div class="form-group">
          <label class="form-label">Nivel Remunerativo</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-currency-dollar" class="input-icon" />
            <select :disabled="!form.profesion_id" v-model="form.nivel_remunerativo_id" class="input-clinical" :class="{ 'input-error': errors.nivel_remunerativo_id }"><option value="">{{ form.profesion_id ? 'Seleccione' : 'Seleccione primero la profesión' }}</option><option v-for="n in nivelesCompatibles" :key="n.id" :value="n.id">{{ n.nombre }}</option></select>
          </div>
          <span v-if="errors.nivel_remunerativo_id" class="error-message">{{ errors.nivel_remunerativo_id }}</span>
        </div>
        <SJornadaMedica v-model="form" />
        <SEmpleadoLegajo v-model="form" />
        <SVinculoLaboral v-model="form.vinculo_laboral_codigo" @valido="vinculoValido = $event" />
        <div class="form-group">
          <label class="form-label">Grupo Ocupacional <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-chart-bar" class="input-icon" />
            <select v-model="form.grupo_ocupacional_id" class="input-clinical" :disabled="!!form.profesion_id" :class="{ 'input-error': errors.grupo_ocupacional_id }"><option value="">Seleccione</option><option v-for="g in gruposOcupacionales" :key="g.id" :value="g.id">{{ g.nombre }}</option></select>
          </div>
          <span v-if="errors.grupo_ocupacional_id" class="error-message">{{ errors.grupo_ocupacional_id }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Departamento</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-building-office" class="input-icon" />
            <select v-model="form.departamento_id" class="input-clinical"><option value="">Seleccione</option><option v-for="d in departamentos" :key="d.id" :value="d.id">{{ d.nombre }}</option></select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Servicio / Área <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-folder" class="input-icon" />
            <select v-model="form.servicio_id" class="input-clinical" :class="{ 'input-error': errors.servicio_id }"><option value="">Seleccione</option><option v-for="s in serviciosCompatibles" :key="s.id" :value="s.id">{{ s.nombre }}</option></select>
          </div>
          <span v-if="errors.servicio_id" class="error-message">{{ errors.servicio_id }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">&nbsp;</label>
          <label class="text-xs flex items-center gap-1.5" style="color: var(--ink-soft); padding-top: 0.7rem">
            <input type="checkbox" v-model="form.es_jefe_servicio" /> Jefe de este servicio (podrá aprobar sus roles de turno)
          </label>
        </div>
        <div class="form-group">
          <label class="form-label">Cargo Laboral <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-briefcase" class="input-icon" /><input v-model="form.cargo_laboral" class="input-clinical" maxlength="100" placeholder="Ej: Médico Especialista" :class="{ 'input-error': errors.cargo_laboral }" /></div>
          <span v-if="errors.cargo_laboral" class="error-message">{{ errors.cargo_laboral }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Modalidad <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" />
            <select v-model="form.modalidad" class="input-clinical" :class="{ 'input-error': errors.modalidad }">
              <option value="">Seleccione...</option><option value="nombrado">Nombrado</option><option value="cas">CAS</option>
              <option value="contrato">Contrato</option><option value="snp">SNP</option><option value="tercero">Tercero</option>
            </select>
          </div>
          <span v-if="errors.modalidad" class="error-message">{{ errors.modalidad }}</span>
        </div>
        <div class="form-group">
          <label class="form-label">Código MINSA</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-identification" class="input-icon" /><input v-model="form.codigo_minsa" class="input-clinical font-mono-data" maxlength="20" placeholder="Código institucional" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">N° CMP</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document" class="input-icon" /><input v-model="form.numero_cmp" class="input-clinical font-mono-data" maxlength="10" inputmode="numeric" placeholder="Colegio Médico" @input="form.numero_cmp = form.numero_cmp.replace(/\D/g, '').slice(0, 10)" /></div>
          <p class="field-hint">Solo para médicos</p>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha de Ingreso <span class="required">*</span></label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_ingreso" type="date" class="input-clinical" :class="{ 'input-error': errors.fecha_ingreso }" /></div>
          <span v-if="errors.fecha_ingreso" class="error-message">{{ errors.fecha_ingreso }}</span>
          <p v-if="form.fecha_ingreso && !errors.fecha_ingreso" class="field-hint">Antigüedad: {{ calcularAntiguedad(form.fecha_ingreso) }}</p>
        </div>
        <div class="form-group">
          <label class="form-label">Resolución Nombramiento</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" /><input v-model="form.resolucion_nombramiento" class="input-clinical" placeholder="N° de resolución" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha de Nombramiento</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_nombramiento" type="date" class="input-clinical" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Resolución de Cese</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" /><input v-model="form.resolucion_cese" class="input-clinical" placeholder="N° de resolución" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Fecha de Cese</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_cese" type="date" class="input-clinical" /></div>
        </div>
        <template #actions>
          <div class="wiz-nav">
            <button type="button" class="btn-outline" @click="prevStep"><UIcon name="i-heroicons-arrow-left" class="w-4 h-4" /> Anterior</button>
            <div style="flex: 1" />
            <button type="button" class="btn-primary" @click="nextStep">Siguiente <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" /></button>
          </div>
        </template>
      </SFormCard>

      <!-- Paso 3: Especialidades -->
      <SFormCard v-show="stepActual === 2" title="Especialidades" subtitle="Especialidades médicas del empleado (solo personal médico)"
        icon="i-heroicons-star" icon-bg="var(--purple-soft)" icon-color="var(--purple)">
        <div class="form-group full-width" v-for="(esp, i) in form.especialidades" :key="i">
          <div style="display: grid; grid-template-columns: 1fr 1fr auto auto; gap: 0.75rem; align-items: end; padding: 0.875rem; background: var(--mist); border-radius: 8px">
            <div>
              <label class="form-label">Especialidad</label>
              <div class="input-wrapper"><UIcon name="i-heroicons-star" class="input-icon" />
                <select v-model="esp.especialidad_id" class="input-clinical"><option value="">Seleccione</option><option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option></select>
              </div>
            </div>
            <div>
              <label class="form-label">N° RNE</label>
              <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" /><input v-model="esp.numero_rne" class="input-clinical" placeholder="Registro" /></div>
            </div>
            <label class="text-xs flex items-center gap-1.5" style="color: var(--ink-soft); padding-bottom: 0.6rem"><input type="checkbox" v-model="esp.validado" /> Validado</label>
            <button type="button" class="sigarh-action-btn danger" style="margin-bottom: 0.3rem" @click="form.especialidades.splice(i, 1)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" /></button>
          </div>
        </div>
        <div class="form-group full-width">
          <button type="button" class="btn-outline" :disabled="!esMedico" @click="form.especialidades.push({ especialidad_id: '', numero_rne: '', validado: false })">
            <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Agregar Especialidad
          </button>
        </div>
        <template #actions>
          <div class="wiz-nav">
            <button type="button" class="btn-outline" @click="prevStep"><UIcon name="i-heroicons-arrow-left" class="w-4 h-4" /> Anterior</button>
            <div style="flex: 1" />
            <button type="button" class="btn-primary" @click="nextStep">Siguiente <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" /></button>
          </div>
        </template>
      </SFormCard>

      <!-- Paso 4: Datos Bancarios -->
      <SFormCard v-show="stepActual === 3" title="Datos Bancarios" subtitle="Cuenta para el pago de remuneraciones"
        icon="i-heroicons-banknotes" icon-bg="var(--amber-soft)" icon-color="var(--amber)">
        <div class="form-group">
          <label class="form-label">Banco</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-building-office-2" class="input-icon" />
            <select v-model="form.banco" class="input-clinical"><option value="">Seleccione un banco</option><option v-for="b in bancosPeru" :key="b" :value="b">{{ b }}</option></select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">RUC</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-document" class="input-icon" /><input v-model="form.ruc" class="input-clinical font-mono-data" maxlength="11" inputmode="numeric" placeholder="20123456789" @input="form.ruc = form.ruc.replace(/\D/g, '').slice(0, 11)" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Número de Cuenta</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-credit-card" class="input-icon" /><input v-model="form.numero_cuenta" class="input-clinical font-mono-data" inputmode="numeric" placeholder="10 a 20 dígitos" @input="form.numero_cuenta = form.numero_cuenta.replace(/\D/g, '').slice(0, 20)" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Número CCI</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-credit-card" class="input-icon" /><input v-model="form.numero_cci" class="input-clinical font-mono-data" placeholder="Código interbancario" /></div>
        </div>
        <div class="form-group">
          <label class="form-label">Tipo de Cuenta</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-list-bullet" class="input-icon" />
            <select v-model="form.tipo_cuenta" class="input-clinical"><option value="">Seleccione</option><option value="ahorros">Ahorros</option><option value="corriente">Corriente</option></select>
          </div>
        </div>
        <template #actions>
          <div class="wiz-nav">
            <button type="button" class="btn-outline" @click="prevStep"><UIcon name="i-heroicons-arrow-left" class="w-4 h-4" /> Anterior</button>
            <div style="flex: 1" />
            <button type="button" class="btn-primary" @click="nextStep">Siguiente <UIcon name="i-heroicons-arrow-right" class="w-4 h-4" /></button>
          </div>
        </template>
      </SFormCard>

      <!-- Paso 5: Ubicación -->
      <SFormCard v-show="stepActual === 4" title="Ubicación" subtitle="Domicilio del empleado"
        icon="i-heroicons-map-pin" icon-bg="var(--green-soft)" icon-color="var(--green)" :error="stepActual === 4 ? error : ''">
        <div class="form-group">
          <label class="form-label">Departamento</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-map-pin" class="input-icon" />
            <select v-model="form.departamento_ubigeo" class="input-clinical">
              <option value="">Seleccione</option>
              <option v-for="d in ubigeoDeps" :key="d.id" :value="d.id">{{ d.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Provincia</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-map-pin" class="input-icon" />
            <select v-model="form.provincia_ubigeo" class="input-clinical" :disabled="!form.departamento_ubigeo">
              <option value="">{{ form.departamento_ubigeo ? 'Seleccione' : 'Elige un departamento' }}</option>
              <option v-for="p in ubigeoProvs" :key="p.id" :value="p.id">{{ p.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">Distrito</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-map-pin" class="input-icon" />
            <select v-model="form.distrito_ubigeo" class="input-clinical" :disabled="!form.provincia_ubigeo">
              <option value="">{{ form.provincia_ubigeo ? 'Seleccione' : 'Elige una provincia' }}</option>
              <option v-for="d in ubigeoDists" :key="d.id" :value="d.id">{{ d.nombre }}</option>
            </select>
          </div>
        </div>
        <div class="form-group full-width">
          <label class="form-label">Dirección</label>
          <div class="input-wrapper"><UIcon name="i-heroicons-home" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.direccion" class="input-clinical" rows="2" maxlength="200" placeholder="Dirección completa" /></div>
        </div>
        <template #actions>
          <div class="wiz-nav">
            <button type="button" class="btn-outline" @click="prevStep"><UIcon name="i-heroicons-arrow-left" class="w-4 h-4" /> Anterior</button>
            <div style="flex: 1" />
            <SFormActions :saving="saving" save-text="Crear Empleado" saving-text="Creando..."
              :cancel-to="`/sigarh/rrhh/empleados?tenant=${tenantId}`" @save="handleCreate" />
          </div>
        </template>
      </SFormCard>
    </template>

    <template #sidebar>
      <SWidgetSummary :items="[
        { label: 'Progreso', value: progress + '%' },
        { divider: true },
        { label: 'Empleado', value: fullName },
        { label: 'DNI', value: form.dni, mono: true },
        { label: 'Cargo', value: form.cargo_laboral },
        { label: 'Modalidad', value: form.modalidad },
        { label: 'Estado', value: form.is_active ? 'Activo' : 'Inactivo' },
        { divider: true },
        { label: 'Especialidades', value: String(espCount) },
      ]" />
      <SWidgetInfo :items="['El DNI debe tener 8 dígitos y es único por hospital', 'El correo también es único; no se puede repetir', 'El empleado debe ser mayor de edad', 'Las especialidades solo aplican a personal médico', 'Cuenta bancaria: entre 10 y 20 dígitos']" />
      <SWidgetTip text="El DNI se verifica automáticamente al escribir los 8 dígitos. Si ya existe, no podrás avanzar hasta corregirlo." />
    </template>
  </SFormLayout>
</template>

<style scoped>
.wiz-steps {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}
.wiz-step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  border-radius: 10px;
  border: 1px solid var(--line);
  background: var(--paper);
  font-size: 0.8125rem;
  color: var(--ink-soft);
  cursor: default;
  transition: all 0.2s ease;
}
.wiz-step.done { cursor: pointer; border-color: var(--teal); color: var(--ink); }
.wiz-step.active { border-color: var(--teal); background: var(--teal-soft); color: var(--teal); font-weight: 600; }
.wiz-dot {
  width: 22px;
  height: 22px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6875rem;
  font-weight: 600;
  background: var(--mist);
  color: var(--ink-soft);
}
.wiz-step.done .wiz-dot,
.wiz-step.active .wiz-dot { background: var(--teal); color: #fff; }
.wiz-nav {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
}
@media (max-width: 640px) {
  .wiz-label { display: none; }
}
</style>
