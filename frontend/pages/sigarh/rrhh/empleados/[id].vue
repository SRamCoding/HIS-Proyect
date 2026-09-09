<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })
const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)

const loading = ref(true)
const saving = ref(false)
const error = ref('')

const gruposSanguineos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
const bancosPeru = [
  'Banco de la Nación', 'BCP - Banco de Crédito del Perú', 'BBVA Perú', 'Interbank',
  'Scotiabank Perú', 'BanBif', 'Banco Pichincha', 'MiBanco', 'Banco GNB Perú',
  'BCRP', 'Citibank Perú', 'Banco Falabella', 'Banco Ripley', 'Banco Azteca', 'Compartamos Financiera',
]
const ubigeoDepartamentos = [
  '01 Amazonas', '02 Áncash', '03 Apurímac', '04 Arequipa', '05 Ayacucho', '06 Cajamarca',
  '07 Callao', '08 Cusco', '09 Huancavelica', '10 Huánuco', '11 Ica', '12 Junín',
  '13 La Libertad', '14 Lambayeque', '15 Lima', '16 Loreto', '17 Madre de Dios', '18 Moquegua',
  '19 Pasco', '20 Piura', '21 Puno', '22 San Martín', '23 Tacna', '24 Tumbes', '25 Ucayali',
].map(s => ({ codigo: s.slice(0, 2), nombre: s.slice(3) }))

const tiposTrabajador = ref<any[]>([])
const nivelesRemunerativos = ref<any[]>([])
const gruposOcupacionales = ref<any[]>([])
const departamentos = ref<any[]>([])
const servicios = ref<any[]>([])
const especialidades = ref<any[]>([])

const errors = reactive<Record<string, string>>({
  nombres: '', apellido_paterno: '', apellido_materno: '', celular: '', correo: '', fecha_nacimiento: '', fecha_ingreso: '',
})

const form = reactive({
  dni: '', nombres: '', apellido_paterno: '', apellido_materno: '', fecha_nacimiento: '',
  sexo: '', estado_civil: '', grupo_sanguineo: '', celular: '', telefono_fijo: '', correo: '',
  is_active: true,
  tipo_trabajador_id: '', nivel_remunerativo_id: '', grupo_ocupacional_id: '',
  departamento_id: '', servicio_id: '', cargo_laboral: '', modalidad: '',
  codigo_minsa: '', numero_cmp: '', fecha_ingreso: '', fecha_nombramiento: '', fecha_cese: '',
  resolucion_nombramiento: '', resolucion_cese: '',
  especialidades: [] as any[],
  banco: '', ruc: '', numero_cuenta: '', numero_cci: '', tipo_cuenta: '',
  departamento_ubigeo: '', provincia_ubigeo: '', distrito_ubigeo: '', direccion: '',
})

const fullName = computed(() => [form.nombres, form.apellido_paterno, form.apellido_materno].filter(Boolean).join(' '))
const espCount = computed(() => form.especialidades.filter(e => e.especialidad_id).length)
const progress = computed(() => {
  let p = 0
  if (form.nombres && form.apellido_paterno && form.apellido_materno) p += 20
  if (form.tipo_trabajador_id || form.cargo_laboral) p += 20
  if (espCount.value) p += 20
  if (form.banco || form.ruc || form.numero_cuenta) p += 20
  if (form.departamento_ubigeo || form.direccion) p += 20
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

const validate = (): boolean => {
  errors.nombres = errNombre(form.nombres, 'Los nombres')
  errors.apellido_paterno = errNombre(form.apellido_paterno, 'El apellido paterno')
  errors.apellido_materno = errNombre(form.apellido_materno, 'El apellido materno')
  errors.celular = form.celular && !/^\d{9}$/.test(form.celular) ? 'El celular debe tener 9 dígitos' : ''
  errors.correo = form.correo && !RE_CORREO.test(form.correo) ? 'El correo no tiene un formato válido' : ''
  errors.fecha_nacimiento = ''
  if (form.fecha_nacimiento) {
    if (new Date(form.fecha_nacimiento) >= new Date()) errors.fecha_nacimiento = 'La fecha debe ser anterior a hoy'
    else if (edadEn(form.fecha_nacimiento) < 18) errors.fecha_nacimiento = 'El empleado debe ser mayor de edad'
  }
  errors.fecha_ingreso = ''
  if (form.fecha_ingreso) {
    if (form.fecha_nacimiento && new Date(form.fecha_ingreso) <= new Date(form.fecha_nacimiento)) errors.fecha_ingreso = 'Debe ser posterior a la fecha de nacimiento'
    else if (form.fecha_cese && new Date(form.fecha_cese) < new Date(form.fecha_ingreso)) errors.fecha_ingreso = 'La fecha de cese es anterior a la de ingreso'
    else if (form.fecha_nombramiento && new Date(form.fecha_nombramiento) < new Date(form.fecha_ingreso)) errors.fecha_ingreso = 'La fecha de nombramiento es anterior a la de ingreso'
  }
  return !Object.values(errors).some(Boolean)
}

const quitarEspecialidad = async (i: number) => {
  const esp = form.especialidades[i]
  if (esp.id) {
    if (!confirm('¿Quitar esta especialidad del empleado?')) return
    try { await api(`/sigarh/rrhh/empleados/${id.value}/especialidades/${esp.id}`, { method: 'DELETE' }) }
    catch (e: any) { error.value = apiErr(e, 'No se pudo quitar la especialidad'); return }
  }
  form.especialidades.splice(i, 1)
}

const eliminarEmpleado = async () => {
  if (!confirm(`¿Eliminar al empleado "${fullName.value}"? Esta acción no se puede deshacer.`)) return
  try {
    await api(`/sigarh/rrhh/empleados/${id.value}`, { method: 'DELETE' })
    router.push(`/sigarh/rrhh/empleados?tenant=${tenantId.value}`)
  } catch (e: any) { error.value = apiErr(e, 'No se pudo eliminar el empleado') }
}

const handleSave = async () => {
  if (!validate()) { error.value = 'Revisa los campos marcados en rojo.'; return }
  saving.value = true; error.value = ''
  try {
    await api(`/sigarh/rrhh/empleados/${id.value}`, {
      method: 'PATCH',
      body: {
        nombres: form.nombres, apellido_paterno: form.apellido_paterno, apellido_materno: form.apellido_materno,
        fecha_nacimiento: form.fecha_nacimiento || null, sexo: form.sexo || null, estado_civil: form.estado_civil || null,
        grupo_sanguineo: form.grupo_sanguineo || null, celular: form.celular || null, telefono_fijo: form.telefono_fijo || null,
        correo: form.correo || null, is_active: form.is_active,
        tipo_trabajador_id: form.tipo_trabajador_id || null, nivel_remunerativo_id: form.nivel_remunerativo_id || null,
        grupo_ocupacional_id: form.grupo_ocupacional_id || null, departamento_id: form.departamento_id || null,
        servicio_id: form.servicio_id || null, cargo_laboral: form.cargo_laboral || null, modalidad: form.modalidad || null,
        codigo_minsa: form.codigo_minsa || null, numero_cmp: form.numero_cmp || null,
        fecha_ingreso: form.fecha_ingreso || null, fecha_nombramiento: form.fecha_nombramiento || null, fecha_cese: form.fecha_cese || null,
        resolucion_nombramiento: form.resolucion_nombramiento || null, resolucion_cese: form.resolucion_cese || null,
        banco: form.banco || null, ruc: form.ruc || null, numero_cuenta: form.numero_cuenta || null,
        numero_cci: form.numero_cci || null, tipo_cuenta: form.tipo_cuenta || null,
        departamento_ubigeo: form.departamento_ubigeo || null, provincia_ubigeo: form.provincia_ubigeo || null,
        distrito_ubigeo: form.distrito_ubigeo || null, direccion: form.direccion || null,
      },
    })
    for (const esp of form.especialidades) {
      if (esp.nueva && esp.especialidad_id) {
        await api(`/sigarh/rrhh/empleados/${id.value}/especialidades`, {
          method: 'POST',
          body: { especialidad_id: esp.especialidad_id, numero_rne: esp.numero_rne || null, validado: esp.validado },
        })
      }
    }
    router.push(`/sigarh/rrhh/empleados?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = formatApiError(e, 'No se pudo guardar el empleado')
  } finally { saving.value = false }
}

onMounted(async () => {
  try {
    const [data, tt, nr, go, dep, ser, esp] = await Promise.all([
      api<any>(`/sigarh/rrhh/empleados/${id.value}`),
      api<any[]>('/sigarh/mantenimiento/tipos-trabajador'),
      api<any[]>('/sigarh/mantenimiento/niveles-remunerativos'),
      api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
      api<any[]>('/sigarh/mantenimiento/departamentos'),
      api<any[]>('/sigarh/mantenimiento/servicios'),
      api<any[]>('/sigarh/rrhh/especialidades'),
    ])
    Object.assign(form, {
      dni: data.dni || '', nombres: data.nombres || '', apellido_paterno: data.apellido_paterno || '', apellido_materno: data.apellido_materno || '',
      fecha_nacimiento: data.fecha_nacimiento || '', sexo: data.sexo || '', estado_civil: data.estado_civil || '', grupo_sanguineo: data.grupo_sanguineo || '',
      celular: data.celular || '', telefono_fijo: data.telefono_fijo || '', correo: data.correo || '', is_active: data.is_active,
      tipo_trabajador_id: data.tipo_trabajador_id || '', nivel_remunerativo_id: data.nivel_remunerativo_id || '', grupo_ocupacional_id: data.grupo_ocupacional_id || '',
      departamento_id: data.departamento_id || '', servicio_id: data.servicio_id || '', cargo_laboral: data.cargo_laboral || '', modalidad: data.modalidad || '',
      codigo_minsa: data.codigo_minsa || '', numero_cmp: data.numero_cmp || '', fecha_ingreso: data.fecha_ingreso || '', fecha_nombramiento: data.fecha_nombramiento || '', fecha_cese: data.fecha_cese || '',
      resolucion_nombramiento: data.resolucion_nombramiento || '', resolucion_cese: data.resolucion_cese || '',
      banco: data.banco || '', ruc: data.ruc || '', numero_cuenta: data.numero_cuenta || '', numero_cci: data.numero_cci || '', tipo_cuenta: data.tipo_cuenta || '',
      departamento_ubigeo: data.departamento_ubigeo || '', provincia_ubigeo: data.provincia_ubigeo || '', distrito_ubigeo: data.distrito_ubigeo || '', direccion: data.direccion || '',
    })
    form.especialidades = (data.especialidades || []).map((e: any) => ({
      id: e.id, especialidad_id: e.especialidad_id, numero_rne: e.numero_rne || '', validado: e.validado, nueva: false,
    }))
    tiposTrabajador.value = tt; nivelesRemunerativos.value = nr; gruposOcupacionales.value = go
    departamentos.value = dep; servicios.value = ser; especialidades.value = esp
  } catch (e: any) {
    error.value = 'No se pudo cargar el empleado'
  } finally { loading.value = false }
})
</script>

<template>
  <SFormLayout>
    <template #main>
      <div class="mb-8">
        <div class="flex items-center gap-1.5 text-xs mb-3" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/empleados?tenant=${tenantId}`" class="hover:underline" style="color: var(--ink-soft)">Empleados</NuxtLink>
          <UIcon name="i-heroicons-chevron-right" class="w-3 h-3" /><span style="color: var(--ink)">Editar</span>
        </div>
        <div class="flex items-center justify-between gap-4">
          <div class="flex items-center gap-4">
            <div class="page-header-icon" style="background: var(--teal-soft)"><UIcon name="i-heroicons-user" class="w-6 h-6" style="color: var(--teal)" /></div>
            <div><h1 class="page-title">{{ fullName || 'Editar Empleado' }}</h1><p class="page-subtitle">Actualiza la ficha del colaborador</p></div>
          </div>
          <button v-if="!loading" type="button" class="btn-outline" style="border-color: var(--alert); color: var(--alert)" @click="eliminarEmpleado">
            <UIcon name="i-heroicons-trash" class="w-4 h-4" /> Eliminar
          </button>
        </div>
      </div>

      <div v-if="loading" class="form-card flex items-center justify-center py-16"><UIcon name="i-heroicons-arrow-path" class="w-8 h-8 animate-spin" style="color: var(--teal)" /></div>
      <template v-else>
        <SFormCard title="Identificación Personal" subtitle="Datos de identidad y contacto"
          icon="i-heroicons-identification" icon-bg="var(--teal-soft)" icon-color="var(--teal)" :error="error">
          <div class="form-group">
            <label class="form-label">DNI</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-identification" class="input-icon" /><input :value="form.dni" disabled class="input-clinical font-mono-data" style="background: var(--mist)" /></div>
            <p class="field-hint">El DNI no puede modificarse</p>
          </div>
          <div class="form-group">
            <label class="form-label">Estado</label>
            <div class="status-toggle"><span class="toggle-label">Empleado Activo</span>
              <button type="button" @click="form.is_active = !form.is_active" class="toggle-switch" :class="{ 'toggle-active': form.is_active }"><span class="toggle-slider" /></button>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Nombres <span class="required">*</span></label>
            <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" /><input v-model="form.nombres" class="input-clinical" :class="{ 'input-error': errors.nombres }" /></div>
            <span v-if="errors.nombres" class="error-message">{{ errors.nombres }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">Apellido Paterno <span class="required">*</span></label>
            <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" /><input v-model="form.apellido_paterno" class="input-clinical" :class="{ 'input-error': errors.apellido_paterno }" /></div>
            <span v-if="errors.apellido_paterno" class="error-message">{{ errors.apellido_paterno }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">Apellido Materno <span class="required">*</span></label>
            <div class="input-wrapper"><UIcon name="i-heroicons-user" class="input-icon" /><input v-model="form.apellido_materno" class="input-clinical" :class="{ 'input-error': errors.apellido_materno }" /></div>
            <span v-if="errors.apellido_materno" class="error-message">{{ errors.apellido_materno }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">Fecha de Nacimiento</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_nacimiento" type="date" class="input-clinical" :class="{ 'input-error': errors.fecha_nacimiento }" /></div>
            <span v-if="errors.fecha_nacimiento" class="error-message">{{ errors.fecha_nacimiento }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">Sexo</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-arrows-right-left" class="input-icon" />
              <select v-model="form.sexo" class="input-clinical"><option value="">Seleccione</option><option value="M">Masculino</option><option value="F">Femenino</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Estado Civil</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-heart" class="input-icon" />
              <select v-model="form.estado_civil" class="input-clinical">
                <option value="">Seleccione</option><option value="soltero">Soltero(a)</option><option value="casado">Casado(a)</option>
                <option value="divorciado">Divorciado(a)</option><option value="viudo">Viudo(a)</option><option value="conviviente">Conviviente</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Grupo Sanguíneo</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-beaker" class="input-icon" />
              <select v-model="form.grupo_sanguineo" class="input-clinical"><option value="">Seleccione</option><option v-for="g in gruposSanguineos" :key="g" :value="g">{{ g }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Celular</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-phone" class="input-icon" />
              <input v-model="form.celular" class="input-clinical font-mono-data" maxlength="9" inputmode="numeric" :class="{ 'input-error': errors.celular }" @input="form.celular = form.celular.replace(/\D/g, '').slice(0, 9)" />
            </div>
            <span v-if="errors.celular" class="error-message">{{ errors.celular }}</span>
          </div>
          <div class="form-group">
            <label class="form-label">Teléfono Fijo</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-phone-arrow-up-right" class="input-icon" /><input v-model="form.telefono_fijo" class="input-clinical" /></div>
          </div>
          <div class="form-group full-width">
            <label class="form-label">Correo Electrónico</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-envelope" class="input-icon" /><input v-model="form.correo" type="email" class="input-clinical" :class="{ 'input-error': errors.correo }" /></div>
            <span v-if="errors.correo" class="error-message">{{ errors.correo }}</span>
          </div>
        </SFormCard>

        <SFormCard title="Clasificación Laboral" subtitle="Tipo de trabajador, nivel remunerativo, grupo ocupacional y cargo"
          icon="i-heroicons-briefcase" icon-bg="var(--navy-soft)" icon-color="var(--navy)">
          <div class="form-group">
            <label class="form-label">Tipo de Trabajador</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-user-group" class="input-icon" />
              <select v-model="form.tipo_trabajador_id" class="input-clinical"><option value="">Seleccione</option><option v-for="t in tiposTrabajador" :key="t.id" :value="t.id">{{ t.nombre }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Nivel Remunerativo</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-currency-dollar" class="input-icon" />
              <select v-model="form.nivel_remunerativo_id" class="input-clinical"><option value="">Seleccione</option><option v-for="n in nivelesRemunerativos" :key="n.id" :value="n.id">{{ n.nombre }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Grupo Ocupacional</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-chart-bar" class="input-icon" />
              <select v-model="form.grupo_ocupacional_id" class="input-clinical"><option value="">Seleccione</option><option v-for="g in gruposOcupacionales" :key="g.id" :value="g.id">{{ g.nombre }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Departamento</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-building-office" class="input-icon" />
              <select v-model="form.departamento_id" class="input-clinical"><option value="">Seleccione</option><option v-for="d in departamentos" :key="d.id" :value="d.id">{{ d.nombre }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Servicio / Área</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-folder" class="input-icon" />
              <select v-model="form.servicio_id" class="input-clinical"><option value="">Seleccione</option><option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Cargo Laboral</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-briefcase" class="input-icon" /><input v-model="form.cargo_laboral" class="input-clinical" maxlength="100" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Modalidad</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" />
              <select v-model="form.modalidad" class="input-clinical">
                <option value="">Seleccione...</option><option value="nombrado">Nombrado</option><option value="cas">CAS</option>
                <option value="contrato">Contrato</option><option value="snp">SNP</option><option value="tercero">Tercero</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Código MINSA</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-identification" class="input-icon" /><input v-model="form.codigo_minsa" class="input-clinical font-mono-data" maxlength="20" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">N° CMP</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-document" class="input-icon" /><input v-model="form.numero_cmp" class="input-clinical font-mono-data" maxlength="10" inputmode="numeric" @input="form.numero_cmp = form.numero_cmp.replace(/\D/g, '').slice(0, 10)" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Fecha de Ingreso</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_ingreso" type="date" class="input-clinical" :class="{ 'input-error': errors.fecha_ingreso }" /></div>
            <span v-if="errors.fecha_ingreso" class="error-message">{{ errors.fecha_ingreso }}</span>
            <p v-if="form.fecha_ingreso && !errors.fecha_ingreso" class="field-hint">Antigüedad: {{ calcularAntiguedad(form.fecha_ingreso) }}</p>
          </div>
          <div class="form-group">
            <label class="form-label">Resolución Nombramiento</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" /><input v-model="form.resolucion_nombramiento" class="input-clinical" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Fecha de Nombramiento</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_nombramiento" type="date" class="input-clinical" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Resolución de Cese</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" /><input v-model="form.resolucion_cese" class="input-clinical" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Fecha de Cese</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-calendar" class="input-icon" /><input v-model="form.fecha_cese" type="date" class="input-clinical" /></div>
          </div>
        </SFormCard>

        <SFormCard title="Especialidades" subtitle="Especialidades médicas del empleado"
          icon="i-heroicons-star" icon-bg="var(--purple-soft)" icon-color="var(--purple)">
          <div class="form-group full-width" v-for="(esp, i) in form.especialidades" :key="i">
            <div style="display: grid; grid-template-columns: 1fr 1fr auto auto; gap: 0.75rem; align-items: end; padding: 0.875rem; background: var(--mist); border-radius: 8px">
              <div>
                <label class="form-label">Especialidad</label>
                <div class="input-wrapper"><UIcon name="i-heroicons-star" class="input-icon" />
                  <select v-model="esp.especialidad_id" class="input-clinical" :disabled="!esp.nueva"><option value="">Seleccione</option><option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option></select>
                </div>
              </div>
              <div>
                <label class="form-label">N° RNE</label>
                <div class="input-wrapper"><UIcon name="i-heroicons-document-text" class="input-icon" /><input v-model="esp.numero_rne" class="input-clinical" :disabled="!esp.nueva" /></div>
              </div>
              <label class="text-xs flex items-center gap-1.5" style="color: var(--ink-soft); padding-bottom: 0.6rem"><input type="checkbox" v-model="esp.validado" :disabled="!esp.nueva" /> Validado</label>
              <button type="button" class="sigarh-action-btn danger" style="margin-bottom: 0.3rem" @click="quitarEspecialidad(i)"><UIcon name="i-heroicons-trash" class="w-4 h-4" style="color: var(--alert)" /></button>
            </div>
          </div>
          <div class="form-group full-width">
            <button type="button" class="btn-outline" @click="form.especialidades.push({ id: null, especialidad_id: '', numero_rne: '', validado: false, nueva: true })">
              <UIcon name="i-heroicons-plus" class="w-4 h-4" /> Agregar Especialidad
            </button>
          </div>
        </SFormCard>

        <SFormCard title="Datos Bancarios" subtitle="Cuenta para el pago de remuneraciones"
          icon="i-heroicons-banknotes" icon-bg="var(--amber-soft)" icon-color="var(--amber)">
          <div class="form-group">
            <label class="form-label">Banco</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-building-office-2" class="input-icon" />
              <select v-model="form.banco" class="input-clinical"><option value="">Seleccione un banco</option><option v-for="b in bancosPeru" :key="b" :value="b">{{ b }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">RUC</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-document" class="input-icon" /><input v-model="form.ruc" class="input-clinical font-mono-data" maxlength="11" inputmode="numeric" @input="form.ruc = form.ruc.replace(/\D/g, '').slice(0, 11)" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Número de Cuenta</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-credit-card" class="input-icon" /><input v-model="form.numero_cuenta" class="input-clinical font-mono-data" inputmode="numeric" placeholder="10 a 20 dígitos" @input="form.numero_cuenta = form.numero_cuenta.replace(/\D/g, '').slice(0, 20)" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Número CCI</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-credit-card" class="input-icon" /><input v-model="form.numero_cci" class="input-clinical font-mono-data" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Tipo de Cuenta</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-list-bullet" class="input-icon" />
              <select v-model="form.tipo_cuenta" class="input-clinical"><option value="">Seleccione</option><option value="ahorros">Ahorros</option><option value="corriente">Corriente</option></select>
            </div>
          </div>
        </SFormCard>

        <SFormCard title="Ubicación" subtitle="Domicilio del empleado"
          icon="i-heroicons-map-pin" icon-bg="var(--green-soft)" icon-color="var(--green)">
          <div class="form-group">
            <label class="form-label">Departamento</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-map-pin" class="input-icon" />
              <select v-model="form.departamento_ubigeo" class="input-clinical"><option value="">Seleccione</option><option v-for="d in ubigeoDepartamentos" :key="d.codigo" :value="d.codigo">{{ d.nombre }}</option></select>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">Provincia</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-map-pin" class="input-icon" /><input v-model="form.provincia_ubigeo" class="input-clinical" /></div>
          </div>
          <div class="form-group">
            <label class="form-label">Distrito</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-map-pin" class="input-icon" /><input v-model="form.distrito_ubigeo" class="input-clinical" /></div>
          </div>
          <div class="form-group full-width">
            <label class="form-label">Dirección</label>
            <div class="input-wrapper"><UIcon name="i-heroicons-home" class="input-icon" style="top: 0.75rem; transform: none;" /><textarea v-model="form.direccion" class="input-clinical" rows="2" maxlength="200" /></div>
          </div>
          <template #actions>
            <SFormActions :saving="saving" save-text="Guardar Cambios" saving-text="Guardando..."
              :cancel-to="`/sigarh/rrhh/empleados?tenant=${tenantId}`" @save="handleSave" />
          </template>
        </SFormCard>
      </template>
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
      <SWidgetInfo :items="['El DNI no puede modificarse', 'El correo debe seguir siendo único', 'Quitar una especialidad ya guardada la elimina de inmediato', 'Las especialidades nuevas se guardan al presionar Guardar Cambios']" />
      <SWidgetTip text="Para cesar a un empleado, registra la resolución y fecha de cese; el estado Activo controla si aparece en los selectores." />
    </template>
  </SFormLayout>
</template>
