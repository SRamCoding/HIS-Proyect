<template>
  <div class="max-w-4xl mx-auto">
    <div class="mb-6">
      <div class="flex items-center gap-2 text-sm mb-2" style="color: var(--ink-soft)">
        <NuxtLink :to="`/sigarh/rrhh/empleados?tenant=${tenantId}`" style="color: var(--ink-soft)">Empleados</NuxtLink>
        <span>/</span><span>Crear</span>
      </div>
      <h1 class="text-lg font-semibold" style="color: var(--ink)">Nuevo Empleado</h1>
    </div>

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
        @click="i < stepActual && (stepActual = i)"
      >
        <span v-if="stepActual > i" style="font-size: 12px">✓</span>
        {{ paso }}
      </div>
    </div>

    <!-- STEP 1: Datos Personales -->
    <div v-if="stepActual === 0" class="space-y-4">
      <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <p class="text-sm font-semibold mb-1" style="color: var(--ink)">Identificacion</p>
        <p class="text-xs mb-4" style="color: var(--ink-soft)">Ingrese el DNI y consulte el servicio para autocompletar nombres y apellidos.</p>

        <div class="flex items-center gap-3 mb-4">
          <input type="checkbox" v-model="registroManual" id="manual" />
          <label for="manual" class="text-sm" style="color: var(--ink)">Registro manual</label>
          <span class="text-xs" style="color: var(--ink-soft)">Active si el empleado no figura en el servicio de consulta DNI.</span>
        </div>

        <div class="flex items-end gap-3">
          <div class="flex-1">
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">DNI*</label>
            <input v-model="form.dni" class="input-clinical" placeholder="Ej: 76557726" maxlength="8" />
          </div>
          <button
            class="px-4 py-2 rounded text-sm font-medium flex items-center gap-2"
            style="background: var(--teal); color: white"
            :disabled="consultandoDni || form.dni.length !== 8"
            @click="consultarDni"
          >
            {{ consultandoDni ? 'Consultando...' : 'Consultar DNI' }}
          </button>
        </div>
        <p v-if="dniMsg" class="text-xs mt-2" :style="{ color: dniError ? 'var(--alert)' : 'var(--teal)' }">{{ dniMsg }}</p>
      </div>

      <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <p class="text-sm font-semibold mb-4" style="color: var(--ink)">Informacion Personal</p>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nombres*</label>
            <input v-model="form.nombres" class="input-clinical" :disabled="!registroManual && dniCargado" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Apellido Paterno*</label>
            <input v-model="form.apellido_paterno" class="input-clinical" :disabled="!registroManual && dniCargado" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Apellido Materno*</label>
            <input v-model="form.apellido_materno" class="input-clinical" :disabled="!registroManual && dniCargado" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha de Nacimiento*</label>
            <input v-model="form.fecha_nacimiento" type="date" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Sexo*</label>
            <select v-model="form.sexo" class="input-clinical">
              <option value="">Seleccione una opcion</option>
              <option value="M">Masculino</option>
              <option value="F">Femenino</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Estado Civil*</label>
            <select v-model="form.estado_civil" class="input-clinical">
              <option value="">Seleccione una opcion</option>
              <option value="soltero">Soltero(a)</option>
              <option value="casado">Casado(a)</option>
              <option value="divorciado">Divorciado(a)</option>
              <option value="viudo">Viudo(a)</option>
              <option value="conviviente">Conviviente</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Grupo Sanguineo*</label>
            <select v-model="form.grupo_sanguineo" class="input-clinical">
              <option value="">Seleccione una opcion</option>
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
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Celular*</label>
            <input v-model="form.celular" class="input-clinical" placeholder="+51" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Telefono Fijo</label>
            <input v-model="form.telefono_fijo" class="input-clinical" />
          </div>
          <div class="col-span-2">
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Correo Electronico*</label>
            <input v-model="form.correo" type="email" class="input-clinical" />
          </div>
        </div>
      </div>
    </div>

    <!-- STEP 2: Datos Laborales -->
    <div v-if="stepActual === 1" class="space-y-4">
      <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <p class="text-sm font-semibold mb-1" style="color: var(--ink)">Clasificacion Laboral</p>
        <p class="text-xs mb-4" style="color: var(--ink-soft)">Tipo de trabajador, nivel remunerativo y grupo ocupacional.</p>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Tipo de Trabajador*</label>
            <select v-model="form.tipo_trabajador_id" class="input-clinical">
              <option value="">Seleccione una opcion</option>
              <option v-for="t in tiposTrabajador" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Nivel Remunerativo*</label>
            <select v-model="form.nivel_remunerativo_id" class="input-clinical">
              <option value="">Seleccione una opcion</option>
              <option v-for="n in nivelesRemunerativos" :key="n.id" :value="n.id">{{ n.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Grupo Ocupacional*</label>
            <select v-model="form.grupo_ocupacional_id" class="input-clinical">
              <option value="">Seleccione una opcion</option>
              <option v-for="g in gruposOcupacionales" :key="g.id" :value="g.id">{{ g.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Departamento</label>
            <select v-model="form.departamento_id" class="input-clinical">
              <option value="">Seleccione una opcion</option>
              <option v-for="d in departamentos" :key="d.id" :value="d.id">{{ d.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Servicio / Area*</label>
            <select v-model="form.servicio_id" class="input-clinical">
              <option value="">Seleccione una opcion</option>
              <option v-for="s in servicios" :key="s.id" :value="s.id">{{ s.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Cargo Laboral*</label>
            <input v-model="form.cargo_laboral" class="input-clinical" placeholder="Ej: Medico Especialista" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Modalidad*</label>
            <input v-model="form.modalidad" class="input-clinical" placeholder="Ej: Nombrado" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Codigo Minsa</label>
            <input v-model="form.codigo_minsa" class="input-clinical" />
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">N° CMP</label>
            <input v-model="form.numero_cmp" class="input-clinical" />
            <p class="text-xs mt-1" style="color: var(--ink-soft)">Colegio Medico del Peru — solo para medicos.</p>
          </div>
        </div>
      </div>

      <!-- Resumen laboral -->
      <div v-if="form.cargo_laboral" class="p-4 rounded grid grid-cols-3 gap-4 text-xs" style="border: 1px solid var(--border-accent); background: var(--bg-accent)">
        <div>
          <p class="font-medium mb-1" style="color: var(--text-accent)">CARGO</p>
          <p style="color: var(--ink)">{{ form.cargo_laboral || '—' }}</p>
        </div>
        <div>
          <p class="font-medium mb-1" style="color: var(--text-accent)">TIPO TRABAJADOR</p>
          <p style="color: var(--ink)">{{ tiposTrabajador.find(t => t.id === form.tipo_trabajador_id)?.nombre || '—' }}</p>
        </div>
        <div>
          <p class="font-medium mb-1" style="color: var(--text-accent)">SERVICIO</p>
          <p style="color: var(--ink)">{{ servicios.find(s => s.id === form.servicio_id)?.nombre || '—' }}</p>
        </div>
        <div>
          <p class="font-medium mb-1" style="color: var(--text-accent)">NIVEL REMUNERATIVO</p>
          <p style="color: var(--ink)">{{ nivelesRemunerativos.find(n => n.id === form.nivel_remunerativo_id)?.nombre || '—' }}</p>
        </div>
      </div>

      <div class="p-5" style="background: var(--paper); border: 1px solid var(--line); border-radius: var(--radius)">
        <p class="text-sm font-semibold mb-1" style="color: var(--ink)">Resoluciones y Fechas</p>
        <p class="text-xs mb-4" style="color: var(--ink-soft)">Fechas y documentos de nombramiento, ingreso y cese.</p>
        <div class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Fecha de Ingreso*</label>
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

        <!-- Resumen fechas -->
        <div v-if="form.fecha_ingreso" class="mt-4 p-3 rounded grid grid-cols-3 gap-4 text-xs" style="border: 1px solid var(--border-accent); background: var(--bg-accent)">
          <div>
            <p class="font-medium mb-1" style="color: var(--text-accent)">FECHA DE INGRESO</p>
            <p style="color: var(--ink)">{{ form.fecha_ingreso }}</p>
          </div>
          <div>
            <p class="font-medium mb-1" style="color: var(--text-accent)">ANTIGUEDAD</p>
            <p style="color: var(--ink)">{{ calcularAntiguedad(form.fecha_ingreso) }}</p>
          </div>
          <div>
            <p class="font-medium mb-1" style="color: var(--text-accent)">ESTADO</p>
            <p style="color: var(--teal)">{{ form.fecha_cese ? 'Cesado' : 'En actividad' }}</p>
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
            <button style="color: var(--alert)" @click="form.especialidades.splice(i, 1)">🗑</button>
          </div>
          <div class="grid grid-cols-2 gap-3">
            <div>
              <label class="block text-xs font-medium mb-1" style="color: var(--ink)">Especialidad*</label>
              <select v-model="esp.especialidad_id" class="input-clinical">
                <option value="">Seleccione una opcion</option>
                <option v-for="e in especialidades" :key="e.id" :value="e.id">{{ e.nombre }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-medium mb-1" style="color: var(--ink)">N° RNE</label>
              <input v-model="esp.numero_rne" class="input-clinical" placeholder="Registro Nacional de Especialistas" />
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
          @click="form.especialidades.push({ especialidad_id: '', numero_rne: '', validado: false })"
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
            <input v-model="form.ruc" class="input-clinical" maxlength="11" placeholder="20123456789" />
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
              <option value="">Seleccione una opcion</option>
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
            <select v-model="form.departamento_ubigeo" class="input-clinical" @change="form.provincia_ubigeo = ''; form.distrito_ubigeo = ''">
              <option value="">Seleccione departamento</option>
              <option v-for="d in ubigeo.departamentos" :key="d.codigo" :value="d.codigo">{{ d.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Provincia</label>
            <select v-model="form.provincia_ubigeo" class="input-clinical" @change="form.distrito_ubigeo = ''">
              <option value="">Seleccione provincia</option>
              <option v-for="p in provinciasFiltradas" :key="p.codigo" :value="p.codigo">{{ p.nombre }}</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Distrito</label>
            <select v-model="form.distrito_ubigeo" class="input-clinical">
              <option value="">Seleccione distrito</option>
              <option v-for="d in distritosFiltrados" :key="d.codigo" :value="d.codigo">{{ d.nombre }}</option>
            </select>
          </div>
          <div class="col-span-2">
            <label class="block text-sm font-medium mb-1" style="color: var(--ink)">Direccion</label>
            <textarea v-model="form.direccion" class="input-clinical" rows="2" />
          </div>
        </div>
      </div>
    </div>

    <!-- Error -->
    <div v-if="error" class="mt-4 text-sm px-3 py-2 rounded" style="background: var(--alert-soft); color: var(--alert)">
      {{ error }}
    </div>

    <!-- Navegacion -->
    <div class="flex items-center justify-between mt-6">
      <div>
        <button v-if="stepActual > 0" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)" @click="stepActual--">
          Anterior
        </button>
        <NuxtLink v-else :to="`/sigarh/rrhh/empleados?tenant=${tenantId}`" class="px-4 py-2 rounded text-sm" style="border: 1px solid var(--line); color: var(--ink-soft)">
          Cancelar
        </NuxtLink>
      </div>
      <div class="flex gap-2">
        <button v-if="stepActual < pasos.length - 1" class="btn-primary" @click="stepActual++">
          Siguiente
        </button>
        <button v-else class="btn-primary" :disabled="saving" @click="handleCreate">
          {{ saving ? 'Guardando...' : 'Crear Empleado' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
definePageMeta({ layout: 'sigarh', middleware: ['auth'] })

const { api } = useApi()
const route = useRoute()
const router = useRouter()
const tenantId = computed(() => route.query.tenant as string || '')

const pasos = ['Datos Personales', 'Datos Laborales', 'Especialidades', 'Datos Bancarios', 'Ubicacion']
const stepActual = ref(0)
const saving = ref(false)
const error = ref('')
const registroManual = ref(false)
const dniCargado = ref(false)
const consultandoDni = ref(false)
const dniMsg = ref('')
const dniError = ref(false)

const gruposSanguineos = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']

const bancosPeru = [
  'Banco de la Nacion', 'BCP - Banco de Credito del Peru', 'BBVA Peru',
  'Interbank', 'Scotiabank Peru', 'BanBif', 'Banco Pichincha',
  'MiBanco', 'Banco GNB Peru', 'BCRP', 'Citibank Peru',
  'Banco Falabella', 'Banco Ripley', 'Banco Azteca', 'Compartamos Financiera',
]

// Catálogos
const tiposTrabajador = ref<any[]>([])
const nivelesRemunerativos = ref<any[]>([])
const gruposOcupacionales = ref<any[]>([])
const departamentos = ref<any[]>([])
const servicios = ref<any[]>([])
const especialidades = ref<any[]>([])

// Ubigeo simplificado
const ubigeo = reactive({
  departamentos: [
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
  ],
  provincias: [] as any[],
  distritos: [] as any[],
})

const provinciasFiltradas = computed(() =>
  ubigeo.provincias.filter(p => p.dep_codigo === form.departamento_ubigeo)
)
const distritosFiltrados = computed(() =>
  ubigeo.distritos.filter(d => d.prov_codigo === form.provincia_ubigeo)
)

const form = reactive({
  // Personales
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
  // Laborales
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
  // Especialidades
  especialidades: [] as any[],
  // Bancarios
  banco: '',
  ruc: '',
  numero_cuenta: '',
  numero_cci: '',
  tipo_cuenta: '',
  // Ubicacion
  departamento_ubigeo: '',
  provincia_ubigeo: '',
  distrito_ubigeo: '',
  direccion: '',
})

const calcularAntiguedad = (fecha: string) => {
  if (!fecha) return '—'
  const hoy = new Date()
  const ingreso = new Date(fecha)
  const diff = Math.floor((hoy.getTime() - ingreso.getTime()) / (1000 * 60 * 60 * 24))
  const years = Math.floor(diff / 365)
  const months = Math.floor((diff % 365) / 30)
  if (years > 0) return `hace ${years} año(s) ${months} mes(es)`
  return `hace ${months} mes(es)`
}

const consultarDni = async () => {
  // Por ahora simula la consulta — se conectará a RENIEC en el futuro
  consultandoDni.value = true
  dniMsg.value = ''
  dniError.value = false
  try {
    await new Promise(r => setTimeout(r, 800))
    dniMsg.value = 'Complete los datos manualmente o active el registro manual.'
    dniError.value = false
  } catch {
    dniMsg.value = 'No se pudo consultar el DNI. Active el registro manual.'
    dniError.value = true
  } finally {
    consultandoDni.value = false
  }
}

const handleCreate = async () => {
  saving.value = true
  error.value = ''
  try {
    const payload = {
      ...form,
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
    const created = await api<any>('/sigarh/rrhh/empleados', {
      method: 'POST',
      body: payload,
    })

    // Agregar especialidades si hay
    for (const esp of form.especialidades) {
      if (esp.especialidad_id) {
        await api(`/sigarh/rrhh/empleados/${created.id}/especialidades`, {
          method: 'POST',
          body: esp,
        })
      }
    }

    router.push(`/sigarh/rrhh/empleados?tenant=${tenantId.value}`)
  } catch (e: any) {
    error.value = e?.data?.detail || 'No se pudo crear el empleado'
    stepActual.value = 0
  } finally {
    saving.value = false
  }
}

onMounted(async () => {
  const [tt, nr, go, dep, ser, esp] = await Promise.all([
    api<any[]>('/sigarh/mantenimiento/tipos-trabajador'),
    api<any[]>('/sigarh/mantenimiento/niveles-remunerativos'),
    api<any[]>('/sigarh/mantenimiento/grupos-ocupacionales'),
    api<any[]>('/sigarh/mantenimiento/departamentos'),
    api<any[]>('/sigarh/mantenimiento/servicios'),
    api<any[]>('/sigarh/rrhh/especialidades'),
  ])
  tiposTrabajador.value = tt
  nivelesRemunerativos.value = nr
  gruposOcupacionales.value = go
  departamentos.value = dep
  servicios.value = ser
  especialidades.value = esp
})
</script>