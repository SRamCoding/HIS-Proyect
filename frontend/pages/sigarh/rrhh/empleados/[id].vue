<template>
  <div class="max-w-4xl mx-auto">
    <div class="flex items-center justify-between mb-6">
      <div>
        <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
          <NuxtLink :to="`/sigarh/rrhh/empleados?tenant=${tenantId}`" style="color: var(--ink-soft)">Empleados</NuxtLink>
          <span>/</span><span>Editar</span>
        </div>
        <h1 class="text-lg font-semibold" style="color: var(--ink)">Editar Empleado</h1>
      </div>
      <button class="px-4 py-2 rounded text-sm font-medium" style="background: var(--alert); color: white" @click="confirmarEliminar">
        Borrar
      </button>
    </div>

    <div v-if="loading" class="p-6 text-sm" style="color: var(--ink-soft)">Cargando...</div>

    <template v-else>
      <!-- Progreso -->
      <div class="mb-2 flex justify-between text-xs" style="color: var(--ink-soft)">
        <span>Paso {{ stepActual + 1 }} de {{ pasos.length }}: {{ pasos[stepActual] }}</span>
        <span>{{ Math.round(((stepActual + 1) / pasos.length) * 100) }}%</span>
      </div>
      <div class="mb-6 rounded-full overflow-hidden" style="height: 4px; background: var(--line)">
        <div class="h-full rounded-full transition-all" style="background: var(--teal)" :style="{ width: ((stepActual + 1) / pasos.length * 100) + '%' }" />
      </div>

      <!-- Tabs -->
      <div class="flex gap-0 mb-6 overflow-x-auto">
        <div
          v-for="(paso, i) in pasos"
          :key="i"
          class="flex items-center gap-2 px-4 py-2 text-sm flex-shrink-0 cursor-pointer"
          :style="{
            background: stepActual === i ? 'var(--teal)' : stepActual > i ? 'var(--bg-accent)' : 'var(--paper)',
            color: stepActual === i ? '#fff' : stepActual > i ? 'var(--text-accent)' : 'var(--ink-soft)',
            border: '1px solid var(--line)',
            borderRight: i < pasos.length - 1 ? 'none' : '1px solid var(--line)',
            borderRadius: i === 0 ? 'var(--radius) 0 0 var(--radius)' : i === pasos.length - 1 ? '0 var(--radius) var(--radius) 0' : '0',
          }"
          @click="stepActual = i"
        >
          <span v-if="stepActual > i" style="font-size: 12px">✓</span>
          {{ paso }}
        </div>
      </div>

      <!-- STEP 1: Datos Personales -->
      <div v-if="stepActual === 0" class="space-y-4">
        <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-sm font-semibold mb-4" style="color: var(--ink)">Identificacion</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">DNI*</label>
              <input v-model="form.dni" class="input-clinical" disabled style="opacity: 0.6" />
            </div>
          </div>
        </div>

        <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-sm font-semibold mb-4" style="color: var(--ink)">Informacion Personal</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nombres*</label>
              <input v-model="form.nombres" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Apellido Paterno*</label>
              <input v-model="form.apellido_paterno" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Apellido Materno*</label>
              <input v-model="form.apellido_materno" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha de Nacimiento</label>
              <input v-model="form.fecha_nacimiento" type="date" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Sexo</label>
              <select v-model="form.sexo" class="input-clinical">
                <option value="">Seleccione</option>
                <option value="M">Masculino</option>
                <option value="F">Femenino</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Estado Civil</label>
              <select v-model="form.estado_civil" class="input-clinical">
                <option value="">Seleccione</option>
                <option value="soltero">Soltero(a)</option>
                <option value="casado">Casado(a)</option>
                <option value="divorciado">Divorciado(a)</option>
                <option value="viudo">Viudo(a)</option>
                <option value="conviviente">Conviviente</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Grupo Sanguineo</label>
              <select v-model="form.grupo_sanguineo" class="input-clinical">
                <option value="">Seleccione</option>
                <option v-for="g in gruposSanguineos" :key="g" :value="g">{{ g }}</option>
              </select>
            </div>
            <div class="flex items-center gap-2 mt-4">
              <input type="checkbox" v-model="form.is_active" id="activo" />
              <label for="activo" class="text-sm" style="color: var(--ink)">Empleado Activo</label>
            </div>
          </div>
        </div>

        <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-sm font-semibold mb-4" style="color: var(--ink)">Informacion de Contacto</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Celular</label>
              <input v-model="form.celular" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Telefono Fijo</label>
              <input v-model="form.telefono_fijo" class="input-clinical" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Correo Electronico</label>
              <input v-model="form.correo" type="email" class="input-clinical" />
            </div>
          </div>
        </div>
      </div>

      <!-- STEP 2: Datos Laborales -->
      <div v-if="stepActual === 1" class="space-y-4">
        <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-sm font-semibold mb-4" style="color: var(--ink)">Clasificacion Laboral</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Tipo de Trabajador</label>
              <select v-model="form.tipo_trabajador_id" class="input-clinical">
                <option value="">Seleccione</option>
                <option v-for="t in tiposTrabajador" :key="t.id" :value="t.id">{{ t.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nivel Remunerativo</label>
              <select v-model="form.nivel_remunerativo_id" class="input-clinical">
                <option value="">Seleccione</option>
                <option v-for="n in nivelesRemunerativos" :key="n.id" :value="n.id">{{ n.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Grupo Ocupacional</label>
              <select v-model="form.grupo_ocupacional_id" class="input-clinical">
                <option value="">Seleccione</option>
                <option v-for="g in gruposOcupacionales" :key="g.id" :value="g.id">{{ g.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Departamento</label>
              <select v-model="form.departamento_id" class="input-clinical">
                <option value="">Seleccione</option>
                <option v-for="d in departamentos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Servicio / Area</label>
              <select v-model="form.servicio_id" class="input-clinical">
                <option value="">Seleccione</option>
                <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Cargo Laboral</label>
              <input v-model="form.cargo_laboral" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Modalidad</label>
              <input v-model="form.modalidad" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Codigo Minsa</label>
              <input v-model="form.codigo_minsa" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">N° CMP</label>
              <input v-model="form.numero_cmp" class="input-clinical" />
            </div>
          </div>
        </div>

        <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-sm font-semibold mb-4" style="color: var(--ink)">Resoluciones y Fechas</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha de Ingreso</label>
              <input v-model="form.fecha_ingreso" type="date" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Resolucion Nombramiento</label>
              <input v-model="form.resolucion_nombramiento" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha de Nombramiento</label>
              <input v-model="form.fecha_nombramiento" type="date" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Resolucion de Cese</label>
              <input v-model="form.resolucion_cese" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha de Cese</label>
              <input v-model="form.fecha_cese" type="date" class="input-clinical" />
            </div>
          </div>
        </div>
      </div>

      <!-- STEP 3: Especialidades -->
      <div v-if="stepActual === 2">
        <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-sm font-semibold mb-1" style="color: var(--ink)">Especialidades del Empleado</p>
          <p class="text-xs mb-4" style="color: var(--ink-soft)">Registre las especialidades medicas, numero RNE y documentos de certificacion.</p>

          <div v-for="(esp, i) in form.especialidades" :key="i" class="mb-4 p-4 rounded" style="border: 1px solid var(--line)">
            <div class="flex justify-between mb-3">
              <p class="text-xs font-medium" style="color: var(--ink-soft)">Especialidad {{ i + 1 }}</p>
              <button style="color: var(--alert)" @click="eliminarEsp(i, esp.id)">🗑</button>
            </div>
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--ink)">Especialidad*</label>
                <select v-model="esp.especialidad_id" class="input-clinical">
                  <option value="">Seleccione</option>
                  <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
                </select>
              </div>
              <div>
                <label class="block text-xs font-medium mb-1" style="color: var(--ink)">N° RNE</label>
                <input v-model="esp.numero_rne" class="input-clinical" />
              </div>
              <div class="flex items-center gap-2">
                <input type="checkbox" v-model="esp.validado" :id="`validado_${i}`" />
                <label :for="`validado_${i}`" class="text-sm" style="color: var(--ink)">Validado</label>
              </div>
            </div>
          </div>

          <button
            class="w-full py-2 text-sm rounded mt-2"
            style="border: 1px dashed var(--line); color: var(--ink-soft)"
            @click="form.especialidades.push({ id: null, especialidad_id: '', numero_rne: '', validado: false, nueva: true })"
          >
            + Agregar Especialidad
          </button>
        </div>
      </div>

      <!-- STEP 4: Datos Bancarios -->
      <div v-if="stepActual === 3">
        <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-sm font-semibold mb-4" style="color: var(--ink)">Datos Bancarios</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Banco</label>
              <select v-model="form.banco" class="input-clinical">
                <option value="">Seleccione un banco</option>
                <option v-for="b in bancosPeru" :key="b" :value="b">{{ b }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">RUC</label>
              <input v-model="form.ruc" class="input-clinical" maxlength="11" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Numero de Cuenta</label>
              <input v-model="form.numero_cuenta" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Numero CCI</label>
              <input v-model="form.numero_cci" class="input-clinical" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Tipo de Cuenta</label>
              <select v-model="form.tipo_cuenta" class="input-clinical">
                <option value="">Seleccione</option>
                <option value="ahorros">Ahorros</option>
                <option value="corriente">Corriente</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      <!-- STEP 5: Ubicacion -->
      <div v-if="stepActual === 4">
        <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
          <p class="text-sm font-semibold mb-4" style="color: var(--ink)">Ubicacion</p>
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Departamento</label>
              <select v-model="form.departamento_ubigeo" class="input-clinical">
                <option value="">Seleccione departamento</option>
                <option v-for="d in departamentosUbigeo" :key="d.codigo" :value="d.codigo">{{ d.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Provincia</label>
              <input v-model="form.provincia_ubigeo" class="input-clinical" placeholder="Codigo provincia" />
            </div>
            <div>
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Distrito</label>
              <input v-model="form.distrito_ubigeo" class="input-clinical" placeholder="Codigo distrito" />
            </div>
            <div class="col-span-2">
              <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Direccion</label>
              <textarea v-model="form.direccion" class="input-clinical" rows="2" />
            </div>
          </div>
        </div>
      </div>

      <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">{{ error }}</div>

      <!-- Navegacion -->
      <div class="flex items-center justify-between mt-6">
        <button v-if="stepActual > 0" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)" @click="stepActual--">
          Anterior
        </button>
        <NuxtLink v-else :to="`/sigarh/rrhh/empleados?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">
          Cancelar
        </NuxtLink>

        <div class="flex gap-2">
          <button v-if="stepActual < pasos.length - 1" class="btn-primary" @click="stepActual++">Siguiente</button>
          <button class="btn-primary" :disabled="saving" @click="handleSave">
            {{ saving ? 'Guardando...' : 'Guardar cambios' }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')
const id = computed(() => route.params.id as string)

const pasos = ['Datos Personales', 'Datos Laborales', 'Especialidades', 'Datos Bancarios', 'Ubicacion']
const stepActual = ref(0)
const loading = ref(true)
const saving = ref(false)
const error = ref('')

const gruposSanguineos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
const bancosPeru = [
  'Banco de la Nacion', 'BCP - Banco de Credito del Peru', 'BBVA Peru',
  'Interbank', 'Scotiabank Peru', 'BanBif', 'Banco Pichincha',
  'MiBanco', 'Banco GNB Peru', 'BCRP', 'Citibank Peru',
  'Banco Falabella', 'Banco Ripley', 'Banco Azteca', 'Compartamos Financiera',
]

const departamentosUbigeo = [
  { codigo: '01', nombre: 'Amazonas' }, { codigo: '02', nombre: 'Ancash' },
  { codigo: '03', nombre: 'Apurimac' }, { codigo: '04', nombre: 'Arequipa' },
  { codigo: '05', nombre: 'Ayacucho' }, { codigo: '06', nombre: 'Cajamarca' },
  { codigo: '07', nombre: 'Callao' }, { codigo: '08', nombre: 'Cusco' },
  { codigo: '09', nombre: 'Huancavelica' }, { codigo: '10', nombre: 'Huanuco' },
  { codigo: '11', nombre: 'Ica' }, { codigo: '12', nombre: 'Junin' },
  { codigo: '13', nombre: 'La Libertad' }, { codigo: '14', nombre: 'Lambayeque' },
  { codigo: '15', nombre: 'Lima' }, { codigo: '16', nombre: 'Loreto' },
  { codigo: '17', nombre: 'Madre de Dios' }, { codigo: '18', nombre: 'Moquegua' },
  { codigo: '19', nombre: 'Pasco' }, { codigo: '20', nombre: 'Piura' },
  { codigo: '21', nombre: 'Puno' }, { codigo: '22', nombre: 'San Martin' },
  { codigo: '23', nombre: 'Tacna' }, { codigo: '24', nombre: 'Tumbes' },
  { codigo: '25', nombre: 'Ucayali' },
]

const tiposTrabajador = ref<any[]>([])
const nivelesRemunerativos = ref<any[]>([])
const gruposOcupacionales = ref<any[]>([])
const departamentos = ref<any[]>([])
const servicios = ref<any[]>([])
const especialidades = ref<any[]>([])

const form = reactive({
  dni: '',
  nombres: '',
  apellido_paterno: '',
  apellido_materno: '',
  fecha_nacimiento: '',
  sexo: '',
  estado_civil: '',
  grupo_sanguineo: '',
  celular: '',
  telefono_fijo: '',
  correo: '',
  is_active: true,
  tipo_trabajador_id: '',
  nivel_remunerativo_id: '',
  grupo_ocupacional_id: '',
  departamento_id: '',
  servicio_id: '',
  cargo_laboral: '',
  modalidad: '',
  codigo_minsa: '',
  numero_cmp: '',
  fecha_ingreso: '',
  fecha_nombramiento: '',
  fecha_cese: '',
  resolucion_nombramiento: '',
  resolucion_cese: '',
  banco: '',
  ruc: '',
  numero_cuenta: '',
  numero_cci: '',
  tipo_cuenta: '',
  departamento_ubigeo: '',
  provincia_ubigeo: '',
  distrito_ubigeo: '',
  direccion: '',
  especialidades: [] as any[],
})

const eliminarEsp = async (i: number, espId: string | null) => {
  if (espId && !confirm('¿Eliminar esta especialidad?')) return
  if (espId) {
    await api(`/sigarh/rrhh/empleados/${id.value}/especialidades/${espId}`, { method: 'DELETE' })
  }
  form.especialidades.splice(i, 1)
}

const confirmarEliminar = async () => {
  if (!confirm('¿Eliminar este empleado? Esta accion no se puede deshacer.')) return
  try {
    await api(`/sigarh/rrhh/empleados/${id.value}`, { method: 'DELETE' })
    router.push(`/sigarh/rrhh/empleados?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo eliminar'
  }
}

const handleSave = async () => {
  saving.value = true
  error.value = ''
  try {
    await api(`/sigarh/rrhh/empleados/${id.value}`, {
      method: 'PATCH',
      body: {
        nombres: form.nombres,
        apellido_paterno: form.apellido_paterno,
        apellido_materno: form.apellido_materno,
        fecha_nacimiento: form.fecha_nacimiento || null,
        sexo: form.sexo || null,
        estado_civil: form.estado_civil || null,
        grupo_sanguineo: form.grupo_sanguineo || null,
        celular: form.celular || null,
        telefono_fijo: form.telefono_fijo || null,
        correo: form.correo || null,
        is_active: form.is_active,
        tipo_trabajador_id: form.tipo_trabajador_id || null,
        nivel_remunerativo_id: form.nivel_remunerativo_id || null,
        grupo_ocupacional_id: form.grupo_ocupacional_id || null,
        departamento_id: form.departamento_id || null,
        servicio_id: form.servicio_id || null,
        cargo_laboral: form.cargo_laboral || null,
        modalidad: form.modalidad || null,
        codigo_minsa: form.codigo_minsa || null,
        numero_cmp: form.numero_cmp || null,
        fecha_ingreso: form.fecha_ingreso || null,
        fecha_nombramiento: form.fecha_nombramiento || null,
        fecha_cese: form.fecha_cese || null,
        resolucion_nombramiento: form.resolucion_nombramiento || null,
        resolucion_cese: form.resolucion_cese || null,
        banco: form.banco || null,
        ruc: form.ruc || null,
        numero_cuenta: form.numero_cuenta || null,
        numero_cci: form.numero_cci || null,
        tipo_cuenta: form.tipo_cuenta || null,
        departamento_ubigeo: form.departamento_ubigeo || null,
        provincia_ubigeo: form.provincia_ubigeo || null,
        distrito_ubigeo: form.distrito_ubigeo || null,
        direccion: form.direccion || null,
      },
    })

    // Agregar especialidades nuevas
    for (const esp of form.especialidades) {
      if (esp.nueva && esp.especialidad_id) {
        await api(`/sigarh/rrhh/empleados/${id.value}/especialidades`, {
          method: 'POST',
          body: {
            especialidad_id: esp.especialidad_id,
            numero_rne: esp.numero_rne || null,
            validado: esp.validado,
          },
        })
      }
    }

    router.push(`/sigarh/rrhh/empleados?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo guardar'
  } finally {
    saving.value = false
  }
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

    // Cargar datos del empleado
    form.dni = data.dni
    form.nombres = data.nombres
    form.apellido_paterno = data.apellido_paterno
    form.apellido_materno = data.apellido_materno
    form.fecha_nacimiento = data.fecha_nacimiento || ''
    form.sexo = data.sexo || ''
    form.estado_civil = data.estado_civil || ''
    form.grupo_sanguineo = data.grupo_sanguineo || ''
    form.celular = data.celular || ''
    form.telefono_fijo = data.telefono_fijo || ''
    form.correo = data.correo || ''
    form.is_active = data.is_active
    form.tipo_trabajador_id = data.tipo_trabajador_id || ''
    form.nivel_remunerativo_id = data.nivel_remunerativo_id || ''
    form.grupo_ocupacional_id = data.grupo_ocupacional_id || ''
    form.departamento_id = data.departamento_id || ''
    form.servicio_id = data.servicio_id || ''
    form.cargo_laboral = data.cargo_laboral || ''
    form.modalidad = data.modalidad || ''
    form.codigo_minsa = data.codigo_minsa || ''
    form.numero_cmp = data.numero_cmp || ''
    form.fecha_ingreso = data.fecha_ingreso || ''
    form.fecha_nombramiento = data.fecha_nombramiento || ''
    form.fecha_cese = data.fecha_cese || ''
    form.resolucion_nombramiento = data.resolucion_nombramiento || ''
    form.resolucion_cese = data.resolucion_cese || ''
    form.banco = data.banco || ''
    form.ruc = data.ruc || ''
    form.numero_cuenta = data.numero_cuenta || ''
    form.numero_cci = data.numero_cci || ''
    form.tipo_cuenta = data.tipo_cuenta || ''
    form.departamento_ubigeo = data.departamento_ubigeo || ''
    form.provincia_ubigeo = data.provincia_ubigeo || ''
    form.distrito_ubigeo = data.distrito_ubigeo || ''
    form.direccion = data.direccion || ''
    form.especialidades = (data.especialidades || []).map((e: any) => ({
      id: e.id,
      especialidad_id: e.especialidad_id,
      numero_rne: e.numero_rne || '',
      validado: e.validado,
      nueva: false,
    }))

    tiposTrabajador.value = tt
    nivelesRemunerativos.value = nr
    gruposOcupacionales.value = go
    departamentos.value = dep
    servicios.value = ser
    especialidades.value = esp
  } catch (e: any) {
    error.value = 'No se pudo cargar el empleado'
  } finally {
    loading.value = false
  }
})
</script>